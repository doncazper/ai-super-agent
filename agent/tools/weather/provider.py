from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Callable, Protocol

import httpx

from agent.config.runtime import env_bool, parse_float, parse_int
from agent.tools.weather.cache import WeatherCache, weather_cache_allowed, weather_cache_key
from agent.tools.weather.models import (
    UnitSystem,
    WeatherCurrent,
    WeatherDaily,
    WeatherHourly,
    WeatherLocation,
    WeatherProviderError,
    WeatherResult,
    condition_from_weather_code,
    normalize_unit_system,
)


class WeatherProvider(Protocol):
    name: str

    def is_configured(self) -> bool:
        ...

    def current_weather(self, location: str, units: str, locale: str | None = None) -> dict[str, Any]:
        ...

    def forecast(
        self,
        location: str,
        days: int,
        units: str,
        locale: str | None = None,
        include_hourly: bool = False,
    ) -> dict[str, Any]:
        ...


@dataclass(frozen=True)
class DisabledWeatherProvider:
    name: str = "disabled"

    def is_configured(self) -> bool:
        return False

    def current_weather(self, location: str, units: str, locale: str | None = None) -> dict[str, Any]:
        return {}

    def forecast(
        self,
        location: str,
        days: int,
        units: str,
        locale: str | None = None,
        include_hourly: bool = False,
    ) -> dict[str, Any]:
        return {}


@dataclass(frozen=True)
class UnsupportedWeatherProvider:
    provider_name: str

    @property
    def name(self) -> str:
        return f"unsupported:{self.provider_name}"

    def is_configured(self) -> bool:
        return False

    def current_weather(self, location: str, units: str, locale: str | None = None) -> dict[str, Any]:
        return {}

    def forecast(
        self,
        location: str,
        days: int,
        units: str,
        locale: str | None = None,
        include_hourly: bool = False,
    ) -> dict[str, Any]:
        return {}


@dataclass(frozen=True)
class OpenMeteoProvider:
    timeout_seconds: float = 10
    geocoding_endpoint: str = "https://geocoding-api.open-meteo.com/v1/search"
    forecast_endpoint: str = "https://api.open-meteo.com/v1/forecast"
    client_factory: Callable[[float], httpx.Client] | None = None
    name: str = "open_meteo"

    def is_configured(self) -> bool:
        return True

    def current_weather(self, location: str, units: str, locale: str | None = None) -> dict[str, Any]:
        selected = self._resolve_location(location, locale)
        forecast = self._forecast(
            selected,
            {
                "current": ",".join(
                    [
                        "temperature_2m",
                        "relative_humidity_2m",
                        "apparent_temperature",
                        "precipitation",
                        "rain",
                        "snowfall",
                        "weather_code",
                        "pressure_msl",
                        "wind_speed_10m",
                        "wind_direction_10m",
                        "is_day",
                    ]
                ),
                "timezone": "auto",
                **_unit_params(units),
            },
        )
        current = forecast.get("current")
        if not isinstance(current, dict):
            raise WeatherProviderError("weather provider returned malformed current weather")
        current_units = forecast.get("current_units") if isinstance(forecast.get("current_units"), dict) else {}
        normalized = _normalize_open_meteo_current(current, current_units)
        result = WeatherResult(
            status="ok",
            provider=self.name,
            units=normalize_unit_system(units),
            retrieved_at=datetime.now(UTC).isoformat(),
            location=_weather_location(selected, fallback_timezone=forecast.get("timezone")),
            current=normalized,
            timezone=_string_or_none(forecast.get("timezone")),
            provider_timestamp=normalized.time,
            metadata=_provider_metadata(self.name),
            raw_provider_payload={"forecast": forecast},
        )
        return result.to_dict(include_raw=_debug_raw_enabled())

    def forecast(
        self,
        location: str,
        days: int,
        units: str,
        locale: str | None = None,
        include_hourly: bool = False,
    ) -> dict[str, Any]:
        selected = self._resolve_location(location, locale)
        params: dict[str, Any] = {
            "daily": ",".join(
                [
                    "weather_code",
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "precipitation_probability_max",
                    "rain_sum",
                    "snowfall_sum",
                    "wind_speed_10m_max",
                    "wind_gusts_10m_max",
                    "wind_direction_10m_dominant",
                    "uv_index_max",
                ]
            ),
            "forecast_days": days,
            "timezone": "auto",
            **_unit_params(units),
        }
        if include_hourly:
            params["hourly"] = ",".join(
                [
                    "temperature_2m",
                    "precipitation_probability",
                    "precipitation",
                    "rain",
                    "snowfall",
                    "weather_code",
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "relative_humidity_2m",
                    "pressure_msl",
                    "uv_index",
                ]
            )
        forecast = self._forecast(
            selected,
            params,
        )
        daily = forecast.get("daily")
        if not isinstance(daily, dict):
            raise WeatherProviderError("weather provider returned malformed forecast")
        daily_units = forecast.get("daily_units") if isinstance(forecast.get("daily_units"), dict) else {}
        hourly = forecast.get("hourly") if include_hourly else None
        hourly_units = forecast.get("hourly_units") if isinstance(forecast.get("hourly_units"), dict) else {}
        result = WeatherResult(
            status="ok",
            provider=self.name,
            units=normalize_unit_system(units),
            retrieved_at=datetime.now(UTC).isoformat(),
            location=_weather_location(selected, fallback_timezone=forecast.get("timezone")),
            daily=_normalize_open_meteo_daily(daily, daily_units, days),
            hourly=_normalize_open_meteo_hourly(hourly, hourly_units) if isinstance(hourly, dict) else [],
            timezone=_string_or_none(forecast.get("timezone")),
            metadata=_provider_metadata(self.name),
            raw_provider_payload={"forecast": forecast},
        )
        return result.to_dict(include_raw=_debug_raw_enabled())

    def _resolve_location(self, location: str, locale: str | None) -> dict[str, Any]:
        direct = _parse_direct_coordinates(location)
        if direct is not None:
            return direct
        return self._geocode(location, locale)

    def _geocode(self, location: str, locale: str | None) -> dict[str, Any]:
        params: dict[str, Any] = {"name": location, "count": 5, "format": "json"}
        language = _language_from_locale(locale)
        if language:
            params["language"] = language
        payload = self._get_json(self.geocoding_endpoint, params=params)
        results = payload.get("results") if isinstance(payload, dict) else None
        if not isinstance(results, list) or not results:
            raise WeatherProviderError("location not found")
        selected = results[0]
        if not isinstance(selected, dict):
            raise WeatherProviderError("weather geocoding provider returned malformed result")
        if not isinstance(selected.get("latitude"), (int, float)) or not isinstance(
            selected.get("longitude"),
            (int, float),
        ):
            raise WeatherProviderError("weather geocoding provider returned malformed coordinates")
        alternatives = [_location_match(result) for result in results if isinstance(result, dict)]
        if len(alternatives) > 1:
            selected = dict(selected)
            selected["disambiguation"] = {
                "selected": alternatives[0],
                "alternatives": alternatives,
            }
        return selected

    def _forecast(self, selected_location: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        forecast_params = {
            "latitude": selected_location["latitude"],
            "longitude": selected_location["longitude"],
            **params,
        }
        return self._get_json(self.forecast_endpoint, params=forecast_params)

    def _get_json(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        try:
            with self._client() as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                payload = response.json()
        except httpx.TimeoutException as exc:
            raise WeatherProviderError("weather provider timed out") from exc
        except httpx.HTTPStatusError as exc:
            raise WeatherProviderError(f"weather provider returned HTTP {exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise WeatherProviderError(f"weather provider failed: {type(exc).__name__}") from exc
        except ValueError as exc:
            raise WeatherProviderError("weather provider returned malformed JSON") from exc
        if not isinstance(payload, dict):
            raise WeatherProviderError("weather provider returned malformed JSON")
        if payload.get("error"):
            reason = str(payload.get("reason") or "weather provider returned an error")
            raise WeatherProviderError(reason)
        return payload

    def _client(self) -> httpx.Client:
        if self.client_factory is not None:
            return self.client_factory(self.timeout_seconds)
        return httpx.Client(timeout=self.timeout_seconds)


def provider_from_env() -> WeatherProvider:
    provider_name = os.getenv("WEATHER_PROVIDER", "").strip().lower()
    timeout = parse_float(
        "WEATHER_TIMEOUT_SECONDS",
        os.getenv("WEATHER_TIMEOUT_SECONDS", "10"),
        minimum=1,
        maximum=60,
    )
    if provider_name in {"disabled", "none"}:
        return DisabledWeatherProvider()
    if provider_name in {"", "open_meteo", "open-meteo", "openmeteo"}:
        return OpenMeteoProvider(timeout_seconds=timeout)
    return UnsupportedWeatherProvider(provider_name)


def make_weather_tools(provider: WeatherProvider | None = None) -> dict[str, Any]:
    active_provider = provider or provider_from_env()

    def status() -> dict[str, Any]:
        return weather_provider_status(active_provider)

    def current(
        location: str,
        units: str | None = None,
        locale: str | None = None,
        no_cache: bool = False,
    ) -> dict[str, Any]:
        location_error = _validate_location(location)
        if location_error:
            return _error_payload(active_provider, location_error, configured=_provider_configured(active_provider))
        configured_error = _configuration_error(active_provider)
        if configured_error:
            return configured_error
        resolved_units = _resolve_units(units)
        cache_allowed = weather_cache_allowed(location)
        cache = WeatherCache(_weather_cache_path())
        cache_key = weather_cache_key(
            provider=active_provider.name,
            location=location,
            request_type="current",
            units=resolved_units,
        )
        cache_summary = "weather cache miss"
        if not no_cache and cache_allowed:
            cached_entry = cache.get(cache_key)
            if cached_entry is not None and not cached_entry.expired:
                return _with_weather_audit(
                    _apply_cache_metadata(cached_entry.payload, cached=True, cached_at=cached_entry.cached_at, expires_at=cached_entry.expires_at),
                    active_provider,
                    "weather cache hit",
                )
            if cached_entry is not None and cached_entry.expired:
                cache_summary = "weather cache expired refresh"
        try:
            raw = active_provider.current_weather(location.strip(), resolved_units, locale)
        except Exception as exc:
            return _provider_error(active_provider, exc)
        if isinstance(raw, dict) and raw.get("status") == "ok":
            if no_cache or not cache_allowed:
                return _with_weather_audit(
                    _apply_cache_metadata(raw, cached=False, cached_at=None, expires_at=None),
                    active_provider,
                    _weather_cache_skip_summary(no_cache, cache_allowed),
                )
            cache_entry = cache.set(cache_key, raw, _weather_cache_ttl("current"))
            return _with_weather_audit(
                _apply_cache_metadata(raw, cached=False, cached_at=cache_entry.cached_at, expires_at=cache_entry.expires_at),
                active_provider,
                cache_summary,
            )
        retrieved_at = datetime.now(UTC).isoformat()
        fallback = {
            "status": "ok",
            "provider": active_provider.name,
            "location": _display_location(raw, location),
            "units": resolved_units,
            "trust_level": "UNTRUSTED_WEB",
            "retrieved_at": retrieved_at,
            "timezone": raw.get("timezone") if isinstance(raw, dict) else None,
            "provider_timestamp": raw.get("provider_timestamp") if isinstance(raw, dict) else None,
            "coordinates": raw.get("coordinates") if isinstance(raw, dict) else None,
            "disambiguation": raw.get("disambiguation") if isinstance(raw, dict) else None,
            "current": _normalize_mapping(raw.get("current", raw)),
        }
        if no_cache or not cache_allowed:
            return _with_weather_audit(
                _apply_cache_metadata(fallback, cached=False, cached_at=None, expires_at=None),
                active_provider,
                _weather_cache_skip_summary(no_cache, cache_allowed),
            )
        cache_entry = cache.set(cache_key, fallback, _weather_cache_ttl("current"))
        return _with_weather_audit(
            _apply_cache_metadata(fallback, cached=False, cached_at=cache_entry.cached_at, expires_at=cache_entry.expires_at),
            active_provider,
            cache_summary,
        )

    def forecast(
        location: str,
        days: int | None = None,
        units: str | None = None,
        locale: str | None = None,
        include_hourly: bool = False,
        no_cache: bool = False,
    ) -> dict[str, Any]:
        location_error = _validate_location(location)
        if location_error:
            return _error_payload(active_provider, location_error, configured=_provider_configured(active_provider))
        configured_error = _configuration_error(active_provider)
        if configured_error:
            return configured_error
        resolved_units = _resolve_units(units)
        max_days = parse_int(
            "WEATHER_MAX_FORECAST_DAYS",
            os.getenv("WEATHER_MAX_FORECAST_DAYS", "7"),
            minimum=1,
            maximum=16,
        )
        requested_days = days if days is not None else min(max_days, 3)
        clamped_days = max(1, min(int(requested_days), max_days, 16))
        cache_allowed = weather_cache_allowed(location)
        cache = WeatherCache(_weather_cache_path())
        cache_key = weather_cache_key(
            provider=active_provider.name,
            location=location,
            request_type="forecast",
            units=resolved_units,
            days=clamped_days,
            include_hourly=bool(include_hourly),
        )
        cache_summary = "weather cache miss"
        if not no_cache and cache_allowed:
            cached_entry = cache.get(cache_key)
            if cached_entry is not None and not cached_entry.expired:
                payload = dict(cached_entry.payload)
                payload["days"] = clamped_days
                return _with_weather_audit(
                    _apply_cache_metadata(payload, cached=True, cached_at=cached_entry.cached_at, expires_at=cached_entry.expires_at),
                    active_provider,
                    "weather cache hit",
                )
            if cached_entry is not None and cached_entry.expired:
                cache_summary = "weather cache expired refresh"
        try:
            raw = active_provider.forecast(
                location.strip(),
                clamped_days,
                resolved_units,
                locale,
                bool(include_hourly),
            )
        except Exception as exc:
            return _provider_error(active_provider, exc)
        if isinstance(raw, dict) and raw.get("status") == "ok":
            payload = dict(raw)
            payload["days"] = clamped_days
            if no_cache or not cache_allowed:
                return _with_weather_audit(
                    _apply_cache_metadata(payload, cached=False, cached_at=None, expires_at=None),
                    active_provider,
                    _weather_cache_skip_summary(no_cache, cache_allowed),
                )
            cache_entry = cache.set(cache_key, payload, _weather_cache_ttl("forecast"))
            return _with_weather_audit(
                _apply_cache_metadata(payload, cached=False, cached_at=cache_entry.cached_at, expires_at=cache_entry.expires_at),
                active_provider,
                cache_summary,
            )
        periods = raw.get("forecast", raw.get("periods", [])) if isinstance(raw, dict) else []
        if not isinstance(periods, list):
            periods = []
        retrieved_at = datetime.now(UTC).isoformat()
        fallback = {
            "status": "ok",
            "provider": active_provider.name,
            "location": _display_location(raw, location),
            "units": resolved_units,
            "days": clamped_days,
            "trust_level": "UNTRUSTED_WEB",
            "retrieved_at": retrieved_at,
            "timezone": raw.get("timezone") if isinstance(raw, dict) else None,
            "coordinates": raw.get("coordinates") if isinstance(raw, dict) else None,
            "disambiguation": raw.get("disambiguation") if isinstance(raw, dict) else None,
            "forecast": [_normalize_mapping(item) for item in periods[:clamped_days] if isinstance(item, dict)],
            "hourly": raw.get("hourly") if isinstance(raw, dict) else None,
        }
        if no_cache or not cache_allowed:
            return _with_weather_audit(
                _apply_cache_metadata(fallback, cached=False, cached_at=None, expires_at=None),
                active_provider,
                _weather_cache_skip_summary(no_cache, cache_allowed),
            )
        cache_entry = cache.set(cache_key, fallback, _weather_cache_ttl("forecast"))
        return _with_weather_audit(
            _apply_cache_metadata(fallback, cached=False, cached_at=cache_entry.cached_at, expires_at=cache_entry.expires_at),
            active_provider,
            cache_summary,
        )

    def cache_clear() -> dict[str, Any]:
        cleared = WeatherCache(_weather_cache_path()).clear()
        return {
            "status": "ok",
            "provider": active_provider.name,
            "cleared_entries": cleared,
            "_audit": {"result_summary": "weather cache cleared"},
        }

    return {
        "weather.status": status,
        "weather.current": current,
        "weather.forecast": forecast,
        "weather.cache_clear": cache_clear,
    }


def weather_provider_status(provider: WeatherProvider | None = None) -> dict[str, Any]:
    active_provider = provider or provider_from_env()
    configured = _provider_configured(active_provider)
    supported = active_provider.name not in {"disabled"} and not active_provider.name.startswith("unsupported:")
    error = None
    if active_provider.name == "disabled":
        error = "weather provider is not configured"
    elif active_provider.name.startswith("unsupported:"):
        error = "configured weather provider is not supported by this build"
        if not os.getenv("WEATHER_API_KEY", "").strip():
            error += "; WEATHER_API_KEY is not set if this provider requires one"
    return {
        "status": "ok" if configured and supported else "error",
        "provider": active_provider.name,
        "configured": configured,
        "supported": supported,
        "requires_api_key": False if active_provider.name == "open_meteo" else active_provider.name.startswith("unsupported:"),
        "api_key_configured": bool(os.getenv("WEATHER_API_KEY", "").strip()),
        "web_access_enabled": os.getenv("WEB_ACCESS_ENABLED", "true").strip().casefold() not in {"0", "false", "no", "off"},
        "trust_level": "UNTRUSTED_WEB",
        "error": error,
    }


def _validate_location(location: str) -> str | None:
    if not isinstance(location, str) or not location.strip():
        return "location is required"
    if len(location.strip()) > 200:
        return "location is too long"
    return None


def _resolve_units(units: str | None) -> str:
    requested = (units or os.getenv("WEATHER_DEFAULT_UNITS", "metric")).strip().lower()
    if requested in {"metric", "imperial"}:
        return requested
    return "metric"


def _configuration_error(provider: WeatherProvider) -> dict[str, Any] | None:
    if provider.name == "disabled":
        return _error_payload(provider, "weather provider is not configured", configured=False)
    if provider.name.startswith("unsupported:"):
        return _error_payload(provider, "configured weather provider is not supported by this build", configured=False)
    if not _provider_configured(provider):
        return _error_payload(provider, f"{provider.name} weather provider is not configured", configured=False)
    return None


def _provider_error(provider: WeatherProvider, exc: Exception) -> dict[str, Any]:
    if isinstance(exc, WeatherProviderError):
        error = str(exc)
    else:
        error = f"weather provider failed: {type(exc).__name__}"
    return {
        "status": "error",
        "provider": provider.name,
        "error": error,
        "configured": _provider_configured(provider),
        "trust_level": "UNTRUSTED_WEB",
        "_audit": {"network_domains": _provider_domains(provider.name)},
    }


def _with_weather_audit(payload: dict[str, Any], provider: WeatherProvider, summary: str = "weather provider call") -> dict[str, Any]:
    result = dict(payload)
    result["_audit"] = {"network_domains": _provider_domains(provider.name), "result_summary": summary}
    return result


def _apply_cache_metadata(
    payload: dict[str, Any],
    *,
    cached: bool,
    cached_at: str | None,
    expires_at: str | None,
) -> dict[str, Any]:
    result = dict(payload)
    result["cached"] = cached
    result["cached_at"] = cached_at
    result["expires_at"] = expires_at
    return result


def _weather_cache_path() -> str:
    return os.getenv("WEATHER_CACHE_PATH", "data/weather_cache.json")


def _weather_cache_ttl(request_type: str) -> int:
    if request_type == "current":
        return parse_int(
            "WEATHER_CURRENT_CACHE_TTL_SECONDS",
            os.getenv("WEATHER_CURRENT_CACHE_TTL_SECONDS", "900"),
            minimum=0,
            maximum=86400,
        )
    return parse_int(
        "WEATHER_FORECAST_CACHE_TTL_SECONDS",
        os.getenv("WEATHER_FORECAST_CACHE_TTL_SECONDS", "3600"),
        minimum=0,
        maximum=604800,
    )


def _weather_cache_skip_summary(no_cache: bool, cache_allowed: bool) -> str:
    if no_cache:
        return "weather cache bypass"
    if not cache_allowed:
        return "weather cache skipped precise location"
    return "weather cache miss"


def _error_payload(provider: WeatherProvider, error: str, *, configured: bool) -> dict[str, Any]:
    return {
        "status": "error",
        "provider": provider.name,
        "error": error,
        "configured": configured,
        "trust_level": "UNTRUSTED_WEB",
    }


def _provider_configured(provider: WeatherProvider) -> bool:
    checker = getattr(provider, "is_configured", None)
    if callable(checker):
        return bool(checker())
    return provider.name != "disabled" and not provider.name.startswith("unsupported:")


def _display_location(raw: dict[str, Any], fallback: str) -> str:
    if isinstance(raw, dict):
        location = raw.get("location")
        if isinstance(location, str) and location.strip():
            return location.strip()
    return fallback.strip()


def _normalize_mapping(value: dict[str, Any]) -> dict[str, Any]:
    return {str(key): item for key, item in value.items() if key != "location"}


def _provider_domains(provider_name: str) -> list[str]:
    if provider_name == "open_meteo":
        return ["geocoding-api.open-meteo.com", "api.open-meteo.com"]
    if provider_name in {"disabled", ""}:
        return []
    if provider_name.startswith("unsupported:"):
        return [provider_name]
    return [provider_name]


def _provider_metadata(provider_name: str) -> dict[str, Any]:
    return {"name": provider_name, "domains": _provider_domains(provider_name)}


def _debug_raw_enabled() -> bool:
    return env_bool("DEBUG", default=False)


def _language_from_locale(locale: str | None) -> str | None:
    if not locale:
        return None
    language = locale.replace("_", "-").split("-", 1)[0].strip().lower()
    return language or None


def _unit_params(units: str) -> dict[str, str]:
    if units == "imperial":
        return {
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
        }
    return {
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
    }


def _location_label(location: dict[str, Any]) -> str:
    if location.get("direct_coordinates"):
        return str(location.get("name") or "direct coordinates")
    pieces = [
        str(location.get("name") or "").strip(),
        str(location.get("admin1") or "").strip(),
        str(location.get("country") or "").strip(),
    ]
    return ", ".join(piece for piece in pieces if piece)


def _weather_location(location: dict[str, Any], *, fallback_timezone: Any = None) -> WeatherLocation:
    return WeatherLocation(
        name=_location_label(location),
        latitude=float(location["latitude"]) if isinstance(location.get("latitude"), (int, float)) else None,
        longitude=float(location["longitude"]) if isinstance(location.get("longitude"), (int, float)) else None,
        timezone=_string_or_none(location.get("timezone") or fallback_timezone),
        admin1=_string_or_none(location.get("admin1")),
        country=_string_or_none(location.get("country")),
        disambiguation=location.get("disambiguation") if isinstance(location.get("disambiguation"), dict) else None,
    )


def _string_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _coordinates(location: dict[str, Any]) -> dict[str, float] | None:
    latitude = location.get("latitude")
    longitude = location.get("longitude")
    if isinstance(latitude, (int, float)) and isinstance(longitude, (int, float)):
        return {"latitude": float(latitude), "longitude": float(longitude)}
    return None


def _parse_direct_coordinates(location: str) -> dict[str, Any] | None:
    text = location.strip()
    match = re.fullmatch(
        r"(?:lat(?:itude)?\s*=\s*)?([+-]?\d+(?:\.\d+)?)\s*[, ]\s*(?:lon(?:gitude)?\s*=\s*)?([+-]?\d+(?:\.\d+)?)",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    latitude = float(match.group(1))
    longitude = float(match.group(2))
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise WeatherProviderError("direct coordinates are outside valid latitude/longitude ranges")
    return {
        "name": f"{latitude:.6f},{longitude:.6f}",
        "latitude": latitude,
        "longitude": longitude,
        "direct_coordinates": True,
    }


def _location_match(location: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": location.get("name"),
        "admin1": location.get("admin1"),
        "country": location.get("country"),
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),
        "timezone": location.get("timezone"),
    }


def _normalize_open_meteo_current(current: dict[str, Any], units: dict[str, Any]) -> WeatherCurrent:
    return WeatherCurrent(
        time=_string_or_none(current.get("time")),
        temperature=current.get("temperature_2m"),
        temperature_unit=_string_or_none(units.get("temperature_2m")),
        apparent_temperature=current.get("apparent_temperature"),
        apparent_temperature_unit=_string_or_none(units.get("apparent_temperature")),
        humidity=current.get("relative_humidity_2m"),
        humidity_unit=_string_or_none(units.get("relative_humidity_2m")),
        precipitation=current.get("precipitation"),
        precipitation_unit=_string_or_none(units.get("precipitation")),
        rain=current.get("rain"),
        rain_unit=_string_or_none(units.get("rain")),
        snow=current.get("snowfall"),
        snow_unit=_string_or_none(units.get("snowfall")),
        weather_code=_int_or_none(current.get("weather_code")),
        condition=condition_from_weather_code(current.get("weather_code")),
        pressure=current.get("pressure_msl"),
        pressure_unit=_string_or_none(units.get("pressure_msl")),
        wind_speed=current.get("wind_speed_10m"),
        wind_speed_unit=_string_or_none(units.get("wind_speed_10m")),
        wind_direction=current.get("wind_direction_10m"),
        wind_direction_unit=_string_or_none(units.get("wind_direction_10m")),
    )


def _normalize_open_meteo_daily(daily: dict[str, Any], units: dict[str, Any], days: int) -> list[WeatherDaily]:
    dates = daily.get("time")
    if not isinstance(dates, list):
        raise WeatherProviderError("weather provider returned malformed forecast dates")
    normalized: list[WeatherDaily] = []
    for index, date_value in enumerate(dates[:days]):
        weather_code = _int_or_none(_daily_value(daily, "weather_code", index))
        normalized.append(
            WeatherDaily(
                date=str(date_value),
                weather_code=weather_code,
                condition=condition_from_weather_code(weather_code),
                temperature_max=_daily_value(daily, "temperature_2m_max", index),
                temperature_max_unit=_string_or_none(units.get("temperature_2m_max")),
                temperature_min=_daily_value(daily, "temperature_2m_min", index),
                temperature_min_unit=_string_or_none(units.get("temperature_2m_min")),
                precipitation_sum=_daily_value(daily, "precipitation_sum", index),
                precipitation_sum_unit=_string_or_none(units.get("precipitation_sum")),
                precipitation_probability_max=_daily_value(daily, "precipitation_probability_max", index),
                precipitation_probability_max_unit=_string_or_none(units.get("precipitation_probability_max")),
                rain_sum=_daily_value(daily, "rain_sum", index),
                rain_sum_unit=_string_or_none(units.get("rain_sum")),
                snow_sum=_daily_value(daily, "snowfall_sum", index),
                snow_sum_unit=_string_or_none(units.get("snowfall_sum")),
                wind_speed_max=_daily_value(daily, "wind_speed_10m_max", index),
                wind_speed_max_unit=_string_or_none(units.get("wind_speed_10m_max")),
                wind_gusts_max=_daily_value(daily, "wind_gusts_10m_max", index),
                wind_gusts_max_unit=_string_or_none(units.get("wind_gusts_10m_max")),
                wind_direction_dominant=_daily_value(daily, "wind_direction_10m_dominant", index),
                wind_direction_dominant_unit=_string_or_none(units.get("wind_direction_10m_dominant")),
                uv_index_max=_daily_value(daily, "uv_index_max", index),
            )
        )
    return normalized


def _normalize_open_meteo_hourly(hourly: dict[str, Any], units: dict[str, Any]) -> list[WeatherHourly]:
    times = hourly.get("time")
    if not isinstance(times, list):
        raise WeatherProviderError("weather provider returned malformed hourly forecast")
    normalized: list[WeatherHourly] = []
    for index, time_value in enumerate(times):
        weather_code = _int_or_none(_daily_value(hourly, "weather_code", index))
        normalized.append(
            WeatherHourly(
                time=str(time_value),
                temperature=_daily_value(hourly, "temperature_2m", index),
                temperature_unit=_string_or_none(units.get("temperature_2m")),
                precipitation_probability=_daily_value(hourly, "precipitation_probability", index),
                precipitation_probability_unit=_string_or_none(units.get("precipitation_probability")),
                precipitation=_daily_value(hourly, "precipitation", index),
                precipitation_unit=_string_or_none(units.get("precipitation")),
                rain=_daily_value(hourly, "rain", index),
                rain_unit=_string_or_none(units.get("rain")),
                snow=_daily_value(hourly, "snowfall", index),
                snow_unit=_string_or_none(units.get("snowfall")),
                weather_code=weather_code,
                condition=condition_from_weather_code(weather_code),
                wind_speed=_daily_value(hourly, "wind_speed_10m", index),
                wind_speed_unit=_string_or_none(units.get("wind_speed_10m")),
                wind_direction=_daily_value(hourly, "wind_direction_10m", index),
                wind_direction_unit=_string_or_none(units.get("wind_direction_10m")),
                humidity=_daily_value(hourly, "relative_humidity_2m", index),
                humidity_unit=_string_or_none(units.get("relative_humidity_2m")),
                pressure=_daily_value(hourly, "pressure_msl", index),
                pressure_unit=_string_or_none(units.get("pressure_msl")),
                uv_index=_daily_value(hourly, "uv_index", index),
            )
        )
    return normalized


def _daily_value(daily: dict[str, Any], key: str, index: int) -> Any:
    values = daily.get(key)
    if not isinstance(values, list) or index >= len(values):
        return None
    return values[index]


def _int_or_none(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


WEATHER_SCHEMAS = {
    "weather.status": {
        "type": "function",
        "function": {
            "name": "weather.status",
            "description": "Report configured weather provider status without making network calls.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
    "weather.current": {
        "type": "function",
        "function": {
            "name": "weather.current",
            "description": "Fetch current weather for a user-provided location through a configured weather provider.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "units": {"type": "string", "enum": ["metric", "imperial"]},
                    "locale": {"type": "string"},
                    "no_cache": {"type": "boolean"},
                },
                "required": ["location"],
                "additionalProperties": False,
            },
        },
    },
    "weather.forecast": {
        "type": "function",
        "function": {
            "name": "weather.forecast",
            "description": "Fetch a weather forecast for a user-provided location through a configured weather provider.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "days": {"type": "integer", "minimum": 1, "maximum": 16},
                    "units": {"type": "string", "enum": ["metric", "imperial"]},
                    "locale": {"type": "string"},
                    "include_hourly": {"type": "boolean"},
                    "no_cache": {"type": "boolean"},
                },
                "required": ["location"],
                "additionalProperties": False,
            },
        },
    },
    "weather.cache_clear": {
        "type": "function",
        "function": {
            "name": "weather.cache_clear",
            "description": "Clear the local TTL weather cache without reading personal data.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
}
