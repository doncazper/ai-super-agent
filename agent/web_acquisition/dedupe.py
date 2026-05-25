from __future__ import annotations

import hashlib
from typing import Any, Mapping

from agent.safety.redaction import SecretRedactor
from agent.web_acquisition.citations import canonical_source_url, source_domain, stable_source_id


HASH_FIELDS = ("title", "snippet", "text", "content", "summary", "excerpt")


def content_hash_for_source(source: Mapping[str, Any]) -> str:
    parts: list[str] = []
    for field in HASH_FIELDS:
        value = str(source.get(field) or "").strip()
        if value:
            parts.append(value)
    if not parts:
        parts.append(canonical_source_url(str(source.get("url") or "")))
    text = "\n".join(parts).strip()
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def source_id_for_source(source: Mapping[str, Any], *, provider: str | None = None) -> str:
    url = canonical_source_url(str(source.get("url") or ""))
    provider_name = str(source.get("provider") or provider or "unknown")
    return stable_source_id(url, provider_name)


def dedupe_sources(sources: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[str, dict[str, Any]] = {}
    for source in sources:
        normalized = normalize_dedupe_source(source)
        key = normalized.get("content_hash") or normalized.get("source_id") or normalized.get("url")
        if not key:
            continue
        if key not in by_key:
            by_key[key] = normalized
            continue
        by_key[key] = _prefer_richer_source(by_key[key], normalized)
    return list(by_key.values())


def normalize_dedupe_source(source: Mapping[str, Any]) -> dict[str, Any]:
    redactor = SecretRedactor()
    payload = redactor.redact(dict(source))
    url = canonical_source_url(str(payload.get("url") or ""))
    provider = str(payload.get("provider") or "unknown")
    payload["url"] = url
    payload["domain"] = str(payload.get("domain") or source_domain(url))
    payload["source_id"] = str(payload.get("source_id") or stable_source_id(url, provider))
    payload["content_hash"] = str(payload.get("content_hash") or content_hash_for_source(payload))
    return payload


def _prefer_richer_source(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    left_score = _richness_score(left)
    right_score = _richness_score(right)
    if right_score > left_score:
        merged = dict(left)
        merged.update(right)
        return merged
    merged = dict(right)
    merged.update(left)
    return merged


def _richness_score(source: Mapping[str, Any]) -> int:
    score = 0
    for field in ("title", "snippet", "text", "published_at", "author"):
        if str(source.get(field) or "").strip():
            score += 1
    if source.get("fetched"):
        score += 2
    return score
