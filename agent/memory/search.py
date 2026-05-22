from __future__ import annotations

from agent.memory.persistent_memory import MemoryRecord, PersistentMemoryStore


class MemorySearch:
    def __init__(self, store: PersistentMemoryStore) -> None:
        self.store = store

    def search(self, query: str, *, scope: str = "default", limit: int = 10) -> list[MemoryRecord]:
        return self.store.search(query, scope=scope, limit=limit)
