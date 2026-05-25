from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, Mapping
from urllib.parse import urlparse, urlunparse

from agent.safety.redaction import SecretRedactor
from agent.web_acquisition.trust import UNTRUSTED_WEB


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def canonical_source_url(url: str) -> str:
    parsed = urlparse(str(url).strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    normalized = parsed._replace(
        scheme=parsed.scheme.lower(),
        netloc=parsed.netloc.lower(),
        fragment="",
    )
    path = normalized.path or "/"
    return urlunparse(normalized._replace(path=path))


def source_domain(url: str) -> str:
    return (urlparse(canonical_source_url(url)).hostname or "").lower()


def stable_source_id(url: str, provider: str = "unknown") -> str:
    canonical = canonical_source_url(url)
    if not canonical:
        return ""
    provider_label = str(provider or "unknown").strip().casefold()
    digest = hashlib.sha256(f"{provider_label}|{canonical}".encode("utf-8")).hexdigest()[:16]
    return f"src_{digest}"


def content_hash(value: str | None) -> str:
    text = (value or "").strip()
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SourceReference:
    source_id: str
    title: str
    url: str
    domain: str
    provider: str
    retrieved_at: str
    content_hash: str
    trust_level: str = UNTRUSTED_WEB
    reliability_signals: Mapping[str, Any] = field(default_factory=dict)
    published_at: str | None = None
    author: str | None = None

    def to_dict(self) -> dict[str, Any]:
        redactor = SecretRedactor()
        payload = asdict(self)
        payload["reliability_signals"] = dict(self.reliability_signals)
        return redactor.redact(payload)


@dataclass(frozen=True)
class CitationSpan:
    citation_id: str
    text: str
    source_ids: tuple[str, ...]
    start: int | None = None
    end: int | None = None
    evidence_type: str = "fetched"
    snippet_only: bool = False

    def to_dict(self) -> dict[str, Any]:
        return SecretRedactor().redact(asdict(self))


def source_reference_from_mapping(source: Mapping[str, Any], *, default_provider: str = "unknown") -> SourceReference | None:
    url = canonical_source_url(str(source.get("url", "")))
    provider = str(source.get("provider") or default_provider or "unknown")
    source_id = stable_source_id(url, provider)
    if not url or not source_id:
        return None
    fetched = bool(source.get("fetched", False))
    fetch_error = str(source.get("fetch_error") or "").strip()
    snippet_only = not fetched and not fetch_error
    evidence_text = str(source.get("excerpt") or source.get("snippet") or source.get("title") or url)
    reliability = {
        "evidence_type": "fetched" if fetched else "snippet_only",
        "fetched": fetched,
        "snippet_only": snippet_only,
        "failed_fetch": bool(fetch_error),
    }
    if source.get("evidence_type"):
        reliability["source_evidence_type"] = str(source.get("evidence_type"))
    if source.get("language_hint"):
        reliability["language_hint"] = str(source.get("language_hint"))
    return SourceReference(
        source_id=source_id,
        title=SecretRedactor().redact_text(str(source.get("title") or url)),
        url=url,
        domain=str(source.get("source") or source_domain(url)),
        provider=provider,
        retrieved_at=str(source.get("retrieved_at") or utc_now_iso()),
        published_at=str(source.get("published_at")) if source.get("published_at") else None,
        author=SecretRedactor().redact_text(str(source.get("author"))) if source.get("author") else None,
        content_hash=content_hash(evidence_text),
        trust_level=str(source.get("trust_level") or UNTRUSTED_WEB),
        reliability_signals=reliability,
    )


def citation_span_for_source(source: Mapping[str, Any], reference: SourceReference) -> CitationSpan | None:
    if source.get("fetch_error"):
        return None
    text = str(source.get("excerpt") or source.get("snippet") or source.get("title") or reference.title).strip()
    if not text:
        return None
    fetched = bool(source.get("fetched", False))
    evidence_type = "fetched" if fetched else "snippet_only"
    digest = hashlib.sha256(f"{reference.source_id}|{text}".encode("utf-8")).hexdigest()[:12]
    return CitationSpan(
        citation_id=f"cite_{digest}",
        text=SecretRedactor().redact_text(text),
        source_ids=(reference.source_id,),
        evidence_type=evidence_type,
        snippet_only=not fetched,
    )
