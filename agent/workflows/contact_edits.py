from __future__ import annotations

import json
from typing import Any

from agent.core.tool_broker import ToolBroker
from agent.safety.actions import ActionCenter, ActionRecord, ActionStatus
from agent.safety.approvals import ApprovalManager, ApprovalResult
from agent.safety.contact_redaction import is_sensitive_contact_field, redact_contact_changes, redact_contact_value


CONTACT_UPDATE_ACTION = "contacts.update_selected"
CONTACT_CREATE_ACTION = "contacts.create"
_BULK_TOKENS = {"*", "all", "everyone", "all contacts", "bulk", "export"}


def draft_contact_update(
    center: ActionCenter,
    *,
    selected_scope_token: str,
    changes: dict[str, Any],
    old_values: dict[str, Any] | None = None,
    source_workflow: str = "manual",
) -> ActionRecord:
    token = selected_scope_token.strip()
    if token.casefold() in _BULK_TOKENS:
        raise ValueError("contacts.update_selected requires one selected contact; bulk edit is denied")
    if not changes:
        raise ValueError("contacts update draft requires at least one changed field")
    old_values = old_values or {}
    field_diff = [_diff_item(field, old_values.get(field), new_value) for field, new_value in changes.items()]
    args: dict[str, Any] = {
        "selected_scope_token": token,
        "changes": redact_contact_changes(changes),
        "field_diff": field_diff,
        "bulk_edit": False,
        "stored_in_memory": False,
    }
    return center.create_action(CONTACT_UPDATE_ACTION, args, source_workflow=f"contacts.{source_workflow}")


def draft_contact_create(
    center: ActionCenter,
    *,
    display_name: str,
    fields: dict[str, Any] | None = None,
    source_workflow: str = "manual",
) -> ActionRecord:
    if not display_name.strip():
        raise ValueError("contacts create draft requires a display name")
    safe_fields = redact_contact_changes(fields or {})
    args: dict[str, Any] = {
        "display_name": display_name.strip(),
        "fields": safe_fields,
        "stored_in_memory": False,
    }
    return center.create_action(CONTACT_CREATE_ACTION, args, source_workflow=f"contacts.{source_workflow}")


def execute_contact_action(
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
        center.record_failure(action_id, "contact action type mismatch")
        return {
            "status": "error",
            "executed": False,
            "error": f"action type mismatch: expected {expected_action_type}, got {record.action_type}",
            "action_id": action_id,
            "action_status": record.status.value,
        }
    if record.status is not ActionStatus.APPROVED:
        center.record_failure(action_id, "contact action execution blocked because approval is missing")
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
        center.record_failure(action_id, "contact action ToolBroker execution failed or was denied")
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


def parse_field_assignments(assignments: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for assignment in assignments:
        if "=" not in assignment:
            raise ValueError(f"field assignment must be key=value: {assignment}")
        key, value = assignment.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"field assignment must include a field name: {assignment}")
        parsed[key] = value
    return parsed


def _diff_item(field: str, old_value: Any, new_value: Any) -> dict[str, Any]:
    sensitive = is_sensitive_contact_field(field)
    return {
        "field": field,
        "old": redact_contact_value(field, old_value) if old_value is not None else "[UNKNOWN]",
        "new": redact_contact_value(field, new_value),
        "sensitive": sensitive,
    }
