from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Mapping
from urllib.parse import urlparse

from agent.safety.redaction import SecretRedactor
from agent.web_acquisition.trust import UNTRUSTED_WEB


class SearchProviderStatus(str, Enum):
    AVAILABLE = "available"
    SETUP_REQUIRED = "setup_required"
    DISABLED = "disabled"
    ERROR = "error"


class SearchCostClass(str, Enum):
    LOCAL = "local"
    FREE = "free"
    QUOTA_LIMITED = "quota_limited"
    PAID = "paid"


@dataclass(frozen=True)
class SearchProviderInfo:
    provider_name: str
    configured: bool
    enabled: bool
    cost_class: SearchCostClass | str
    requires_api_key: bool
    supports_news: bool
    supports_images: bool
    supports_time_filter: bool
    setup_hint: str
    status: SearchProviderStatus | str = SearchProviderStatus.SETUP_REQUIRED
    rate_limit_status: Mapping[str, Any] = field(default_factory=dict)
    default_enabled: bool = False
    docs_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_name": self.provider_name,
            "configured": self.configured,
            "enabled": self.enabled,
            "cost_class": self.cost_class.value if isinstance(self.cost_class, SearchCostClass) else str(self.cost_class),
            "requires_api_key": self.requires_api_key,
            "supports_news": self.supports_news,
            "supports_images": self.supports_images,
            "supports_time_filter": self.supports_time_filter,
            "setup_hint": SecretRedactor().redact(self.setup_hint),
            "status": self.status.value if isinstance(self.status, SearchProviderStatus) else str(self.status),
            "rate_limit_status": dict(self.rate_limit_status),
            "default_enabled": self.default_enabled,
            "docs_path": self.docs_path,
        }


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str
    provider: str
    retrieved_at: str
    rank: int
    published_at: str | None = None
    language: str | None = None
    content_type: str | None = None
    reliability_signals: Mapping[str, Any] = field(default_factory=dict)
    trust_level: str = UNTRUSTED_WEB

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
            "provider": self.provider,
            "retrieved_at": self.retrieved_at,
            "rank": self.rank,
            "reliability_signals": dict(self.reliability_signals),
            "trust_level": self.trust_level,
        }
        if self.published_at:
            payload["published_at"] = self.published_at
        if self.language:
            payload["language"] = self.language
        if self.content_type:
            payload["content_type"] = self.content_type
        return payload


@dataclass(frozen=True)
class SearchResponse:
    status: str
    provider: str
    query_hash: str
    redacted_query: str
    results: list[SearchResult] = field(default_factory=list)
    errors: list[Mapping[str, Any]] = field(default_factory=list)
    rate_limit_status: Mapping[str, Any] = field(default_factory=dict)
    paid_api_used: bool = False
    cache_used: bool = False
    retrieved_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    query_history_persisted: bool = False
    trust_level: str = UNTRUSTED_WEB

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "provider": self.provider,
            "query_hash": self.query_hash,
            "redacted_query": self.redacted_query,
            "results": [result.to_dict() for result in self.results],
            "errors": [dict(error) for error in self.errors],
            "rate_limit_status": dict(self.rate_limit_status),
            "paid_api_used": self.paid_api_used,
            "cache_used": self.cache_used,
            "retrieved_at": self.retrieved_at,
            "query_history_persisted": self.query_history_persisted,
            "trust_level": self.trust_level,
        }


def query_hash(query: str) -> str:
    return hashlib.sha256(query.strip().encode("utf-8")).hexdigest()


def redacted_query(query: str) -> str:
    redacted = SecretRedactor().redact(query.strip())
    if redacted != query.strip():
        return redacted
    return "[WEB_SEARCH_QUERY_REDACTED]"


def source_from_url(url: str) -> str:
    return (urlparse(url).hostname or "").lower()
