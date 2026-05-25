from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_V2EX_CACHE_PATH = Path("data/v2ex/cache.json")


def v2ex_cache_key(operation: str, *parts: object) -> str:
    material = "|".join([operation, *(str(part) for part in parts)])
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


@dataclass
class V2EXCache:
    path: Path = DEFAULT_V2EX_CACHE_PATH
    ttl_seconds: int = 86400
    enabled: bool = True

    def get(self, key: str) -> Any | None:
        if not self.enabled:
            return None
        entry = self._read().get(key)
        if not isinstance(entry, dict):
            return None
        if float(entry.get("expires_at", 0)) <= time.time():
            return None
        return entry.get("payload")

    def set(self, key: str, payload: Any, *, source: str) -> None:
        if not self.enabled or self.ttl_seconds <= 0:
            return
        entries = self._read()
        encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        entries[key] = {
            "source": source,
            "retrieved_at": time.time(),
            "expires_at": time.time() + self.ttl_seconds,
            "content_hash": hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
            "payload": payload,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(entries, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")

    def clear(self) -> dict[str, Any]:
        before = len(self._read())
        if self.path.exists():
            self.path.unlink()
        return {"entries_deleted": before, "path": str(self.path)}

    def status(self) -> dict[str, Any]:
        entries = self._read()
        now = time.time()
        return {
            "enabled": self.enabled,
            "path": str(self.path),
            "entry_count": len(entries),
            "expired_count": sum(1 for entry in entries.values() if isinstance(entry, dict) and float(entry.get("expires_at", 0)) <= now),
            "ttl_seconds": self.ttl_seconds,
            "raw_content_returned": False,
        }

    def sweep(self) -> dict[str, Any]:
        entries = self._read()
        now = time.time()
        kept = {key: entry for key, entry in entries.items() if isinstance(entry, dict) and float(entry.get("expires_at", 0)) > now}
        deleted = len(entries) - len(kept)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(kept, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        return {"entries_deleted": deleted, "entries_remaining": len(kept), "path": str(self.path)}

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return loaded if isinstance(loaded, dict) else {}
