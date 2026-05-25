from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol
from urllib.parse import urlparse

import httpx

from agent.config.runtime import env_bool, parse_float, parse_int
from agent.connectors.cost_policy import (
    ProviderCandidate,
    ProviderCostConfig,
    ProviderDecision,
    ProviderDecisionStatus,
    audit_provider_decision,
    select_provider,
    web_provider_candidates,
)
from agent.safety.audit import AuditLogger
from agent.safety.redaction import SecretRedactor
from agent.tools.errors import ToolError
from agent.web_acquisition.search import default_search_registry, query_hash, redacted_query, registry_status_payload

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
    enabled: bool = False
    timeout_seconds: float = 10
    max_results: int = 10
    safe_search_enabled: bool = True
    endpoint: str = "https://api.search.brave.com/res/v1/web/search"
    transport: httpx.BaseTransport | None = None
    name: str = "brave"

    @classmethod
    def from_env(cls) -> "BraveSearchProvider":
        timeout = parse_float(
            "BRAVE_SEARCH_TIMEOUT_SECONDS",
            os.getenv("BRAVE_SEARCH_TIMEOUT_SECONDS", os.getenv("WEB_SEARCH_TIMEOUT_SECONDS", "10")),
            minimum=1,
            maximum=60,
        )
        max_results = parse_int(
            "BRAVE_SEARCH_MAX_RESULTS",
            os.getenv("BRAVE_SEARCH_MAX_RESULTS", "10"),
            minimum=1,
            maximum=50,
        )
        return cls(
            api_key=os.getenv("BRAVE_SEARCH_API_KEY", "").strip(),
            enabled=env_bool("BRAVE_SEARCH_ENABLED", default=False),
            timeout_seconds=timeout,
            max_results=max_results,
            safe_search_enabled=env_bool("BRAVE_SEARCH_SAFE_SEARCH", default=True),
        )

    def is_configured(self) -> bool:
        return bool(self.api_key.strip())

    def is_enabled(self) -> bool:
        return self.enabled

    def setup_hint(self) -> str:
        if not self.is_configured():
            return (
                "Set BRAVE_SEARCH_API_KEY and BRAVE_SEARCH_ENABLED=true. "
                "Because Brave is quota-limited, also set ALLOW_PAID_APIS=true and MAX_PAID_API_CALLS_PER_DAY>0 before use."
            )
        if not self.enabled:
            return "Set BRAVE_SEARCH_ENABLED=true after confirming Brave quota and cost-policy settings."
        return "Brave Search is configured; quota-limited cost policy still applies."

    def search(
        self,
        query: str,
        max_results: int,
        locale: str | None = None,
        safe_search: bool = True,
    ) -> list[dict[str, str]]:
        if not self.is_configured():
            raise ToolError(self.setup_hint())
        if not self.enabled:
            raise ToolError("Brave Search provider is disabled; set BRAVE_SEARCH_ENABLED=true to use it.")
        count = max(1, min(max_results, self.max_results))
        params: dict[str, Any] = {
            "q": query,
            "count": count,
            "safesearch": "strict" if safe_search and self.safe_search_enabled else "off",
        }
        params.update(_locale_params(locale))
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key,
        }
        try:
            with httpx.Client(timeout=self.timeout_seconds, transport=self.transport, follow_redirects=False) as client:
                response = client.get(self.endpoint, headers=headers, params=params)
                response.raise_for_status()
                payload = response.json()
        except httpx.TimeoutException as exc:
            raise ToolError("Brave Search timed out") from exc
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            if status in {401, 403}:
                raise ToolError("Brave Search returned HTTP 403/401; verify BRAVE_SEARCH_API_KEY and account access.") from exc
            if status == 429:
                raise ToolError("Brave Search rate limit exceeded") from exc
            raise ToolError(f"Brave Search provider returned HTTP {status}") from exc
        except httpx.HTTPError as exc:
            raise ToolError(f"Brave Search provider failed: {type(exc).__name__}") from exc
        except ValueError as exc:
            raise ToolError("Brave Search provider returned malformed JSON") from exc
        if isinstance(payload, dict) and payload.get("error"):
            raise ToolError("Brave Search provider returned an error")
        return normalize_brave_results(payload, count)

    def rate_limit_status(self) -> dict[str, object]:
        return {
            "enforced_by_toolbroker": True,
            "provider": "brave",
            "max_results": self.max_results,
            "timeout_seconds": self.timeout_seconds,
        }


@dataclass(frozen=True)
class SerpApiSearchProvider:
    api_key: str
    enabled: bool = False
    timeout_seconds: float = 10
    max_results: int = 10
    endpoint: str = "https://serpapi.com/search.json"
    transport: httpx.BaseTransport | None = None
    name: str = "serpapi"

    @classmethod
    def from_env(cls) -> "SerpApiSearchProvider":
        timeout = parse_float(
            "SERPAPI_TIMEOUT_SECONDS",
            os.getenv("SERPAPI_TIMEOUT_SECONDS", os.getenv("WEB_SEARCH_TIMEOUT_SECONDS", "10")),
            minimum=1,
            maximum=60,
        )
        max_results = parse_int(
            "SERPAPI_MAX_RESULTS",
            os.getenv("SERPAPI_MAX_RESULTS", "10"),
            minimum=1,
            maximum=50,
        )
        return cls(
            api_key=os.getenv("SERPAPI_API_KEY", "").strip(),
            enabled=env_bool("SERPAPI_ENABLED", default=False),
            timeout_seconds=timeout,
            max_results=max_results,
        )

    def is_configured(self) -> bool:
        return bool(self.api_key.strip())

    def is_enabled(self) -> bool:
        return self.enabled

    def setup_hint(self) -> str:
        if not self.is_configured():
            return (
                "Set SERPAPI_API_KEY and SERPAPI_ENABLED=true. "
                "Because SerpAPI is paid/quota-limited, also set ALLOW_PAID_APIS=true "
                "and MAX_PAID_API_CALLS_PER_DAY>0 before use."
            )
        if not self.enabled:
            return "Set SERPAPI_ENABLED=true after confirming SerpAPI quota and cost-policy settings."
        return "SerpAPI is configured; paid/quota-limited cost policy still applies."

    def search(
        self,
        query: str,
        max_results: int,
        locale: str | None = None,
        safe_search: bool = True,
    ) -> list[dict[str, str]]:
        if not self.is_configured():
            raise ToolError(self.setup_hint())
        if not self.enabled:
            raise ToolError("SerpAPI provider is disabled; set SERPAPI_ENABLED=true to use it.")
        count = max(1, min(max_results, self.max_results))
        params: dict[str, Any] = {
            "engine": "google",
            "q": query,
            "api_key": self.api_key,
            "num": count,
            "safe": "active" if safe_search else "off",
        }
        params.update(_serpapi_locale_params(locale))
        try:
            with httpx.Client(timeout=self.timeout_seconds, transport=self.transport, follow_redirects=False) as client:
                response = client.get(self.endpoint, params=params)
                response.raise_for_status()
                payload = response.json()
        except httpx.TimeoutException as exc:
            raise ToolError("SerpAPI search timed out") from exc
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            if status in {401, 403}:
                raise ToolError("SerpAPI returned HTTP 403/401; verify SERPAPI_API_KEY and account access.") from exc
            if status == 429:
                raise ToolError("SerpAPI rate limit exceeded") from exc
            raise ToolError(f"SerpAPI search provider returned HTTP {status}") from exc
        except httpx.HTTPError as exc:
            raise ToolError(f"SerpAPI search provider failed: {type(exc).__name__}") from exc
        except ValueError as exc:
            raise ToolError("SerpAPI search provider returned malformed JSON") from exc
        if isinstance(payload, dict) and payload.get("error"):
            raise ToolError("SerpAPI search provider returned an error")
        return normalize_serpapi_results(payload, count)

    def rate_limit_status(self) -> dict[str, object]:
        return {
            "enforced_by_toolbroker": True,
            "provider": "serpapi",
            "max_results": self.max_results,
            "timeout_seconds": self.timeout_seconds,
        }


@dataclass(frozen=True)
class SearXngSearchProvider:
    base_url: str
    enabled: bool = False
    timeout_seconds: float = 10
    max_results: int = 10
    safe_search_level: str = "1"
    categories: str = "general"
    transport: httpx.BaseTransport | None = None
    name: str = "searxng"

    @classmethod
    def from_env(cls) -> "SearXngSearchProvider":
        timeout = parse_float(
            "SEARXNG_TIMEOUT_SECONDS",
            os.getenv("SEARXNG_TIMEOUT_SECONDS", "10"),
            minimum=1,
            maximum=60,
        )
        max_results = parse_int(
            "SEARXNG_MAX_RESULTS",
            os.getenv("SEARXNG_MAX_RESULTS", "10"),
            minimum=1,
            maximum=50,
        )
        return cls(
            base_url=os.getenv("SEARXNG_BASE_URL", "").strip(),
            enabled=env_bool("SEARXNG_ENABLED", default=False),
            timeout_seconds=timeout,
            max_results=max_results,
            safe_search_level=os.getenv("SEARXNG_SAFE_SEARCH", "1").strip() or "1",
            categories=os.getenv("SEARXNG_CATEGORIES", "general").strip() or "general",
        )

    def is_configured(self) -> bool:
        return bool(_valid_http_base_url(self.base_url))

    def is_enabled(self) -> bool:
        return self.enabled

    def setup_hint(self) -> str:
        if not self.base_url.strip():
            return "Set SEARXNG_BASE_URL to your self-hosted SearXNG instance and SEARXNG_ENABLED=true."
        if not self.is_configured():
            return "SEARXNG_BASE_URL must be a valid http(s) URL for a self-hosted SearXNG instance."
        if not self.enabled:
            return "Set SEARXNG_ENABLED=true after confirming the configured SearXNG instance allows JSON output."
        return "SearXNG is configured. Ensure JSON output is enabled on the instance."

    def search(
        self,
        query: str,
        max_results: int,
        locale: str | None = None,
        safe_search: bool = True,
    ) -> list[dict[str, str]]:
        if not self.is_configured():
            raise ToolError(self.setup_hint())
        if not self.enabled:
            raise ToolError("SearXNG search provider is disabled; set SEARXNG_ENABLED=true to use the configured instance.")
        base_url = self.base_url.rstrip("/")
        params: dict[str, Any] = {
            "q": query,
            "format": "json",
            "categories": self.categories,
            "safesearch": self.safe_search_level if safe_search else "0",
        }
        params.update(_searxng_locale_params(locale))
        try:
            with httpx.Client(timeout=self.timeout_seconds, transport=self.transport, follow_redirects=False) as client:
                response = client.get(f"{base_url}/search", params=params)
                response.raise_for_status()
                payload = response.json()
        except httpx.TimeoutException as exc:
            raise ToolError("SearXNG search timed out") from exc
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            if status == 403:
                raise ToolError(
                    "SearXNG search returned HTTP 403; confirm the configured instance allows JSON output and API access."
                ) from exc
            if status == 429:
                raise ToolError("SearXNG search rate limit exceeded") from exc
            raise ToolError(f"SearXNG search provider returned HTTP {status}") from exc
        except httpx.HTTPError as exc:
            raise ToolError(f"SearXNG search provider failed: {type(exc).__name__}") from exc
        except ValueError as exc:
            raise ToolError(
                "SearXNG search returned malformed JSON. Enable JSON output on the configured SearXNG instance."
            ) from exc
        return normalize_searxng_results(payload, min(max_results, self.max_results))

    def rate_limit_status(self) -> dict[str, object]:
        return {
            "enforced_by_toolbroker": True,
            "provider": "searxng",
            "max_results": self.max_results,
            "timeout_seconds": self.timeout_seconds,
        }


def normalize_brave_results(payload: dict[str, Any], max_results: int) -> list[dict[str, str]]:
    web_payload = payload.get("web") if isinstance(payload, dict) else None
    news_payload = payload.get("news") if isinstance(payload, dict) else None
    raw_results: list[tuple[dict[str, Any], str]] = []
    if isinstance(web_payload, dict):
        raw_results.extend((item, "web") for item in web_payload.get("results", []) if isinstance(item, dict))
    if isinstance(news_payload, dict):
        raw_results.extend((item, "news") for item in news_payload.get("results", []) if isinstance(item, dict))
    normalized: list[dict[str, str]] = []
    for item, content_type in raw_results[:max_results]:
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
                "published_at": str(item.get("age") or item.get("page_age") or item.get("published") or "").strip(),
                "content_type": content_type,
                "trust_level": "UNTRUSTED_WEB",
            }
        )
    return normalized


def normalize_searxng_results(payload: dict[str, Any], max_results: int) -> list[dict[str, str]]:
    raw_results = payload.get("results", []) if isinstance(payload, dict) else []
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
                "snippet": str(item.get("content") or item.get("snippet") or "").strip(),
                "source": str(item.get("engine") or item.get("source") or "").strip() or _hostname(url),
                "published_at": str(item.get("publishedDate") or item.get("published_date") or "").strip(),
                "content_type": str(item.get("template") or "").strip(),
                "trust_level": "UNTRUSTED_WEB",
            }
        )
    return normalized


def normalize_serpapi_results(payload: dict[str, Any], max_results: int) -> list[dict[str, str]]:
    raw_results = payload.get("organic_results", []) if isinstance(payload, dict) else []
    normalized: list[dict[str, str]] = []
    for item in raw_results[:max_results]:
        if not isinstance(item, dict):
            continue
        url = str(item.get("link") or item.get("url") or "").strip()
        if not url:
            continue
        normalized.append(
            {
                "title": str(item.get("title") or "").strip(),
                "url": url,
                "snippet": str(item.get("snippet") or "").strip(),
                "source": str(item.get("displayed_link") or "").strip() or _hostname(url),
                "published_at": str(item.get("date") or "").strip(),
                "content_type": "organic_result",
                "trust_level": "UNTRUSTED_WEB",
            }
        )
    return normalized


def provider_from_env() -> SearchProvider:
    provider_name = os.getenv("WEB_SEARCH_PROVIDER", "").strip().lower()
    if provider_name in {"", "disabled", "none"}:
        return DisabledSearchProvider()
    if provider_name == "searxng":
        return SearXngSearchProvider.from_env()
    if provider_name == "brave":
        return BraveSearchProvider.from_env()
    if provider_name == "serpapi":
        return SerpApiSearchProvider.from_env()
    return UnsupportedSearchProvider(provider_name)


def make_search_tool(provider: SearchProvider | None = None):
    active_provider = provider or provider_from_env()

    def search(
        query: str,
        max_results: int | None = None,
        locale: str | None = None,
        language: str | None = None,
        safe_search: bool | None = None,
        provider: str | None = None,
        freshness: str | None = None,
    ) -> dict[str, object]:
        if not query.strip():
            return {
                "status": "error",
                "provider": active_provider.name,
                "error": "query is required",
                "errors": [{"code": "invalid_query", "message": "query is required"}],
                "configured": _provider_configured(active_provider),
                "results": [],
                "query_history_persisted": False,
            }
        selected_provider = _resolve_explicit_provider(provider, active_provider)
        if isinstance(selected_provider, dict):
            selected_provider.update(_response_metadata(query, provider=str(provider or active_provider.name), status=str(selected_provider.get("status", "error"))))
            return selected_provider
        run_provider = selected_provider
        if run_provider.name == "disabled":
            return {
                "status": "error",
                "error": "web search provider is not configured",
                "errors": [{"code": "setup_required", "message": "web search provider is not configured"}],
                "provider": run_provider.name,
                "configured": False,
                "results": [],
                **_response_metadata(query, provider=run_provider.name, status="error"),
            }
        if run_provider.name.startswith("unsupported:"):
            message = "configured web search provider is not supported by this build"
            return {
                "status": "error",
                "error": message,
                "errors": [{"code": "unknown_provider", "message": message}],
                "provider": run_provider.name,
                "configured": False,
                "results": [],
                **_response_metadata(query, provider=run_provider.name, status="error"),
            }
        if not _provider_configured(run_provider):
            message = _setup_hint_for_provider(run_provider) or f"{run_provider.name} search provider is not configured"
            return {
                "status": "setup_required",
                "provider": run_provider.name,
                "error": message,
                "setup_hint": message,
                "errors": [{"code": "setup_required", "message": message}],
                "configured": False,
                "results": [],
                **_response_metadata(query, provider=run_provider.name, status="setup_required"),
            }
        if not _provider_enabled(run_provider):
            message = _setup_hint_for_provider(run_provider) or f"{run_provider.name} search provider is disabled"
            return {
                "status": "setup_required",
                "provider": run_provider.name,
                "error": message,
                "setup_hint": message,
                "errors": [{"code": "setup_required", "message": message}],
                "configured": True,
                "enabled": False,
                "results": [],
                **_response_metadata(query, provider=run_provider.name, status="setup_required"),
            }
        provider_decision: ProviderDecision | None = None
        if run_provider.name in {"brave", "serpapi"}:
            provider_decision = _paid_search_provider_decision(run_provider)
            if provider_decision.status is not ProviderDecisionStatus.SELECTED:
                payload = _provider_decision_error(run_provider, provider_decision)
                payload.update(_response_metadata(query, provider=run_provider.name, status="error"))
                return payload
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
        results = _provider_search(run_provider, query, max_results_clamped, resolved_locale, safe)
        return {
            "status": "ok",
            "query": query,
            "query_hash": query_hash(query),
            "redacted_query": redacted_query(query),
            "errors": [],
            "provider": run_provider.name,
            "configured": True,
            "trust_level": "UNTRUSTED_WEB",
            "results": [_finalize_result(result, retrieved_at, run_provider.name, index + 1) for index, result in enumerate(results)],
            "provider_decision": provider_decision.to_dict() if provider_decision else None,
            "rate_limit_status": _rate_limit_status(run_provider),
            "paid_api_used": run_provider.name in {"brave", "serpapi"},
            "cache_used": False,
            "retrieved_at": retrieved_at,
            "query_history_persisted": False,
            "_audit": {
                "network_domains": [_provider_domain(run_provider)],
                "result_summary": f"search provider {run_provider.name} selected",
            },
        }

    return search


def make_serpapi_search_tool(provider: SerpApiSearchProvider | None = None):
    active_provider = provider or SerpApiSearchProvider.from_env()

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
                "provider": "serpapi",
                "error": "query is required",
                "errors": [{"code": "invalid_query", "message": "query is required"}],
                "configured": _provider_configured(active_provider),
                "results": [],
                "query_history_persisted": False,
            }
        if not _provider_configured(active_provider):
            message = _setup_hint_for_provider(active_provider) or (
                "Set SERPAPI_API_KEY, SERPAPI_ENABLED=true, ALLOW_PAID_APIS=true, "
                "and MAX_PAID_API_CALLS_PER_DAY>0 to use SerpAPI."
            )
            payload: dict[str, object] = {
                "status": "setup_required",
                "provider": "serpapi",
                "configured": False,
                "error": "serpapi is not configured",
                "setup_hint": message,
                "errors": [{"code": "setup_required", "message": message}],
                "results": [],
                "_audit": {
                    "network_domains": [],
                    "result_summary": "SerpAPI setup required; missing API key.",
                },
            }
            payload.update(_response_metadata(query, provider="serpapi", status="setup_required"))
            return payload
        provider_decision = _paid_search_provider_decision(active_provider)
        if provider_decision.status is not ProviderDecisionStatus.SELECTED:
            payload = _provider_decision_error(active_provider, provider_decision)
            payload.update(_response_metadata(query, provider="serpapi", status="error"))
            return payload
        if not _provider_enabled(active_provider):
            message = _setup_hint_for_provider(active_provider) or (
                "Set SERPAPI_ENABLED=true to enable the configured SerpAPI provider."
            )
            payload = {
                "status": "setup_required",
                "provider": "serpapi",
                "configured": True,
                "enabled": False,
                "error": "serpapi is disabled",
                "setup_hint": message,
                "provider_decision": provider_decision.to_dict(),
                "errors": [{"code": "setup_required", "message": message}],
                "results": [],
                "_audit": {
                    "network_domains": [],
                    "result_summary": "SerpAPI setup required; provider disabled.",
                },
            }
            payload.update(_response_metadata(query, provider="serpapi", status="setup_required"))
            return payload
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
            "query_hash": query_hash(query),
            "redacted_query": redacted_query(query),
            "errors": [],
            "provider": active_provider.name,
            "configured": True,
            "trust_level": "UNTRUSTED_WEB",
            "provider_decision": provider_decision.to_dict(),
            "results": [_finalize_result(result, retrieved_at, active_provider.name, index + 1) for index, result in enumerate(results)],
            "rate_limit_status": {"enforced_by_toolbroker": True},
            "paid_api_used": True,
            "cache_used": False,
            "retrieved_at": retrieved_at,
            "query_history_persisted": False,
            "_audit": {
                "network_domains": [_provider_domain(active_provider)],
                "result_summary": provider_decision.reason,
            },
        }

    return search


def make_serpapi_doctor_tool(provider: SerpApiSearchProvider | None = None):
    active_provider = provider or SerpApiSearchProvider.from_env()

    def doctor() -> dict[str, object]:
        cost_config = ProviderCostConfig.from_env()
        configured = active_provider.is_configured()
        enabled = active_provider.is_enabled()
        paid_policy_allowed = cost_config.allow_paid_apis and cost_config.max_paid_api_calls_per_day > 0
        return {
            "status": "ok" if configured and enabled and paid_policy_allowed else "setup_required",
            "provider": "serpapi",
            "configured": configured,
            "enabled": enabled,
            "requires_api_key": True,
            "api_key_configured": configured,
            "api_key_redacted": "[REDACTED]" if configured else "",
            "timeout_seconds": active_provider.timeout_seconds,
            "max_results": active_provider.max_results,
            "paid_or_quota_limited": True,
            "allow_paid_apis": cost_config.allow_paid_apis,
            "max_paid_api_calls_per_day": cost_config.max_paid_api_calls_per_day,
            "disabled_by_cost_policy": not paid_policy_allowed,
            "query_history_persisted": False,
            "captcha_bypass_supported": False,
            "setup_hint": active_provider.setup_hint()
            if not paid_policy_allowed
            else "SerpAPI is configured and allowed by paid/quota policy.",
            "notes": [
                "SerpAPI is optional and paid/quota-limited; it is explicit fallback only.",
                "This doctor is config-only and does not call SerpAPI.",
                "SerpAPI is not used for CAPTCHA, paywall, login, or anti-bot bypass in this project.",
                "Search results are labeled UNTRUSTED_WEB and webpage text cannot alter policy or request tools.",
            ],
            "_audit": {
                "network_domains": [],
                "result_summary": "Displayed SerpAPI provider setup status without provider calls.",
            },
        }

    return doctor


def make_searxng_doctor_tool(provider: SearXngSearchProvider | None = None):
    active_provider = provider or SearXngSearchProvider.from_env()

    def doctor() -> dict[str, object]:
        parsed = urlparse(active_provider.base_url.strip())
        configured = active_provider.is_configured()
        enabled = active_provider.is_enabled()
        return {
            "status": "ok" if configured and enabled else "setup_required",
            "provider": "searxng",
            "configured": configured,
            "enabled": enabled,
            "requires_api_key": False,
            "base_url_configured": bool(active_provider.base_url.strip()),
            "base_url_host": (parsed.hostname or "") if configured else "",
            "timeout_seconds": active_provider.timeout_seconds,
            "max_results": active_provider.max_results,
            "safe_search": active_provider.safe_search_level,
            "categories": active_provider.categories,
            "json_output_required": True,
            "default_public_instance_used": False,
            "query_history_persisted": False,
            "setup_hint": active_provider.setup_hint(),
            "notes": [
                "SearXNG is used only when SEARXNG_BASE_URL is configured and SEARXNG_ENABLED=true.",
                "This doctor is config-only and does not call the SearXNG instance.",
                "Search results are labeled UNTRUSTED_WEB and webpage text cannot alter policy or request tools.",
            ],
            "_audit": {
                "network_domains": [],
                "result_summary": "Displayed SearXNG provider setup status without provider calls.",
            },
        }

    return doctor


def make_brave_doctor_tool(provider: BraveSearchProvider | None = None):
    active_provider = provider or BraveSearchProvider.from_env()

    def doctor() -> dict[str, object]:
        cost_config = ProviderCostConfig.from_env()
        configured = active_provider.is_configured()
        enabled = active_provider.is_enabled()
        paid_policy_allowed = cost_config.allow_paid_apis and cost_config.max_paid_api_calls_per_day > 0
        return {
            "status": "ok" if configured and enabled and paid_policy_allowed else "setup_required",
            "provider": "brave",
            "configured": configured,
            "enabled": enabled,
            "requires_api_key": True,
            "api_key_configured": configured,
            "api_key_redacted": "[REDACTED]" if configured else "",
            "timeout_seconds": active_provider.timeout_seconds,
            "max_results": active_provider.max_results,
            "safe_search": active_provider.safe_search_enabled,
            "paid_or_quota_limited": True,
            "allow_paid_apis": cost_config.allow_paid_apis,
            "max_paid_api_calls_per_day": cost_config.max_paid_api_calls_per_day,
            "disabled_by_cost_policy": not paid_policy_allowed,
            "query_history_persisted": False,
            "setup_hint": active_provider.setup_hint()
            if not paid_policy_allowed
            else "Brave Search is configured and allowed by paid/quota policy.",
            "notes": [
                "Brave Search is optional and quota-limited; it is not selected by key presence alone.",
                "This doctor is config-only and does not call Brave Search.",
                "Search results are labeled UNTRUSTED_WEB and webpage text cannot alter policy or request tools.",
            ],
            "_audit": {
                "network_domains": [],
                "result_summary": "Displayed Brave provider setup status without provider calls.",
            },
        }

    return doctor


def make_provider_policy_tools(audit_logger: AuditLogger | None = None):
    def providers() -> dict[str, object]:
        config = ProviderCostConfig.from_env()
        candidates = web_provider_candidates()
        return {
            "status": "ok",
            "providers": [_candidate_to_dict(candidate, config) for candidate in candidates],
            "provider_order": list(config.search_allowed_providers),
            "default_provider": config.search_default_provider,
            "cost_mode": config.cost_mode.value,
            "allow_paid_apis": config.allow_paid_apis,
            "max_paid_api_calls_per_day": config.max_paid_api_calls_per_day,
            "search_store_history": config.search_store_history,
            "search_cache_enabled": config.search_cache_enabled,
            "search_cache_ttl_seconds": config.search_cache_ttl_seconds,
            "_audit": {
                "network_domains": [],
                "result_summary": "Listed web provider policy metadata without provider calls.",
            },
        }

    def provider_policy() -> dict[str, object]:
        config = ProviderCostConfig.from_env()
        return {
            "status": "ok",
            "provider_cost_mode": config.cost_mode.value,
            "allow_paid_apis": config.allow_paid_apis,
            "max_paid_api_calls_per_day": config.max_paid_api_calls_per_day,
            "search_default_provider": config.search_default_provider,
            "search_allowed_providers": list(config.search_allowed_providers),
            "search_store_history": config.search_store_history,
            "search_cache_enabled": config.search_cache_enabled,
            "search_cache_ttl_seconds": config.search_cache_ttl_seconds,
            "rules": [
                "Prefer cache, user-provided URL, RSS/Atom feed, sitemap, official API, self-hosted SearXNG, Brave, then SerpAPI.",
                "Paid or quota-limited providers are skipped unless policy explicitly allows them.",
                "Provider selection does not execute provider calls or persist search history by default.",
                "Web content remains UNTRUSTED_WEB or UNTRUSTED_DOCUMENT.",
            ],
            "_audit": {
                "network_domains": [],
                "result_summary": "Displayed web provider cost policy without provider calls.",
            },
        }

    def provider_decision(query: str, provider: str | None = None, cache_available: bool = False) -> dict[str, object]:
        normalized_query = query.strip()
        if not normalized_query:
            raise ToolError("query is required")
        config = ProviderCostConfig.from_env()
        explicit_provider = None if provider in {None, "", "auto"} else str(provider)
        candidates = _decision_candidates_for_query(normalized_query, cache_available=cache_available)
        decision = select_provider("web", candidates, config=config, explicit_provider=explicit_provider)
        if audit_logger is not None:
            audit_provider_decision(audit_logger, decision, request_id="web-provider-decision-cli")
        payload = decision.to_dict()
        payload.update(
            {
                "status": "ok" if decision.status is ProviderDecisionStatus.SELECTED else "unavailable",
                "query": _redact_query_for_output(normalized_query),
                "query_history_persisted": False,
                "trust_level": "UNTRUSTED_WEB",
            }
        )
        payload["_audit"] = {
            "network_domains": [],
            "result_summary": payload["audit_summary"],
        }
        return payload

    return {
        "web.providers": providers,
        "web.provider_policy": provider_policy,
        "web.provider_decision": provider_decision,
        "web.search_providers": lambda: registry_status_payload(),
    }


def _locale_params(locale: str | None) -> dict[str, str]:
    if not locale:
        return {}
    normalized = locale.replace("_", "-")
    parts = normalized.split("-", 1)
    params = {"search_lang": parts[0].lower()}
    if len(parts) == 2 and len(parts[1]) == 2:
        params["country"] = parts[1].upper()
    return params


def _serpapi_locale_params(locale: str | None) -> dict[str, str]:
    if not locale:
        return {}
    normalized = locale.replace("_", "-")
    parts = normalized.split("-", 1)
    params = {"hl": parts[0].lower()}
    if len(parts) == 2 and len(parts[1]) == 2:
        params["gl"] = parts[1].lower()
    return params


def _searxng_locale_params(locale: str | None) -> dict[str, str]:
    if not locale:
        return {}
    return {"language": locale.replace("_", "-")}


def _paid_search_provider_decision(provider: SearchProvider) -> ProviderDecision:
    provider_name = provider.name
    candidates = [
        _candidate_with_configured(candidate, provider.is_configured())
        if candidate.name == provider_name
        else candidate
        for candidate in web_provider_candidates()
    ]
    return select_provider("web", candidates, explicit_provider=provider_name)


def _decision_candidates_for_query(query: str, *, cache_available: bool) -> list[ProviderCandidate]:
    candidates = web_provider_candidates()
    is_url = _looks_like_url(query)
    is_feed = is_url and any(marker in query.casefold() for marker in ("rss", "atom", "feed"))
    is_sitemap = "sitemap" in query.casefold()
    replacements = {
        "cache": ProviderCandidate(
            "cache",
            "web",
            cache_available,
            "Enable SEARCH_CACHE_ENABLED=true and populate the local cache before search.",
            local=True,
            cached=True,
            no_key_required=True,
        ),
        "url": ProviderCandidate(
            "url",
            "web",
            is_url,
            "Provide a public URL to fetch directly.",
            no_key_required=True,
            user_provided=True,
        ),
        "feed": ProviderCandidate("feed", "web", is_feed, "Provide an RSS/Atom feed URL.", no_key_required=True),
        "sitemap": ProviderCandidate("sitemap", "web", is_sitemap, "Provide a domain with a public sitemap.", no_key_required=True),
    }
    return [replacements.get(candidate.name, candidate) for candidate in candidates]


def _candidate_with_configured(candidate: ProviderCandidate, configured: bool) -> ProviderCandidate:
    return ProviderCandidate(
        name=candidate.name,
        domain=candidate.domain,
        configured=configured,
        setup_hint=candidate.setup_hint,
        no_key_required=candidate.no_key_required,
        official=candidate.official,
        local=candidate.local,
        cached=candidate.cached,
        user_provided=candidate.user_provided,
        paid_api=candidate.paid_api,
        quota_limited=candidate.quota_limited,
        supports_requested_action=candidate.supports_requested_action,
        metadata=candidate.metadata,
    )


def _provider_decision_error(provider: SearchProvider, decision: ProviderDecision) -> dict[str, object]:
    return {
        "status": "error",
        "provider": provider.name,
        "configured": _provider_configured(provider),
        "error": decision.reason,
        "setup_hint": decision.setup_hint,
        "provider_decision": decision.to_dict(),
        "results": [],
        "_audit": {
            "network_domains": [],
            "result_summary": f"provider selection failed: {decision.reason}",
        },
    }


def _candidate_to_dict(candidate: ProviderCandidate, config: ProviderCostConfig) -> dict[str, object]:
    allowed, reason = _provider_allowed_for_display(candidate, config)
    return {
        "provider": candidate.name,
        "configured": candidate.configured,
        "allowed_by_policy": allowed,
        "skip_reason": reason,
        "paid_api": candidate.paid_api,
        "quota_limited": candidate.quota_limited,
        "local": candidate.local,
        "cached": candidate.cached,
        "official": candidate.official,
        "no_key_required": candidate.no_key_required,
        "user_provided": candidate.user_provided,
        "setup_hint": SecretRedactor().redact(candidate.setup_hint),
    }


def _provider_allowed_for_display(candidate: ProviderCandidate, config: ProviderCostConfig) -> tuple[bool, str | None]:
    if candidate.name not in config.search_allowed_providers:
        return False, "not in SEARCH_ALLOWED_PROVIDERS"
    if candidate.requires_paid_opt_in:
        if not config.allow_paid_apis:
            return False, "ALLOW_PAID_APIS=false"
        if config.max_paid_api_calls_per_day <= 0:
            return False, "MAX_PAID_API_CALLS_PER_DAY=0"
    return True, None


def _looks_like_url(value: str) -> bool:
    from urllib.parse import urlparse

    parsed = urlparse(value if "://" in value else f"https://{value}")
    return bool(parsed.scheme in {"http", "https"} and parsed.netloc and "." in parsed.netloc)


def _redact_query_for_output(query: str) -> str:
    redacted = SecretRedactor().redact(query)
    if redacted != query:
        return redacted
    return "[WEB_SEARCH_QUERY_REDACTED]"


def _provider_configured(provider: SearchProvider) -> bool:
    checker = getattr(provider, "is_configured", None)
    if callable(checker):
        return bool(checker())
    return provider.name not in {"disabled"} and not provider.name.startswith("unsupported:")


def _provider_enabled(provider: SearchProvider) -> bool:
    checker = getattr(provider, "is_enabled", None)
    if callable(checker):
        return bool(checker())
    return True


def _setup_hint_for_provider(provider: SearchProvider) -> str:
    setup_hint = getattr(provider, "setup_hint", None)
    if callable(setup_hint):
        return str(setup_hint())
    return ""


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


def _finalize_result(result: dict[str, str], retrieved_at: str, provider: str, rank: int) -> dict[str, str | int | dict[str, object] | None]:
    url = str(result.get("url", ""))
    return {
        "title": str(result.get("title", "")),
        "url": url,
        "snippet": str(result.get("snippet", "")),
        "source": str(result.get("source", "")) or _hostname(url),
        "provider": str(result.get("provider", "")) or provider,
        "trust_level": "UNTRUSTED_WEB",
        "retrieved_at": retrieved_at,
        "rank": int(result.get("rank", rank)) if str(result.get("rank", rank)).isdigit() else rank,
        "published_at": result.get("published_at"),
        "language": result.get("language"),
        "content_type": result.get("content_type"),
        "reliability_signals": result.get("reliability_signals", {}),
    }


def _resolve_explicit_provider(provider_name: str | None, active_provider: SearchProvider) -> SearchProvider | dict[str, object]:
    requested = (provider_name or "auto").strip().casefold().replace("-", "_")
    if requested in {"", "auto"}:
        return active_provider
    if requested == "searxng":
        if active_provider.name == "searxng":
            return active_provider
        return SearXngSearchProvider.from_env()
    if requested == "brave":
        if active_provider.name == "brave":
            return active_provider
        return BraveSearchProvider.from_env()
    if requested == "serpapi":
        return SerpApiSearchProvider.from_env()
    registry = default_search_registry()
    try:
        info = registry.get(requested).info()
    except Exception as exc:
        message = str(exc)
        return {
            "status": "error",
            "provider": requested,
            "configured": False,
            "error": message,
            "errors": [{"code": "unknown_provider", "message": message}],
            "results": [],
            "_audit": {"network_domains": [], "result_summary": message},
        }
    message = info.setup_hint
    return {
        "status": "setup_required",
        "provider": requested,
        "configured": info.configured,
        "enabled": info.enabled,
        "error": message,
        "setup_hint": message,
        "errors": [{"code": "setup_required", "message": message}],
        "results": [],
        "_audit": {"network_domains": [], "result_summary": f"search provider {requested} requires setup"},
    }


def _response_metadata(query: str, *, provider: str, status: str) -> dict[str, object]:
    return {
        "query_hash": query_hash(query),
        "redacted_query": redacted_query(query),
        "rate_limit_status": {},
        "paid_api_used": status == "ok" and provider in {"brave", "serpapi"},
        "cache_used": False,
        "retrieved_at": datetime.now(UTC).isoformat(),
        "query_history_persisted": False,
        "trust_level": "UNTRUSTED_WEB",
    }


def _hostname(url: str) -> str:
    from urllib.parse import urlparse

    return (urlparse(url).hostname or "").lower()


def _provider_domain(provider: SearchProvider | str) -> str:
    provider_name = provider if isinstance(provider, str) else provider.name
    if provider_name == "brave":
        return "api.search.brave.com"
    if provider_name == "searxng":
        base_url = str(getattr(provider, "base_url", "") or SearXngSearchProvider.from_env().base_url)
        parsed = urlparse(base_url)
        return (parsed.hostname or "searxng").lower()
    if provider_name == "serpapi":
        return "serpapi.com"
    return provider_name


def _rate_limit_status(provider: SearchProvider) -> dict[str, object]:
    checker = getattr(provider, "rate_limit_status", None)
    if callable(checker):
        return dict(checker())
    return {"enforced_by_toolbroker": True}


def _valid_http_base_url(value: str) -> str:
    parsed = urlparse(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    return value.strip().rstrip("/")


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
                "provider": {"type": "string"},
                "freshness": {"type": "string"},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}

WEB_SERPAPI_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.search.serpapi",
        "description": "Search the web with SerpAPI only when SERPAPI_API_KEY and paid API policy allow it.",
        "parameters": WEB_SEARCH_SCHEMA["function"]["parameters"],
    },
}

WEB_SERPAPI_DOCTOR_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.serpapi.doctor",
        "description": "Show SerpAPI provider setup status without calling SerpAPI.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}

WEB_SEARXNG_DOCTOR_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.searxng.doctor",
        "description": "Show SearXNG provider setup status without calling the configured instance.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}

WEB_BRAVE_DOCTOR_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.brave.doctor",
        "description": "Show Brave Search provider setup status without calling Brave.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}

WEB_PROVIDERS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.providers",
        "description": "List web provider policy metadata without executing provider calls.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}

WEB_SEARCH_PROVIDERS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.search_providers",
        "description": "List pluggable search provider registry metadata without executing provider calls.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}

WEB_PROVIDER_POLICY_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.provider_policy",
        "description": "Show cost-aware web provider policy without executing provider calls.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}

WEB_PROVIDER_DECISION_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.provider_decision",
        "description": "Explain deterministic cost-aware web provider selection for a query without executing providers.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "provider": {"type": "string"},
                "cache_available": {"type": "boolean"},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}
