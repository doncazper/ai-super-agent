from __future__ import annotations

import json

from agent.config.loader import load_capabilities_config
from agent.core.tool_broker import ToolBroker
from agent.safety.actions import ActionCenter, ActionCenterStore, ActionStatus
from agent.safety.approvals import ApprovalStore
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry
from agent.workflows.contact_edits import (
    CONTACT_CREATE_ACTION,
    CONTACT_UPDATE_ACTION,
    draft_contact_create,
    draft_contact_update,
    execute_contact_action,
)


CONTACT_CAPABILITIES = {
    CONTACT_UPDATE_ACTION: Capability(
        CONTACT_UPDATE_ACTION,
        RiskLevel.CRITICAL,
        default_enabled=True,
        approval_required="per_action",
        approval_reuse_allowed=False,
    ),
    CONTACT_CREATE_ACTION: Capability(
        CONTACT_CREATE_ACTION,
        RiskLevel.CRITICAL,
        default_enabled=True,
        approval_required="per_action",
        approval_reuse_allowed=False,
    ),
}


def _center(tmp_path) -> ActionCenter:
    return ActionCenter(
        store=ActionCenterStore(tmp_path / "actions.json"),
        approval_store=ApprovalStore(tmp_path / "approvals.json"),
        audit_logger=AuditLogger(tmp_path / "action-audit.jsonl"),
        session_id="test-session",
        model="test-model",
    )


def _broker(tmp_path, *, enabled: bool = True) -> ToolBroker:
    capabilities = {
        name: Capability(
            capability.name,
            capability.risk_level,
            default_enabled=enabled,
            approval_required=capability.approval_required,
            approval_reuse_allowed=capability.approval_reuse_allowed,
        )
        for name, capability in CONTACT_CAPABILITIES.items()
    }
    return ToolBroker(
        default_registry(project_root=tmp_path),
        PolicyEngine(capabilities),
        AuditLogger(tmp_path / "broker-audit.jsonl"),
        session_id="broker-session",
        model="test-model",
        route="test",
    )


def _call(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    return {
        "id": f"call_{tool_name}",
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments)},
    }


def test_contacts_write_capabilities_disabled_by_default() -> None:
    tools = load_capabilities_config("config/capabilities.yaml")["tools"]

    for name in (CONTACT_UPDATE_ACTION, CONTACT_CREATE_ACTION):
        assert tools[name]["default_enabled"] is False
        assert tools[name]["risk_level"] == "CRITICAL"
        assert tools[name]["approval_required"] == "per_action"
        assert tools[name]["approval_reuse_allowed"] is False


def test_contact_update_creates_pending_action_with_field_diff(tmp_path) -> None:
    action = draft_contact_update(
        _center(tmp_path),
        selected_scope_token="person-1",
        changes={"company": "NewCo"},
        old_values={"company": "OldCo"},
    )

    assert action.status is ActionStatus.PENDING
    assert action.action_type == CONTACT_UPDATE_ACTION
    assert action.preview["title"] == "Contact update"
    assert action.sanitized_args["field_diff"][0] == {
        "field": "company",
        "old": "OldCo",
        "new": "NewCo",
        "sensitive": False,
    }


def test_contact_update_requires_approval(tmp_path) -> None:
    center = _center(tmp_path)
    action = draft_contact_update(center, selected_scope_token="person-1", changes={"company": "NewCo"})

    report = execute_contact_action(
        _broker(tmp_path),
        center,
        action_id=action.action_id,
        expected_action_type=CONTACT_UPDATE_ACTION,
    )

    assert report["status"] == "error"
    assert report["executed"] is False
    assert "approved" in report["error"]


def test_denial_prevents_contact_write(tmp_path) -> None:
    center = _center(tmp_path)
    action = draft_contact_update(center, selected_scope_token="person-1", changes={"company": "NewCo"})
    center.deny(action.action_id)

    report = execute_contact_action(
        _broker(tmp_path),
        center,
        action_id=action.action_id,
        expected_action_type=CONTACT_UPDATE_ACTION,
    )

    assert report["status"] == "error"
    assert report["executed"] is False
    assert report["action_status"] == "denied"


def test_approved_contact_update_executes_once_with_stub_and_no_memory_write(tmp_path) -> None:
    center = _center(tmp_path)
    action = draft_contact_update(center, selected_scope_token="person-1", changes={"company": "NewCo"})
    center.approve(action.action_id)

    first = execute_contact_action(
        _broker(tmp_path),
        center,
        action_id=action.action_id,
        expected_action_type=CONTACT_UPDATE_ACTION,
    )
    second = execute_contact_action(
        _broker(tmp_path),
        center,
        action_id=action.action_id,
        expected_action_type=CONTACT_UPDATE_ACTION,
    )

    assert first["status"] == "ok"
    assert first["executed"] is True
    assert first["tool_result"]["executed"] is False
    assert first["tool_result"]["connector_configured"] is False
    assert first["tool_result"]["stored_in_memory"] is False
    assert first["action_status"] == "used"
    assert second["status"] == "error"


def test_contact_create_is_action_center_stub(tmp_path) -> None:
    center = _center(tmp_path)
    action = draft_contact_create(center, display_name="Sam Example", fields={"company": "ExampleCo"})
    center.approve(action.action_id)

    report = execute_contact_action(
        _broker(tmp_path),
        center,
        action_id=action.action_id,
        expected_action_type=CONTACT_CREATE_ACTION,
    )

    assert report["status"] == "ok"
    assert report["tool_result"]["created"] is False
    assert report["tool_result"]["stored_in_memory"] is False


def test_sensitive_phone_email_address_values_redacted_in_action_and_audit(tmp_path) -> None:
    center = _center(tmp_path)
    action = draft_contact_update(
        center,
        selected_scope_token="person-1",
        changes={"email": "sam@example.com", "phone": "555-0100", "address": "1 Main St"},
        old_values={"email": "old@example.com", "phone": "555-0000", "address": "Old Address"},
    )
    center.approve(action.action_id)
    execute_contact_action(_broker(tmp_path), center, action_id=action.action_id, expected_action_type=CONTACT_UPDATE_ACTION)

    assert "[CONTACT_FIELD_REDACTED]" in json.dumps(action.to_dict())
    assert "sam@example.com" not in json.dumps(action.to_dict())
    broker_log = (tmp_path / "broker-audit.jsonl").read_text(encoding="utf-8")
    assert "[CONTACT_FIELD_REDACTED]" in broker_log
    assert "sam@example.com" not in broker_log
    assert "555-0100" not in broker_log


def test_bulk_contact_edit_denied_at_draft_time(tmp_path) -> None:
    try:
        draft_contact_update(_center(tmp_path), selected_scope_token="all", changes={"company": "NewCo"})
    except ValueError as exc:
        assert "bulk edit is denied" in str(exc)
    else:
        raise AssertionError("bulk contact edit should be denied")


def test_contact_delete_remains_deferred_not_registered() -> None:
    assert default_registry().get("contacts.delete") is None


def test_contact_write_disabled_policy_denies_direct_tool_execution(tmp_path) -> None:
    result = _broker(tmp_path, enabled=False).execute(
        _call(CONTACT_UPDATE_ACTION, {"selected_scope_token": "person-1", "changes": {"company": "NewCo"}})
    )

    assert result.allowed is False
    assert json.loads(result.content)["decision"] == "DENY"


def test_contact_write_audits_draft_approval_and_write(tmp_path) -> None:
    center = _center(tmp_path)
    action = draft_contact_update(center, selected_scope_token="person-1", changes={"company": "NewCo"})
    center.approve(action.action_id)
    execute_contact_action(_broker(tmp_path), center, action_id=action.action_id, expected_action_type=CONTACT_UPDATE_ACTION)

    action_events = [json.loads(line)["tool_name"] for line in (tmp_path / "action-audit.jsonl").read_text(encoding="utf-8").splitlines()]
    broker_events = [json.loads(line)["tool_name"] for line in (tmp_path / "broker-audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert "action.created" in action_events
    assert "action.approved" in action_events
    assert "action.used" in action_events
    assert CONTACT_UPDATE_ACTION in broker_events
