from __future__ import annotations

import json

from agent.core.tool_broker import ToolBroker
from agent.safety.approvals import ApprovalManager
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry


def critical_capabilities() -> dict[str, Capability]:
    return {
        name: Capability(
            name,
            RiskLevel.CRITICAL,
            default_enabled=True,
            approval_required="per_action",
            approval_reuse_allowed=False,
        )
        for name in [
            "calendar.create_event",
            "calendar.update_event",
            "calendar.delete_event",
            "contacts.update_selected",
            "email.send_approved",
            "messages.send_approved",
        ]
    }


def make_broker(tmp_path, approvals: ApprovalManager | None = None) -> ToolBroker:
    return ToolBroker(
        default_registry(project_root=tmp_path),
        PolicyEngine(critical_capabilities()),
        AuditLogger(tmp_path / "audit.jsonl"),
        session_id="test-session",
        model="test-model",
        route="test",
        approval_manager=approvals,
    )


def call(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    return {
        "id": f"call_{tool_name}",
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments)},
    }


def test_email_send_requires_approval(tmp_path) -> None:
    approvals = ApprovalManager()
    broker = make_broker(tmp_path, approvals)

    result = broker.execute(
        call("email.send_approved", {"to": "a@example.com", "subject": "Hi", "body": "Exact body"})
    )

    assert result.allowed is False
    assert json.loads(result.content)["approval_result"] == "denied"
    assert "recipient=a@example.com" in approvals.requests[0].summary
    assert "body=Exact body" in approvals.requests[0].summary
    assert approvals.requests[0].per_action is True


def test_text_send_requires_approval(tmp_path) -> None:
    broker = make_broker(tmp_path)

    result = broker.execute(call("messages.send_approved", {"to": "+15555550100", "body": "Hello"}))

    assert result.allowed is False
    assert json.loads(result.content)["approval_result"] == "denied"


def test_calendar_create_requires_approval(tmp_path) -> None:
    broker = make_broker(tmp_path)

    result = broker.execute(
        call("calendar.create_event", {"title": "Meeting", "start": "2026-05-22T10:00", "end": "2026-05-22T10:30"})
    )

    assert result.allowed is False
    assert json.loads(result.content)["approval_result"] == "denied"


def test_contact_edit_requires_approval(tmp_path) -> None:
    broker = make_broker(tmp_path)

    result = broker.execute(
        call("contacts.update_selected", {"selected_scope_token": "selected", "changes": {"company": "NewCo"}})
    )

    assert result.allowed is False
    assert json.loads(result.content)["approval_result"] == "denied"


def test_no_approval_reuse_for_critical_actions(tmp_path) -> None:
    approvals = ApprovalManager(auto_approve={"email.send_approved"})
    broker = make_broker(tmp_path, approvals)

    first = broker.execute(
        call("email.send_approved", {"to": "a@example.com", "subject": "One", "body": "Body one"})
    )
    second = broker.execute(
        call("email.send_approved", {"to": "b@example.com", "subject": "Two", "body": "Body two"})
    )

    assert first.allowed is True
    assert second.allowed is False
    assert len(approvals.requests) == 2
    assert all(request.per_action for request in approvals.requests)


def test_denial_prevents_execution(tmp_path) -> None:
    broker = make_broker(tmp_path)

    result = broker.execute(
        call("email.send_approved", {"to": "a@example.com", "subject": "Hi", "body": "No send"})
    )

    payload = json.loads(result.content)
    assert result.allowed is False
    assert payload["error"] == "approval required"
    assert "sent" not in payload


def test_audit_logs_approval_and_execution(tmp_path) -> None:
    approvals = ApprovalManager(auto_approve={"messages.send_approved"})
    broker = make_broker(tmp_path, approvals)

    result = broker.execute(call("messages.send_approved", {"to": "+15555550100", "body": "Approved body"}))

    assert result.allowed is True
    payload = json.loads(result.content)
    assert payload["sent"] is False
    assert payload["executed"] is False
    events = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [event["tool_name"] for event in events][:4] == [
        "approval.requested",
        "approval.approved",
        "approval.used",
        "messages.send_approved",
    ]
    execution = events[-1]
    assert execution["policy_decision"] == "ALLOW"
    assert execution["approval_result"] == "approved"
    assert execution["sanitized_args"]["body"] == "[PERSONAL_CONTENT_REDACTED]"
