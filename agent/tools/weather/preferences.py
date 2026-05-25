from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from agent.config.runtime import parse_int


DEFAULT_PREFERENCES_PATH = "config/weather_preferences.json"
PROVIDER_VALUES = {
    "auto",
    "open_meteo",
    "open-meteo",
    "openmeteo",
    "nws",
    "weatherapi",
    "weatherkit",
    "disabled",
    "none",
}
UNIT_VALUES = {"metric", "imperial"}


@dataclass(frozen=True)
class WeatherDefaultLocation:
    location: str
    source: str


@dataclass(frozen=True)
class WeatherPreferences:
    default_location: str | None
    default_location_source: str | None
    units: str
    provider: str
    cache_enabled: bool
    cache_ttl_seconds: int | None
    path: str

    @property
    def default_configured(self) -> bool:
        return bool(self.default_location)

    def to_dict(self) -> dict[str, Any]:
        return {
            "default_location_configured": self.default_configured,
            "default_location": self.default_location,
            "default_location_source": self.default_location_source,
            "units": self.units,
            "provider": self.provider,
            "cache_enabled": self.cache_enabled,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "config_path": self.path,
            "uses_device_location": False,
            "uses_ip_geolocation": False,
            "stored_in_memory": False,
        }


def weather_preferences(env: Mapping[str, str] | None = None) -> WeatherPreferences:
    env = env or os.environ
    path = _preferences_path(env)
    file_payload = _read_preferences(path)
    default = _default_location(env, file_payload)
    units = _units(env, file_payload)
    provider = _provider(env, file_payload)
    cache_enabled = _cache_enabled(env, file_payload)
    cache_ttl = _cache_ttl(env, file_payload)
    return WeatherPreferences(
        default_location=default.location if default else None,
        default_location_source=default.source if default else None,
        units=units,
        provider=provider,
        cache_enabled=cache_enabled,
        cache_ttl_seconds=cache_ttl,
        path=str(path),
    )


def configured_default_location(env: Mapping[str, str] | None = None) -> WeatherDefaultLocation | None:
    prefs = weather_preferences(env)
    if not prefs.default_location or not prefs.default_location_source:
        return None
    return WeatherDefaultLocation(prefs.default_location, prefs.default_location_source)


def set_default_location(location: str, env: Mapping[str, str] | None = None) -> dict[str, Any]:
    text = location.strip()
    if not text:
        return {"status": "error", "error": "default weather location is required"}
    if len(text) > 200:
        return {"status": "error", "error": "default weather location is too long"}
    path = _preferences_path(env or os.environ)
    payload = _read_preferences(path)
    payload["WEATHER_DEFAULT_LOCATION"] = text
    payload.pop("WEATHER_DEFAULT_LATITUDE", None)
    payload.pop("WEATHER_DEFAULT_LONGITUDE", None)
    _write_preferences(path, payload)
    return {
        "status": "ok",
        "default_location_configured": True,
        "default_location": text,
        "config_path": str(path),
        "stored_in_memory": False,
    }


def clear_default_location(env: Mapping[str, str] | None = None) -> dict[str, Any]:
    path = _preferences_path(env or os.environ)
    payload = _read_preferences(path)
    removed = any(key in payload for key in ("WEATHER_DEFAULT_LOCATION", "WEATHER_DEFAULT_LATITUDE", "WEATHER_DEFAULT_LONGITUDE"))
    payload.pop("WEATHER_DEFAULT_LOCATION", None)
    payload.pop("WEATHER_DEFAULT_LATITUDE", None)
    payload.pop("WEATHER_DEFAULT_LONGITUDE", None)
    _write_preferences(path, payload)
    active = configured_default_location(env)
    return {
        "status": "ok",
        "removed_file_default": removed,
        "default_location_configured": active is not None,
        "default_location_source": active.source if active else None,
        "config_path": str(path),
        "stored_in_memory": False,
    }


def _preferences_path(env: Mapping[str, str]) -> Path:
    return Path(env.get("WEATHER_PREFERENCES_PATH") or DEFAULT_PREFERENCES_PATH)


def _read_preferences(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_preferences(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def _default_location(env: Mapping[str, str], file_payload: dict[str, Any]) -> WeatherDefaultLocation | None:
    env_location = (env.get("WEATHER_DEFAULT_LOCATION") or "").strip()
    if env_location:
        return WeatherDefaultLocation(env_location, "env:WEATHER_DEFAULT_LOCATION")
    env_coordinates = _coordinate_location(env.get("WEATHER_DEFAULT_LATITUDE"), env.get("WEATHER_DEFAULT_LONGITUDE"))
    if env_coordinates:
        return WeatherDefaultLocation(env_coordinates, "env:WEATHER_DEFAULT_LATITUDE/WEATHER_DEFAULT_LONGITUDE")
    file_location = _string(file_payload.get("WEATHER_DEFAULT_LOCATION"))
    if file_location:
        return WeatherDefaultLocation(file_location, "config_file:WEATHER_DEFAULT_LOCATION")
    file_coordinates = _coordinate_location(
        file_payload.get("WEATHER_DEFAULT_LATITUDE"),
        file_payload.get("WEATHER_DEFAULT_LONGITUDE"),
    )
    if file_coordinates:
        return WeatherDefaultLocation(file_coordinates, "config_file:WEATHER_DEFAULT_LATITUDE/WEATHER_DEFAULT_LONGITUDE")
    return None


def _coordinate_location(latitude: Any, longitude: Any) -> str | None:
    if latitude in (None, "") or longitude in (None, ""):
        return None
    try:
        lat = float(latitude)
        lon = float(longitude)
    except (TypeError, ValueError):
        return None
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None
    return f"{lat:.6f},{lon:.6f}"


def _units(env: Mapping[str, str], file_payload: dict[str, Any]) -> str:
    value = (
        env.get("WEATHER_UNITS")
        or env.get("WEATHER_DEFAULT_UNITS")
        or _string(file_payload.get("WEATHER_UNITS"))
        or _string(file_payload.get("WEATHER_DEFAULT_UNITS"))
        or "metric"
    )
    normalized = value.strip().lower()
    return normalized if normalized in UNIT_VALUES else "metric"


def _provider(env: Mapping[str, str], file_payload: dict[str, Any]) -> str:
    value = env.get("WEATHER_PROVIDER") or _string(file_payload.get("WEATHER_PROVIDER")) or "auto"
    normalized = value.strip().lower()
    return normalized if normalized in PROVIDER_VALUES else normalized


def _cache_enabled(env: Mapping[str, str], file_payload: dict[str, Any]) -> bool:
    if "WEATHER_CACHE_ENABLED" in env:
        return str(env.get("WEATHER_CACHE_ENABLED", "")).strip().casefold() not in {"0", "false", "no", "off"}
    raw = file_payload.get("WEATHER_CACHE_ENABLED")
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, str):
        return raw.strip().casefold() not in {"0", "false", "no", "off"}
    return True


def _cache_ttl(env: Mapping[str, str], file_payload: dict[str, Any]) -> int | None:
    raw = env.get("WEATHER_CACHE_TTL_SECONDS")
    if raw is not None:
        return parse_int("WEATHER_CACHE_TTL_SECONDS", raw, minimum=0, maximum=604800)
    raw = file_payload.get("WEATHER_CACHE_TTL_SECONDS")
    if raw is not None:
        return parse_int("WEATHER_CACHE_TTL_SECONDS", str(raw), minimum=0, maximum=604800)
    return None


def _string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
