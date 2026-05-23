from __future__ import annotations

import json

from agent.safety.actions import ActionCenter, ActionCenterStore, ActionStatus
from agent.safety.approvals import ApprovalStatus, ApprovalStore
from agent.safety.audit import AuditLogger
from agent.safety.policy import RiskLevel
from agent.ui.cli_commands import dispatch_cli


def _center(tmp_path) -> ActionCenter:
    return ActionCenter(
        store=ActionCenterStore(tmp_path / "actions.json"),
        approval_store=ApprovalStore(tmp_path / "approvals.json"),
        audit_logger=AuditLogger(tmp_path / "audit.jsonl"),
        session_id="test-session",
        model="test-model",
    )


def _email_args() -> dict[str, object]:
    return {"to": "a@example.com", "subject": "Hello", "body": "Exact body"}


def test_action_list_show_works(tmp_path) -> None:
    center = _center(tmp_path)
    action = center.create_action("git.commit", {"message": "checkpoint"}, source_workflow="test")

    assert center.list_actions()[0].action_id == action.action_id
    assert center.get_action(action.action_id).preview["title"] == "Git commit"


def test_high_action_requires_approval(tmp_path) -> None:
    center = _center(tmp_path)
    action = center.create_action("git.commit", {"message": "checkpoint"})

    assert action.risk_level is RiskLevel.HIGH
    assert action.approval_required is True
    assert action.approval_request_id
    assert ApprovalStore(tmp_path / "approvals.json").get(action.approval_request_id).status is ApprovalStatus.PENDING


def test_critical_action_requires_per_action_approval(tmp_path) -> None:
    center = _center(tmp_path)
    action = center.create_action("email.send_approved", _email_args())

    assert action.risk_level is RiskLevel.CRITICAL
    assert action.approval_required == "per_action"
    assert action.approval_reuse_allowed is False
    approval = ApprovalStore(tmp_path / "approvals.json").get(action.approval_request_id)
    assert approval.per_action is True


def test_approval_once_works_once(tmp_path) -> None:
    center = _center(tmp_path)
    action = center.create_action("email.send_approved", _email_args())

    center.approve(action.action_id)

    assert center.consume_approval_once(action.action_id) is True
    assert center.consume_approval_once(action.action_id) is False
    assert center.get_action(action.action_id).status is ActionStatus.USED
    assert ApprovalStore(tmp_path / "approvals.json").get(action.approval_request_id).status is ApprovalStatus.USED


def test_denial_prevents_execution(tmp_path) -> None:
    center = _center(tmp_path)
    action = center.create_action("email.send_approved", _email_args())

    center.deny(action.action_id)

    assert center.consume_approval_once(action.action_id) is False
    assert center.get_action(action.action_id).status is ActionStatus.DENIED


def test_edit_updates_preview_and_invalidates_previous_approval(tmp_path) -> None:
    center = _center(tmp_path)
    action = center.create_action("email.send_approved", _email_args())
    center.approve(action.action_id)

    edited = center.edit(action.action_id, {"body": "Revised exact body"})

    assert edited.status is ActionStatus.PENDING
    assert edited.approval_result == "not_required"
    assert edited.approval_request_id != action.approval_request_id
    assert "Revised exact body" in edited.preview["summary"]
    assert ApprovalStore(tmp_path / "approvals.json").get(action.approval_request_id).status is ApprovalStatus.DENIED


def test_non_interactive_mode_blocks_action_execution(tmp_path) -> None:
    center = _center(tmp_path)
    action = center.create_action("file.delete", {"path": "workspace/old.txt"})

    gate = center.execution_gate(action.action_id, interactive=False)

    assert gate["allowed"] is False
    assert "non-interactive" in gate["reason"]


def test_audit_logs_action_lifecycle(tmp_path) -> None:
    center = _center(tmp_path)
    action = center.create_action("git.commit", {"message": "checkpoint"})
    center.approve(action.action_id)
    center.consume_approval_once(action.action_id)

    lines = (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()
    events = [json.loads(line)["tool_name"] for line in lines]
    assert "action.created" in events
    assert "action.approved" in events
    assert "action.used" in events


def test_secrets_redacted_in_action_previews(tmp_path) -> None:
    center = _center(tmp_path)
    action = center.create_action(
        "email.send_approved",
        {
            "to": "a@example.com",
            "subject": "Hello",
            "body": "token=sk-supersecretvalue1234567890",
            "api_key": "sk-supersecretvalue1234567890",
        },
    )

    rendered = json.dumps(action.to_dict())
    assert "sk-supersecretvalue1234567890" not in rendered
    assert "[REDACTED]" in rendered


def test_actions_cli_list_show_approve_deny_export(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    center = ActionCenter(
        store=ActionCenterStore(),
        approval_store=ApprovalStore(),
        audit_logger=AuditLogger(),
    )
    action = center.create_action("git.commit", {"message": "checkpoint"})

    assert dispatch_cli(["actions", "list"]) == 0
    assert dispatch_cli(["actions", "show", action.action_id]) == 0
    assert dispatch_cli(["actions", "approve", action.action_id]) == 0
    assert ActionCenterStore().get(action.action_id).status is ActionStatus.APPROVED
    assert dispatch_cli(["actions", "deny", action.action_id]) == 0
    assert ActionCenterStore().get(action.action_id).status is ActionStatus.DENIED
    assert dispatch_cli(["actions", "export"]) == 0
    assert dispatch_cli(["actions", "clear-denied"]) == 0

    output = capsys.readouterr().out
    assert action.action_id in output
