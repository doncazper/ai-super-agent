from __future__ import annotations

import json
from typing import Any

from agent.core.tool_broker import ToolBroker
from agent.safety.actions import ActionCenter, ActionRecord, ActionStatus
from agent.safety.approvals import ApprovalManager, ApprovalResult


TASK_CREATE_ACTION = "tasks.create"


def draft_task_create(
    center: ActionCenter,
    *,
    title: str,
    due: str = "",
    notes: str = "",
    list_name: str = "",
    source_workflow: str = "manual",
    allow_notes: bool = False,
) -> ActionRecord:
    args: dict[str, Any] = {
        "title": title,
        "due": due,
        "list_name": list_name,
    }
    if allow_notes and notes:
        args["notes"] = notes
    elif notes:
        args["notes_omitted"] = True
    return center.create_action(TASK_CREATE_ACTION, args, source_workflow=f"tasks.{source_workflow}")


def execute_task_action(
    broker: ToolBroker,
    center: ActionCenter,
    *,
    action_id: str,
    expected_action_type: str = TASK_CREATE_ACTION,
) -> dict[str, Any]:
    record = center.get_action(action_id)
    if record is None:
        return {"status": "error", "executed": False, "error": "action not found", "action_id": action_id}
    if record.action_type != expected_action_type:
        center.record_failure(action_id, "task action type mismatch")
        return {
            "status": "error",
            "executed": False,
            "error": f"action type mismatch: expected {expected_action_type}, got {record.action_type}",
            "action_id": action_id,
            "action_status": record.status.value,
        }
    if record.status is not ActionStatus.APPROVED:
        center.record_failure(action_id, "task action execution blocked because approval is missing")
        return {
            "status": "error",
            "executed": False,
            "error": "action must be approved in Action Center before execution",
            "action_id": action_id,
            "action_status": record.status.value,
        }
    tool_call = {
        "id": f"action_{action_id}",
        "type": "function",
        "function": {
            "name": record.tool_name,
            "arguments": json.dumps(record.sanitized_args),
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
        center.record_failure(action_id, "task action ToolBroker execution failed or was denied")
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
