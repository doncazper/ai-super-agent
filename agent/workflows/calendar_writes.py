from __future__ import annotations

import base64
import json
from typing import Any

from agent.core.tool_broker import ToolBroker
from agent.safety.actions import ActionCenter, ActionRecord, ActionStatus
from agent.safety.approvals import ApprovalManager, ApprovalResult


CALENDAR_CREATE_ACTION = "calendar.create_event"
CALENDAR_UPDATE_ACTION = "calendar.update_event"
CALENDAR_DELETE_ACTION = "calendar.delete_event"


def draft_calendar_create(
    center: ActionCenter,
    *,
    title: str,
    start: str,
    end: str,
    calendar_name: str = "",
    attendees: list[str] | None = None,
    location: str = "",
    notes: str = "",
    allow_notes: bool = False,
) -> ActionRecord:
    args: dict[str, Any] = {
        "title": title,
        "start": start,
        "end": end,
        "calendar_name": calendar_name,
        "attendees": attendees or [],
        "location": location,
        "send_invites": False,
        "recurrence": None,
    }
    if allow_notes and notes:
        args["notes"] = notes
    elif notes:
        args["notes_omitted"] = True
    return center.create_action(CALENDAR_CREATE_ACTION, args, source_workflow="calendar.draft-create")


def draft_calendar_update(
    center: ActionCenter,
    *,
    event_id: str,
    changes: dict[str, Any],
) -> ActionRecord:
    if not changes:
        raise ValueError("calendar update draft requires at least one changed field")
    args: dict[str, Any] = {
        "event_id": event_id,
        "changes": changes,
        "rollback_data": _rollback_from_event_token(event_id),
        "send_invites": False,
        "recurrence": None,
    }
    return center.create_action(CALENDAR_UPDATE_ACTION, args, source_workflow="calendar.draft-update")


def draft_calendar_delete(center: ActionCenter, *, event_id: str) -> ActionRecord:
    args: dict[str, Any] = {
        "event_id": event_id,
        "rollback_data": _rollback_from_event_token(event_id),
        "rollback_availability": False,
    }
    return center.create_action(CALENDAR_DELETE_ACTION, args, source_workflow="calendar.draft-delete")


def execute_calendar_action(
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
        center.record_failure(action_id, "calendar action type mismatch")
        return {
            "status": "error",
            "executed": False,
            "error": f"action type mismatch: expected {expected_action_type}, got {record.action_type}",
            "action_id": action_id,
            "action_status": record.status.value,
        }
    if record.status is not ActionStatus.APPROVED:
        center.record_failure(action_id, "calendar action execution blocked because approval is missing")
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
        center.record_failure(action_id, "calendar action ToolBroker execution failed or was denied")
    return {
        "status": "ok" if result.allowed else "error",
        "executed": result.allowed,
        "action_id": action_id,
        "action_status": center.get_action(action_id).status.value if center.get_action(action_id) else "unknown",
        "tool_name": record.tool_name,
        "tool_result": payload,
        "debug": result.debug or {},
    }


def _rollback_from_event_token(event_id: str) -> dict[str, str]:
    if not event_id.startswith("calevt_"):
        return {}
    raw = event_id.removeprefix("calevt_")
    padded = raw + "=" * (-len(raw) % 4)
    try:
        payload = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8"))
    except (ValueError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict):
        return {}
    return {str(key): str(value) for key, value in payload.items() if value is not None}
