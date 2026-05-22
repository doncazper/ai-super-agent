from __future__ import annotations

from enum import StrEnum

from agent.safety.trust import TrustLevel


class MemoryCategory(StrEnum):
    SESSION_CONTEXT = "session_context"
    USER_PREFERENCE = "user_preference"
    PROJECT_FACT = "project_fact"
    WORKFLOW_LESSON = "workflow_lesson"
    TEMPORARY_PERSONAL_CONTEXT = "temporary_personal_context"
    PERSONAL_DATA_REFERENCE = "personal_data_reference"


PERSONAL_MEMORY_CATEGORIES = {
    MemoryCategory.TEMPORARY_PERSONAL_CONTEXT,
    MemoryCategory.PERSONAL_DATA_REFERENCE,
}

PERSONAL_SOURCE_TRUST = {
    TrustLevel.LOCAL_PRIVATE_DATA,
    TrustLevel.UNTRUSTED_EMAIL,
    TrustLevel.UNTRUSTED_MESSAGE,
    TrustLevel.UNTRUSTED_DOCUMENT,
}


def parse_category(category: str) -> MemoryCategory:
    try:
        return MemoryCategory(category)
    except ValueError as exc:
        raise ValueError("unknown memory category") from exc


def parse_trust_level(trust_level: str) -> TrustLevel:
    try:
        return TrustLevel(trust_level)
    except ValueError as exc:
        raise ValueError("unknown trust level") from exc


def requires_personal_approval(category: MemoryCategory, trust_level: TrustLevel) -> bool:
    return category in PERSONAL_MEMORY_CATEGORIES or trust_level in PERSONAL_SOURCE_TRUST
