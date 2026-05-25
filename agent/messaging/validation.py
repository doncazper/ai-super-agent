from __future__ import annotations

from typing import Any

from agent.messaging.errors import DirectSendNotSupportedError, MessageValidationError
from agent.messaging.models import (
    MessageAttachmentRef,
    MessageChannel,
    MessageDeliveryStatus,
    MessageDraft,
    MessageRecipient,
    MessageSendRequest,
)
from agent.safety.policy import RiskLevel
from agent.safety.trust import TrustLevel


UNTRUSTED_SOURCE_TRUST: tuple[tuple[str, TrustLevel], ...] = (
    ("email", TrustLevel.UNTRUSTED_EMAIL),
    ("web", TrustLevel.UNTRUSTED_WEB),
    ("browser", TrustLevel.UNTRUSTED_WEB),
    ("url", TrustLevel.UNTRUSTED_WEB),
    ("message", TrustLevel.UNTRUSTED_MESSAGE),
    ("sms", TrustLevel.UNTRUSTED_MESSAGE),
    ("imessage", TrustLevel.UNTRUSTED_MESSAGE),
    ("document", TrustLevel.UNTRUSTED_DOCUMENT),
    ("file", TrustLevel.UNTRUSTED_DOCUMENT),
)


def infer_trust_level(source_context: dict[str, Any] | None, fallback: TrustLevel = TrustLevel.MODEL_OUTPUT) -> TrustLevel:
    raw = " ".join(str(value) for value in (source_context or {}).values()).casefold()
    for marker, trust_level in UNTRUSTED_SOURCE_TRUST:
        if marker in raw:
            return trust_level
    return fallback


def recipient_from_value(value: Any) -> MessageRecipient:
    if isinstance(value, MessageRecipient):
        return value
    if isinstance(value, list):
        raise MessageValidationError("multiple recipients are rejected in messaging v1")
    if isinstance(value, str):
        return MessageRecipient(recipient_id=value.strip(), channel_address=value.strip(), display_name=value.strip())
    if not isinstance(value, dict):
        raise MessageValidationError("recipient is required")
    return MessageRecipient(
        recipient_id=str(value.get("recipient_id") or value.get("id") or value.get("channel_address") or "").strip(),
        channel_address=str(value.get("channel_address") or value.get("address") or "").strip(),
        display_name=str(value.get("display_name") or value.get("name") or "").strip(),
        recipient_type=str(value.get("recipient_type") or "individual").strip() or "individual",
        allowlisted=bool(value.get("allowlisted", False)),
    )


def attachment_from_value(value: Any) -> MessageAttachmentRef:
    if isinstance(value, MessageAttachmentRef):
        return value
    if not isinstance(value, dict):
        raise MessageValidationError("attachment entries must be objects")
    trust_raw = str(value.get("trust_level") or TrustLevel.UNTRUSTED_DOCUMENT.value)
    try:
        trust_level = TrustLevel(trust_raw)
    except ValueError as exc:
        raise MessageValidationError(f"invalid attachment trust_level: {trust_raw}") from exc
    return MessageAttachmentRef(
        attachment_id=str(value.get("attachment_id") or value.get("id") or "").strip(),
        path=str(value.get("path") or "").strip(),
        filename=str(value.get("filename") or "").strip(),
        content_type=str(value.get("content_type") or "").strip(),
        size_bytes=value.get("size_bytes") if isinstance(value.get("size_bytes"), int) else None,
        trust_level=trust_level,
        approval_required=bool(value.get("approval_required", True)),
    )


def draft_from_dict(payload: dict[str, Any]) -> MessageDraft:
    try:
        channel = MessageChannel(str(payload.get("channel") or ""))
    except ValueError as exc:
        raise MessageValidationError(f"unknown message channel: {payload.get('channel')}") from exc
    source_context = payload.get("source_context") if isinstance(payload.get("source_context"), dict) else {}
    trust_raw = payload.get("trust_level")
    fallback_trust = TrustLevel(str(trust_raw)) if trust_raw else infer_trust_level(source_context)
    trust_level = infer_trust_level(source_context, fallback=fallback_trust)
    risk_raw = str(payload.get("risk_level") or RiskLevel.MEDIUM.value)
    status_raw = str(payload.get("status") or MessageDeliveryStatus.DRAFT.value)
    draft = MessageDraft(
        draft_id=str(payload.get("draft_id") or "").strip(),
        channel=channel,
        recipient=recipient_from_value(payload.get("recipient")),
        recipient_display=str(payload.get("recipient_display") or "").strip(),
        body=str(payload.get("body") or ""),
        attachments=[attachment_from_value(item) for item in payload.get("attachments", [])],
        source_context=source_context,
        trust_level=trust_level,
        risk_level=RiskLevel(risk_raw),
        created_at=str(payload.get("created_at") or ""),
        expires_at=str(payload.get("expires_at") or ""),
        status=MessageDeliveryStatus(status_raw),
        redaction_status=str(payload.get("redaction_status") or "redacted"),
    )
    validate_draft(draft)
    return draft


def validate_recipient(recipient: MessageRecipient) -> None:
    if not recipient.recipient_id and not recipient.channel_address:
        raise MessageValidationError("message recipient is required")
    raw = f"{recipient.recipient_id} {recipient.channel_address}"
    if "," in raw or ";" in raw:
        raise MessageValidationError("multiple recipients are rejected in messaging v1")
    if recipient.recipient_type != "individual":
        raise MessageValidationError("group sending is rejected in messaging v1")


def validate_draft(draft: MessageDraft, *, allow_empty_body: bool = False) -> None:
    if not draft.draft_id:
        raise MessageValidationError("draft_id is required")
    validate_recipient(draft.recipient)
    if not allow_empty_body and not draft.body.strip():
        raise MessageValidationError("message body is required")


def validate_send_request(request: MessageSendRequest) -> None:
    from agent.messaging.registry import MessageChannelRegistry

    registry = MessageChannelRegistry()
    definition = registry.get(request.channel)
    if not definition.supports_send:
        raise DirectSendNotSupportedError(f"channel {request.channel.value} does not support sending in v1")
    validate_recipient(request.recipient)
    if not request.body.strip():
        raise MessageValidationError("message body is required")
    if request.risk_level is not RiskLevel.CRITICAL:
        raise MessageValidationError("message send requests must be CRITICAL")
    if not request.approval_required:
        raise MessageValidationError("message send requests require approval")
    if request.approval_reuse_allowed:
        raise MessageValidationError("message send approval reuse is forbidden")
    if not request.exact_preview_required:
        raise MessageValidationError("message send requests require exact preview")
    if request.attachments:
        raise MessageValidationError("message attachments are unsupported in messaging v1")
