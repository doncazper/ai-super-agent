from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from agent.safety.policy import RiskLevel
from agent.safety.trust import TrustLevel


class LeadSourceType(StrEnum):
    GMAIL = "gmail"
    TELEGRAM = "telegram"
    APPLE_MESSAGES_FOR_BUSINESS = "apple_messages_for_business"
    PERSONAL_IMESSAGE_MANUAL = "personal_imessage_manual"
    WEB_FORM = "web_form"
    MANUAL = "manual"
    MOCK = "mock"


class LeadStatus(StrEnum):
    NEW = "new"
    REVIEWED = "reviewed"
    NEEDS_INFO = "needs_info"
    DRAFTED = "drafted"
    PENDING_APPROVAL = "pending_approval"
    RESPONDED = "responded"
    CLOSED = "closed"
    BLOCKED = "blocked"


class LeadPriority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class LeadConsentStatus(StrEnum):
    UNKNOWN = "unknown"
    OPTED_IN = "opted_in"
    OPTED_OUT = "opted_out"
    NEEDS_REVIEW = "needs_review"


@dataclass(frozen=True)
class LeadRecord:
    lead_id: str
    source: LeadSourceType
    channel: str
    sender_ref: str
    sender_display: str
    received_at: str
    subject_or_context: str
    message_preview: str
    full_message_ref: str = ""
    trust_level: TrustLevel = TrustLevel.UNTRUSTED_MESSAGE
    risk_level: RiskLevel = RiskLevel.MEDIUM
    status: LeadStatus = LeadStatus.NEW
    linked_contact_id: str = ""
    linked_thread_id: str = ""
    linked_actions: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    priority: LeadPriority = LeadPriority.NORMAL
    consent_status: LeadConsentStatus = LeadConsentStatus.UNKNOWN

    def to_dict(self, *, minimal: bool = False) -> dict[str, Any]:
        payload = asdict(self)
        payload["source"] = self.source.value
        payload["trust_level"] = self.trust_level.value
        payload["risk_level"] = self.risk_level.value
        payload["status"] = self.status.value
        payload["priority"] = self.priority.value
        payload["consent_status"] = self.consent_status.value
        if minimal:
            payload["sender_ref"] = "[REDACTED_UNTIL_SELECTED]"
            payload["message_preview"] = _shorten(payload["message_preview"])
            payload["full_message_ref"] = "[SELECTED_READ_REQUIRED]" if self.full_message_ref else ""
        return payload


@dataclass(frozen=True)
class LeadClassification:
    lead_id: str
    priority: LeadPriority
    tags: list[str]
    reasons: list[str]
    suggested_next_step: str
    actions_created: list[str] = field(default_factory=list)
    memory_written: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["priority"] = self.priority.value
        return payload


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def lead_from_dict(payload: dict[str, Any]) -> LeadRecord:
    return LeadRecord(
        lead_id=str(payload.get("lead_id") or "").strip(),
        source=LeadSourceType(str(payload.get("source") or LeadSourceType.MOCK.value)),
        channel=str(payload.get("channel") or "").strip(),
        sender_ref=str(payload.get("sender_ref") or "").strip(),
        sender_display=str(payload.get("sender_display") or "").strip(),
        received_at=str(payload.get("received_at") or now_iso()),
        subject_or_context=str(payload.get("subject_or_context") or "").strip(),
        message_preview=str(payload.get("message_preview") or "").strip(),
        full_message_ref=str(payload.get("full_message_ref") or "").strip(),
        trust_level=TrustLevel(str(payload.get("trust_level") or TrustLevel.UNTRUSTED_MESSAGE.value)),
        risk_level=RiskLevel(str(payload.get("risk_level") or RiskLevel.MEDIUM.value)),
        status=LeadStatus(str(payload.get("status") or LeadStatus.NEW.value)),
        linked_contact_id=str(payload.get("linked_contact_id") or "").strip(),
        linked_thread_id=str(payload.get("linked_thread_id") or "").strip(),
        linked_actions=[str(item) for item in payload.get("linked_actions", [])],
        tags=[str(item) for item in payload.get("tags", [])],
        priority=LeadPriority(str(payload.get("priority") or LeadPriority.NORMAL.value)),
        consent_status=LeadConsentStatus(str(payload.get("consent_status") or LeadConsentStatus.UNKNOWN.value)),
    )


def _shorten(value: str, limit: int = 180) -> str:
    cleaned = " ".join(value.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."
