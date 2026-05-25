from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Mapping, Sequence

from agent.news.config import NewsConfig


NEWS_PROVIDER_ORDER = (
    "cache",
    "url",
    "feed",
    "sitemap",
    "gdelt",
    "mediacloud",
    "searxng",
    "brave",
    "serpapi",
    "newsapi",
)

NEWS_PROVIDER_ALIASES = {
    "local_news_cache": "cache",
    "local_cache": "cache",
    "user_url": "url",
    "rss": "feed",
    "rss_atom": "feed",
    "atom": "feed",
    "news_sitemap": "sitemap",
    "media_cloud": "mediacloud",
    "news_api": "newsapi",
}


@dataclass(frozen=True)
class NewsProviderCandidate:
    provider_id: str
    configured: bool
    setup_hint: str
    paid_api: bool = False
    local: bool = False
    cached: bool = False
    no_key_required: bool = False
    supports: tuple[str, ...] = ("status", "search", "top", "timeline", "brief", "compare")
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class NewsProviderDecision:
    status: str
    selected_provider: str | None
    reason: str
    setup_hint: str
    requested_provider: str | None
    skipped_providers: tuple[dict[str, object], ...]
    paid_api_used: bool
    cache_used: bool
    trust_level: str
    memory_behavior: str
    audit_fields: tuple[str, ...]
    config: Mapping[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "selected_provider": self.selected_provider,
            "reason": self.reason,
            "setup_hint": self.setup_hint,
            "requested_provider": self.requested_provider,
            "skipped_providers": list(self.skipped_providers),
            "paid_api_used": self.paid_api_used,
            "cache_used": self.cache_used,
            "trust_level": self.trust_level,
            "memory_behavior": self.memory_behavior,
            "audit_fields": list(self.audit_fields),
            "config": dict(self.config),
        }


def news_provider_candidates(config: NewsConfig | None = None, env: Mapping[str, str] | None = None) -> list[NewsProviderCandidate]:
    active_config = config or NewsConfig.from_env(env)
    source = env or os.environ
    searxng_configured = bool(source.get("SEARXNG_BASE_URL", "").strip())
    brave_configured = bool(source.get("BRAVE_SEARCH_API_KEY", "").strip())
    serpapi_configured = bool(source.get("SERPAPI_API_KEY", "").strip())
    return [
        NewsProviderCandidate(
            "cache",
            active_config.cache_enabled,
            "Enable NEWS_CACHE_ENABLED=true and populate the local news cache.",
            local=True,
            cached=True,
            no_key_required=True,
            supports=("status", "search", "top", "brief", "timeline", "compare", "multilingual"),
            metadata={"ttl_seconds": active_config.cache_ttl_seconds},
        ),
        NewsProviderCandidate(
            "url",
            False,
            "Provide a selected public news URL; direct fetch is not implemented in the news module yet.",
            no_key_required=True,
            supports=("article_fetch", "article_extract"),
        ),
        NewsProviderCandidate(
            "feed",
            False,
            "Configure RSS/Atom feeds before feed headline acquisition.",
            no_key_required=True,
            supports=("top", "search", "feed_fetch"),
        ),
        NewsProviderCandidate(
            "sitemap",
            False,
            "Configure public news sitemaps before sitemap acquisition.",
            no_key_required=True,
            supports=("top", "search", "sitemap_fetch"),
        ),
        NewsProviderCandidate(
            "gdelt",
            active_config.gdelt_enabled,
            "GDELT is the planned free public news provider; implementation is still future work.",
            no_key_required=True,
            supports=("search", "top", "timeline", "brief", "compare", "multilingual"),
        ),
        NewsProviderCandidate(
            "mediacloud",
            active_config.mediacloud_enabled,
            "Set NEWS_MEDIACLOUD_ENABLED=true and configure Media Cloud before use.",
            paid_api=True,
            supports=("search", "compare", "brief"),
        ),
        NewsProviderCandidate(
            "searxng",
            searxng_configured,
            "Set SEARXNG_BASE_URL and use the existing web provider policy before news search uses SearXNG.",
            supports=("search", "top"),
        ),
        NewsProviderCandidate(
            "brave",
            brave_configured,
            "Set BRAVE_SEARCH_API_KEY and explicitly allow paid/quota-limited providers before use.",
            paid_api=True,
            supports=("search", "top"),
        ),
        NewsProviderCandidate(
            "serpapi",
            serpapi_configured,
            "Set SERPAPI_API_KEY and explicitly allow paid/quota-limited providers before use.",
            paid_api=True,
            supports=("search", "top"),
        ),
        NewsProviderCandidate(
            "newsapi",
            active_config.newsapi_enabled,
            "Set NEWS_NEWSAPI_ENABLED=true and explicitly allow paid APIs before NewsAPI fallback use.",
            paid_api=True,
            supports=("search", "top"),
        ),
    ]


def select_news_provider(
    *,
    config: NewsConfig | None = None,
    candidates: Sequence[NewsProviderCandidate] | None = None,
    requested_provider: str | None = None,
    purpose: str = "search",
) -> NewsProviderDecision:
    active_config = config or NewsConfig.from_env()
    provider_candidates = list(candidates or news_provider_candidates(active_config))
    requested = _normalize_provider(requested_provider or active_config.default_provider)
    if requested == "auto":
        requested = None

    if not active_config.enabled:
        return _unavailable(
            active_config,
            requested,
            "news is disabled by NEWS_ENABLED=false",
            "Set NEWS_ENABLED=true to enable future News Intelligence metadata paths.",
            (),
        )

    by_id = {_normalize_provider(candidate.provider_id): candidate for candidate in provider_candidates}
    skipped: list[dict[str, object]] = []

    if requested:
        candidate = by_id.get(requested)
        if candidate is None:
            return _unavailable(
                active_config,
                requested,
                f"requested news provider '{requested}' is not supported",
                f"Choose one of: {', '.join(NEWS_PROVIDER_ORDER)}.",
                (),
            )
        allowed, reason = _candidate_allowed(candidate, active_config, purpose)
        if candidate.configured and allowed:
            return _selected(active_config, candidate, requested, "explicit news provider selected", skipped)
        skipped.append(_skip(candidate, reason or _unavailable_reason(candidate, purpose)))
        return _unavailable(active_config, requested, skipped[-1]["reason"], candidate.setup_hint, tuple(skipped))

    for candidate in sorted(provider_candidates, key=_rank):
        allowed, reason = _candidate_allowed(candidate, active_config, purpose)
        if candidate.configured and allowed:
            return _selected(active_config, candidate, None, f"free_first selected {candidate.provider_id}", skipped)
        skipped.append(_skip(candidate, reason or _unavailable_reason(candidate, purpose)))

    return _unavailable(
        active_config,
        None,
        "no configured news provider is available under the current policy",
        _first_setup_hint(provider_candidates),
        tuple(skipped),
    )


def _candidate_allowed(candidate: NewsProviderCandidate, config: NewsConfig, purpose: str) -> tuple[bool, str | None]:
    if purpose not in candidate.supports:
        return False, f"{candidate.provider_id} does not support {purpose}"
    if candidate.paid_api and not config.allow_paid_apis:
        return False, f"{candidate.provider_id} skipped because NEWS_ALLOW_PAID_APIS=false"
    return True, None


def _selected(
    config: NewsConfig,
    candidate: NewsProviderCandidate,
    requested: str | None,
    reason: str,
    skipped: Sequence[dict[str, object]],
) -> NewsProviderDecision:
    return NewsProviderDecision(
        status="selected",
        selected_provider=candidate.provider_id,
        reason=reason,
        setup_hint=candidate.setup_hint,
        requested_provider=requested,
        skipped_providers=tuple(skipped),
        paid_api_used=candidate.paid_api,
        cache_used=candidate.cached,
        trust_level="UNTRUSTED_WEB",
        memory_behavior="no_store_history_or_article_bodies",
        audit_fields=("provider", "selected_provider", "skipped_providers", "paid_api_used", "cache_used"),
        config=config.to_safe_dict(),
    )


def _unavailable(
    config: NewsConfig,
    requested: str | None,
    reason: object,
    setup_hint: str,
    skipped: Sequence[dict[str, object]],
) -> NewsProviderDecision:
    return NewsProviderDecision(
        status="unavailable",
        selected_provider=None,
        reason=str(reason),
        setup_hint=setup_hint,
        requested_provider=requested,
        skipped_providers=tuple(skipped),
        paid_api_used=False,
        cache_used=False,
        trust_level="UNTRUSTED_WEB",
        memory_behavior="no_store_history_or_article_bodies",
        audit_fields=("provider", "selected_provider", "skipped_providers", "paid_api_used", "cache_used"),
        config=config.to_safe_dict(),
    )


def _skip(candidate: NewsProviderCandidate, reason: str) -> dict[str, object]:
    return {
        "provider": candidate.provider_id,
        "configured": candidate.configured,
        "paid_api": candidate.paid_api,
        "reason": reason,
        "setup_hint": candidate.setup_hint,
    }


def _rank(candidate: NewsProviderCandidate) -> tuple[int, int, str]:
    try:
        index = NEWS_PROVIDER_ORDER.index(candidate.provider_id)
    except ValueError:
        index = len(NEWS_PROVIDER_ORDER) + 10
    return (1 if candidate.paid_api else 0, index, candidate.provider_id)


def _unavailable_reason(candidate: NewsProviderCandidate, purpose: str) -> str:
    if purpose not in candidate.supports:
        return f"{candidate.provider_id} does not support {purpose}"
    if not candidate.configured:
        return f"{candidate.provider_id} is not configured"
    return f"{candidate.provider_id} is unavailable"


def _first_setup_hint(candidates: Sequence[NewsProviderCandidate]) -> str:
    for candidate in candidates:
        if candidate.setup_hint:
            return candidate.setup_hint
    return "Configure a compliant news provider or use a selected public URL."


def _normalize_provider(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().casefold().replace("-", "_")
    return NEWS_PROVIDER_ALIASES.get(normalized, normalized) or None
