from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest

from agent.core.tool_broker import ToolBroker
from agent.messaging.macos_send import (
    MACOS_MESSAGE_SEND_ACTION,
    SEND_HISTORY_PATH,
    SEND_STATUS_PATH,
    execute_macos_message_send_action,
    macos_messages_status,
    run_live_send_probe,
)
from agent.safety.actions import ActionCenter, ActionCenterStore, ActionStatus
from agent.safety.approvals import ApprovalManager, ApprovalStore
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry


def _center(tmp_path: Path) -> ActionCenter:
    return ActionCenter(
        store=ActionCenterStore(tmp_path / "actions.json"),
        approval_store=ApprovalStore(tmp_path / "approvals.json"),
        audit_logger=AuditLogger(tmp_path / "action-audit.jsonl"),
        session_id="macos-messages-test",
        model="test-model",
    )


def _broker(tmp_path: Path, center: ActionCenter) -> ToolBroker:
    capabilities = {
        "messaging.draft.create": Capability("messaging.draft.create", RiskLevel.MEDIUM, default_enabled=True),
        "messaging.action.create_send": Capability("messaging.action.create_send", RiskLevel.MEDIUM, default_enabled=True),
        "messages.macos.status": Capability("messages.macos.status", RiskLevel.LOW, default_enabled=True),
        "messages.macos.allowed_recipients.manage": Capability(
            "messages.macos.allowed_recipients.manage",
            RiskLevel.MEDIUM,
            default_enabled=True,
        ),
        "messages.macos.live_send_probe": Capability(
            "messages.macos.live_send_probe",
            RiskLevel.CRITICAL,
            default_enabled=True,
            approval_required="per_action",
            approval_reuse_allowed=False,
        ),
        "messages.macos.send_approved": Capability(
            "messages.macos.send_approved",
            RiskLevel.CRITICAL,
            default_enabled=True,
            approval_required="per_action",
            approval_reuse_allowed=False,
        ),
    }
    return ToolBroker(
        default_registry(project_root=tmp_path, action_center=center),
        PolicyEngine(capabilities),
        AuditLogger(tmp_path / "broker-audit.jsonl"),
        session_id="broker-session",
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


def _create_macos_action(broker: ToolBroker, center: ActionCenter, *, to: str = "+15555555555") -> str:
    draft_result = broker.execute(
        _call(
            "messaging.draft.create",
            {
                "channel": "macos_messages",
                "to": to,
                "body": "Reviewed iMessage body.",
                "source_context": {"source": "trusted_user", "requested_by": "test"},
            },
        )
    )
    assert draft_result.allowed is True
    draft_id = json.loads(draft_result.content)["draft_id"]
    action_result = broker.execute(_call("messaging.action.create_send", {"draft_id": draft_id}))
    assert action_result.allowed is True
    action_id = json.loads(action_result.content)["action"]["action_id"]
    action = center.get_action(action_id)
    assert action is not None
    assert action.action_type == MACOS_MESSAGE_SEND_ACTION
    return action_id


def _fake_success(command):
    return subprocess.CompletedProcess(list(command), 0, stdout="", stderr="")


def _fake_failure(command):
    return subprocess.CompletedProcess(list(command), 1, stdout="", stderr="Not authorized to send Apple events.")


def _write_passing_probe(tmp_path: Path) -> None:
    path = tmp_path / SEND_STATUS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "status": "passed",
                "passed": True,
                "timestamp": datetime.now(UTC).isoformat(),
                "send_capability_known": True,
                "private_messages_db_accessed": False,
                "full_disk_access_required": False,
            }
        ),
        encoding="utf-8",
    )


def _enable_env(monkeypatch: pytest.MonkeyPatch, *, max_sends: str = "5") -> None:
    monkeypatch.setenv("MACOS_MESSAGES_ENABLED", "true")
    monkeypatch.setenv("MACOS_MESSAGES_ALLOW_SEND", "true")
    monkeypatch.setenv("MACOS_MESSAGES_REQUIRE_LIVE_PROBE", "true")
    monkeypatch.setenv("MACOS_MESSAGES_MAX_SENDS_PER_DAY", max_sends)


def test_send_disabled_by_default(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("MACOS_MESSAGES_ENABLED", raising=False)
    monkeypatch.delenv("MACOS_MESSAGES_ALLOW_SEND", raising=False)

    status = macos_messages_status(tmp_path)

    assert status["connector_enabled"] is False
    assert status["send_allowed"] is False
    assert status["send_capability_enabled"] is False


def test_macos_send_action_is_critical_exact_and_no_reuse(tmp_path) -> None:
    center = _center(tmp_path)
    broker = _broker(tmp_path, center)

    action_id = _create_macos_action(broker, center)
    action = center.get_action(action_id)

    assert action is not None
    assert action.risk_level is RiskLevel.CRITICAL
    assert action.approval_required == "per_action"
    assert action.approval_reuse_allowed is False
    assert action.preview["exact_preview"]["channel"] == "macos_messages"
    assert action.preview["exact_preview"]["body"] == "Reviewed iMessage body."
    assert action.preview["exact_preview"]["approval_reuse_allowed"] is False
    assert action.preview["exact_preview"]["rollback"] == "impossible_after_send"


def test_send_requires_approved_action(tmp_path) -> None:
    center = _center(tmp_path)
    broker = _broker(tmp_path, center)
    action_id = _create_macos_action(broker, center)

    report = execute_macos_message_send_action(broker, center, action_id=action_id)

    assert report["status"] == "error"
    assert "approved in Action Center" in report["error"]
    assert center.get_action(action_id).status is ActionStatus.PENDING


def test_send_requires_allowlisted_recipient(tmp_path, monkeypatch) -> None:
    _enable_env(monkeypatch)
    _write_passing_probe(tmp_path)
    monkeypatch.setattr("agent.messaging.macos_send.platform.system", lambda: "Darwin")
    monkeypatch.setattr("agent.messaging.macos_send.shutil.which", lambda name: "/usr/bin/osascript")
    monkeypatch.setattr("agent.messaging.macos_send._run_command", _fake_success)
    center = _center(tmp_path)
    broker = _broker(tmp_path, center)
    action_id = _create_macos_action(broker, center)
    center.approve(action_id)

    report = execute_macos_message_send_action(broker, center, action_id=action_id)

    assert report["status"] == "error"
    assert "allowlisted" in report["tool_result"]["error"]


def test_send_requires_recent_live_probe(tmp_path, monkeypatch) -> None:
    _enable_env(monkeypatch)
    broker_center = _center(tmp_path)
    broker = _broker(tmp_path, broker_center)
    broker.execute(_call("messages.macos.allowed_recipients.manage", {"recipient": "+15555555555"}))
    action_id = _create_macos_action(broker, broker_center)
    broker_center.approve(action_id)

    report = execute_macos_message_send_action(broker, broker_center, action_id=action_id)

    assert report["status"] == "error"
    assert "live-send probe" in report["tool_result"]["error"]


def test_approved_send_executes_once_and_consumes_approval(tmp_path, monkeypatch) -> None:
    _enable_env(monkeypatch)
    _write_passing_probe(tmp_path)
    monkeypatch.setattr("agent.messaging.macos_send.platform.system", lambda: "Darwin")
    monkeypatch.setattr("agent.messaging.macos_send.shutil.which", lambda name: "/usr/bin/osascript")
    monkeypatch.setattr("agent.messaging.macos_send._run_command", _fake_success)
    center = _center(tmp_path)
    broker = _broker(tmp_path, center)
    broker.execute(_call("messages.macos.allowed_recipients.manage", {"recipient": "+15555555555"}))
    action_id = _create_macos_action(broker, center)
    center.approve(action_id)

    first = execute_macos_message_send_action(broker, center, action_id=action_id)
    second = execute_macos_message_send_action(broker, center, action_id=action_id)

    assert first["status"] == "ok"
    assert first["tool_result"]["sent"] is True
    assert center.get_action(action_id).status is ActionStatus.USED
    assert second["status"] == "error"
    assert "approved in Action Center" in second["error"]
    assert (tmp_path / SEND_HISTORY_PATH).exists()


def test_rate_limit_enforced(tmp_path, monkeypatch) -> None:
    _enable_env(monkeypatch, max_sends="1")
    _write_passing_probe(tmp_path)
    monkeypatch.setattr("agent.messaging.macos_send.platform.system", lambda: "Darwin")
    monkeypatch.setattr("agent.messaging.macos_send.shutil.which", lambda name: "/usr/bin/osascript")
    monkeypatch.setattr("agent.messaging.macos_send._run_command", _fake_success)
    center = _center(tmp_path)
    broker = _broker(tmp_path, center)
    broker.execute(_call("messages.macos.allowed_recipients.manage", {"recipient": "+15555555555"}))
    first_action = _create_macos_action(broker, center)
    center.approve(first_action)
    assert execute_macos_message_send_action(broker, center, action_id=first_action)["status"] == "ok"
    second_action = _create_macos_action(broker, center)
    center.approve(second_action)

    second = execute_macos_message_send_action(broker, center, action_id=second_action)

    assert second["status"] == "error"
    assert "rate limit" in second["tool_result"]["error"]


def test_non_interactive_action_center_execution_blocked(tmp_path) -> None:
    center = _center(tmp_path)
    broker = _broker(tmp_path, center)
    action_id = _create_macos_action(broker, center)

    gate = center.execution_gate(action_id, interactive=False)

    assert gate["allowed"] is False
    assert "non-interactive" in gate["reason"]


def test_unsupported_platform_returns_clear_error(tmp_path, monkeypatch) -> None:
    _enable_env(monkeypatch)
    _write_passing_probe(tmp_path)
    monkeypatch.setattr("agent.messaging.macos_send.platform.system", lambda: "Linux")
    center = _center(tmp_path)
    broker = _broker(tmp_path, center)
    broker.execute(_call("messages.macos.allowed_recipients.manage", {"recipient": "+15555555555"}))
    action_id = _create_macos_action(broker, center)
    center.approve(action_id)

    report = execute_macos_message_send_action(broker, center, action_id=action_id)

    assert report["status"] == "error"
    assert "supported only on macOS" in report["tool_result"]["error"]


def test_probe_failure_records_limitation_and_keeps_send_disabled(tmp_path, monkeypatch) -> None:
    _enable_env(monkeypatch)
    monkeypatch.setenv("MACOS_MESSAGES_SELF_TEST_RECIPIENT", "+15555555555")
    center = _center(tmp_path)
    broker = _broker(tmp_path, center)
    broker.execute(_call("messages.macos.allowed_recipients.manage", {"recipient": "+15555555555"}))
    monkeypatch.setattr("agent.messaging.macos_send.shutil.which", lambda name: "/usr/bin/osascript")

    result = run_live_send_probe(tmp_path, to="+15555555555", runner=_fake_failure, platform_name="Darwin")
    status = macos_messages_status(tmp_path)

    assert result["passed"] is False
    assert result["send_capability_known"] is False
    assert status["send_capability_enabled"] is False
    assert "unsupported" in result["status"]


def test_no_private_messages_db_access_or_bulk_send(tmp_path, monkeypatch) -> None:
    _enable_env(monkeypatch)
    center = _center(tmp_path)
    broker = _broker(tmp_path, center)

    bulk = broker.execute(
        _call(
            "messaging.draft.create",
            {"channel": "macos_messages", "to": "+15555555555,+16666666666", "body": "Hi"},
        )
    )

    assert bulk.allowed is False
    assert "multiple recipients" in json.loads(bulk.content)["error"]
    assert not (tmp_path / "Library" / "Messages").exists()
    assert "~/Library/Messages" not in (tmp_path / "broker-audit.jsonl").read_text(encoding="utf-8")


def test_audit_logs_attempts_without_raw_body(tmp_path, monkeypatch) -> None:
    _enable_env(monkeypatch)
    _write_passing_probe(tmp_path)
    monkeypatch.setattr("agent.messaging.macos_send.platform.system", lambda: "Darwin")
    monkeypatch.setattr("agent.messaging.macos_send.shutil.which", lambda name: "/usr/bin/osascript")
    monkeypatch.setattr("agent.messaging.macos_send._run_command", _fake_success)
    center = _center(tmp_path)
    broker = _broker(tmp_path, center)
    broker.execute(_call("messages.macos.allowed_recipients.manage", {"recipient": "+15555555555"}))
    action_id = _create_macos_action(broker, center)
    center.approve(action_id)

    report = execute_macos_message_send_action(broker, center, action_id=action_id)

    assert report["status"] == "ok"
    audit = (tmp_path / "broker-audit.jsonl").read_text(encoding="utf-8")
    assert "messages.macos.send_approved" in audit
    assert "Reviewed iMessage body." not in audit
    assert "osascript -e <Messages send script redacted>" in audit
