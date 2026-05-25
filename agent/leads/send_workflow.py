from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent.core.tool_broker import ToolBroker
from agent.leads.inbox import _write_lead_status
from agent.messaging.actions import MACOS_MESSAGE_SEND_ACTION, MESSAGE_SEND_ACTION, draft_fingerprint
from agent.messaging.macos_send import execute_macos_message_send_action
from agent.messaging.models import MessageChannel
from agent.messaging.registry import load_draft
from agent.safety.actions import ActionCenter, ActionStatus
from agent.safety.policy import RiskLevel


def execute_lead_send_action(
    project_root: str | Path,
    broker: ToolBroker,
    center: ActionCenter,
    *,
    action_id: str,
) -> dict[str, Any]:
    """Route an approved lead response action to the safest channel path.

    This function intentionally does not implement a new send adapter. It
    verifies the exact Action Center record, consumes one-time approvals only
    through supported brokered flows, and returns fallbacks for channels that
    cannot safely send in v1.
    """

    root = Path(project_root).resolve()
    record = center.get_action(action_id)
    if record is None:
        return _error(action_id, "action not found")
    if record.action_type not in {MESSAGE_SEND_ACTION, MACOS_MESSAGE_SEND_ACTION}:
        center.record_failure(action_id, "lead response send blocked because action type is not a message send action")
        return _error(action_id, "action is not a message send action", action_status=record.status.value)
    if record.status is not ActionStatus.APPROVED:
        center.record_failure(action_id, "lead response send blocked because approval is missing")
        return _error(
            action_id,
            "action must be approved in Action Center before lead response send/handoff",
            action_status=record.status.value,
        )

    draft_id = str(record.sanitized_args.get("draft_id") or "")
    try:
        draft = load_draft(root, draft_id)
    except Exception as exc:
        center.record_failure(action_id, f"lead response send blocked because draft could not be loaded: {exc}")
        return _error(action_id, str(exc), action_status=record.status.value)

    current_fingerprint = draft_fingerprint(draft)
    if current_fingerprint != record.sanitized_args.get("draft_fingerprint"):
        center.record_failure(action_id, "lead response send blocked because draft was edited after approval")
        return _error(action_id, "draft was edited after approval; create and approve a new send action", action_status=record.status.value)

    recipient = draft.recipient.channel_address or draft.recipient.recipient_id
    if "," in recipient or ";" in recipient:
        center.record_failure(action_id, "lead response send blocked because bulk recipients are forbidden")
        return _error(action_id, "bulk lead responses are forbidden in v1", action_status=record.status.value)

    lead_id = _lead_id_from_record(record.sanitized_args)
    if record.action_type == MACOS_MESSAGE_SEND_ACTION:
        return _execute_macos(root, broker, center, action_id=action_id, lead_id=lead_id)

    if draft.channel is MessageChannel.IOS_COMPOSE:
        return _create_ios_handoff(root, broker, center, action_id=action_id, draft_id=draft.draft_id, lead_id=lead_id)

    fallback = _fallback_options(draft.channel, draft.draft_id)
    center.record_failure(action_id, f"lead response send unsupported for channel {draft.channel.value}; fallback required")
    return {
        "status": "unsupported",
        "executed": False,
        "sent": False,
        "action_id": action_id,
        "action_status": record.status.value,
        "draft_id": draft.draft_id,
        "lead_id": lead_id,
        "channel": draft.channel.value,
        "risk_level": RiskLevel.CRITICAL.value,
        "approval_reuse_allowed": False,
        "bulk_allowed": False,
        "auto_send_enabled": False,
        "stored_in_memory": False,
        "error": f"channel {draft.channel.value} has no enabled lead response send adapter in v1",
        "fallback_options": fallback,
    }


def _execute_macos(
    root: Path,
    broker: ToolBroker,
    center: ActionCenter,
    *,
    action_id: str,
    lead_id: str,
) -> dict[str, Any]:
    payload = execute_macos_message_send_action(broker, center, action_id=action_id)
    sent = bool(payload.get("executed") and payload.get("tool_result", {}).get("sent"))
    status_path = ""
    if sent and lead_id:
        status_path = str(
            _write_lead_status(
                root,
                lead_id,
                status="responded",
                action_id=action_id,
                channel=MessageChannel.MACOS_MESSAGES.value,
                note="lead response sent through gated macOS Messages adapter",
            )
        )
    if not sent:
        payload["fallback_options"] = _fallback_options(MessageChannel.MACOS_MESSAGES, str(payload.get("tool_result", {}).get("draft_id") or ""))
    payload.update(
        {
            "lead_response_send": True,
            "lead_id": lead_id,
            "sent": sent,
            "lead_status_path": status_path,
            "bulk_allowed": False,
            "auto_send_enabled": False,
            "stored_in_memory": False,
        }
    )
    return payload


def _create_ios_handoff(
    root: Path,
    broker: ToolBroker,
    center: ActionCenter,
    *,
    action_id: str,
    draft_id: str,
    lead_id: str,
) -> dict[str, Any]:
    tool_call = {
        "id": f"lead_ios_handoff_{action_id}",
        "type": "function",
        "function": {
            "name": "messaging.ios_compose.create_handoff",
            "arguments": json.dumps(
                {
                    "draft_id": draft_id,
                    "action_id": action_id,
                    "compose_only": False,
                    "expires_minutes": 15,
                }
            ),
        },
    }
    result = broker.execute(tool_call)
    payload = json.loads(result.content)
    status_path = ""
    if result.allowed:
        center.consume_approval_once(action_id)
        if lead_id:
            status_path = str(
                _write_lead_status(
                    root,
                    lead_id,
                    status="handoff_ready",
                    draft_id=draft_id,
                    action_id=action_id,
                    channel=MessageChannel.IOS_COMPOSE.value,
                    note="iOS user-confirmed compose handoff payload created; user must tap Send or Cancel",
                )
            )
    else:
        center.record_failure(action_id, "lead response iOS compose handoff failed or was denied")
    refreshed = center.get_action(action_id)
    return {
        "status": "handoff_ready" if result.allowed else "error",
        "executed": False,
        "sent": False,
        "action_id": action_id,
        "action_status": refreshed.status.value if refreshed else "unknown",
        "draft_id": draft_id,
        "lead_id": lead_id,
        "channel": MessageChannel.IOS_COMPOSE.value,
        "handoff_payload": payload.get("handoff_payload"),
        "handoff_path": payload.get("path", ""),
        "lead_status_path": status_path,
        "requires_user_tap_send": True,
        "silent_send_supported": False,
        "bulk_allowed": False,
        "auto_send_enabled": False,
        "stored_in_memory": False,
        "tool_result": payload,
        "debug": result.debug or {},
    }


def _lead_id_from_record(args: dict[str, Any]) -> str:
    context = args.get("source_context")
    if isinstance(context, dict):
        value = str(context.get("lead_id") or "").strip()
        if value:
            return value
    return ""


def _fallback_options(channel: MessageChannel, draft_id: str) -> list[str]:
    if channel is MessageChannel.MANUAL_HANDOFF:
        return [
            f"Use `leads handoff {draft_id}` to create save/copy Action Center items.",
            f"Use `messages handoff {draft_id}` for generic message handoff instructions.",
            "No silent or provider send exists for manual_handoff.",
        ]
    if channel is MessageChannel.IOS_COMPOSE:
        return [
            "Retry only after exact Action Center approval.",
            "Use iOS compose handoff; the user must tap Send or Cancel in the compose UI.",
        ]
    if channel is MessageChannel.MACOS_MESSAGES:
        return [
            "Use iOS compose or manual handoff if macOS Messages connector is disabled, unsupported, not allowlisted, or lacks a recent live probe.",
            "Do not fake success; macOS send must be verified by the gated adapter.",
        ]
    if channel is MessageChannel.APPLE_MESSAGES_FOR_BUSINESS:
        return [
            f"Use `leads handoff {draft_id}` until an Apple Messages for Business provider is configured.",
            "Business provider send remains disabled by default and CRITICAL.",
        ]
    if channel in {MessageChannel.TELEGRAM, MessageChannel.EMAIL}:
        return [
            f"Use `leads handoff {draft_id}` unless an existing approved {channel.value} send adapter is configured and enabled.",
            "Telegram/email sends remain CRITICAL and disabled unless their approved adapters exist.",
        ]
    return [f"Use `leads handoff {draft_id}` for a manual fallback."]


def _error(action_id: str, error: str, *, action_status: str = "unknown") -> dict[str, Any]:
    return {
        "status": "error",
        "executed": False,
        "sent": False,
        "action_id": action_id,
        "action_status": action_status,
        "error": error,
        "bulk_allowed": False,
        "auto_send_enabled": False,
        "stored_in_memory": False,
    }
