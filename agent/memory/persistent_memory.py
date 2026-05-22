from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class MemoryRecord:
    id: str
    category: str
    scope: str
    content: str
    source_trust: str
    metadata: dict[str, Any]
    created_at: str


class PersistentMemoryStore:
    def __init__(self, path: str | Path = "data/memory.sqlite3") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def add(
        self,
        *,
        content: str,
        category: str,
        scope: str = "default",
        source_trust: str = "TRUSTED_USER",
        metadata: dict[str, Any] | None = None,
    ) -> MemoryRecord:
        record = MemoryRecord(
            id=str(uuid4()),
            category=category,
            scope=scope,
            content=content,
            source_trust=source_trust,
            metadata=metadata or {},
            created_at=utc_now_iso(),
        )
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO memories (id, category, scope, content, source_trust, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.category,
                    record.scope,
                    record.content,
                    record.source_trust,
                    json.dumps(record.metadata, sort_keys=True),
                    record.created_at,
                ),
            )
        return record

    def search(self, query: str, *, scope: str = "default", limit: int = 10) -> list[MemoryRecord]:
        like = f"%{query}%"
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, category, scope, content, source_trust, metadata_json, created_at
                FROM memories
                WHERE scope = ? AND content LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (scope, like, limit),
            ).fetchall()
        return [self._row_to_record(row) for row in rows]

    def export(self, *, scope: str = "default") -> list[MemoryRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, category, scope, content, source_trust, metadata_json, created_at
                FROM memories
                WHERE scope = ?
                ORDER BY created_at DESC
                """,
                (scope,),
            ).fetchall()
        return [self._row_to_record(row) for row in rows]

    def delete(self, record_id: str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM memories WHERE id = ?", (record_id,))
        return cursor.rowcount > 0

    def vacuum(self) -> None:
        with self._connect() as conn:
            conn.execute("VACUUM")

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source_trust TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_scope_content ON memories(scope, content)")

    def _row_to_record(self, row: sqlite3.Row) -> MemoryRecord:
        return MemoryRecord(
            id=row["id"],
            category=row["category"],
            scope=row["scope"],
            content=row["content"],
            source_trust=row["source_trust"],
            metadata=json.loads(row["metadata_json"]),
            created_at=row["created_at"],
        )
