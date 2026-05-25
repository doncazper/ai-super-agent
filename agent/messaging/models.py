from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

from agent.safety.policy import RiskLevel
from agent.safety.trust import TrustLevel


class MessageChannel(StrEnum):
    IOS_COMPOSE = "ios_compose"
    MACOS_MESSAGES = "macos_messages"
    APPLE_MESSAGES_FOR_BUSINESS = "apple_messages_for_business"
    TELEGRAM = "telegram"
    EMAIL = "email"
    MANUAL_HANDOFF = "manual_handoff"
    MOCK = "mock"


class MessageDeliveryStatus(StrEnum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    DENIED = "denied"
    BLOCKED = "blocked"
    HANDOFF_READY = "handoff_ready"
    SENT = "sent"
    FAILED = "failed"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class MessageRecipient:
    recipient_id: str
    channel_address: str
    display_name: str = ""
    recipient_type: str = "individual"
    allowlisted: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MessageAttachmentRef:
    attachment_id: str
    path: str = ""
    filename: str = ""
    content_type: str = ""
    size_bytes: int | None = None
    trust_level: TrustLevel = TrustLevel.UNTRUSTED_DOCUMENT
    approval_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["trust_level"] = self.trust_level.value
        return payload


@dataclass(frozen=True)
class MessageThreadRef:
    thread_id: str
    channel: MessageChannel
    external_thread_ref: str = ""
    trust_level: TrustLevel = TrustLevel.UNTRUSTED_MESSAGE
    selected_scope_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["channel"] = self.channel.value
        payload["trust_level"] = self.trust_level.value
        return payload


@dataclass(frozen=True)
class MessageRiskProfile:
    risk_level: RiskLevel = RiskLevel.CRITICAL
    trust_level: TrustLevel = TrustLevel.UNTRUSTED_MESSAGE
    approval_required: bool = True
    approval_reuse_allowed: bool = False
    exact_preview_required: bool = True
    bulk_allowed: bool = False
    group_send_allowed: bool = False
    attachments_allowed: bool = False
    direct_send_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["risk_level"] = self.risk_level.value
        payload["trust_level"] = self.trust_level.value
        return payload


@dataclass(frozen=True)
class MessageDraft:
    draft_id: str
    channel: MessageChannel
    recipient: MessageRecipient
    recipient_display: str
    body: str
    attachments: list[MessageAttachmentRef] = field(default_factory=list)
    source_context: dict[str, Any] = field(default_factory=dict)
    trust_level: TrustLevel = TrustLevel.MODEL_OUTPUT
    risk_level: RiskLevel = RiskLevel.MEDIUM
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    expires_at: str = field(default_factory=lambda: (datetime.now(UTC) + timedelta(days=1)).isoformat())
    status: MessageDeliveryStatus = MessageDeliveryStatus.DRAFT
    redaction_status: str = "redacted"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["channel"] = self.channel.value
        payload["recipient"] = self.recipient.to_dict()
        payload["attachments"] = [attachment.to_dict() for attachment in self.attachments]
        payload["trust_level"] = self.trust_level.value
        payload["risk_level"] = self.risk_level.value
        payload["status"] = self.status.value
        return payload


@dataclass(frozen=True)
class MessageSendRequest:
    action_id: str
    draft_id: str
    channel: MessageChannel
    recipient: MessageRecipient
    body: str
    attachments: list[MessageAttachmentRef] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.CRITICAL
    approval_required: bool = True
    approval_reuse_allowed: bool = False
    source_workflow: str = ""
    exact_preview_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["channel"] = self.channel.value
        payload["recipient"] = self.recipient.to_dict()
        payload["attachments"] = [attachment.to_dict() for attachment in self.attachments]
        payload["risk_level"] = self.risk_level.value
        return payload


@dataclass(frozen=True)
class MessageSendResult:
    request_id: str
    channel: MessageChannel
    status: MessageDeliveryStatus
    sent: bool = False
    provider_message_id: str = ""
    error: str = ""
    audit_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["channel"] = self.channel.value
        payload["status"] = self.status.value
        return payload
