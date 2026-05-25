from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agent.web_acquisition.errors import WebAcquisitionError
from agent.web_acquisition.trust import UNTRUSTED_DOCUMENT, UNTRUSTED_WEB


class SourceType(str, Enum):
    CACHE = "cache"
    USER_URL = "user_url"
    RSS_FEED = "rss_feed"
    SITEMAP = "sitemap"
    OFFICIAL_API = "official_api"
    SEARXNG = "searxng"
    BRAVE_SEARCH = "brave_search"
    SERPAPI = "serpapi"
    DIRECT_FETCH = "direct_fetch"
    BLOCKED = "blocked"


class SourceTrust(str, Enum):
    UNTRUSTED_WEB = UNTRUSTED_WEB
    UNTRUSTED_DOCUMENT = UNTRUSTED_DOCUMENT
    TRUSTED_METADATA = "TRUSTED_METADATA"


KNOWN_PROVIDERS = {
    "auto",
    "cache",
    "local_cache",
    "url",
    "user_url",
    "direct_url",
    "direct_fetch",
    "feed",
    "rss",
    "rss_atom",
    "rss_feed",
    "sitemap",
    "official_api",
    "searxng",
    "brave",
    "brave_search",
    "serpapi",
    "blocked",
}


@dataclass(frozen=True)
class SourceCandidate:
    source_type: SourceType
    provider: str
    configured: bool
    reason: str
    setup_hint: str = ""
    url: str | None = None
    paid_api: bool = False
    quota_limited: bool = False
    no_key_required: bool = False
    official: bool = False
    local: bool = False
    cached: bool = False
    user_provided: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_type": self.source_type.value,
            "provider": self.provider,
            "configured": self.configured,
            "reason": self.reason,
            "setup_hint": self.setup_hint,
            "url": self.url,
            "paid_api": self.paid_api,
            "quota_limited": self.quota_limited,
            "no_key_required": self.no_key_required,
            "official": self.official,
            "local": self.local,
            "cached": self.cached,
            "user_provided": self.user_provided,
        }


@dataclass(frozen=True)
class ProviderDecision:
    selected_provider: str | None
    skipped_providers: list[dict[str, Any]]
    skip_reasons: dict[str, str]
    cost_mode: str
    paid_api_used: bool
    cache_used: bool
    audit_summary: str
    status: str = "unavailable"
    reason: str = ""
    setup_hint: str = ""

    @classmethod
    def from_cost_policy(cls, payload: dict[str, Any]) -> "ProviderDecision":
        return cls(
            selected_provider=payload.get("selected_provider"),
            skipped_providers=list(payload.get("skipped_providers") or []),
            skip_reasons=dict(payload.get("skip_reasons") or {}),
            cost_mode=str(payload.get("cost_mode") or "free_first"),
            paid_api_used=bool(payload.get("paid_api_used")),
            cache_used=bool(payload.get("cache_used")),
            audit_summary=str(payload.get("audit_summary") or ""),
            status=str(payload.get("status") or "unavailable"),
            reason=str(payload.get("reason") or ""),
            setup_hint=str(payload.get("setup_hint") or ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "selected_provider": self.selected_provider,
            "skipped_providers": self.skipped_providers,
            "skip_reasons": self.skip_reasons,
            "cost_mode": self.cost_mode,
            "paid_api_used": self.paid_api_used,
            "cache_used": self.cache_used,
            "audit_summary": self.audit_summary,
            "reason": self.reason,
            "setup_hint": self.setup_hint,
        }


@dataclass(frozen=True)
class AcquisitionRequest:
    query: str | None = None
    url: str | None = None
    source_type: SourceType | str | None = None
    provider: str | None = None
    max_results: int = 5
    max_chars: int = 20000
    no_cache: bool = False
    respect_robots: bool = True

    def __post_init__(self) -> None:
        query = (self.query or "").strip()
        url = (self.url or "").strip()
        if not query and not url:
            raise WebAcquisitionError("AcquisitionRequest requires query or url")
        if self.max_results < 1 or self.max_results > 20:
            raise WebAcquisitionError("max_results must be between 1 and 20")
        if self.max_chars < 1 or self.max_chars > 100000:
            raise WebAcquisitionError("max_chars must be between 1 and 100000")
        if self.source_type is not None and not isinstance(self.source_type, SourceType):
            try:
                SourceType(str(self.source_type))
            except ValueError as exc:
                raise WebAcquisitionError(f"unknown source_type: {self.source_type}") from exc
        provider = (self.provider or "auto").strip().casefold()
        if provider not in KNOWN_PROVIDERS:
            raise WebAcquisitionError(f"unknown provider: {self.provider}")


@dataclass(frozen=True)
class AcquisitionResult:
    status: str
    source_type: SourceType
    provider: str | None
    trust_level: SourceTrust = SourceTrust.UNTRUSTED_WEB
    document_trust_level: SourceTrust = SourceTrust.UNTRUSTED_DOCUMENT
    provider_decision: ProviderDecision | None = None
    candidates: list[SourceCandidate] = field(default_factory=list)
    url: str | None = None
    query: str | None = None
    content: str | None = None
    error: str | None = None
    reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self.status,
            "source_type": self.source_type.value,
            "provider": self.provider,
            "trust_level": self.trust_level.value,
            "document_trust_level": self.document_trust_level.value,
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "metadata": self.metadata,
        }
        if self.provider_decision is not None:
            payload["provider_decision"] = self.provider_decision.to_dict()
        if self.url:
            payload["url"] = self.url
        if self.query:
            payload["query"] = self.query
        if self.content is not None:
            payload["content"] = self.content
        if self.error:
            payload["error"] = self.error
        if self.reason:
            payload["reason"] = self.reason
        return payload

