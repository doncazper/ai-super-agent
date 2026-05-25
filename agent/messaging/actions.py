from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

from agent.messaging.errors import DirectSendNotSupportedError, MessageValidationError, MessagingError
from agent.messaging.models import MessageChannel, MessageDeliveryStatus, MessageDraft
from agent.messaging.registry import MessageChannelRegistry, load_draft, save_draft
from agent.messaging.validation import infer_trust_level, recipient_from_value, validate_draft
from agent.safety.actions import ActionCenter, ActionRecord, ActionStatus
from agent.safety.policy import RiskLevel
from agent.safety.trust import TrustLevel


MESSAGE_SEND_ACTION = "messaging.send_approved"
MACOS_MESSAGE_SEND_ACTION = "messages.macos.send_approved"
MESSAGE_SEND_ACTION_TYPES = {MESSAGE_SEND_ACTION, MACOS_MESSAGE_SEND_ACTION}


def create_message_draft(
    project_root: str,
    *,
    channel: str,
    recipient: Any,
    body: str,
    draft_id: str = "",
    recipient_display: str = "",
    source_context: dict[str, Any] | None = None,
    risk_level: RiskLevel | None = None,
    action_center: ActionCenter | None = None,
) -> tuple[MessageDraft, str, list[str]]:
    channel_value = MessageChannel(channel)
    MessageChannelRegistry().get(channel_value)
    parsed_recipient = recipient_from_value(recipient)
    context = dict(source_context or {"source": "trusted_user"})
    trust_level = infer_trust_level(context, fallback=TrustLevel.MODEL_OUTPUT)
    chosen_risk = risk_level or (RiskLevel.HIGH if trust_level is not TrustLevel.MODEL_OUTPUT else RiskLevel.MEDIUM)
    safe_draft_id = draft_id.strip() or _new_draft_id(channel_value, parsed_recipient.channel_address, body)
    draft = MessageDraft(
        draft_id=safe_draft_id,
        channel=channel_value,
        recipient=parsed_recipient,
        recipient_display=recipient_display.strip() or parsed_recipient.display_name,
        body=body,
        attachments=[],
        source_context=context,
        trust_level=trust_level,
        risk_level=chosen_risk,
        created_at=datetime.now(UTC).isoformat(),
        expires_at=(datetime.now(UTC) + timedelta(days=1)).isoformat(),
        status=MessageDeliveryStatus.DRAFT,
        redaction_status="redacted",
    )
    validate_draft(draft)
    path = save_draft(project_root, draft)
    invalidated = []
    if action_center is not None:
        invalidated = invalidate_send_actions_for_draft(action_center, draft.draft_id, "message draft was edited")
    return draft, str(path), invalidated


def create_send_action_from_draft(
    project_root: str,
    action_center: ActionCenter,
    *,
    draft_id: str,
    source_workflow: str = "messaging.create-send-action",
    user_requested: bool = True,
) -> ActionRecord:
    if not user_requested:
        raise MessageValidationError("untrusted content cannot create a message send action without an explicit user request")
    draft = load_draft(project_root, draft_id)
    validate_draft(draft)
    if draft.attachments:
        raise MessageValidationError("message attachments are denied for send actions in messaging v1")
    if not draft.body.strip():
        raise MessageValidationError("message body is required")
    # Most built-in channels still report supports_send=false. macOS Messages
    # has a separate disabled-by-default adapter; it remains gated by config,
    # live probe, allowlist, and per-action Action Center approval.
    definition = MessageChannelRegistry().get(draft.channel)
    fingerprint = draft_fingerprint(draft)
    _invalidate_stale_send_actions(action_center, draft.draft_id, fingerprint)
    is_macos_send = draft.channel is MessageChannel.MACOS_MESSAGES
    action_type = MACOS_MESSAGE_SEND_ACTION if is_macos_send else MESSAGE_SEND_ACTION
    macos_send_enabled = False
    macos_send_status = "not_applicable"
    preview_allowlist_status = allowlist_status(draft.recipient.channel_address or draft.recipient.recipient_id)
    if is_macos_send:
        try:
            from agent.messaging.macos_send import MacOSMessagesSendConfig, _load_allowed_recipients, macos_messages_status

            status = macos_messages_status(project_root)
            macos_send_enabled = bool(status.get("send_capability_enabled"))
            macos_send_status = "ready" if macos_send_enabled else "blocked_by_status"
            configured = _load_allowed_recipients(Path(project_root).resolve(), MacOSMessagesSendConfig.from_env())
            recipient_value = draft.recipient.channel_address or draft.recipient.recipient_id
            preview_allowlist_status = "allowlisted" if recipient_value in configured else "not_allowlisted_extra_review_required"
        except Exception:
            macos_send_status = "status_unavailable"
    args = {
        "draft_id": draft.draft_id,
        "channel": draft.channel.value,
        "to": draft.recipient.channel_address or draft.recipient.recipient_id,
        "recipient_id": draft.recipient.recipient_id,
        "recipient_display": draft.recipient_display or draft.recipient.display_name,
        "body": draft.body,
        "attachments": [],
        "source_context": draft.source_context,
        "source_trust_level": draft.trust_level.value,
        "draft_risk_level": draft.risk_level.value,
        "risk_level": RiskLevel.CRITICAL.value,
        "rollback": "impossible_after_send",
        "approval_type": "explicit_per_action",
        "approval_reuse_allowed": False,
        "exact_preview_required": True,
        "allowlist_status": preview_allowlist_status,
        "rate_limit_status": "not_configured",
        "channel_supports_send": definition.supports_send,
        "send_supported": macos_send_enabled,
        "execution_supported": macos_send_enabled,
        "macos_send_status": macos_send_status,
        "draft_fingerprint": fingerprint,
        "stored_in_memory": False,
        "sent": False,
    }
    record = action_center.create_action(action_type, args, source_workflow=source_workflow)
    return record


def validate_send_action_current(project_root: str, record: ActionRecord) -> None:
    if record.action_type not in MESSAGE_SEND_ACTION_TYPES:
        raise MessageValidationError("action is not a messaging send action")
    draft_id = str(record.sanitized_args.get("draft_id") or "")
    draft = load_draft(project_root, draft_id)
    current_fingerprint = draft_fingerprint(draft)
    if current_fingerprint != record.sanitized_args.get("draft_fingerprint"):
        raise MessageValidationError("draft was edited after approval; create a new send action")
    raise DirectSendNotSupportedError("no messaging send adapter is implemented in v1")


def invalidate_send_actions_for_draft(center: ActionCenter, draft_id: str, reason: str) -> list[str]:
    invalidated: list[str] = []
    for record in center.list_actions():
        if record.action_type not in MESSAGE_SEND_ACTION_TYPES:
            continue
        if record.sanitized_args.get("draft_id") != draft_id:
            continue
        if record.status not in {ActionStatus.PENDING, ActionStatus.APPROVED}:
            continue
        updated = center.invalidate(record.action_id, f"{reason}; previous message send approval invalidated")
        if updated is not None:
            invalidated.append(record.action_id)
    return invalidated


def draft_fingerprint(draft: MessageDraft) -> str:
    payload = {
        "channel": draft.channel.value,
        "recipient": draft.recipient.to_dict(),
        "recipient_display": draft.recipient_display,
        "body": draft.body,
        "attachments": [attachment.to_dict() for attachment in draft.attachments],
        "source_context": draft.source_context,
        "trust_level": draft.trust_level.value,
        "risk_level": draft.risk_level.value,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def allowlist_status(recipient: str) -> str:
    configured = [item.strip() for item in os.getenv("MESSAGING_ALLOWED_RECIPIENTS", "").split(",") if item.strip()]
    if not configured:
        return "not_configured_extra_review_required"
    return "allowlisted" if recipient in configured else "not_allowlisted_extra_review_required"


def _invalidate_stale_send_actions(center: ActionCenter, draft_id: str, fingerprint: str) -> None:
    for record in center.list_actions():
        if record.action_type not in MESSAGE_SEND_ACTION_TYPES:
            continue
        if record.sanitized_args.get("draft_id") != draft_id:
            continue
        if record.sanitized_args.get("draft_fingerprint") == fingerprint:
            continue
        if record.status in {ActionStatus.PENDING, ActionStatus.APPROVED}:
            center.invalidate(record.action_id, "message draft changed; previous send action invalidated")


def _new_draft_id(channel: MessageChannel, recipient: str, body: str) -> str:
    seed = f"{channel.value}:{recipient}:{body}:{uuid4()}"
    return "msgdraft_" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
