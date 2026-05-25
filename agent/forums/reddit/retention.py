from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Mapping

from .models import utc_now_iso
from .policy import RedditPolicyConfig, load_reddit_policy_config


DEFAULT_REDDIT_CACHE_PATH = Path("data/reddit/cache.json")


class RedditCache:
    def __init__(
        self,
        path: str | Path | None = None,
        *,
        config: RedditPolicyConfig | None = None,
    ) -> None:
        self.path = Path(path or DEFAULT_REDDIT_CACHE_PATH)
        self.config = config or load_reddit_policy_config()

    def get(self, key: str) -> dict[str, Any] | None:
        if not self.config.cache_enabled:
            return None
        records = self._read_records()
        payload = records.get(key)
        if not isinstance(payload, dict):
            return None
        if _is_expired(payload.get("expires_at")):
            return None
        return dict(payload.get("value") or {})

    def set(self, key: str, value: Mapping[str, Any], *, content_kind: str = "reddit") -> dict[str, Any]:
        if not self.config.cache_enabled:
            return {"status": "disabled", "stored": False}
        if self.config.cache_ttl_seconds <= 0:
            return {"status": "disabled", "stored": False, "reason": "retention_ttl_not_positive"}
        if _contains_removed(value):
            return {"status": "skipped", "stored": False, "reason": "removed_or_deleted_content"}
        sanitized = _minimize_for_cache(value, store_author_metadata=self.config.store_author_metadata)
        records = self._read_records()
        now = datetime.now(UTC)
        expires_at = now + timedelta(seconds=max(0, self.config.cache_ttl_seconds))
        records[key] = {
            "key": key,
            "content_kind": content_kind,
            "retrieved_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "value": sanitized,
            "content_hash": content_hash(sanitized),
            "source": "reddit_api",
        }
        self._write_records(records)
        return {
            "status": "stored",
            "stored": True,
            "key": key,
            "source": "reddit_api",
            "expires_at": expires_at.isoformat(),
            "content_hash": records[key]["content_hash"],
            "_audit": {
                "files_written": [str(self.path)],
                "result_summary": "Reddit cache entry stored with TTL-bounded metadata.",
            },
        }

    def clear(self) -> dict[str, Any]:
        count = len(self._read_records())
        if self.path.exists():
            self.path.unlink()
        return {
            "status": "cleared",
            "entries_deleted": count,
            "path": str(self.path),
            "retention_action": "clear",
            "_audit": {
                "files_written": [str(self.path)],
                "result_summary": f"Reddit cache cleared; entries_deleted={count}.",
            },
        }

    def sweep(self, *, now: datetime | None = None) -> dict[str, Any]:
        records = self._read_records()
        cutoff = now or datetime.now(UTC)
        kept: dict[str, Any] = {}
        deleted = 0
        for key, payload in records.items():
            if _is_expired(payload.get("expires_at"), now=cutoff):
                deleted += 1
            else:
                kept[key] = payload
        self._write_records(kept)
        return {
            "status": "swept",
            "entries_deleted": deleted,
            "entries_remaining": len(kept),
            "path": str(self.path),
            "retention_action": "sweep",
            "query_history_stored": False,
            "author_metadata_stored_by_default": self.config.store_author_metadata,
            "_audit": {
                "files_written": [str(self.path)],
                "result_summary": f"Reddit retention sweep completed; entries_deleted={deleted}.",
            },
        }

    def status(self) -> dict[str, Any]:
        records = self._read_records()
        active = [payload for payload in records.values() if not _is_expired(payload.get("expires_at"))]
        return {
            "status": "ok",
            "enabled": self.config.cache_enabled,
            "retention_policy_guaranteed": self.config.cache_enabled and self.config.cache_ttl_seconds > 0,
            "path": str(self.path),
            "entry_count": len(records),
            "active_count": len(active),
            "expired_count": len(records) - len(active),
            "cache_ttl_seconds": self.config.cache_ttl_seconds,
            "delete_user_content_after_seconds": self.config.delete_user_content_after_seconds,
            "store_author_metadata": self.config.store_author_metadata,
            "query_history_stored": False,
            "permanent_user_content_storage_default": False,
            "content_hashes_tracked": sum(1 for payload in records.values() if payload.get("content_hash")),
            "entries_with_author_metadata": _count_records_matching(records, _has_author_metadata),
            "entries_with_removed_content": _count_records_matching(records, _contains_removed),
            "entries_with_raw_query": _count_records_matching(records, _has_raw_query),
        }

    def retention_status(self) -> dict[str, Any]:
        status = self.status()
        status.update(
            {
                "retention_action": "status",
                "cache_disabled_if_policy_not_guaranteed": self.config.cache_ttl_seconds <= 0,
                "removed_deleted_content_retained": status["entries_with_removed_content"] > 0,
                "author_metadata_stored_by_default": self.config.store_author_metadata,
                "use_for_training": self.config.use_for_training,
                "trust_level": "UNTRUSTED_WEB",
            }
        )
        return status

    def privacy_report(self) -> dict[str, Any]:
        status = self.status()
        return {
            "status": "ok",
            "report_type": "counts_only",
            "cache_enabled": status["enabled"],
            "retention_policy_guaranteed": status["retention_policy_guaranteed"],
            "entry_count": status["entry_count"],
            "active_count": status["active_count"],
            "expired_count": status["expired_count"],
            "content_hashes_tracked": status["content_hashes_tracked"],
            "entries_with_author_metadata": status["entries_with_author_metadata"],
            "entries_with_removed_content": status["entries_with_removed_content"],
            "query_history_entries": status["entries_with_raw_query"],
            "query_history_stored": False,
            "raw_content_included": False,
            "author_metadata_stored_by_default": self.config.store_author_metadata,
            "model_training_allowed": self.config.use_for_training,
            "trust_level": "UNTRUSTED_WEB",
            "notes": [
                "This report intentionally returns counts and policy flags only.",
                "Cached Reddit payloads remain untrusted web content and are TTL-bounded.",
            ],
        }

    def find_source(self, source_id: str) -> dict[str, Any] | None:
        source_id = str(source_id or "").strip()
        if not source_id:
            return None
        for payload in self._read_records().values():
            if not isinstance(payload, Mapping) or _is_expired(payload.get("expires_at")):
                continue
            value = payload.get("value")
            found = _find_source_in_value(value, source_id)
            if found:
                return {
                    "cache_key": payload.get("key"),
                    "content_kind": payload.get("content_kind"),
                    "retrieved_at": payload.get("retrieved_at"),
                    "expires_at": payload.get("expires_at"),
                    "content_hash": payload.get("content_hash"),
                    "source": found,
                }
        return None

    def _read_records(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return dict(payload) if isinstance(payload, dict) else {}

    def _write_records(self, records: Mapping[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(records, indent=2, sort_keys=True), encoding="utf-8")


def reddit_cache_key(operation: str, *, query: str = "", subreddit: str = "", post_id: str = "") -> str:
    query_digest = hashlib.sha256(query.strip().encode("utf-8")).hexdigest() if query.strip() else ""
    material = "|".join(["reddit_api", operation, query_digest, subreddit.strip().casefold(), post_id.strip()])
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def content_hash(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _is_expired(value: Any, *, now: datetime | None = None) -> bool:
    if not value:
        return True
    try:
        expires = datetime.fromisoformat(str(value))
    except ValueError:
        return True
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=UTC)
    return expires <= (now or datetime.now(UTC))


def _contains_removed(value: Any) -> bool:
    if isinstance(value, Mapping):
        if value.get("removed") is True:
            return True
        return any(_contains_removed(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_removed(item) for item in value)
    return False


def _minimize_for_cache(value: Any, *, store_author_metadata: bool) -> Any:
    if isinstance(value, Mapping):
        minimized = {}
        for key, item in value.items():
            if not store_author_metadata and key == "author_display":
                continue
            if key in {"query", "raw_query", "search_query"}:
                minimized[f"{key}_redacted"] = "[REDDIT_QUERY_REDACTED]"
                continue
            minimized[key] = _minimize_for_cache(item, store_author_metadata=store_author_metadata)
        minimized.setdefault("cache_retrieved_at", utc_now_iso())
        return minimized
    if isinstance(value, list):
        return [_minimize_for_cache(item, store_author_metadata=store_author_metadata) for item in value]
    return value


def _find_source_in_value(value: Any, source_id: str) -> dict[str, Any] | None:
    if isinstance(value, Mapping):
        if value.get("source_id") == source_id:
            return dict(value)
        for key in ("results", "source_references", "comments"):
            found = _find_source_in_value(value.get(key), source_id)
            if found:
                return found
        for key in ("post", "subreddit"):
            item = value.get(key)
            if isinstance(item, Mapping) and item.get("source_id") == source_id:
                return dict(item)
    if isinstance(value, list):
        for item in value:
            found = _find_source_in_value(item, source_id)
            if found:
                return found
    return None


def _count_records_matching(records: Mapping[str, Any], predicate: Any) -> int:
    return sum(1 for payload in records.values() if predicate(payload))


def _has_author_metadata(value: Any) -> bool:
    if isinstance(value, Mapping):
        if "author_display" in value:
            return True
        return any(_has_author_metadata(item) for item in value.values())
    if isinstance(value, list):
        return any(_has_author_metadata(item) for item in value)
    return False


def _has_raw_query(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key in {"query", "raw_query", "search_query"} and isinstance(item, str) and item:
                return True
            if _has_raw_query(item):
                return True
    if isinstance(value, list):
        return any(_has_raw_query(item) for item in value)
    return False
