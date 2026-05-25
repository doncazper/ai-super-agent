from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping

from agent.web_acquisition.cache import WebCacheStore
from agent.web_acquisition.index import LocalWebIndex


WEB_CACHE_STATUS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.cache.status",
        "description": "Inspect public web cache status without network calls or memory writes.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}
WEB_CACHE_CLEAR_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.cache.clear",
        "description": "Clear the public web cache.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}
WEB_CACHE_LOOKUP_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.cache.lookup",
        "description": "Look up a public web cache entry by source ID, URL, or query hash.",
        "parameters": {
            "type": "object",
            "properties": {
                "source_id": {"type": "string"},
                "url": {"type": "string"},
                "provider": {"type": "string"},
                "query": {"type": "string"},
                "query_hash": {"type": "string"},
                "include_expired": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
    },
}
WEB_INDEX_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.index.search",
        "description": "Search the local lightweight public web index without network calls.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "minimum": 1, "maximum": 50}},
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}
WEB_INDEX_ADD_PUBLIC_SOURCE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.index.add_public_source",
        "description": "Add a public untrusted web source to the cache and local index.",
        "parameters": {
            "type": "object",
            "properties": {
                "source": {"type": "object"},
                "source_type": {"type": "string"},
                "provider": {"type": "string"},
                "query": {"type": "string"},
                "query_hash": {"type": "string"},
            },
            "required": ["source"],
            "additionalProperties": False,
        },
    },
}
WEB_INDEX_REBUILD_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.index.rebuild",
        "description": "Rebuild the local web index from non-expired public cache metadata.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}

WEB_CACHE_INDEX_SCHEMAS = {
    "web.cache.status": WEB_CACHE_STATUS_SCHEMA,
    "web.cache.clear": WEB_CACHE_CLEAR_SCHEMA,
    "web.cache.lookup": WEB_CACHE_LOOKUP_SCHEMA,
    "web.index.search": WEB_INDEX_SEARCH_SCHEMA,
    "web.index.add_public_source": WEB_INDEX_ADD_PUBLIC_SOURCE_SCHEMA,
    "web.index.rebuild": WEB_INDEX_REBUILD_SCHEMA,
}


def make_web_cache_index_tools(*, project_root: str | Path = ".") -> dict[str, Callable[..., dict[str, Any]]]:
    root = Path(project_root).resolve()
    cache = WebCacheStore(root / "data" / "web_cache" / "cache.json")
    index = LocalWebIndex(root / "data" / "web_cache" / "index.json")

    def cache_status() -> dict[str, Any]:
        payload = cache.status()
        payload["index"] = index.status()
        payload["_audit"] = {
            "files_read": [str(cache.path), str(index.path)],
            "result_summary": "Web cache/index status inspected.",
        }
        return payload

    def cache_clear() -> dict[str, Any]:
        cache_result = cache.clear()
        index_result = index.clear()
        payload = {"status": "cleared", "cache": cache_result, "index": index_result}
        payload["_audit"] = {
            "files_written": [str(cache.path), str(index.path)],
            "result_summary": "Web cache and local index cleared.",
        }
        return payload

    def cache_lookup(
        source_id: str = "",
        url: str = "",
        provider: str = "unknown",
        query: str = "",
        query_hash: str = "",
        include_expired: bool = False,
    ) -> dict[str, Any]:
        entry = cache.lookup(
            source_id=source_id or None,
            url=url or None,
            provider=provider or None,
            raw_query=query or None,
            query_hash_value=query_hash or None,
            include_expired=include_expired,
        )
        payload: dict[str, Any] = {
            "status": "hit" if entry else "miss",
            "cache_used": bool(entry),
            "query_persisted": False,
            "entry": entry,
        }
        payload["_audit"] = {"files_read": [str(cache.path)], "result_summary": f"Web cache lookup {payload['status']}."}
        return payload

    def index_search(query: str, limit: int = 10) -> dict[str, Any]:
        payload = index.search(query, limit=limit)
        payload["_audit"] = {"files_read": [str(index.path)], "result_summary": "Local web index searched."}
        return payload

    def add_public_source(
        source: Mapping[str, Any],
        source_type: str = "web",
        provider: str = "",
        query: str = "",
        query_hash: str = "",
    ) -> dict[str, Any]:
        cache_result = cache.put_public_source(
            source,
            provider=provider or None,
            source_type=source_type,
            raw_query=query or None,
            query_hash_value=query_hash or None,
        )
        index_result = index.add_public_source(source)
        payload = {
            "status": "ok" if cache_result.get("stored") or index_result.get("indexed") else "not_stored",
            "cache": cache_result,
            "index": index_result,
            "query_persisted": False,
        }
        payload["_audit"] = {
            "files_written": [str(cache.path), str(index.path)],
            "network_domains": [],
            "result_summary": "Public web source cache/index add attempted.",
        }
        return payload

    def index_rebuild() -> dict[str, Any]:
        payload = index.rebuild_from_cache(cache)
        payload["_audit"] = {
            "files_read": [str(cache.path)],
            "files_written": [str(index.path)],
            "result_summary": "Local web index rebuilt from cache.",
        }
        return payload

    return {
        "web.cache.status": cache_status,
        "web.cache.clear": cache_clear,
        "web.cache.lookup": cache_lookup,
        "web.index.search": index_search,
        "web.index.add_public_source": add_public_source,
        "web.index.rebuild": index_rebuild,
    }
