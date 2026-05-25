from __future__ import annotations

import re
from urllib.parse import urlparse

from agent.tools.errors import ToolError
from agent.tools.web.fetch import DomainRules, normalize_url
from agent.web_acquisition.audit import audit_payload
from agent.web_acquisition.errors import WebAcquisitionError
from agent.web_acquisition.models import AcquisitionRequest, AcquisitionResult, SourceType
from agent.web_acquisition.policy import decide_provider
from agent.web_acquisition.providers import source_candidates


class WebAcquisitionRouter:
    """Plan public web acquisition without executing network fetches."""

    def __init__(self, *, domain_rules: DomainRules | None = None) -> None:
        self.domain_rules = domain_rules or DomainRules.from_env()

    def plan(self, request: AcquisitionRequest, *, cache_available: bool = False) -> AcquisitionResult:
        source_type = self._source_type_for(request, cache_available=cache_available)
        explicit_provider = request.provider if request.provider not in {None, "", "auto"} else None
        decision = decide_provider(
            explicit_provider=explicit_provider,
            cache_available=cache_available,
            url_available=source_type in {SourceType.USER_URL, SourceType.DIRECT_FETCH},
            feed_available=source_type == SourceType.RSS_FEED,
            sitemap_available=source_type == SourceType.SITEMAP,
        )
        candidates = source_candidates(
            cache_available=cache_available,
            url_available=source_type in {SourceType.USER_URL, SourceType.DIRECT_FETCH},
            feed_available=source_type == SourceType.RSS_FEED,
            sitemap_available=source_type == SourceType.SITEMAP,
        )
        provider = decision.selected_provider or self._provider_for_source(source_type)
        status = "ok" if source_type != SourceType.BLOCKED else "unavailable"
        return AcquisitionResult(
            status=status,
            source_type=source_type,
            provider=provider,
            provider_decision=decision,
            candidates=candidates,
            query=request.query,
            url=request.url,
            error="source_blocked_or_unavailable" if status == "unavailable" else None,
            reason=decision.reason,
            metadata={
                "final_model_handling": "web results are passed as data, never as instructions",
                "query_history_stored": False,
                "cache_preferred": cache_available and not request.no_cache,
            },
        )

    def source_status(self, url: str) -> AcquisitionResult:
        try:
            normalized_url = normalize_url(url)
            domain = self.domain_rules.validate_url(normalized_url)
        except (ToolError, ValueError) as exc:
            decision = decide_provider()
            return AcquisitionResult(
                status="unavailable",
                source_type=SourceType.BLOCKED,
                provider="blocked",
                provider_decision=decision,
                error="blocked_or_invalid_url",
                reason=str(exc),
                url=url,
                metadata={
                    "bypass_attempted": False,
                    "network_actions": "none",
                    "_audit": audit_payload(source_type=SourceType.BLOCKED, provider="blocked", decision=decision),
                },
            )
        source_type = self._source_type_for(AcquisitionRequest(url=normalized_url))
        decision = decide_provider(
            url_available=source_type in {SourceType.USER_URL, SourceType.DIRECT_FETCH},
            feed_available=source_type == SourceType.RSS_FEED,
            sitemap_available=source_type == SourceType.SITEMAP,
        )
        return AcquisitionResult(
            status="ok",
            source_type=source_type,
            provider=decision.selected_provider or self._provider_for_source(source_type),
            provider_decision=decision,
            candidates=source_candidates(
                url_available=source_type in {SourceType.USER_URL, SourceType.DIRECT_FETCH},
                feed_available=source_type == SourceType.RSS_FEED,
                sitemap_available=source_type == SourceType.SITEMAP,
            ),
            url=normalized_url,
            metadata={
                "domain": domain,
                "network_actions": "none",
                "requires_fetch_for_content": True,
                "bypass_attempted": False,
                "final_model_handling": "web results are passed as data, never as instructions",
                "_audit": audit_payload(
                    source_type=source_type,
                    provider=decision.selected_provider,
                    network_domains=[domain],
                    decision=decision,
                ),
            },
        )

    def _source_type_for(self, request: AcquisitionRequest, *, cache_available: bool = False) -> SourceType:
        if cache_available and not request.no_cache:
            return SourceType.CACHE
        if request.source_type is not None:
            return request.source_type if isinstance(request.source_type, SourceType) else SourceType(str(request.source_type))
        value = (request.url or request.query or "").strip()
        if not value:
            raise WebAcquisitionError("query or url is required")
        if _looks_like_sitemap(value):
            return SourceType.SITEMAP
        if _looks_like_feed(value):
            return SourceType.RSS_FEED
        if _looks_like_url(value):
            return SourceType.USER_URL
        if _looks_like_domain(value):
            return SourceType.SITEMAP
        return SourceType.BLOCKED

    @staticmethod
    def _provider_for_source(source_type: SourceType) -> str | None:
        return {
            SourceType.CACHE: "cache",
            SourceType.USER_URL: "url",
            SourceType.RSS_FEED: "feed",
            SourceType.SITEMAP: "sitemap",
            SourceType.OFFICIAL_API: "official_api",
            SourceType.SEARXNG: "searxng",
            SourceType.BRAVE_SEARCH: "brave",
            SourceType.SERPAPI: "serpapi",
            SourceType.DIRECT_FETCH: "url",
            SourceType.BLOCKED: None,
        }[source_type]


def _looks_like_url(value: str) -> bool:
    parsed = urlparse(value if urlparse(value).scheme else f"https://{value}")
    return bool(parsed.netloc and "." in parsed.netloc and (urlparse(value).scheme or "/" in value))


def _looks_like_domain(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}", value.strip()))


def _looks_like_feed(value: str) -> bool:
    path = urlparse(value if urlparse(value).scheme else f"https://{value}").path.casefold()
    return any(marker in path for marker in ("/feed", "rss", "atom")) or path.endswith((".rss", ".atom", ".xml"))


def _looks_like_sitemap(value: str) -> bool:
    return "sitemap" in urlparse(value if urlparse(value).scheme else f"https://{value}").path.casefold()
