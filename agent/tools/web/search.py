from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol


class SearchProvider(Protocol):
    name: str

    def search(self, query: str, max_results: int = 5, language: str | None = None) -> list[dict[str, str]]:
        ...


@dataclass(frozen=True)
class DisabledSearchProvider:
    name: str = "disabled"

    def search(self, query: str, max_results: int = 5, language: str | None = None) -> list[dict[str, str]]:
        return []


def provider_from_env() -> SearchProvider:
    # M4 intentionally ships without a live search backend. A future provider
    # can implement this protocol without changing ToolBroker semantics.
    provider_name = os.getenv("WEB_SEARCH_PROVIDER", "").strip().lower()
    if not provider_name:
        return DisabledSearchProvider()
    return DisabledSearchProvider(name=f"unsupported:{provider_name}")


def make_search_tool(provider: SearchProvider | None = None):
    active_provider = provider or provider_from_env()

    def search(query: str, max_results: int = 5, language: str | None = None) -> dict[str, object]:
        if not query.strip():
            return {"error": "query is required", "provider": active_provider.name, "results": []}
        if active_provider.name == "disabled":
            return {
                "error": "web search provider is not configured",
                "provider": active_provider.name,
                "results": [],
            }
        if active_provider.name.startswith("unsupported:"):
            return {
                "error": "configured web search provider is not supported by this build",
                "provider": active_provider.name,
                "results": [],
            }
        max_results_clamped = max(1, min(max_results, 10))
        results = active_provider.search(query, max_results_clamped, language)
        return {
            "query": query,
            "provider": active_provider.name,
            "retrieved_at": datetime.now(UTC).isoformat(),
            "results": results,
        }

    return search


WEB_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.search",
        "description": "Search the web through a configured provider. Returns a clear error if no provider is configured.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "max_results": {"type": "integer", "minimum": 1, "maximum": 10},
                "language": {"type": "string"},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}
