from __future__ import annotations

import json

from agent.core.tool_broker import ToolBroker
from agent.messaging.actions import create_message_draft
from agent.messaging.handoff_payloads import load_handoff_payload
from agent.safety.actions import ActionCenter, ActionCenterStore
from agent.safety.approvals import ApprovalManager, ApprovalStore
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry


def _center(tmp_path) -> ActionCenter:
    return ActionCenter(
        store=ActionCenterStore(tmp_path / "actions.json"),
        approval_store=ApprovalStore(tmp_path / "approvals.json"),
        audit_logger=AuditLogger(tmp_path / "action-audit.jsonl"),
        session_id="ios-compose-test",
        model="test-model",
    )


def _broker(tmp_path, center: ActionCenter | None = None) -> ToolBroker:
    capabilities = {
        "messaging.draft.create": Capability("messaging.draft.create", RiskLevel.MEDIUM, default_enabled=True),
        "messaging.action.create_send": Capability("messaging.action.create_send", RiskLevel.MEDIUM, default_enabled=True),
        "messaging.ios_compose.create_handoff": Capability(
            "messaging.ios_compose.create_handoff",
            RiskLevel.MEDIUM,
            default_enabled=True,
        ),
        "messaging.ios_compose.record_result": Capability(
            "messaging.ios_compose.record_result",
            RiskLevel.MEDIUM,
            default_enabled=True,
        ),
        "messaging.ios_compose.status": Capability("messaging.ios_compose.status", RiskLevel.LOW, default_enabled=True),
    }
    return ToolBroker(
        default_registry(project_root=tmp_path, action_center=center),
        PolicyEngine(capabilities),
        AuditLogger(tmp_path / "broker-audit.jsonl"),
        session_id="ios-compose-broker",
        model="test-model",
        route="test",
        approval_manager=ApprovalManager(),
    )


def _call(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    return {
        "id": f"call_{tool_name}",
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments)},
    }


def _create_draft(broker: ToolBroker, **overrides) -> str:
    args = {
        "channel": "ios_compose",
        "to": "+15551234567",
        "body": "Reviewed iOS compose body.",
        "source_context": {"source": "trusted_user", "requested_by": "user"},
    }
    args.update(overrides)
    result = broker.execute(_call("messaging.draft.create", args))
    payload = json.loads(result.content)
    assert result.allowed is True
    return payload["draft_id"]


def _create_approved_action(tmp_path, broker: ToolBroker, center: ActionCenter, draft_id: str) -> str:
    result = broker.execute(_call("messaging.action.create_send", {"draft_id": draft_id}))
    assert result.allowed is True
    action_id = json.loads(result.content)["action"]["action_id"]
    center.approve(action_id)
    return action_id


def test_handoff_payload_created_from_approved_draft(tmp_path) -> None:
    center = _center(tmp_path)
    broker = _broker(tmp_path, center)
    draft_id = _create_draft(broker, body="Exact iOS body.")
    action_id = _create_approved_action(tmp_path, broker, center, draft_id)

    result = broker.execute(
        _call(
            "messaging.ios_compose.create_handoff",
            {"draft_id": draft_id, "action_id": action_id, "compose_only": False},
        )
    )

    payload = json.loads(result.content)
    handoff = payload["handoff_payload"]
    assert result.allowed is True
    assert handoff["draft_id"] == draft_id
    assert handoff["action_id"] == action_id
    assert handoff["recipient"] == "+15551234567"
    assert handoff["body"] == "Exact iOS body."
    assert handoff["requires_user_tap_send"] is True
    assert handoff["silent_send_supported"] is False
    assert handoff["send_executed"] is False
    assert handoff["integrity_hash"]
    assert load_handoff_payload(tmp_path, draft_id).integrity_hash == handoff["integrity_hash"]


def test_unapproved_draft_blocked_unless_compose_only_mode_allowed(tmp_path) -> None:
    broker = _broker(tmp_path, _center(tmp_path))
    draft_id = _create_draft(broker)

    blocked = broker.execute(
        _call("messaging.ios_compose.create_handoff", {"draft_id": draft_id, "compose_only": False})
    )
    allowed = broker.execute(
        _call("messaging.ios_compose.create_handoff", {"draft_id": draft_id, "compose_only": True})
    )

    assert blocked.allowed is False
    assert "approved Action Center action or compose-only mode" in json.loads(blocked.content)["error"]
    assert allowed.allowed is True
    assert json.loads(allowed.content)["handoff_payload"]["approval_status"] == "user_confirmed_compose_mode"


def test_payload_expires_and_blocks_late_sent_result(tmp_path) -> None:
    broker = _broker(tmp_path, _center(tmp_path))
    draft_id = _create_draft(broker)
    result = broker.execute(
        _call(
            "messaging.ios_compose.create_handoff",
            {"draft_id": draft_id, "compose_only": True, "expires_minutes": -1},
        )
    )
    assert result.allowed is True

    status = broker.execute(_call("messaging.ios_compose.status", {"draft_id": draft_id}))
    late_sent = broker.execute(_call("messaging.ios_compose.record_result", {"draft_id": draft_id, "result": "sent"}))

    status_payload = json.loads(status.content)
    assert status_payload["payload_expired"] is True
    assert status_payload["handoff_payload"]["body"] == "[REDACTED_STATUS_PREVIEW]"
    assert late_sent.allowed is False
    assert "expired" in json.loads(late_sent.content)["error"]


def test_body_or_recipient_mismatch_rejected_after_approval(tmp_path) -> None:
    center = _center(tmp_path)
    broker = _broker(tmp_path, center)
    draft_id = _create_draft(broker, draft_id="ios-compose-1", body="Original exact body.")
    action_id = _create_approved_action(tmp_path, broker, center, draft_id)
    create_message_draft(
        str(tmp_path),
        channel="ios_compose",
        recipient="+15551234567",
        body="Edited after approval.",
        draft_id="ios-compose-1",
    )

    result = broker.execute(
        _call("messaging.ios_compose.create_handoff", {"draft_id": draft_id, "action_id": action_id})
    )

    assert result.allowed is False
    assert "does not match approved preview" in json.loads(result.content)["error"]


def test_sent_cancelled_and_failed_results_recorded(tmp_path) -> None:
    broker = _broker(tmp_path, _center(tmp_path))
    for status in ("sent", "cancelled", "failed"):
        draft_id = _create_draft(broker, body=f"Body for {status}")
        broker.execute(_call("messaging.ios_compose.create_handoff", {"draft_id": draft_id, "compose_only": True}))

        result = broker.execute(
            _call(
                "messaging.ios_compose.record_result",
                {"draft_id": draft_id, "result": status, "provider_message_id": f"ios-{status}"},
            )
        )

        payload = json.loads(result.content)
        assert result.allowed is True
        assert payload["compose_result"]["result"] == status
        assert payload["compose_result"]["send_marked_complete"] is (status == "sent")
        assert payload["send_executed_by_agent"] is False


def test_audit_logs_payload_creation_and_result(tmp_path) -> None:
    broker = _broker(tmp_path, _center(tmp_path))
    draft_id = _create_draft(broker)

    broker.execute(_call("messaging.ios_compose.create_handoff", {"draft_id": draft_id, "compose_only": True}))
    broker.execute(_call("messaging.ios_compose.record_result", {"draft_id": draft_id, "result": "cancelled"}))

    audit = (tmp_path / "broker-audit.jsonl").read_text(encoding="utf-8")
    assert "messaging.ios_compose.create_handoff" in audit
    assert "messaging.ios_compose.record_result" in audit
    assert "no send executed" in audit


def test_no_silent_send_path_exists(tmp_path) -> None:
    registry = default_registry(project_root=tmp_path, action_center=_center(tmp_path))

    assert registry.get("messaging.ios_compose.send") is None
    assert registry.get("messaging.send_approved") is None
