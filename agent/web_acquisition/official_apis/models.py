from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Mapping
from urllib.parse import urlparse

from agent.safety.redaction import SecretRedactor
from agent.web_acquisition.search.models import SearchResult, query_hash, redacted_query
from agent.web_acquisition.trust import UNTRUSTED_WEB


class OfficialApiCapability(str, Enum):
    FETCH_RESOURCE = "fetch_resource"
    SEARCH = "search"
    STATUS = "status"


@dataclass(frozen=True)
class OfficialApiProviderStatus:
    provider_name: str
    configured: bool
    enabled: bool
    requires_api_key: bool
    requires_oauth: bool
    authenticated_apis_enabled: bool
    supported_domains: tuple[str, ...]
    capabilities: tuple[str, ...]
    rate_limit: Mapping[str, Any]
    setup_hint: str
    default_enabled: bool = False
    status: str = "setup_required"
    docs_path: str = ""
    web_scraping_fallback: bool = False
    personal_data_access: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_name": self.provider_name,
            "configured": self.configured,
            "enabled": self.enabled,
            "requires_api_key": self.requires_api_key,
            "requires_oauth": self.requires_oauth,
            "authenticated_apis_enabled": self.authenticated_apis_enabled,
            "supported_domains": list(self.supported_domains),
            "capabilities": list(self.capabilities),
            "rate_limit": dict(self.rate_limit),
            "setup_hint": SecretRedactor().redact(self.setup_hint),
            "default_enabled": self.default_enabled,
            "status": self.status,
            "docs_path": self.docs_path,
            "web_scraping_fallback": self.web_scraping_fallback,
            "personal_data_access": self.personal_data_access,
        }


@dataclass(frozen=True)
class OfficialApiResult:
    title: str
    url: str
    snippet: str
    source: str
    provider: str
    retrieved_at: str
    rank: int
    content_type: str = "official_api_result"
    published_at: str | None = None
    language: str | None = None
    reliability_signals: Mapping[str, Any] = field(default_factory=dict)
    trust_level: str = UNTRUSTED_WEB

    def to_search_result(self) -> SearchResult:
        return SearchResult(
            title=self.title,
            url=self.url,
            snippet=self.snippet,
            source=self.source,
            provider=self.provider,
            retrieved_at=self.retrieved_at,
            rank=self.rank,
            published_at=self.published_at,
            language=self.language,
            content_type=self.content_type,
            reliability_signals=dict(self.reliability_signals),
            trust_level=self.trust_level,
        )

    def to_dict(self) -> dict[str, Any]:
        return self.to_search_result().to_dict()


@dataclass(frozen=True)
class OfficialApiResponse:
    status: str
    provider: str
    results: list[OfficialApiResult] = field(default_factory=list)
    errors: list[Mapping[str, Any]] = field(default_factory=list)
    query_hash: str | None = None
    redacted_query: str | None = None
    resource: str | None = None
    provider_domains: tuple[str, ...] = ()
    rate_limit_status: Mapping[str, Any] = field(default_factory=dict)
    paid_api_used: bool = False
    cache_used: bool = False
    live_call_performed: bool = False
    retrieved_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    query_history_persisted: bool = False
    trust_level: str = UNTRUSTED_WEB

    @classmethod
    def for_query(
        cls,
        *,
        status: str,
        provider: str,
        query: str,
        results: list[OfficialApiResult] | None = None,
        errors: list[Mapping[str, Any]] | None = None,
        provider_domains: tuple[str, ...] = (),
        rate_limit_status: Mapping[str, Any] | None = None,
        live_call_performed: bool = False,
    ) -> "OfficialApiResponse":
        return cls(
            status=status,
            provider=provider,
            query_hash=query_hash(query),
            redacted_query=redacted_query(query),
            results=results or [],
            errors=errors or [],
            provider_domains=provider_domains,
            rate_limit_status=rate_limit_status or {},
            live_call_performed=live_call_performed,
        )

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self.status,
            "provider": self.provider,
            "results": [result.to_dict() for result in self.results],
            "errors": [dict(error) for error in self.errors],
            "provider_domains": list(self.provider_domains),
            "rate_limit_status": dict(self.rate_limit_status),
            "paid_api_used": self.paid_api_used,
            "cache_used": self.cache_used,
            "live_call_performed": self.live_call_performed,
            "retrieved_at": self.retrieved_at,
            "query_history_persisted": self.query_history_persisted,
            "trust_level": self.trust_level,
        }
        if self.query_hash:
            payload["query_hash"] = self.query_hash
        if self.redacted_query:
            payload["redacted_query"] = self.redacted_query
        if self.resource:
            payload["resource"] = self.resource
        return payload


def source_from_url(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def content_hash(*parts: object) -> str:
    joined = "\n".join(str(part or "") for part in parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()
