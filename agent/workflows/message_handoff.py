from __future__ import annotations

import json
from typing import Any

from agent.core.tool_broker import ToolBroker
from agent.safety.actions import ActionCenter, ActionRecord, ActionStatus
from agent.safety.approvals import ApprovalManager, ApprovalResult
from agent.safety.trust import TrustLevel


MESSAGE_SAVE_DRAFT_ACTION = "messages.save_draft"
MESSAGE_COPY_DRAFT_ACTION = "messages.copy_draft"


def draft_message_handoff_actions(
    center: ActionCenter,
    *,
    to: str,
    draft: str,
    source_thread_id: str = "",
    save_path: str = "",
    source_workflow: str = "draft_from_text",
) -> dict[str, ActionRecord]:
    if not to.strip():
        raise ValueError("message draft handoff requires a recipient")
    if not draft.strip():
        raise ValueError("message draft handoff requires draft text")
    base_args: dict[str, Any] = {
        "to": to.strip(),
        "draft": draft,
        "source_thread_id": source_thread_id,
        "source_trust_level": TrustLevel.UNTRUSTED_MESSAGE.value,
        "stored_in_memory": False,
        "sent": False,
    }
    save_args = dict(base_args)
    if save_path:
        save_args["path"] = save_path
    return {
        "save": center.create_action(
            MESSAGE_SAVE_DRAFT_ACTION,
            save_args,
            source_workflow=f"messages.{source_workflow}.save",
        ),
        "copy": center.create_action(
            MESSAGE_COPY_DRAFT_ACTION,
            dict(base_args),
            source_workflow=f"messages.{source_workflow}.copy",
        ),
    }


def execute_message_handoff_action(
    broker: ToolBroker,
    center: ActionCenter,
    *,
    action_id: str,
    expected_action_type: str,
) -> dict[str, Any]:
    record = center.get_action(action_id)
    if record is None:
        return {"status": "error", "executed": False, "error": "action not found", "action_id": action_id}
    if record.action_type != expected_action_type:
        center.record_failure(action_id, "message handoff action type mismatch")
        return {
            "status": "error",
            "executed": False,
            "error": f"action type mismatch: expected {expected_action_type}, got {record.action_type}",
            "action_id": action_id,
            "action_status": record.status.value,
        }
    if record.status is not ActionStatus.APPROVED:
        center.record_failure(action_id, "message handoff blocked because approval is missing")
        return {
            "status": "error",
            "executed": False,
            "error": "action must be approved in Action Center before execution",
            "action_id": action_id,
            "action_status": record.status.value,
        }
    tool_args = dict(record.sanitized_args)
    tool_args["source_action_id"] = action_id
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
        center.record_failure(action_id, "message handoff ToolBroker execution failed or was denied")
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
