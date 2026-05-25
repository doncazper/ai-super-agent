from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from agent.config.runtime import env_bool, parse_int
from agent.web_acquisition.search.base import SearchProvider
from agent.web_acquisition.search.errors import (
    SearchProviderError,
    SearchProviderNotFoundError,
    SearchProviderSetupError,
)
from agent.web_acquisition.search.models import SearchCostClass, SearchProviderInfo, SearchResponse
from agent.web_acquisition.search.normalization import error_response, normalize_search_response


@dataclass(frozen=True)
class MetadataOnlySearchProvider(SearchProvider):
    provider_name: str
    cost_class: SearchCostClass | str
    requires_api_key: bool
    configured: bool
    enabled: bool
    hint: str
    supports_news: bool = False
    supports_images: bool = False
    supports_time_filter: bool = False
    docs_path: str = ""

    def is_configured(self) -> bool:
        return self.configured

    def is_enabled(self) -> bool:
        return self.enabled

    def setup_hint(self) -> str:
        return self.hint

    def search(
        self,
        query: str,
        max_results: int,
        locale: str | None = None,
        safe_search: bool = True,
        freshness: str | None = None,
    ) -> list[dict[str, Any]]:
        raise SearchProviderSetupError(self.hint)

    def info(self) -> SearchProviderInfo:
        base = super().info()
        return SearchProviderInfo(
            provider_name=base.provider_name,
            configured=base.configured,
            enabled=base.enabled,
            cost_class=base.cost_class,
            requires_api_key=base.requires_api_key,
            supports_news=base.supports_news,
            supports_images=base.supports_images,
            supports_time_filter=base.supports_time_filter,
            setup_hint=base.setup_hint,
            status=base.status,
            rate_limit_status=base.rate_limit_status,
            default_enabled=False,
            docs_path=self.docs_path,
        )


class SearchProviderRegistry:
    def __init__(self, providers: Iterable[SearchProvider] | None = None) -> None:
        self._providers: dict[str, SearchProvider] = {}
        for provider in providers or ():
            self.register(provider)

    def register(self, provider: SearchProvider) -> None:
        self._providers[_normalize_provider_name(provider.provider_name)] = provider

    def provider_names(self) -> list[str]:
        return sorted(self._providers)

    def get(self, provider_name: str) -> SearchProvider:
        provider = self._providers.get(_normalize_provider_name(provider_name))
        if provider is None:
            raise SearchProviderNotFoundError(f"unknown search provider: {provider_name}")
        return provider

    def list_providers(self) -> list[dict[str, Any]]:
        return [self._providers[name].info().to_dict() for name in self.provider_names()]

    def search(
        self,
        provider_name: str,
        query: str,
        max_results: int,
        *,
        locale: str | None = None,
        safe_search: bool = True,
        freshness: str | None = None,
        brokered_execution: bool = False,
    ) -> SearchResponse:
        provider_key = _normalize_provider_name(provider_name)
        if not brokered_execution:
            return error_response(
                query=query,
                provider=provider_key,
                exc=SearchProviderError("search provider execution requires ToolBroker routing"),
                status="denied",
            )
        try:
            provider = self.get(provider_key)
        except SearchProviderNotFoundError as exc:
            return error_response(query=query, provider=provider_key, exc=exc)
        if not provider.is_configured() or not provider.is_enabled():
            return error_response(
                query=query,
                provider=provider.provider_name,
                exc=SearchProviderSetupError(provider.setup_hint()),
                status="setup_required",
            )
        try:
            raw_results = provider.search(query, max_results, locale=locale, safe_search=safe_search, freshness=freshness)
        except Exception as exc:
            return error_response(query=query, provider=provider.provider_name, exc=exc)
        return normalize_search_response(
            query=query,
            provider=provider.provider_name,
            results=list(raw_results),
            rate_limit_status=provider.rate_limit_status(),
            paid_api_used=provider.info().cost_class in {SearchCostClass.PAID.value, "paid"},
            cache_used=provider.provider_name in {"cache", "local_cache"},
        )


def default_search_registry(env: Mapping[str, str] | None = None) -> SearchProviderRegistry:
    source = env or os.environ
    return SearchProviderRegistry(
        [
            MetadataOnlySearchProvider(
                "searxng",
                SearchCostClass.FREE,
                requires_api_key=False,
                configured=bool((source.get("SEARXNG_BASE_URL") or "").strip()),
                enabled=_bool_env(source, "SEARXNG_ENABLED", default=False),
                hint="Set SEARXNG_BASE_URL and SEARXNG_ENABLED=true after configuring a self-hosted SearXNG instance.",
                supports_time_filter=True,
                docs_path="docs/web/providers/searxng.md",
            ),
            MetadataOnlySearchProvider(
                "brave",
                SearchCostClass.QUOTA_LIMITED,
                requires_api_key=True,
                configured=bool((source.get("BRAVE_SEARCH_API_KEY") or "").strip()),
                enabled=_bool_env(source, "BRAVE_SEARCH_ENABLED", default=False) or (source.get("WEB_SEARCH_PROVIDER") == "brave"),
                hint="Set BRAVE_SEARCH_API_KEY and BRAVE_SEARCH_ENABLED=true; paid/quota-limited policy still applies.",
                supports_news=True,
                supports_images=True,
                supports_time_filter=True,
                docs_path="docs/web/providers/brave.md",
            ),
            MetadataOnlySearchProvider(
                "serpapi",
                SearchCostClass.PAID,
                requires_api_key=True,
                configured=bool((source.get("SERPAPI_API_KEY") or "").strip()),
                enabled=_bool_env(source, "SERPAPI_ENABLED", default=False),
                hint=(
                    "Set SERPAPI_API_KEY, SERPAPI_ENABLED=true, ALLOW_PAID_APIS=true, "
                    "and MAX_PAID_API_CALLS_PER_DAY>0; SerpAPI is explicit/fallback only."
                ),
                supports_news=True,
                supports_images=True,
                supports_time_filter=True,
                docs_path="docs/web/providers/serpapi.md",
            ),
        ]
    )


def registry_status_payload(registry: SearchProviderRegistry | None = None) -> dict[str, Any]:
    active = registry or default_search_registry()
    return {
        "status": "ok",
        "providers": active.list_providers(),
        "provider_count": len(active.provider_names()),
        "query_history_persisted": False,
        "trust_level": "UNTRUSTED_WEB",
        "notes": [
            "Provider registry inspection is metadata-only and does not call providers.",
            "Search execution must route through ToolBroker and provider policy.",
        ],
        "_audit": {
            "network_domains": [],
            "result_summary": "Listed search provider registry metadata without provider calls.",
        },
    }


def _normalize_provider_name(value: str) -> str:
    return value.strip().casefold().replace("-", "_")


def _bool_env(source: Mapping[str, str], name: str, *, default: bool) -> bool:
    value = source.get(name)
    if value is None or value == "":
        return default
    return value.strip().casefold() in {"1", "true", "yes", "on"}


def default_max_results(env: Mapping[str, str] | None = None) -> int:
    source = env or os.environ
    return parse_int("WEB_SEARCH_MAX_RESULTS", source.get("WEB_SEARCH_MAX_RESULTS", "8"), minimum=1, maximum=20)
