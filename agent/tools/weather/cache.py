from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class WeatherCacheEntry:
    cached_at: str
    expires_at: str
    payload: dict[str, Any]

    @property
    def expired(self) -> bool:
        try:
            expires_at = datetime.fromisoformat(self.expires_at)
        except ValueError:
            return True
        return datetime.now(UTC) >= expires_at


class WeatherCache:
    def __init__(self, path: str | Path = "data/weather_cache.json") -> None:
        self.path = Path(path)

    def get(self, key: str) -> WeatherCacheEntry | None:
        records = self._read()
        record = records.get(key)
        if not isinstance(record, dict):
            return None
        payload = record.get("payload")
        if not isinstance(payload, dict):
            return None
        return WeatherCacheEntry(
            cached_at=str(record.get("cached_at", "")),
            expires_at=str(record.get("expires_at", "")),
            payload=payload,
        )

    def set(self, key: str, payload: dict[str, Any], ttl_seconds: int) -> WeatherCacheEntry:
        now = datetime.now(UTC)
        entry = WeatherCacheEntry(
            cached_at=now.isoformat(),
            expires_at=(now + timedelta(seconds=max(0, ttl_seconds))).isoformat(),
            payload=payload,
        )
        records = self._read()
        records[key] = {
            "cached_at": entry.cached_at,
            "expires_at": entry.expires_at,
            "payload": payload,
        }
        self._write(records)
        return entry

    def clear(self) -> int:
        records = self._read()
        count = len(records)
        self._write({})
        return count

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return payload if isinstance(payload, dict) else {}

    def _write(self, records: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(json.dumps(records, sort_keys=True), encoding="utf-8")
        temporary.replace(self.path)


def weather_cache_key(
    *,
    provider: str,
    location: str,
    request_type: str,
    units: str,
    days: int | None = None,
    include_hourly: bool = False,
) -> str:
    material = json.dumps(
        {
            "provider": provider,
            "location": location.strip().casefold(),
            "request_type": request_type,
            "units": units,
            "days": days,
            "include_hourly": include_hourly,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def weather_cache_allowed(location: str) -> bool:
    """Avoid caching precise-looking user locations in the operational weather cache."""
    text = location.strip()
    if not text:
        return False
    if _DIRECT_COORDINATES_RE.fullmatch(text):
        return False
    if _STREET_ADDRESS_RE.search(text):
        return False
    return True


_DIRECT_COORDINATES_RE = re.compile(
    r"(?:lat(?:itude)?\s*=\s*)?[+-]?\d+(?:\.\d+)?\s*[, ]\s*(?:lon(?:gitude)?\s*=\s*)?[+-]?\d+(?:\.\d+)?",
    re.IGNORECASE,
)
_STREET_ADDRESS_RE = re.compile(
    r"\b\d{1,6}\s+[a-z0-9 .'-]+?\b(?:street|st|avenue|ave|road|rd|boulevard|blvd|lane|ln|drive|dr|court|ct|way|circle|cir|place|pl|terrace|trail|pkwy|parkway)\b",
    re.IGNORECASE,
)
