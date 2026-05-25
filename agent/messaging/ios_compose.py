from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

from agent.messaging.actions import MESSAGE_SEND_ACTION, draft_fingerprint
from agent.messaging.errors import MessagingError, MessageValidationError
from agent.messaging.handoff_payloads import (
    IOSComposeHandoffPayload,
    integrity_hash,
    load_compose_result,
    load_handoff_payload,
    save_compose_result,
    save_handoff_payload,
)
from agent.messaging.registry import load_draft
from agent.messaging.validation import validate_draft
from agent.safety.actions import ActionCenter, ActionRecord, ActionStatus
from agent.safety.policy import RiskLevel
from agent.tools.errors import ToolError


IOS_COMPOSE_SCHEMAS: dict[str, dict[str, Any]] = {
    "messaging.ios_compose.create_handoff": {
        "type": "function",
        "function": {
            "name": "messaging.ios_compose.create_handoff",
            "description": (
                "Create a local iOS user-confirmed compose handoff payload from a local draft. "
                "The iOS user still reviews the compose UI and taps Send or Cancel."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "draft_id": {"type": "string"},
                    "action_id": {"type": "string"},
                    "compose_only": {"type": "boolean"},
                    "expires_minutes": {"type": "integer"},
                },
                "required": ["draft_id"],
                "additionalProperties": False,
            },
        },
    },
    "messaging.ios_compose.record_result": {
        "type": "function",
        "function": {
            "name": "messaging.ios_compose.record_result",
            "description": "Record an iOS compose result returned by a future companion app; does not send.",
            "parameters": {
                "type": "object",
                "properties": {
                    "draft_id": {"type": "string"},
                    "result": {"type": "string"},
                    "action_id": {"type": "string"},
                    "provider_message_id": {"type": "string"},
                    "error": {"type": "string"},
                },
                "required": ["draft_id", "result"],
                "additionalProperties": False,
            },
        },
    },
    "messaging.ios_compose.status": {
        "type": "function",
        "function": {
            "name": "messaging.ios_compose.status",
            "description": "Show local iOS compose handoff payload/result status; does not query iOS or send.",
            "parameters": {
                "type": "object",
                "properties": {"draft_id": {"type": "string"}},
                "required": ["draft_id"],
                "additionalProperties": False,
            },
        },
    },
}


def create_ios_compose_handoff(
    project_root: str | Path,
    *,
    draft_id: str,
    action_center: ActionCenter | None = None,
    action_id: str = "",
    compose_only: bool = False,
    expires_minutes: int = 15,
) -> tuple[IOSComposeHandoffPayload, str]:
    draft = load_draft(project_root, draft_id)
    validate_draft(draft)
    if draft.attachments:
        raise MessageValidationError("iOS compose attachments are deferred in v1")
    if not action_id and not compose_only:
        raise MessageValidationError("iOS compose handoff requires an approved Action Center action or compose-only mode")
    approval_status = "user_confirmed_compose_mode"
    if action_id:
        record = _require_current_approved_action(project_root, action_center, action_id, draft_id)
        approval_status = f"approved_action:{record.status.value}"
    expires_at = (datetime.now(UTC) + timedelta(minutes=expires_minutes)).isoformat()
    payload = IOSComposeHandoffPayload(
        draft_id=draft.draft_id,
        recipient=draft.recipient.channel_address or draft.recipient.recipient_id,
        body=draft.body,
        attachments=[],
        expires_at=expires_at,
        action_id=action_id,
        nonce=f"ios_{uuid4().hex}",
        risk_level=RiskLevel.CRITICAL,
        approval_status=approval_status,
        created_at=datetime.now(UTC).isoformat(),
        requires_user_tap_send=True,
        silent_send_supported=False,
        send_executed=False,
    )
    payload = IOSComposeHandoffPayload.from_dict({**payload.to_dict(), "integrity_hash": integrity_hash(payload)})
    path = save_handoff_payload(project_root, payload)
    return payload, str(path)


def record_ios_compose_result(
    project_root: str | Path,
    *,
    draft_id: str,
    result: str,
    action_id: str = "",
    provider_message_id: str = "",
    error: str = "",
) -> tuple[dict[str, Any], str]:
    payload = load_handoff_payload(project_root, draft_id)
    normalized = result.strip().lower()
    if normalized not in {"sent", "queued", "cancelled", "failed"}:
        raise MessageValidationError("iOS compose result must be one of sent, queued, cancelled, failed")
    if action_id and payload.action_id and action_id != payload.action_id:
        raise MessageValidationError("iOS compose result action_id does not match the handoff payload")
    if payload.is_expired() and normalized in {"sent", "queued"}:
        raise MessageValidationError("iOS compose payload is expired; sent/queued result cannot be accepted")
    send_marked_complete = normalized in {"sent", "queued"}
    record = {
        "draft_id": payload.draft_id,
        "action_id": action_id or payload.action_id,
        "channel": payload.channel,
        "result": normalized,
        "provider_message_id": provider_message_id,
        "error": error,
        "recorded_at": datetime.now(UTC).isoformat(),
        "send_marked_complete": send_marked_complete,
        "requires_user_tap_send": True,
        "silent_send_supported": False,
    }
    path = save_compose_result(project_root, draft_id, record)
    return record, str(path)


def ios_compose_status(project_root: str | Path, *, draft_id: str) -> dict[str, Any]:
    payload: IOSComposeHandoffPayload | None = None
    result: dict[str, Any] | None = None
    payload_error = ""
    try:
        payload = load_handoff_payload(project_root, draft_id)
    except FileNotFoundError:
        payload = None
    except Exception as exc:
        payload_error = str(exc)
    try:
        result = load_compose_result(project_root, draft_id)
    except FileNotFoundError:
        result = None
    return {
        "status": "ok",
        "draft_id": draft_id,
        "payload_exists": payload is not None,
        "payload_error": payload_error,
        "payload_expired": payload.is_expired() if payload is not None else None,
        "handoff_payload": _status_payload(payload) if payload is not None else None,
        "compose_result": result,
        "send_marked_complete": bool(result and result.get("send_marked_complete")),
        "silent_send_supported": False,
    }


def make_ios_compose_tools(project_root: str | Path, action_center: ActionCenter | None = None) -> dict[str, Any]:
    root = Path(project_root).resolve()

    def create_handoff(
        draft_id: str,
        action_id: str = "",
        compose_only: bool = False,
        expires_minutes: int = 15,
    ) -> dict[str, Any]:
        try:
            payload, path = create_ios_compose_handoff(
                root,
                draft_id=draft_id,
                action_center=action_center,
                action_id=action_id,
                compose_only=compose_only,
                expires_minutes=expires_minutes,
            )
        except (MessagingError, ValueError, FileNotFoundError) as exc:
            raise ToolError(str(exc)) from exc
        return {
            "status": "ok",
            "handoff_payload": payload.to_dict(),
            "path": path,
            "send_executed": False,
            "silent_send_supported": False,
            "requires_user_tap_send": True,
            "next_steps": [
                "Open this payload with a future iOS companion app or deep-link bridge.",
                "The iOS app must present Apple's compose UI.",
                "The user must tap Send or Cancel in the iOS compose UI.",
            ],
            "_audit": {
                "files_written": [path],
                "result_summary": (
                    f"iOS compose handoff payload created for {draft_id}; user-confirmed compose only; no send executed."
                ),
            },
        }

    def record_result(
        draft_id: str,
        result: str,
        action_id: str = "",
        provider_message_id: str = "",
        error: str = "",
    ) -> dict[str, Any]:
        try:
            record, path = record_ios_compose_result(
                root,
                draft_id=draft_id,
                result=result,
                action_id=action_id,
                provider_message_id=provider_message_id,
                error=error,
            )
        except (MessagingError, ValueError, FileNotFoundError) as exc:
            raise ToolError(str(exc)) from exc
        return {
            "status": "ok",
            "compose_result": record,
            "path": path,
            "send_executed_by_agent": False,
            "_audit": {
                "files_written": [path],
                "result_summary": f"iOS compose result recorded as {record['result']} for {draft_id}; no agent send executed.",
            },
        }

    def status(draft_id: str) -> dict[str, Any]:
        try:
            payload = ios_compose_status(root, draft_id=draft_id)
        except (MessagingError, ValueError, FileNotFoundError) as exc:
            raise ToolError(str(exc)) from exc
        payload["_audit"] = {"result_summary": f"iOS compose status inspected for {draft_id}; no send executed."}
        return payload

    return {
        "messaging.ios_compose.create_handoff": create_handoff,
        "messaging.ios_compose.record_result": record_result,
        "messaging.ios_compose.status": status,
    }


def _require_current_approved_action(
    project_root: str | Path,
    action_center: ActionCenter | None,
    action_id: str,
    draft_id: str,
) -> ActionRecord:
    if action_center is None:
        raise MessageValidationError("Action Center is required to verify approved iOS compose handoff actions")
    record = action_center.get_action(action_id)
    if record is None:
        raise MessageValidationError("message send action not found")
    if record.action_type != MESSAGE_SEND_ACTION:
        raise MessageValidationError("action is not a messaging send action")
    if record.status is not ActionStatus.APPROVED:
        raise MessageValidationError("message send action must be approved before creating an approved iOS handoff payload")
    if record.sanitized_args.get("draft_id") != draft_id:
        raise MessageValidationError("approved action draft_id does not match requested draft")
    draft = load_draft(project_root, draft_id)
    if draft_fingerprint(draft) != record.sanitized_args.get("draft_fingerprint"):
        raise MessageValidationError("draft recipient or body does not match approved preview; create a new send action")
    return record


def _status_payload(payload: IOSComposeHandoffPayload) -> dict[str, Any]:
    data = payload.to_dict()
    data["body"] = "[REDACTED_STATUS_PREVIEW]"
    return data
