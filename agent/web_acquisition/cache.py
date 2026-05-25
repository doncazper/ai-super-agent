from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Mapping

from agent.config.runtime import env_bool, parse_int
from agent.safety.redaction import SecretRedactor
from agent.tools.errors import ToolError
from agent.web_acquisition.citations import canonical_source_url, source_domain
from agent.web_acquisition.dedupe import content_hash_for_source, source_id_for_source
from agent.web_acquisition.trust import UNTRUSTED_DOCUMENT, UNTRUSTED_WEB
from agent.web_acquisition.url_normalization import DomainRules


DEFAULT_CACHE_PATH = Path("data/web_cache/cache.json")
DEFAULT_CACHE_TTL_SECONDS = 3600
SOURCE_TYPE_TTLS = {
    "search": 3600,
    "feed": 900,
    "sitemap": 86400,
    "fetch": 86400,
    "article": 86400,
    "web": 3600,
}
PERSONAL_OR_AUTH_KEYS = {
    "authenticated",
    "auth_required",
    "personal_data",
    "private_data",
    "contains_personal_data",
    "requires_login",
    "cookie_used",
    "session_used",
}
RAW_QUERY_KEYS = {"query", "raw_query", "search_query", "user_query"}
CONTENT_FIELDS = {"text", "html_sanitized", "content", "body_text", "full_content", "raw", "article_body"}


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def query_hash(query: str | None) -> str:
    import hashlib

    value = (query or "").strip()
    if not value:
        return ""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def cache_key_for(url: str, *, provider: str = "unknown", query_hash_value: str = "") -> str:
    import hashlib

    canonical = canonical_source_url(url)
    provider_label = str(provider or "unknown").strip().casefold()
    material = f"{provider_label}|{canonical}|{query_hash_value}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class WebCacheEntry:
    cache_key: str
    source_id: str
    url: str
    provider: str
    query_hash: str = ""
    title: str = ""
    snippet: str = ""
    content_hash: str = ""
    retrieved_at: str = field(default_factory=utc_now_iso)
    expires_at: str = ""
    source_type: str = "web"
    trust_level: str = UNTRUSTED_WEB
    status: str = "ok"
    source_metadata: dict[str, Any] = field(default_factory=dict)
    full_content: str | None = None
    blocked_reason: str = ""

    def is_expired(self, *, now: datetime | None = None) -> bool:
        expires = _parse_timestamp(self.expires_at)
        if expires is None:
            return True
        return expires <= (now or datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return SecretRedactor().redact(asdict(self))

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "WebCacheEntry":
        return cls(
            cache_key=str(payload.get("cache_key") or ""),
            source_id=str(payload.get("source_id") or ""),
            url=str(payload.get("url") or ""),
            provider=str(payload.get("provider") or "unknown"),
            query_hash=str(payload.get("query_hash") or ""),
            title=str(payload.get("title") or ""),
            snippet=str(payload.get("snippet") or ""),
            content_hash=str(payload.get("content_hash") or ""),
            retrieved_at=str(payload.get("retrieved_at") or utc_now_iso()),
            expires_at=str(payload.get("expires_at") or ""),
            source_type=str(payload.get("source_type") or "web"),
            trust_level=str(payload.get("trust_level") or UNTRUSTED_WEB),
            status=str(payload.get("status") or "ok"),
            source_metadata=dict(payload.get("source_metadata") or {}),
            full_content=str(payload.get("full_content")) if payload.get("full_content") is not None else None,
            blocked_reason=str(payload.get("blocked_reason") or ""),
        )


class WebCacheStore:
    def __init__(self, path: str | Path | None = None, *, store_full_content: bool | None = None) -> None:
        self.path = Path(path or os.getenv("WEB_CACHE_PATH", str(DEFAULT_CACHE_PATH))).resolve()
        self.enabled = env_bool("WEB_CACHE_ENABLED", default=True)
        self.store_full_content = (
            env_bool("WEB_CACHE_STORE_FULL_CONTENT", default=False)
            if store_full_content is None
            else store_full_content
        )

    def put_public_source(
        self,
        source: Mapping[str, Any],
        *,
        provider: str | None = None,
        source_type: str = "web",
        raw_query: str | None = None,
        query_hash_value: str | None = None,
        ttl_seconds: int | None = None,
    ) -> dict[str, Any]:
        if not self.enabled:
            return {"status": "disabled", "stored": False, "reason": "WEB_CACHE_ENABLED=false"}
        decision = cacheability_decision(source)
        if not decision["cacheable"]:
            return {"status": "denied", "stored": False, "reason": decision["reason"]}
        entry = self._entry_from_source(
            source,
            provider=provider,
            source_type=source_type,
            raw_query=raw_query,
            query_hash_value=query_hash_value,
            ttl_seconds=ttl_seconds,
        )
        records = self._read_records()
        records[entry.cache_key] = entry.to_dict()
        self._write_records(records)
        return {"status": "stored", "stored": True, "cache_key": entry.cache_key, "source_id": entry.source_id}

    def lookup(
        self,
        *,
        url: str | None = None,
        provider: str | None = None,
        raw_query: str | None = None,
        query_hash_value: str | None = None,
        source_id: str | None = None,
        include_expired: bool = False,
    ) -> dict[str, Any] | None:
        records = self._read_records()
        if source_id:
            for payload in records.values():
                entry = WebCacheEntry.from_dict(payload)
                if entry.source_id == source_id:
                    if include_expired or not entry.is_expired():
                        return entry.to_dict()
                    return None
            return None
        if not url:
            return None
        canonical = canonical_source_url(url)
        q_hash = query_hash_value if query_hash_value is not None else query_hash(raw_query)
        key = cache_key_for(canonical, provider=provider or "unknown", query_hash_value=q_hash or "")
        payload = records.get(key)
        if not payload:
            return None
        entry = WebCacheEntry.from_dict(payload)
        if not include_expired and entry.is_expired():
            return None
        return entry.to_dict()

    def records(self, *, include_expired: bool = True) -> list[dict[str, Any]]:
        entries = [WebCacheEntry.from_dict(payload) for payload in self._read_records().values()]
        if not include_expired:
            entries = [entry for entry in entries if not entry.is_expired()]
        return [entry.to_dict() for entry in entries]

    def status(self) -> dict[str, Any]:
        entries = [WebCacheEntry.from_dict(payload) for payload in self._read_records().values()]
        active = [entry for entry in entries if not entry.is_expired()]
        expired = [entry for entry in entries if entry.is_expired()]
        return {
            "status": "ok",
            "enabled": self.enabled,
            "path": str(self.path),
            "entry_count": len(entries),
            "active_count": len(active),
            "expired_count": len(expired),
            "store_full_content": self.store_full_content,
            "default_ttl_seconds": _ttl_for_source_type("web"),
            "source_type_ttls": dict(SOURCE_TYPE_TTLS),
            "stores_personal_or_authenticated_content": False,
            "stores_sensitive_query_history": False,
        }

    def clear(self) -> dict[str, Any]:
        count = len(self._read_records())
        if self.path.exists():
            self.path.unlink()
        return {"status": "cleared", "entries_deleted": count, "path": str(self.path)}

    def delete(self, source_id: str) -> dict[str, Any]:
        records = self._read_records()
        for key, payload in list(records.items()):
            if str(payload.get("source_id") or "") == source_id:
                records.pop(key)
                self._write_records(records)
                return {"status": "deleted", "source_id": source_id}
        return {"status": "not_found", "source_id": source_id}

    def export_metadata(self) -> dict[str, Any]:
        return {"status": "ok", "records": self.records(include_expired=True)}

    def get_or_refresh(
        self,
        *,
        url: str,
        provider: str,
        loader: Callable[[], Mapping[str, Any]],
        source_type: str = "web",
        raw_query: str | None = None,
        ttl_seconds: int | None = None,
    ) -> dict[str, Any]:
        cached = self.lookup(url=url, provider=provider, raw_query=raw_query)
        if cached is not None:
            return {"status": "hit", "cache_used": True, "loaded": False, "entry": cached}
        loaded = dict(loader())
        store_result = self.put_public_source(
            loaded,
            provider=provider,
            source_type=source_type,
            raw_query=raw_query,
            ttl_seconds=ttl_seconds,
        )
        entry = self.lookup(url=str(loaded.get("url") or url), provider=provider, raw_query=raw_query)
        return {
            "status": "refreshed",
            "cache_used": False,
            "loaded": True,
            "store_result": store_result,
            "entry": entry,
        }

    def _entry_from_source(
        self,
        source: Mapping[str, Any],
        *,
        provider: str | None,
        source_type: str,
        raw_query: str | None,
        query_hash_value: str | None,
        ttl_seconds: int | None,
    ) -> WebCacheEntry:
        redactor = SecretRedactor()
        canonical = canonical_source_url(str(source.get("url") or ""))
        if not canonical:
            raise ToolError("cache source requires a public http/https URL")
        DomainRules.from_env().validate_url(canonical)
        provider_name = str(source.get("provider") or provider or "unknown")
        q_hash = query_hash_value if query_hash_value is not None else query_hash(raw_query)
        status = str(source.get("status") or "ok")
        blocked_reason = str(source.get("blocked_reason") or source.get("error") or "")
        metadata = _sanitize_source_metadata(dict(source.get("source_metadata") or source.get("metadata") or {}))
        if _is_blocked_status(status, blocked_reason):
            title = ""
            snippet = ""
            full_content = None
            metadata = {"status": status, "blocked_reason": blocked_reason, **metadata}
        else:
            title = redactor.redact_text(str(source.get("title") or canonical))
            snippet = redactor.redact_text(str(source.get("snippet") or source.get("summary") or ""))
            full_content = _optional_full_content(source, self.store_full_content)
        retrieved_at = str(source.get("retrieved_at") or utc_now_iso())
        expires_at = (datetime.now(UTC) + timedelta(seconds=ttl_seconds or _ttl_for_source_type(source_type))).isoformat()
        cache_key = cache_key_for(canonical, provider=provider_name, query_hash_value=q_hash or "")
        return WebCacheEntry(
            cache_key=cache_key,
            source_id=str(source.get("source_id") or source_id_for_source({"url": canonical, "provider": provider_name})),
            url=canonical,
            provider=provider_name,
            query_hash=q_hash or "",
            title=title,
            snippet=snippet,
            content_hash=str(source.get("content_hash") or content_hash_for_source(source)),
            retrieved_at=retrieved_at,
            expires_at=expires_at,
            source_type=source_type,
            trust_level=str(source.get("trust_level") or UNTRUSTED_WEB),
            status=status,
            source_metadata=metadata,
            full_content=full_content,
            blocked_reason=blocked_reason if _is_blocked_status(status, blocked_reason) else "",
        )

    def _read_records(self) -> dict[str, dict[str, Any]]:
        if not self.path.exists():
            return {}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        records = payload.get("records") if isinstance(payload, dict) else None
        return records if isinstance(records, dict) else {}

    def _write_records(self, records: dict[str, dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 1,
            "updated_at": utc_now_iso(),
            "records": SecretRedactor().redact(records),
        }
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def cacheability_decision(source: Mapping[str, Any]) -> dict[str, Any]:
    trust = str(source.get("trust_level") or UNTRUSTED_WEB)
    if trust not in {UNTRUSTED_WEB, UNTRUSTED_DOCUMENT}:
        return {"cacheable": False, "reason": "only public untrusted web/document sources are cached by default"}
    if not canonical_source_url(str(source.get("url") or "")):
        return {"cacheable": False, "reason": "source URL must be public http/https"}
    metadata = dict(source.get("source_metadata") or source.get("metadata") or {})
    for key in PERSONAL_OR_AUTH_KEYS:
        if bool(metadata.get(key)) or bool(source.get(key)):
            return {"cacheable": False, "reason": "personal or authenticated content is not cached"}
    return {"cacheable": True, "reason": "public web source"}


def _sanitize_source_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    for key in list(metadata):
        if key in RAW_QUERY_KEYS or key in CONTENT_FIELDS:
            metadata.pop(key, None)
    return SecretRedactor().redact(metadata)


def _optional_full_content(source: Mapping[str, Any], enabled: bool) -> str | None:
    if not enabled:
        return None
    for field in CONTENT_FIELDS:
        value = str(source.get(field) or "").strip()
        if value:
            return SecretRedactor().redact_text(value)
    return None


def _is_blocked_status(status: str, reason: str) -> bool:
    value = f"{status} {reason}".casefold()
    return any(marker in value for marker in ("blocked", "captcha", "login", "unavailable", "forbidden"))


def _ttl_for_source_type(source_type: str) -> int:
    key = source_type.upper().replace("-", "_")
    env_name = f"WEB_CACHE_TTL_{key}_SECONDS"
    default = SOURCE_TYPE_TTLS.get(source_type, DEFAULT_CACHE_TTL_SECONDS)
    return parse_int(env_name, os.getenv(env_name, os.getenv("WEB_CACHE_TTL_SECONDS", str(default))), minimum=1, maximum=604800)


def _parse_timestamp(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
