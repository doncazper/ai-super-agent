from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol

import httpx

from agent.config.runtime import env_bool, parse_float, parse_int
from agent.tools.errors import ToolError

class SearchProvider(Protocol):
    name: str

    def is_configured(self) -> bool:
        ...

    def search(
        self,
        query: str,
        max_results: int,
        locale: str | None = None,
        safe_search: bool = True,
    ) -> list[dict[str, str]]:
        ...


@dataclass(frozen=True)
class DisabledSearchProvider:
    name: str = "disabled"

    def is_configured(self) -> bool:
        return False

    def search(
        self,
        query: str,
        max_results: int,
        locale: str | None = None,
        safe_search: bool = True,
    ) -> list[dict[str, str]]:
        return []


@dataclass(frozen=True)
class UnsupportedSearchProvider:
    provider_name: str

    @property
    def name(self) -> str:
        return f"unsupported:{self.provider_name}"

    def is_configured(self) -> bool:
        return False

    def search(
        self,
        query: str,
        max_results: int,
        locale: str | None = None,
        safe_search: bool = True,
    ) -> list[dict[str, str]]:
        return []


@dataclass(frozen=True)
class BraveSearchProvider:
    api_key: str
    timeout_seconds: float = 10
    endpoint: str = "https://api.search.brave.com/res/v1/web/search"
    name: str = "brave"

    def is_configured(self) -> bool:
        return bool(self.api_key.strip())

    def search(
        self,
        query: str,
        max_results: int,
        locale: str | None = None,
        safe_search: bool = True,
    ) -> list[dict[str, str]]:
        if not self.is_configured():
            raise ToolError("Brave Search is selected but BRAVE_SEARCH_API_KEY is not set")
        params: dict[str, Any] = {
            "q": query,
            "count": max_results,
            "safesearch": "strict" if safe_search else "off",
        }
        params.update(_locale_params(locale))
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key,
        }
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.get(self.endpoint, headers=headers, params=params)
                response.raise_for_status()
                payload = response.json()
        except httpx.TimeoutException as exc:
            raise ToolError("web search timed out") from exc
        except httpx.HTTPStatusError as exc:
            raise ToolError(f"web search provider returned HTTP {exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise ToolError(f"web search provider failed: {type(exc).__name__}") from exc
        except ValueError as exc:
            raise ToolError("web search provider returned malformed JSON") from exc
        return normalize_brave_results(payload, max_results)


def normalize_brave_results(payload: dict[str, Any], max_results: int) -> list[dict[str, str]]:
    web_payload = payload.get("web") if isinstance(payload, dict) else None
    raw_results = web_payload.get("results", []) if isinstance(web_payload, dict) else []
    normalized: list[dict[str, str]] = []
    for item in raw_results[:max_results]:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url") or "").strip()
        if not url:
            continue
        normalized.append(
            {
                "title": str(item.get("title") or "").strip(),
                "url": url,
                "snippet": str(item.get("description") or item.get("snippet") or "").strip(),
                "source": str(item.get("profile", {}).get("name") if isinstance(item.get("profile"), dict) else "")
                or _hostname(url),
                "trust_level": "UNTRUSTED_WEB",
            }
        )
    return normalized


def provider_from_env() -> SearchProvider:
    provider_name = os.getenv("WEB_SEARCH_PROVIDER", "").strip().lower()
    api_key = os.getenv("BRAVE_SEARCH_API_KEY", "").strip()
    timeout = parse_float(
        "WEB_SEARCH_TIMEOUT_SECONDS",
        os.getenv("WEB_SEARCH_TIMEOUT_SECONDS", "10"),
        minimum=1,
        maximum=60,
    )
    if provider_name in {"", "auto"} and api_key:
        return BraveSearchProvider(api_key=api_key, timeout_seconds=timeout)
    if provider_name in {"", "disabled", "none"}:
        return DisabledSearchProvider()
    if provider_name == "brave":
        return BraveSearchProvider(api_key=api_key, timeout_seconds=timeout)
    return UnsupportedSearchProvider(provider_name)


def make_search_tool(provider: SearchProvider | None = None):
    active_provider = provider or provider_from_env()

    def search(
        query: str,
        max_results: int | None = None,
        locale: str | None = None,
        language: str | None = None,
        safe_search: bool | None = None,
    ) -> dict[str, object]:
        if not query.strip():
            return {
                "status": "error",
                "provider": active_provider.name,
                "error": "query is required",
                "configured": _provider_configured(active_provider),
                "results": [],
            }
        if active_provider.name == "disabled":
            return {
                "status": "error",
                "error": "web search provider is not configured",
                "provider": active_provider.name,
                "configured": False,
                "results": [],
            }
        if active_provider.name.startswith("unsupported:"):
            return {
                "status": "error",
                "error": "configured web search provider is not supported by this build",
                "provider": active_provider.name,
                "configured": False,
                "results": [],
            }
        if not _provider_configured(active_provider):
            return {
                "status": "error",
                "provider": active_provider.name,
                "error": f"{active_provider.name} search provider is not configured",
                "configured": False,
                "results": [],
            }
        configured_max = parse_int(
            "WEB_SEARCH_MAX_RESULTS",
            os.getenv("WEB_SEARCH_MAX_RESULTS", "8"),
            minimum=1,
            maximum=20,
        )
        requested_max = max_results if max_results is not None else configured_max
        max_results_clamped = max(1, min(int(requested_max), configured_max, 20))
        safe = env_bool("WEB_SAFE_SEARCH", default=True) if safe_search is None else bool(safe_search)
        resolved_locale = locale or language
        retrieved_at = datetime.now(UTC).isoformat()
        results = _provider_search(active_provider, query, max_results_clamped, resolved_locale, safe)
        return {
            "status": "ok",
            "query": query,
            "provider": active_provider.name,
            "configured": True,
            "trust_level": "UNTRUSTED_WEB",
            "results": [_finalize_result(result, retrieved_at) for result in results],
            "_audit": {"network_domains": [_provider_domain(active_provider.name)]},
        }

    return search


def _locale_params(locale: str | None) -> dict[str, str]:
    if not locale:
        return {}
    normalized = locale.replace("_", "-")
    parts = normalized.split("-", 1)
    params = {"search_lang": parts[0].lower()}
    if len(parts) == 2 and len(parts[1]) == 2:
        params["country"] = parts[1].upper()
    return params


def _provider_configured(provider: SearchProvider) -> bool:
    checker = getattr(provider, "is_configured", None)
    if callable(checker):
        return bool(checker())
    return provider.name not in {"disabled"} and not provider.name.startswith("unsupported:")


def _provider_search(
    provider: SearchProvider,
    query: str,
    max_results: int,
    locale: str | None,
    safe_search: bool,
) -> list[dict[str, str]]:
    try:
        return provider.search(query, max_results, locale, safe_search)
    except TypeError:
        return provider.search(query, max_results, locale)  # type: ignore[misc]


def _finalize_result(result: dict[str, str], retrieved_at: str) -> dict[str, str]:
    url = str(result.get("url", ""))
    return {
        "title": str(result.get("title", "")),
        "url": url,
        "snippet": str(result.get("snippet", "")),
        "source": str(result.get("source", "")) or _hostname(url),
        "trust_level": "UNTRUSTED_WEB",
        "retrieved_at": retrieved_at,
    }


def _hostname(url: str) -> str:
    from urllib.parse import urlparse

    return (urlparse(url).hostname or "").lower()


def _provider_domain(provider_name: str) -> str:
    if provider_name == "brave":
        return "api.search.brave.com"
    return provider_name


WEB_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.search",
        "description": "Search the web through a configured provider. Returns a clear error if no provider is configured.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "max_results": {"type": "integer", "minimum": 1, "maximum": 20},
                "locale": {"type": "string"},
                "language": {"type": "string"},
                "safe_search": {"type": "boolean"},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}
