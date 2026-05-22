from __future__ import annotations

import json

from agent.core.tool_broker import ToolBroker
from agent.safety.audit import AuditLogger
from agent.safety.policy import PolicyDecision, PolicyEngine
from agent.tools.registry import default_registry


def make_broker(tmp_path) -> ToolBroker:
    return ToolBroker(
        default_registry(),
        PolicyEngine(),
        AuditLogger(tmp_path / "audit.jsonl"),
        session_id="test-session",
        model="test-model",
        route="test",
    )


def test_get_current_time_is_allowed(tmp_path) -> None:
    broker = make_broker(tmp_path)

    result = broker.execute(
        {
            "id": "call_1",
            "type": "function",
            "function": {
                "name": "time.get_current_time",
                "arguments": json.dumps({"timezone": "UTC"}),
            },
        }
    )

    assert result.allowed is True
    assert result.tool_call_id == "call_1"
    payload = json.loads(result.content)
    assert payload["timezone"] == "UTC"
    assert "iso_time" in payload


def test_unknown_tool_is_denied_and_audited(tmp_path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    broker = ToolBroker(
        default_registry(),
        PolicyEngine(),
        AuditLogger(audit_path),
        session_id="test-session",
        model="test-model",
        route="test",
    )

    result = broker.execute(
        {
            "id": "call_unknown",
            "type": "function",
            "function": {"name": "unknown.tool", "arguments": "{}"},
        }
    )

    assert result.allowed is False
    assert json.loads(result.content)["error"] == "unknown tool denied"
    lines = audit_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    event = json.loads(lines[0])
    assert event["tool_name"] == "unknown.tool"
    assert event["policy_decision"] == PolicyDecision.DENY.value
    assert event["hash_current"]


def test_audit_log_records_execution_and_denial(tmp_path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    broker = ToolBroker(
        default_registry(),
        PolicyEngine(),
        AuditLogger(audit_path),
        session_id="test-session",
        model="test-model",
        route="test",
    )

    broker.execute(
        {
            "id": "call_allowed",
            "type": "function",
            "function": {"name": "time.get_current_time", "arguments": "{}"},
        }
    )
    broker.execute(
        {
            "id": "call_denied",
            "type": "function",
            "function": {"name": "unknown.tool", "arguments": "{}"},
        }
    )

    events = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
    assert [event["policy_decision"] for event in events] == ["ALLOW", "DENY"]
    assert events[1]["hash_previous"] == events[0]["hash_current"]
