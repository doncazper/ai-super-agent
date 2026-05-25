from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class NewsConfig:
    enabled: bool = True
    default_provider: str = "auto"
    cost_mode: str = "free_first"
    allow_paid_apis: bool = False
    store_history: bool = False
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    article_cache_ttl_seconds: int = 86400
    max_sources: int = 8
    max_fetched_articles: int = 5
    freshness_default: str = "recent"
    gdelt_enabled: bool = True
    mediacloud_enabled: bool = False
    newsapi_enabled: bool = False
    require_source_grounding: bool = True

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "NewsConfig":
        source = env or os.environ
        return cls(
            enabled=_bool(source.get("NEWS_ENABLED"), default=cls.enabled),
            default_provider=(source.get("NEWS_DEFAULT_PROVIDER") or cls.default_provider).strip().casefold() or "auto",
            cost_mode=(source.get("NEWS_COST_MODE") or cls.cost_mode).strip().casefold() or "free_first",
            allow_paid_apis=_bool(source.get("NEWS_ALLOW_PAID_APIS"), default=cls.allow_paid_apis),
            store_history=_bool(source.get("NEWS_STORE_HISTORY"), default=cls.store_history),
            cache_enabled=_bool(source.get("NEWS_CACHE_ENABLED"), default=cls.cache_enabled),
            cache_ttl_seconds=_int(source.get("NEWS_CACHE_TTL_SECONDS"), default=cls.cache_ttl_seconds),
            article_cache_ttl_seconds=_int(
                source.get("NEWS_ARTICLE_CACHE_TTL_SECONDS"),
                default=cls.article_cache_ttl_seconds,
            ),
            max_sources=_int(source.get("NEWS_MAX_SOURCES"), default=cls.max_sources),
            max_fetched_articles=_int(
                source.get("NEWS_MAX_FETCHED_ARTICLES"),
                default=cls.max_fetched_articles,
            ),
            freshness_default=(source.get("NEWS_FRESHNESS_DEFAULT") or cls.freshness_default).strip().casefold()
            or "recent",
            gdelt_enabled=_bool(source.get("NEWS_GDELT_ENABLED"), default=cls.gdelt_enabled),
            mediacloud_enabled=_bool(source.get("NEWS_MEDIACLOUD_ENABLED"), default=cls.mediacloud_enabled),
            newsapi_enabled=_bool(source.get("NEWS_NEWSAPI_ENABLED"), default=cls.newsapi_enabled),
            require_source_grounding=_bool(
                source.get("NEWS_REQUIRE_SOURCE_GROUNDING"),
                default=cls.require_source_grounding,
            ),
        )

    def to_safe_dict(self) -> dict[str, object]:
        return {
            "enabled": self.enabled,
            "default_provider": self.default_provider,
            "cost_mode": self.cost_mode,
            "allow_paid_apis": self.allow_paid_apis,
            "store_history": self.store_history,
            "cache_enabled": self.cache_enabled,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "article_cache_ttl_seconds": self.article_cache_ttl_seconds,
            "max_sources": self.max_sources,
            "max_fetched_articles": self.max_fetched_articles,
            "freshness_default": self.freshness_default,
            "gdelt_enabled": self.gdelt_enabled,
            "mediacloud_enabled": self.mediacloud_enabled,
            "newsapi_enabled": self.newsapi_enabled,
            "require_source_grounding": self.require_source_grounding,
        }


def _bool(value: str | None, *, default: bool) -> bool:
    if value is None or value == "":
        return default
    return value.strip().casefold() in {"1", "true", "yes", "on"}


def _int(value: str | None, *, default: int) -> int:
    if value is None or value == "":
        return default
    try:
        return max(0, int(value))
    except ValueError:
        return default
