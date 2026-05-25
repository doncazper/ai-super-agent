from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping

from agent.safety.redaction import SecretRedactor
from agent.web_acquisition.citations import (
    CitationSpan,
    SourceReference,
    citation_span_for_source,
    source_reference_from_mapping,
    stable_source_id,
    utc_now_iso,
)
from agent.web_acquisition.trust import UNTRUSTED_WEB


DEFAULT_SOURCE_BUNDLE_PATH = Path("reports/research/last_sources.json")


@dataclass(frozen=True)
class ClaimAttribution:
    claim_id: str
    claim: str
    source_ids: tuple[str, ...]
    support_level: str
    inference: bool = False
    limitations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return SecretRedactor().redact(asdict(self))


@dataclass(frozen=True)
class ResearchSourceBundle:
    status: str
    generated_at: str
    sources: tuple[SourceReference, ...] = ()
    citations: tuple[CitationSpan, ...] = ()
    claims: tuple[ClaimAttribution, ...] = ()
    failed_sources: tuple[Mapping[str, Any], ...] = ()
    limitations: tuple[str, ...] = ()
    trust_level: str = UNTRUSTED_WEB
    query_hash: str | None = None
    provider: str | None = None

    def to_dict(self) -> dict[str, Any]:
        redactor = SecretRedactor()
        return redactor.redact(
            {
                "status": self.status,
                "generated_at": self.generated_at,
                "query_hash": self.query_hash,
                "provider": self.provider,
                "trust_level": self.trust_level,
                "sources": [source.to_dict() for source in self.sources],
                "citations": [citation.to_dict() for citation in self.citations],
                "claims": [claim.to_dict() for claim in self.claims],
                "failed_sources": [dict(item) for item in self.failed_sources],
                "limitations": list(self.limitations),
            }
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "ResearchSourceBundle":
        sources = tuple(SourceReference(**item) for item in payload.get("sources", []) if isinstance(item, dict))
        citations = tuple(
            CitationSpan(
                citation_id=str(item.get("citation_id", "")),
                text=str(item.get("text", "")),
                source_ids=tuple(str(source_id) for source_id in item.get("source_ids", [])),
                start=item.get("start"),
                end=item.get("end"),
                evidence_type=str(item.get("evidence_type", "")),
                snippet_only=bool(item.get("snippet_only", False)),
            )
            for item in payload.get("citations", [])
            if isinstance(item, dict)
        )
        claims = tuple(
            ClaimAttribution(
                claim_id=str(item.get("claim_id", "")),
                claim=str(item.get("claim", "")),
                source_ids=tuple(str(source_id) for source_id in item.get("source_ids", [])),
                support_level=str(item.get("support_level", "")),
                inference=bool(item.get("inference", False)),
                limitations=tuple(str(limit) for limit in item.get("limitations", [])),
            )
            for item in payload.get("claims", [])
            if isinstance(item, dict)
        )
        return cls(
            status=str(payload.get("status", "unknown")),
            generated_at=str(payload.get("generated_at") or utc_now_iso()),
            query_hash=str(payload.get("query_hash")) if payload.get("query_hash") else None,
            provider=str(payload.get("provider")) if payload.get("provider") else None,
            trust_level=str(payload.get("trust_level") or UNTRUSTED_WEB),
            sources=sources,
            citations=citations,
            claims=claims,
            failed_sources=tuple(dict(item) for item in payload.get("failed_sources", []) if isinstance(item, dict)),
            limitations=tuple(str(item) for item in payload.get("limitations", [])),
        )


def research_query_hash(query: str | None) -> str | None:
    if not query:
        return None
    return hashlib.sha256(query.strip().encode("utf-8")).hexdigest()


def build_research_source_bundle(report: Mapping[str, Any]) -> ResearchSourceBundle:
    source_items = [item for item in report.get("sources", []) if isinstance(item, Mapping)]
    references: list[SourceReference] = []
    citations: list[CitationSpan] = []
    failed_urls = {str(item.get("url", "")) for item in report.get("fetch_failures", []) if isinstance(item, Mapping)}

    for item in source_items:
        reference = source_reference_from_mapping(item, default_provider=str(report.get("provider") or "unknown"))
        if reference is None:
            continue
        references.append(reference)
        if item.get("fetch_error") or reference.url in failed_urls:
            continue
        citation = citation_span_for_source(item, reference)
        if citation is not None:
            citations.append(citation)

    failed_sources = _failed_sources(report.get("fetch_failures", []), references, source_items)
    claims = _claim_attributions(citations, tuple(str(item) for item in report.get("limitations", [])))
    return ResearchSourceBundle(
        status="ok",
        generated_at=utc_now_iso(),
        query_hash=research_query_hash(str(report.get("query") or "")),
        provider=str(report.get("provider")) if report.get("provider") else None,
        sources=tuple(references),
        citations=tuple(citations),
        claims=claims,
        failed_sources=tuple(failed_sources),
        limitations=tuple(str(item) for item in report.get("limitations", [])),
        trust_level=UNTRUSTED_WEB,
    )


def verify_source_bundle(bundle: ResearchSourceBundle | Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(bundle, ResearchSourceBundle):
        bundle = ResearchSourceBundle.from_dict(bundle)
    errors: list[str] = []
    warnings: list[str] = []
    source_ids = {source.source_id for source in bundle.sources}
    failed_ids = {str(item.get("source_id")) for item in bundle.failed_sources if item.get("source_id")}
    for source in bundle.sources:
        expected = stable_source_id(source.url, source.provider)
        if not source.source_id:
            errors.append(f"source missing source_id for {source.url}")
        elif expected != source.source_id:
            errors.append(f"source_id is not stable for {source.url}")
        if not source.retrieved_at:
            errors.append(f"source {source.source_id} missing retrieved_at")
        if source.trust_level != UNTRUSTED_WEB:
            warnings.append(f"source {source.source_id} trust_level is {source.trust_level}; web content should remain untrusted")
        if not source.url.startswith(("http://", "https://")):
            errors.append(f"source {source.source_id} has invalid URL scheme")
        if source.reliability_signals.get("snippet_only") and source.reliability_signals.get("fetched"):
            errors.append(f"source {source.source_id} cannot be both fetched and snippet-only")
    for citation in bundle.citations:
        if any(source_id not in source_ids for source_id in citation.source_ids):
            errors.append(f"citation {citation.citation_id} references an unknown source")
        if any(source_id in failed_ids for source_id in citation.source_ids):
            errors.append(f"citation {citation.citation_id} cites a failed source")
        if "http://" in citation.text or "https://" in citation.text:
            warnings.append(f"citation {citation.citation_id} includes raw URL text; citations should point to source_ids")
    for claim in bundle.claims:
        if claim.support_level != "inference" and any(source_id not in source_ids for source_id in claim.source_ids):
            errors.append(f"claim {claim.claim_id} references an unknown source")
        if any(source_id in failed_ids for source_id in claim.source_ids):
            errors.append(f"claim {claim.claim_id} uses a failed source as support")
    return {
        "status": "ok" if not errors else "error",
        "errors": errors,
        "warnings": warnings,
        "source_count": len(bundle.sources),
        "citation_count": len(bundle.citations),
        "failed_source_count": len(bundle.failed_sources),
        "trust_level": bundle.trust_level,
    }


def default_source_bundle_path() -> Path:
    configured = os.getenv("RESEARCH_SOURCE_BUNDLE_PATH", "").strip()
    return Path(configured) if configured else DEFAULT_SOURCE_BUNDLE_PATH


def save_last_source_bundle(bundle: ResearchSourceBundle, path: Path | None = None) -> Path:
    target = path or default_source_bundle_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(bundle.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return target


def load_last_source_bundle(path: Path | None = None) -> ResearchSourceBundle:
    target = path or default_source_bundle_path()
    if not target.exists():
        raise FileNotFoundError(f"No last research source bundle found at {target}")
    payload = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Last research source bundle is malformed")
    return ResearchSourceBundle.from_dict(payload)


def _failed_sources(
    failures: Any,
    references: list[SourceReference],
    source_items: list[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    by_url = {reference.url: reference for reference in references}
    failed: list[dict[str, Any]] = []
    redactor = SecretRedactor()
    for item in failures if isinstance(failures, list) else []:
        if not isinstance(item, Mapping):
            continue
        url = str(item.get("url", ""))
        reference = by_url.get(url)
        if reference is None:
            for source in source_items:
                if str(source.get("url", "")) == url:
                    reference = source_reference_from_mapping(source)
                    break
        failed.append(
            redactor.redact(
                {
                    "source_id": reference.source_id if reference else None,
                    "url": url,
                    "error": str(item.get("error") or "fetch failed"),
                }
            )
        )
    return failed


def _claim_attributions(citations: list[CitationSpan], limitations: tuple[str, ...]) -> tuple[ClaimAttribution, ...]:
    claims: list[ClaimAttribution] = []
    for index, citation in enumerate(citations, start=1):
        support = "snippet_only" if citation.snippet_only else "source_backed"
        claims.append(
            ClaimAttribution(
                claim_id=f"claim_{index}",
                claim=citation.text,
                source_ids=citation.source_ids,
                support_level=support,
                limitations=("Snippet-only evidence; source page was not fetched.",) if citation.snippet_only else (),
            )
        )
    if any("conflict" in item.casefold() or "conflicting" in item.casefold() for item in limitations):
        source_ids: list[str] = []
        for citation in citations:
            source_ids.extend(citation.source_ids)
        claims.append(
            ClaimAttribution(
                claim_id="claim_conflict_1",
                claim="Potentially conflicting source evidence is present.",
                source_ids=tuple(dict.fromkeys(source_ids)),
                support_level="conflicting",
                inference=True,
                limitations=limitations,
            )
        )
    return tuple(claims)
