from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from agent.safety.redaction import SecretRedactor
from agent.memory.permissions import MemoryCategory, parse_category
from agent.memory.persistent_memory import MemoryRecord, PersistentMemoryStore
from agent.safety.trust import TrustLevel


PERSONAL_MEMORY_CATEGORIES = {
    MemoryCategory.TEMPORARY_PERSONAL_CONTEXT.value,
    MemoryCategory.PERSONAL_DATA_REFERENCE.value,
}

PERSONAL_TRUST_LEVELS = {
    TrustLevel.LOCAL_PRIVATE_DATA.value,
    TrustLevel.UNTRUSTED_EMAIL.value,
    TrustLevel.UNTRUSTED_MESSAGE.value,
    TrustLevel.UNTRUSTED_DOCUMENT.value,
}


@dataclass(frozen=True)
class MemoryContext:
    context: str
    injected_ids: list[str]
    records: list[dict[str, object]]
    truncated: bool
    character_budget: int


class MemoryContextBuilder:
    def __init__(self, store: PersistentMemoryStore) -> None:
        self.store = store

    def build(
        self,
        query: str,
        *,
        scope: str = "default",
        categories: Iterable[str] | None = None,
        max_records: int = 5,
        max_chars: int = 1200,
        include_personal: bool = False,
    ) -> MemoryContext:
        parsed_categories = _parse_categories(categories)
        records = self.store.search(
            query,
            scope=scope,
            limit=max(1, min(max_records, 20)),
            categories=parsed_categories or None,
        )
        usable = [record for record in records if include_personal or not _is_personal(record)]
        lines: list[str] = []
        injected: list[MemoryRecord] = []
        budget = max(1, min(max_chars, 8000))
        truncated = False
        for record in usable:
            line = f"- ({record.category}) {_redact_context_text(record.content)}"
            projected = "\n".join([*lines, line])
            if len(projected) > budget:
                truncated = True
                break
            lines.append(line)
            injected.append(record)
        return MemoryContext(
            context="\n".join(lines),
            injected_ids=[record.id for record in injected],
            records=[_record_summary(record) for record in injected],
            truncated=truncated or len(usable) > len(injected),
            character_budget=budget,
        )


def _parse_categories(categories: Iterable[str] | None) -> list[str]:
    parsed: list[str] = []
    for category in categories or []:
        if not category:
            continue
        parsed.append(parse_category(category).value)
    return parsed


def _is_personal(record: MemoryRecord) -> bool:
    return record.category in PERSONAL_MEMORY_CATEGORIES or record.source_trust in PERSONAL_TRUST_LEVELS


def _record_summary(record: MemoryRecord) -> dict[str, object]:
    return {
        "id": record.id,
        "category": record.category,
        "scope": record.scope,
        "source_trust": record.source_trust,
        "created_at": record.created_at,
    }


def _redact_context_text(value: str) -> str:
    redacted = SecretRedactor().redact_text(value)
    redacted = re.sub(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", "[REDACTED_EMAIL]", redacted, flags=re.IGNORECASE)
    redacted = re.sub(r"(?<!\d)(?:\+?\d[\d .()\-]{7,}\d)(?!\d)", "[REDACTED_PHONE]", redacted)
    return redacted
