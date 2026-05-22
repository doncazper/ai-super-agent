from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.memory.lifecycle import MemoryLifecycleManager
from agent.memory.persistent_memory import PersistentMemoryStore


def list_memory(path: str | Path = "data/memory.sqlite3", scope: str = "default") -> list[dict[str, Any]]:
    store = PersistentMemoryStore(path)
    return [record.__dict__ for record in store.export(scope=scope)]


def delete_memory(record_id: str, path: str | Path = "data/memory.sqlite3") -> dict[str, object]:
    return MemoryLifecycleManager(PersistentMemoryStore(path)).delete(record_id)
