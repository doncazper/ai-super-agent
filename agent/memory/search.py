from __future__ import annotations

from typing import Any

from agent.memory.continuity import is_personal_record, redact_memory_text
from agent.memory.persistent_memory import MemoryRecord, PersistentMemoryStore


class MemorySearch:
    def __init__(self, store: PersistentMemoryStore) -> None:
        self.store = store

    def search(
        self,
        query: str,
        *,
        scope: str = "default",
        limit: int = 10,
        categories: list[str] | None = None,
    ) -> list[MemoryRecord]:
        return self.store.search(query, scope=scope, limit=limit, categories=categories)

    def safe_search(
        self,
        query: str,
        *,
        scope: str = "default",
        limit: int = 10,
        categories: list[str] | None = None,
        include_personal: bool = False,
    ) -> list[dict[str, Any]]:
        records = self.search(query, scope=scope, limit=limit, categories=categories)
        usable = [record for record in records if include_personal or not is_personal_record(record)]
        return [
            {
                "id": record.id,
                "category": record.category,
                "scope": record.scope,
                "source_trust": record.source_trust,
                "content": redact_memory_text(record.content),
                "created_at": record.created_at,
            }
            for record in usable
        ]
