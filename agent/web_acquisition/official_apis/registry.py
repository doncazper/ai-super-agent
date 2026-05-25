from __future__ import annotations

from datetime import UTC, datetime
from typing import Iterable
from urllib.parse import urlparse

from agent.web_acquisition.official_apis.arxiv import ArxivOfficialApiProvider
from agent.web_acquisition.official_apis.base import OfficialApiProvider
from agent.web_acquisition.official_apis.errors import (
    OfficialApiError,
    OfficialApiNotFoundError,
    OfficialApiPolicyError,
    OfficialApiSetupError,
    normalize_official_api_error,
)
from agent.web_acquisition.official_apis.github import GitHubOfficialApiProvider
from agent.web_acquisition.official_apis.models import OfficialApiResponse
from agent.web_acquisition.official_apis.reddit import RedditOfficialApiProvider
from agent.web_acquisition.official_apis.wikipedia import WikipediaOfficialApiProvider


class OfficialApiRegistry:
    def __init__(self, providers: Iterable[OfficialApiProvider] | None = None) -> None:
        self._providers: dict[str, OfficialApiProvider] = {}
        for provider in providers or ():
            self.register(provider)

    def register(self, provider: OfficialApiProvider) -> None:
        self._providers[_normalize_provider_name(provider.provider_name)] = provider

    def provider_names(self) -> list[str]:
        return sorted(self._providers)

    def get(self, provider_name: str) -> OfficialApiProvider:
        provider = self._providers.get(_normalize_provider_name(provider_name))
        if provider is None:
            raise OfficialApiNotFoundError(provider_name)
        return provider

    def list_providers(self) -> list[dict[str, object]]:
        return [self._providers[name].status().to_dict() for name in self.provider_names()]

    def match_provider_for_url(self, url_or_domain: str) -> OfficialApiProvider | None:
        host = _host(url_or_domain)
        if not host:
            return None
        for provider in self._providers.values():
            if any(host == domain or host.endswith(f".{domain}") for domain in provider.supported_domains):
                return provider
        return None

    def match_provider_for_domain(self, domain: str) -> OfficialApiProvider | None:
        return self.match_provider_for_url(domain)

    def provider_status(self, provider_name: str) -> dict[str, object]:
        return self.get(provider_name).status().to_dict()

    def search(
        self,
        provider_name: str,
        query: str,
        max_results: int,
        *,
        locale: str | None = None,
        safe_search: bool = True,
        brokered_execution: bool = False,
    ) -> OfficialApiResponse:
        provider_key = _normalize_provider_name(provider_name)
        if not brokered_execution:
            return OfficialApiResponse.for_query(
                status="denied",
                provider=provider_key,
                query=query,
                errors=[
                    normalize_official_api_error(
                        OfficialApiPolicyError("official API execution requires ToolBroker routing")
                    )
                ],
            )
        try:
            provider = self.get(provider_key)
        except OfficialApiNotFoundError as exc:
            return OfficialApiResponse.for_query(
                status="error",
                provider=provider_key,
                query=query,
                errors=[normalize_official_api_error(exc)],
            )
        if not provider.is_configured() or not provider.is_enabled():
            exc = OfficialApiSetupError(provider.setup_hint(), setup_hint=provider.setup_hint())
            return OfficialApiResponse.for_query(
                status="setup_required",
                provider=provider.provider_name,
                query=query,
                errors=[normalize_official_api_error(exc)],
                provider_domains=provider.supported_domains,
                rate_limit_status=provider.rate_limit(),
            )
        try:
            raw_results = provider.search(query, max_results, locale=locale, safe_search=safe_search)
        except OfficialApiError as exc:
            return OfficialApiResponse.for_query(
                status="setup_required" if exc.code == "setup_required" else "error",
                provider=provider.provider_name,
                query=query,
                errors=[normalize_official_api_error(exc)],
                provider_domains=provider.supported_domains,
                rate_limit_status=provider.rate_limit(),
            )
        except Exception as exc:
            return OfficialApiResponse.for_query(
                status="error",
                provider=provider.provider_name,
                query=query,
                errors=[normalize_official_api_error(exc)],
                provider_domains=provider.supported_domains,
                rate_limit_status=provider.rate_limit(),
            )
        return OfficialApiResponse.for_query(
            status="ok",
            provider=provider.provider_name,
            query=query,
            results=list(raw_results),
            provider_domains=provider.supported_domains,
            rate_limit_status=provider.rate_limit(),
            live_call_performed=False,
        )


def default_official_api_registry() -> OfficialApiRegistry:
    return OfficialApiRegistry(
        [
            GitHubOfficialApiProvider(),
            WikipediaOfficialApiProvider(),
            ArxivOfficialApiProvider(),
            RedditOfficialApiProvider(),
        ]
    )


def registry_status_payload(registry: OfficialApiRegistry | None = None) -> dict[str, object]:
    active = registry or default_official_api_registry()
    return {
        "status": "ok",
        "provider_count": len(active.provider_names()),
        "providers": active.list_providers(),
        "retrieved_at": datetime.now(UTC).isoformat(),
        "live_call_performed": False,
        "notes": [
            "Official API registry inspection is metadata-only and performs no provider calls.",
            "Provider bridges may advertise capabilities, but execution must still route through ToolBroker, PolicyEngine, and AuditLogger.",
            "Reddit is read-only/setup-gated and does not use web scraping as an API substitute.",
        ],
        "_audit": {
            "network_domains": [],
            "result_summary": "Listed official API provider registry metadata without provider calls.",
        },
    }


def _normalize_provider_name(value: str) -> str:
    return value.strip().casefold().replace("-", "_")


def _host(url_or_domain: str) -> str:
    value = url_or_domain.strip()
    if not value:
        return ""
    parsed = urlparse(value if "://" in value else f"https://{value}")
    return (parsed.hostname or "").lower()
