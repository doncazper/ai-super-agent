from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Mapping

from agent.web_acquisition.search.errors import normalize_provider_error
from agent.web_acquisition.search.models import SearchResponse, SearchResult, query_hash, redacted_query, source_from_url


def normalize_search_result(raw: SearchResult | Mapping[str, Any], *, provider: str, rank: int, retrieved_at: str) -> SearchResult:
    if isinstance(raw, SearchResult):
        return raw
    url = str(raw.get("url") or "").strip()
    return SearchResult(
        title=str(raw.get("title") or "").strip(),
        url=url,
        snippet=str(raw.get("snippet") or "").strip(),
        source=str(raw.get("source") or "").strip() or source_from_url(url),
        provider=str(raw.get("provider") or provider),
        retrieved_at=str(raw.get("retrieved_at") or retrieved_at),
        rank=int(raw.get("rank") or rank),
        published_at=str(raw.get("published_at") or "").strip() or None,
        language=str(raw.get("language") or "").strip() or None,
        content_type=str(raw.get("content_type") or "").strip() or None,
        reliability_signals=dict(raw.get("reliability_signals") or {}),
        trust_level="UNTRUSTED_WEB",
    )


def normalize_search_response(
    *,
    query: str,
    provider: str,
    results: list[SearchResult | Mapping[str, Any]] | None = None,
    errors: list[Mapping[str, Any]] | None = None,
    status: str = "ok",
    rate_limit_status: Mapping[str, Any] | None = None,
    paid_api_used: bool = False,
    cache_used: bool = False,
) -> SearchResponse:
    retrieved_at = datetime.now(UTC).isoformat()
    normalized_results = [
        normalize_search_result(result, provider=provider, rank=index + 1, retrieved_at=retrieved_at)
        for index, result in enumerate(results or [])
        if str((result.url if isinstance(result, SearchResult) else result.get("url", ""))).strip()
    ]
    return SearchResponse(
        status=status,
        provider=provider,
        query_hash=query_hash(query),
        redacted_query=redacted_query(query),
        results=normalized_results,
        errors=errors or [],
        rate_limit_status=rate_limit_status or {},
        paid_api_used=paid_api_used,
        cache_used=cache_used,
        retrieved_at=retrieved_at,
        query_history_persisted=False,
    )


def error_response(*, query: str, provider: str, exc: Exception, status: str = "error") -> SearchResponse:
    return normalize_search_response(
        query=query,
        provider=provider,
        status=status,
        errors=[normalize_provider_error(exc)],
    )
