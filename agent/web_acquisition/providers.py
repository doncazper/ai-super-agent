from __future__ import annotations

from typing import Mapping

from agent.connectors.cost_policy import ProviderCandidate, ProviderCostConfig, web_provider_candidates
from agent.web_acquisition.models import SourceCandidate, SourceType

PROVIDER_TO_SOURCE = {
    "cache": SourceType.CACHE,
    "url": SourceType.USER_URL,
    "feed": SourceType.RSS_FEED,
    "sitemap": SourceType.SITEMAP,
    "official_api": SourceType.OFFICIAL_API,
    "searxng": SourceType.SEARXNG,
    "brave": SourceType.BRAVE_SEARCH,
    "serpapi": SourceType.SERPAPI,
}


def source_candidates(
    *,
    env: Mapping[str, str] | None = None,
    cache_available: bool = False,
    url_available: bool = False,
    feed_available: bool = False,
    sitemap_available: bool = False,
    official_api_available: bool = False,
) -> list[SourceCandidate]:
    overrides = {
        "cache": cache_available,
        "url": url_available,
        "feed": feed_available,
        "sitemap": sitemap_available,
        "official_api": official_api_available,
    }
    candidates: list[SourceCandidate] = []
    config = ProviderCostConfig.from_env(env)
    for candidate in web_provider_candidates(env):
        configured = overrides.get(candidate.name, candidate.configured)
        source_type = PROVIDER_TO_SOURCE.get(candidate.name, SourceType.BLOCKED)
        candidates.append(
            SourceCandidate(
                source_type=source_type,
                provider=candidate.name,
                configured=configured,
                reason=_candidate_reason(candidate, configured, config),
                setup_hint=candidate.setup_hint,
                paid_api=candidate.paid_api,
                quota_limited=candidate.quota_limited,
                no_key_required=candidate.no_key_required,
                official=candidate.official,
                local=candidate.local,
                cached=candidate.cached,
                user_provided=candidate.user_provided,
            )
        )
    return candidates


def provider_candidates_for_policy(
    *,
    env: Mapping[str, str] | None = None,
    cache_available: bool = False,
    url_available: bool = False,
    feed_available: bool = False,
    sitemap_available: bool = False,
    official_api_available: bool = False,
) -> list[ProviderCandidate]:
    overrides = {
        "cache": cache_available,
        "url": url_available,
        "feed": feed_available,
        "sitemap": sitemap_available,
        "official_api": official_api_available,
    }
    return [
        ProviderCandidate(
            candidate.name,
            candidate.domain,
            overrides.get(candidate.name, candidate.configured),
            candidate.setup_hint,
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
        for candidate in web_provider_candidates(env)
    ]


def _candidate_reason(candidate: ProviderCandidate, configured: bool, config: ProviderCostConfig) -> str:
    if configured:
        if candidate.name == "cache":
            return "local cache has a matching acquisition result"
        if candidate.name == "url":
            return "user provided an explicit public URL"
        return "provider is configured for the acquisition request"
    if candidate.name == "cache" and not config.search_cache_enabled:
        return "local search cache is disabled"
    return candidate.setup_hint or f"{candidate.name} is not configured"

