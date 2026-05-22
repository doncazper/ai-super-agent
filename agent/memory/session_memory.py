from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass
class SessionMemory:
    records: dict[str, dict[str, Any]] = field(default_factory=dict)

    def add(self, content: str, category: str = "session_context") -> dict[str, Any]:
        record_id = str(uuid4())
        record = {"id": record_id, "category": category, "content": content}
        self.records[record_id] = record
        return record

    def search(self, query: str) -> list[dict[str, Any]]:
        query_lower = query.casefold()
        return [record for record in self.records.values() if query_lower in record["content"].casefold()]

    def delete(self, record_id: str) -> bool:
        return self.records.pop(record_id, None) is not None
