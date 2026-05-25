from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

from agent.config.runtime import env_bool
from agent.safety.redaction import SecretRedactor
from agent.web_acquisition.cache import WebCacheStore, cacheability_decision, utc_now_iso
from agent.web_acquisition.citations import canonical_source_url, source_domain
from agent.web_acquisition.dedupe import content_hash_for_source, source_id_for_source
from agent.web_acquisition.trust import UNTRUSTED_WEB


DEFAULT_INDEX_PATH = Path("data/web_cache/index.json")
TOKEN_RE = re.compile(r"[a-z0-9\u4e00-\u9fff]+", re.IGNORECASE)


@dataclass(frozen=True)
class WebIndexEntry:
    source_id: str
    title: str
    url: str
    snippet: str
    content_hash: str
    retrieved_at: str
    provider: str = "unknown"
    source_type: str = "web"
    trust_level: str = UNTRUSTED_WEB
    source_metadata: dict[str, Any] = field(default_factory=dict)
    domain: str = ""

    def to_dict(self) -> dict[str, Any]:
        return SecretRedactor().redact(asdict(self))

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "WebIndexEntry":
        return cls(
            source_id=str(payload.get("source_id") or ""),
            title=str(payload.get("title") or ""),
            url=str(payload.get("url") or ""),
            snippet=str(payload.get("snippet") or ""),
            content_hash=str(payload.get("content_hash") or ""),
            retrieved_at=str(payload.get("retrieved_at") or utc_now_iso()),
            provider=str(payload.get("provider") or "unknown"),
            source_type=str(payload.get("source_type") or "web"),
            trust_level=str(payload.get("trust_level") or UNTRUSTED_WEB),
            source_metadata=dict(payload.get("source_metadata") or {}),
            domain=str(payload.get("domain") or source_domain(str(payload.get("url") or ""))),
        )


class LocalWebIndex:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path or os.getenv("WEB_INDEX_PATH", str(DEFAULT_INDEX_PATH))).resolve()
        self.enabled = env_bool("WEB_INDEX_ENABLED", default=True)

    def add_public_source(self, source: Mapping[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            return {"status": "disabled", "indexed": False, "reason": "WEB_INDEX_ENABLED=false"}
        decision = cacheability_decision(source)
        if not decision["cacheable"]:
            return {"status": "denied", "indexed": False, "reason": decision["reason"]}
        entry = self._entry_from_source(source)
        if not entry.url or not entry.source_id:
            return {"status": "denied", "indexed": False, "reason": "index source requires a public URL"}
        entries = self._read_entries()
        existing_key = self._find_duplicate_key(entries, entry)
        entries[existing_key or entry.source_id] = entry.to_dict()
        self._write_entries(entries)
        return {
            "status": "indexed",
            "indexed": True,
            "source_id": entry.source_id,
            "content_hash": entry.content_hash,
            "deduped": existing_key is not None,
        }

    def search(self, query: str, *, limit: int = 10) -> dict[str, Any]:
        query_terms = _tokenize(query)
        if not query_terms:
            return {"status": "error", "error": "query must contain searchable terms", "results": []}
        entries = [WebIndexEntry.from_dict(payload) for payload in self._read_entries().values()]
        scored: list[tuple[int, WebIndexEntry]] = []
        for entry in entries:
            score = _score_entry(entry, query_terms)
            if score > 0:
                scored.append((score, entry))
        scored.sort(key=lambda item: (-item[0], item[1].retrieved_at, item[1].source_id))
        results = []
        for rank, (score, entry) in enumerate(scored[: max(1, min(limit, 50))], start=1):
            payload = entry.to_dict()
            payload["rank"] = rank
            payload["score"] = score
            results.append(payload)
        return {
            "status": "ok",
            "query_persisted": False,
            "result_count": len(results),
            "results": results,
            "trust_level": UNTRUSTED_WEB,
        }

    def rebuild_from_cache(self, cache_store: WebCacheStore | None = None) -> dict[str, Any]:
        store = cache_store or WebCacheStore()
        entries: dict[str, dict[str, Any]] = {}
        skipped = 0
        for record in store.records(include_expired=False):
            decision = cacheability_decision(record)
            if not decision["cacheable"]:
                skipped += 1
                continue
            entry = self._entry_from_source(record)
            if entry.source_id:
                entries[entry.source_id] = entry.to_dict()
        self._write_entries(entries)
        return {"status": "rebuilt", "indexed_count": len(entries), "skipped_count": skipped, "path": str(self.path)}

    def status(self) -> dict[str, Any]:
        entries = self._read_entries()
        return {
            "status": "ok",
            "enabled": self.enabled,
            "path": str(self.path),
            "entry_count": len(entries),
            "stores_full_content": False,
            "stores_sensitive_query_history": False,
        }

    def clear(self) -> dict[str, Any]:
        count = len(self._read_entries())
        if self.path.exists():
            self.path.unlink()
        return {"status": "cleared", "entries_deleted": count, "path": str(self.path)}

    def _entry_from_source(self, source: Mapping[str, Any]) -> WebIndexEntry:
        url = canonical_source_url(str(source.get("url") or ""))
        provider = str(source.get("provider") or "unknown")
        metadata = _metadata_only(dict(source.get("source_metadata") or source.get("metadata") or {}))
        return WebIndexEntry(
            source_id=str(source.get("source_id") or source_id_for_source({"url": url, "provider": provider})),
            title=SecretRedactor().redact_text(str(source.get("title") or url)),
            url=url,
            snippet=SecretRedactor().redact_text(str(source.get("snippet") or source.get("summary") or "")),
            content_hash=str(source.get("content_hash") or content_hash_for_source(source)),
            retrieved_at=str(source.get("retrieved_at") or utc_now_iso()),
            provider=provider,
            source_type=str(source.get("source_type") or "web"),
            trust_level=str(source.get("trust_level") or UNTRUSTED_WEB),
            source_metadata=metadata,
            domain=source_domain(url),
        )

    def _read_entries(self) -> dict[str, dict[str, Any]]:
        if not self.path.exists():
            return {}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        records = payload.get("entries") if isinstance(payload, dict) else None
        return records if isinstance(records, dict) else {}

    def _write_entries(self, entries: dict[str, dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"schema_version": 1, "updated_at": datetime.now(UTC).isoformat(), "entries": SecretRedactor().redact(entries)}
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def _find_duplicate_key(self, entries: Mapping[str, Mapping[str, Any]], entry: WebIndexEntry) -> str | None:
        for key, payload in entries.items():
            existing = WebIndexEntry.from_dict(payload)
            if existing.content_hash and existing.content_hash == entry.content_hash:
                return str(key)
            if existing.url and existing.url == entry.url:
                return str(key)
        return None


def _tokenize(value: str) -> set[str]:
    return {match.group(0).casefold() for match in TOKEN_RE.finditer(value or "") if match.group(0).strip()}


def _score_entry(entry: WebIndexEntry, terms: set[str]) -> int:
    title = _tokenize(entry.title)
    snippet = _tokenize(entry.snippet)
    domain = _tokenize(entry.domain)
    score = 0
    for term in terms:
        if term in title:
            score += 5
        if term in snippet:
            score += 2
        if term in domain:
            score += 1
    return score


def _metadata_only(metadata: dict[str, Any]) -> dict[str, Any]:
    for key in list(metadata):
        if key in {"query", "raw_query", "search_query", "text", "html_sanitized", "content", "body_text", "full_content"}:
            metadata.pop(key, None)
    return SecretRedactor().redact(metadata)
