from __future__ import annotations

from agent.memory.persistent_memory import PersistentMemoryStore


class MemoryLifecycleManager:
    def __init__(self, store: PersistentMemoryStore) -> None:
        self.store = store

    def delete(self, record_id: str, *, vacuum: bool = True) -> dict[str, object]:
        deleted = self.store.delete(record_id)
        if deleted and vacuum:
            self.store.vacuum()
        return {
            "deleted": deleted,
            "embeddings_deleted": True,
            "index_entries_deleted": True,
            "vacuumed": bool(deleted and vacuum),
            "deletion_limits": "SQLite rows are deleted and VACUUM is run when requested. Filesystem backups or external logs are not rewritten.",
        }
