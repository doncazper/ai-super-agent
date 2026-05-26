from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable

from agent.memory.context import MemoryContextBuilder
from agent.memory.permissions import MemoryCategory, parse_category
from agent.memory.persistent_memory import MemoryRecord, PersistentMemoryStore
from agent.safety.redaction import SecretRedactor
from agent.safety.trust import TrustLevel


SAFE_CONTINUITY_CATEGORIES = {
    MemoryCategory.SESSION_CONTEXT.value,
    MemoryCategory.USER_PREFERENCE.value,
    MemoryCategory.PROJECT_FACT.value,
    MemoryCategory.WORKFLOW_LESSON.value,
}

PERSONAL_CATEGORIES = {
    MemoryCategory.TEMPORARY_PERSONAL_CONTEXT.value,
    MemoryCategory.PERSONAL_DATA_REFERENCE.value,
}

PERSONAL_TRUST_LEVELS = {
    TrustLevel.LOCAL_PRIVATE_DATA.value,
    TrustLevel.UNTRUSTED_EMAIL.value,
    TrustLevel.UNTRUSTED_MESSAGE.value,
    TrustLevel.UNTRUSTED_DOCUMENT.value,
}

EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?\d[\d .()\-]{7,}\d)(?!\d)")


@dataclass(frozen=True)
class ContinuitySummary:
    status: str
    scope: str
    summary: str
    records: list[dict[str, Any]]
    injected_memory_ids: list[str]
    truncated: bool
    character_budget: int
    memory_written: bool
    personal_data_included: bool
    cloud_embeddings_used: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "scope": self.scope,
            "summary": self.summary,
            "records": self.records,
            "injected_memory_ids": self.injected_memory_ids,
            "truncated": self.truncated,
            "character_budget": self.character_budget,
            "memory_written": self.memory_written,
            "personal_data_included": self.personal_data_included,
            "cloud_embeddings_used": self.cloud_embeddings_used,
        }


def redact_memory_text(value: str) -> str:
    redacted = SecretRedactor().redact_text(value)
    redacted = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", redacted)
    redacted = PHONE_PATTERN.sub("[REDACTED_PHONE]", redacted)
    return redacted


def is_personal_record(record: MemoryRecord) -> bool:
    return record.category in PERSONAL_CATEGORIES or record.source_trust in PERSONAL_TRUST_LEVELS


def continuity_status(store: PersistentMemoryStore, *, scope: str = "default") -> dict[str, Any]:
    records = store.export(scope=scope)
    safe_records = [record for record in records if not is_personal_record(record)]
    personal_records = [record for record in records if is_personal_record(record)]
    return {
        "status": "ok",
        "scope": scope,
        "enabled": True,
        "continuity_store": "local_memory_only",
        "automatic_prompt_injection": False,
        "personal_data_included_by_default": False,
        "cloud_embeddings_enabled": False,
        "memory_written": False,
        "total_records": len(records),
        "safe_continuity_records": len(safe_records),
        "personal_records_excluded_by_default": len(personal_records),
        "safe_categories": sorted(SAFE_CONTINUITY_CATEGORIES),
        "policy": "Preview/build only unless a brokered memory.context call injects non-personal snippets and audits injected ids.",
    }


def build_continuity_summary(
    store: PersistentMemoryStore,
    *,
    scope: str = "default",
    query: str = "",
    categories: Iterable[str] | None = None,
    max_records: int = 8,
    max_chars: int = 1600,
) -> ContinuitySummary:
    parsed_categories = _safe_categories(categories)
    records = _candidate_records(
        store,
        scope=scope,
        query=query,
        categories=parsed_categories,
        max_records=max_records,
    )
    budget = max(1, min(max_chars, 8000))
    lines: list[str] = []
    included: list[MemoryRecord] = []
    truncated = False
    for record in records:
        line = f"- ({record.category}) {redact_memory_text(record.content)}"
        projected = "\n".join([*lines, line])
        if len(projected) > budget:
            truncated = True
            break
        lines.append(line)
        included.append(record)
    return ContinuitySummary(
        status="ok",
        scope=scope,
        summary="\n".join(lines),
        records=[_record_summary(record) for record in included],
        injected_memory_ids=[record.id for record in included],
        truncated=truncated or len(records) > len(included),
        character_budget=budget,
        memory_written=False,
        personal_data_included=False,
        cloud_embeddings_used=False,
    )


def context_preview(
    store: PersistentMemoryStore,
    query: str,
    *,
    scope: str = "default",
    categories: Iterable[str] | None = None,
    max_records: int = 5,
    max_chars: int = 1200,
) -> dict[str, Any]:
    context = MemoryContextBuilder(store).build(
        query,
        scope=scope,
        categories=categories,
        max_records=max_records,
        max_chars=max_chars,
        include_personal=False,
    )
    return {
        "status": "ok",
        "query": query,
        "scope": scope,
        "context_preview": context.context,
        "records": context.records,
        "injected_memory_ids": context.injected_ids,
        "truncated": context.truncated,
        "character_budget": context.character_budget,
        "injection_performed": False,
        "personal_data_included": False,
        "memory_written": False,
        "cloud_embeddings_used": False,
        "policy": "Preview only. Use memory.context through ToolBroker for audited prompt injection.",
    }


def clear_continuity() -> dict[str, Any]:
    return {
        "status": "ok",
        "cleared": False,
        "memory_written": False,
        "message": "No separate continuity profile is persisted in v1; delete/clear specific memory records to remove source data.",
    }


def _safe_categories(categories: Iterable[str] | None) -> list[str]:
    requested = [parse_category(category).value for category in categories or [] if category]
    if not requested:
        return sorted(SAFE_CONTINUITY_CATEGORIES)
    return [category for category in requested if category in SAFE_CONTINUITY_CATEGORIES]


def _candidate_records(
    store: PersistentMemoryStore,
    *,
    scope: str,
    query: str,
    categories: list[str],
    max_records: int,
) -> list[MemoryRecord]:
    limit = max(1, min(max_records, 20))
    if query.strip():
        records = store.search(query, scope=scope, limit=limit, categories=categories)
    else:
        records = [
            record
            for record in store.export(scope=scope)
            if record.category in categories
        ][:limit]
    return [record for record in records if not is_personal_record(record)]


def _record_summary(record: MemoryRecord) -> dict[str, Any]:
    return {
        "id": record.id,
        "category": record.category,
        "scope": record.scope,
        "source_trust": record.source_trust,
        "created_at": record.created_at,
        "content_preview": redact_memory_text(record.content)[:160],
    }
