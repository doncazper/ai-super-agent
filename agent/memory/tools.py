from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.memory.continuity import (
    build_continuity_summary,
    clear_continuity,
    context_preview,
    continuity_status,
)
from agent.memory.context import MemoryContextBuilder
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
    context_builder = MemoryContextBuilder(store)
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

    def search_memory(
        query: str,
        scope: str = "default",
        limit: int = 10,
        categories: list[str] | None = None,
    ) -> dict[str, Any]:
        if not query.strip():
            raise ToolError("query is required")
        parsed_categories = [parse_category(category).value for category in categories or []]
        records = store.search(
            query,
            scope=scope,
            limit=max(1, min(limit, 50)),
            categories=parsed_categories or None,
        )
        return {
            "query": query,
            "scope": scope,
            "categories": parsed_categories,
            "results": [_serialize(record) for record in records],
        }

    def export_memory(scope: str = "default") -> dict[str, Any]:
        return {"scope": scope, "records": [_serialize(record) for record in store.export(scope=scope)]}

    def delete_memory(record_id: str) -> dict[str, Any]:
        return lifecycle.delete(record_id)

    def clear_memory(scope: str = "default") -> dict[str, Any]:
        deleted = store.clear(scope=scope)
        if deleted:
            store.vacuum()
        return {
            "scope": scope,
            "deleted_count": deleted,
            "vacuumed": bool(deleted),
            "deletion_limits": "SQLite rows are deleted and VACUUM is run when possible. Filesystem backups or external logs are not rewritten.",
        }

    def build_context(
        query: str,
        scope: str = "default",
        categories: list[str] | None = None,
        max_records: int = 5,
        max_chars: int = 1200,
        include_personal: bool = False,
    ) -> dict[str, Any]:
        if include_personal:
            raise ToolError("personal memory context injection requires explicit approval and is disabled by default")
        context = context_builder.build(
            query,
            scope=scope,
            categories=categories or [],
            max_records=max_records,
            max_chars=max_chars,
            include_personal=False,
        )
        return {
            "query": query,
            "scope": scope,
            "categories": [parse_category(category).value for category in categories or []],
            "context": context.context,
            "injected_memory_ids": context.injected_ids,
            "records": context.records,
            "truncated": context.truncated,
            "character_budget": context.character_budget,
            "_audit": {
                "result_summary": "Injected memory ids: " + ", ".join(context.injected_ids)
                if context.injected_ids
                else "No memory injected.",
            },
        }

    def continuity_status_tool(scope: str = "default") -> dict[str, Any]:
        return continuity_status(store, scope=scope)

    def continuity_build_summary(
        scope: str = "default",
        query: str = "",
        categories: list[str] | None = None,
        max_records: int = 8,
        max_chars: int = 1600,
    ) -> dict[str, Any]:
        summary = build_continuity_summary(
            store,
            scope=scope,
            query=query,
            categories=categories or [],
            max_records=max_records,
            max_chars=max_chars,
        )
        payload = summary.to_dict()
        payload["_audit"] = {
            "result_summary": "Continuity summary memory ids: " + ", ".join(summary.injected_memory_ids)
            if summary.injected_memory_ids
            else "No continuity memory snippets selected.",
        }
        return payload

    def continuity_clear_tool() -> dict[str, Any]:
        return clear_continuity()

    def context_preview_tool(
        query: str,
        scope: str = "default",
        categories: list[str] | None = None,
        max_records: int = 5,
        max_chars: int = 1200,
    ) -> dict[str, Any]:
        if not query.strip():
            raise ToolError("query is required")
        payload = context_preview(
            store,
            query,
            scope=scope,
            categories=categories or [],
            max_records=max_records,
            max_chars=max_chars,
        )
        payload["_audit"] = {
            "result_summary": "Context preview memory ids: " + ", ".join(payload["injected_memory_ids"])
            if payload["injected_memory_ids"]
            else "No memory preview snippets selected.",
        }
        return payload

    return {
        "memory.store": store_memory,
        "memory.store_personal": store_personal_memory,
        "memory.search": search_memory,
        "memory.export": export_memory,
        "memory.delete": delete_memory,
        "memory.clear": clear_memory,
        "memory.context": build_context,
        "memory.continuity_status": continuity_status_tool,
        "memory.continuity_build_summary": continuity_build_summary,
        "memory.continuity_clear": continuity_clear_tool,
        "memory.context_preview": context_preview_tool,
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
                    "categories": {"type": "array", "items": {"type": "string"}},
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
    "memory.clear": {
        "type": "function",
        "function": {
            "name": "memory.clear",
            "description": "Clear memory records for one scope and compact the local store when possible.",
            "parameters": {
                "type": "object",
                "properties": {"scope": {"type": "string"}},
                "additionalProperties": False,
            },
        },
    },
    "memory.context": {
        "type": "function",
        "function": {
            "name": "memory.context",
            "description": "Build a bounded non-personal memory context block for safe prompt injection.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "scope": {"type": "string"},
                    "categories": {"type": "array", "items": {"type": "string"}},
                    "max_records": {"type": "integer", "minimum": 1, "maximum": 20},
                    "max_chars": {"type": "integer", "minimum": 1, "maximum": 8000},
                    "include_personal": {"type": "boolean"},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    "memory.continuity_status": {
        "type": "function",
        "function": {
            "name": "memory.continuity_status",
            "description": "Show safe long-term memory continuity status without injecting context or writing memory.",
            "parameters": {
                "type": "object",
                "properties": {"scope": {"type": "string"}},
                "additionalProperties": False,
            },
        },
    },
    "memory.continuity_build_summary": {
        "type": "function",
        "function": {
            "name": "memory.continuity_build_summary",
            "description": "Build a redacted non-personal continuity summary from safe memory categories.",
            "parameters": {
                "type": "object",
                "properties": {
                    "scope": {"type": "string"},
                    "query": {"type": "string"},
                    "categories": {"type": "array", "items": {"type": "string"}},
                    "max_records": {"type": "integer", "minimum": 1, "maximum": 20},
                    "max_chars": {"type": "integer", "minimum": 1, "maximum": 8000},
                },
                "additionalProperties": False,
            },
        },
    },
    "memory.continuity_clear": {
        "type": "function",
        "function": {
            "name": "memory.continuity_clear",
            "description": "Clear the separate continuity profile; v1 is a safe no-op because no profile is persisted.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
    "memory.context_preview": {
        "type": "function",
        "function": {
            "name": "memory.context_preview",
            "description": "Preview bounded non-personal memory context without injecting it into a prompt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "scope": {"type": "string"},
                    "categories": {"type": "array", "items": {"type": "string"}},
                    "max_records": {"type": "integer", "minimum": 1, "maximum": 20},
                    "max_chars": {"type": "integer", "minimum": 1, "maximum": 8000},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
}
