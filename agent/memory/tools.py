from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.memory.lifecycle import MemoryLifecycleManager
from agent.memory.permissions import parse_category, parse_trust_level, requires_personal_approval
from agent.memory.persistent_memory import MemoryRecord, PersistentMemoryStore
from agent.safety.redaction import SecretRedactor
from agent.safety.trust import TrustLevel
from agent.tools.errors import ToolError


def _serialize(record: MemoryRecord) -> dict[str, Any]:
    return {
        "id": record.id,
        "category": record.category,
        "scope": record.scope,
        "content": record.content,
        "source_trust": record.source_trust,
        "metadata": record.metadata,
        "created_at": record.created_at,
    }


def make_memory_tools(memory_path: str | Path | None = None) -> dict[str, Any]:
    store = PersistentMemoryStore(memory_path or "data/memory.sqlite3")
    lifecycle = MemoryLifecycleManager(store)
    redactor = SecretRedactor()

    def store_memory(
        content: str,
        category: str,
        scope: str = "default",
        source_trust: str = TrustLevel.TRUSTED_USER.value,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if redactor.contains_secret(content) or redactor.contains_secret(metadata or {}):
            raise ToolError("memory content contains a secret and was not stored")
        try:
            parsed_category = parse_category(category)
            parsed_trust = parse_trust_level(source_trust)
        except ValueError as exc:
            raise ToolError(str(exc)) from exc
        if requires_personal_approval(parsed_category, parsed_trust):
            raise ToolError("personal data memory requires approval")
        record = store.add(
            content=content,
            category=parsed_category.value,
            scope=scope,
            source_trust=parsed_trust.value,
            metadata=metadata or {},
        )
        return {"stored": True, "record": _serialize(record)}

    def store_personal_memory(
        content: str,
        category: str,
        scope: str = "default",
        source_trust: str = TrustLevel.LOCAL_PRIVATE_DATA.value,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if redactor.contains_secret(content) or redactor.contains_secret(metadata or {}):
            raise ToolError("memory content contains a secret and was not stored")
        try:
            parsed_category = parse_category(category)
            parsed_trust = parse_trust_level(source_trust)
        except ValueError as exc:
            raise ToolError(str(exc)) from exc
        record = store.add(
            content=content,
            category=parsed_category.value,
            scope=scope,
            source_trust=parsed_trust.value,
            metadata=metadata or {},
        )
        return {"stored": True, "record": _serialize(record)}

    def search_memory(query: str, scope: str = "default", limit: int = 10) -> dict[str, Any]:
        if not query.strip():
            raise ToolError("query is required")
        records = store.search(query, scope=scope, limit=max(1, min(limit, 50)))
        return {"query": query, "scope": scope, "results": [_serialize(record) for record in records]}

    def export_memory(scope: str = "default") -> dict[str, Any]:
        return {"scope": scope, "records": [_serialize(record) for record in store.export(scope=scope)]}

    def delete_memory(record_id: str) -> dict[str, Any]:
        return lifecycle.delete(record_id)

    return {
        "memory.store": store_memory,
        "memory.store_personal": store_personal_memory,
        "memory.search": search_memory,
        "memory.export": export_memory,
        "memory.delete": delete_memory,
    }


MEMORY_SCHEMAS = {
    "memory.store": {
        "type": "function",
        "function": {
            "name": "memory.store",
            "description": "Store non-personal memory such as user preferences, project facts, or workflow lessons. Refuses secrets and personal data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "category": {"type": "string"},
                    "scope": {"type": "string"},
                    "source_trust": {"type": "string"},
                    "metadata": {"type": "object"},
                },
                "required": ["content", "category"],
                "additionalProperties": False,
            },
        },
    },
    "memory.store_personal": {
        "type": "function",
        "function": {
            "name": "memory.store_personal",
            "description": "Store personal-data memory only after approval.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "category": {"type": "string"},
                    "scope": {"type": "string"},
                    "source_trust": {"type": "string"},
                    "metadata": {"type": "object"},
                },
                "required": ["content", "category"],
                "additionalProperties": False,
            },
        },
    },
    "memory.search": {
        "type": "function",
        "function": {
            "name": "memory.search",
            "description": "Search memory within a scope.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "scope": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 50},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    "memory.export": {
        "type": "function",
        "function": {
            "name": "memory.export",
            "description": "Export memory records for a scope.",
            "parameters": {
                "type": "object",
                "properties": {"scope": {"type": "string"}},
                "additionalProperties": False,
            },
        },
    },
    "memory.delete": {
        "type": "function",
        "function": {
            "name": "memory.delete",
            "description": "Delete a memory record and compact the local store when possible.",
            "parameters": {
                "type": "object",
                "properties": {"record_id": {"type": "string"}},
                "required": ["record_id"],
                "additionalProperties": False,
            },
        },
    },
}
