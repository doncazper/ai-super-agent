from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent.core.tool_broker import ToolBroker
from agent.safety.actions import ActionCenter, ActionRecord, ActionStatus
from agent.safety.approvals import ApprovalManager, ApprovalResult
from agent.safety.trust import TrustLevel


EMAIL_SEND_ACTION = "email.send_approved"


def draft_email_new(
    center: ActionCenter,
    *,
    to: str,
    subject: str,
    body: str,
    from_account: str = "",
    provider: str = "",
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    attachments: list[str] | None = None,
    source_workflow: str = "manual",
) -> ActionRecord:
    args = _email_send_args(
        to=to,
        subject=subject,
        body=body,
        from_account=from_account,
        provider=provider,
        cc=cc,
        bcc=bcc,
        attachments=attachments,
        thread_id="",
        reply_context="new_message",
        source_trust_level=TrustLevel.MODEL_OUTPUT.value,
    )
    return center.create_action(EMAIL_SEND_ACTION, args, source_workflow=f"email.{source_workflow}")


def draft_email_reply_action(
    center: ActionCenter,
    *,
    thread_id: str,
    to: str,
    subject: str,
    body: str,
    from_account: str = "",
    provider: str = "",
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    attachments: list[str] | None = None,
    source_workflow: str = "draft_reply",
) -> ActionRecord:
    args = _email_send_args(
        to=to,
        subject=subject,
        body=body,
        from_account=from_account,
        provider=provider,
        cc=cc,
        bcc=bcc,
        attachments=attachments,
        thread_id=thread_id,
        reply_context="selected_thread_reply",
        source_trust_level=TrustLevel.UNTRUSTED_EMAIL.value,
    )
    return center.create_action(EMAIL_SEND_ACTION, args, source_workflow=f"email.{source_workflow}")


def execute_email_send_action(
    broker: ToolBroker,
    center: ActionCenter,
    *,
    action_id: str,
) -> dict[str, Any]:
    record = center.get_action(action_id)
    if record is None:
        return {"status": "error", "executed": False, "error": "action not found", "action_id": action_id}
    if record.action_type != EMAIL_SEND_ACTION:
        center.record_failure(action_id, "email send action type mismatch")
        return {
            "status": "error",
            "executed": False,
            "error": f"action type mismatch: expected {EMAIL_SEND_ACTION}, got {record.action_type}",
            "action_id": action_id,
            "action_status": record.status.value,
        }
    if record.status is not ActionStatus.APPROVED:
        center.record_failure(action_id, "email send blocked because approval is missing")
        return {
            "status": "error",
            "executed": False,
            "error": "action must be approved in Action Center before execution",
            "action_id": action_id,
            "action_status": record.status.value,
        }
    tool_args = dict(record.sanitized_args)
    tool_args["action_id"] = action_id
    tool_call = {
        "id": f"action_{action_id}",
        "type": "function",
        "function": {
            "name": record.tool_name,
            "arguments": json.dumps(tool_args),
        },
    }
    previous_manager = broker.approval_manager

    def decision_provider(request):
        if request.capability == record.capability and record.status is ActionStatus.APPROVED:
            return ApprovalResult.APPROVED
        return ApprovalResult.DENIED

    broker.approval_manager = ApprovalManager(
        decision_provider=decision_provider,
        store=center.approval_store,
    )
    broker.approval_manager.configure_audit(
        broker.audit_logger,
        session_id=broker.session_id,
        model=broker.model,
        route=broker.route,
    )
    try:
        result = broker.execute(tool_call)
    finally:
        broker.approval_manager = previous_manager

    payload = json.loads(result.content)
    if result.allowed:
        center.consume_approval_once(action_id)
    else:
        center.record_failure(action_id, "email send ToolBroker execution failed or was denied")
    refreshed = center.get_action(action_id)
    return {
        "status": "ok" if result.allowed else "error",
        "executed": result.allowed,
        "action_id": action_id,
        "action_status": refreshed.status.value if refreshed else "unknown",
        "tool_name": record.tool_name,
        "tool_result": payload,
        "debug": result.debug or {},
    }


def read_body_argument(body: str | None, body_file: str | None) -> str:
    if body and body_file:
        raise ValueError("provide either --body or --body-file, not both")
    if body_file:
        path = Path(body_file).expanduser()
        return path.read_text(encoding="utf-8")
    return body or ""


def _email_send_args(
    *,
    to: str,
    subject: str,
    body: str,
    from_account: str,
    provider: str,
    cc: list[str] | None,
    bcc: list[str] | None,
    attachments: list[str] | None,
    thread_id: str,
    reply_context: str,
    source_trust_level: str,
) -> dict[str, Any]:
    to_list = _normalize_recipients([to])
    cc_list = _normalize_recipients(cc or [])
    bcc_list = _normalize_recipients(bcc or [])
    attachment_list = [item for item in (attachments or []) if item]
    if not to_list:
        raise ValueError("email send draft requires exactly one primary recipient")
    if len(to_list) != 1:
        raise ValueError("bulk email sends are denied; provide exactly one primary recipient")
    if not subject.strip():
        raise ValueError("email send draft requires a subject")
    if not body.strip():
        raise ValueError("email send draft requires the full body")
    if attachment_list:
        raise ValueError("email send v1 blocks attachments; remove attachments and create a new reviewed draft")
    return {
        "from_account": from_account.strip() or "configured_default",
        "provider": provider.strip() or "configured_default",
        "to": to_list[0],
        "cc": cc_list,
        "bcc": bcc_list,
        "subject": subject,
        "body": body,
        "attachments": [],
        "thread_id": thread_id,
        "reply_context": reply_context,
        "source_trust_level": source_trust_level,
        "rollback_available": False,
        "rollback_note": "Email sending is irreversible after provider acceptance.",
        "stored_in_memory": False,
    }


def _normalize_recipients(values: list[str]) -> list[str]:
    recipients: list[str] = []
    for value in values:
        for part in value.replace(";", ",").split(","):
            stripped = part.strip()
            if stripped:
                recipients.append(stripped)
    return recipients
