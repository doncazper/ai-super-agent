from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Callable, Protocol

import httpx

from agent.config.runtime import parse_float, parse_int


class WeatherProvider(Protocol):
    name: str

    def is_configured(self) -> bool:
        ...

    def current_weather(self, location: str, units: str, locale: str | None = None) -> dict[str, Any]:
        ...

    def forecast(self, location: str, days: int, units: str, locale: str | None = None) -> dict[str, Any]:
        ...


class WeatherProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class DisabledWeatherProvider:
    name: str = "disabled"

    def is_configured(self) -> bool:
        return False

    def current_weather(self, location: str, units: str, locale: str | None = None) -> dict[str, Any]:
        return {}

    def forecast(self, location: str, days: int, units: str, locale: str | None = None) -> dict[str, Any]:
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

    def forecast(self, location: str, days: int, units: str, locale: str | None = None) -> dict[str, Any]:
        return {}


@dataclass(frozen=True)
class OpenMeteoProvider:
    timeout_seconds: float = 10
    geocoding_endpoint: str = "https://geocoding-api.open-meteo.com/v1/search"
    forecast_endpoint: str = "https://api.open-meteo.com/v1/forecast"
    client_factory: Callable[[float], httpx.Client] | None = None
    name: str = "open-meteo"

    def is_configured(self) -> bool:
        return True

    def current_weather(self, location: str, units: str, locale: str | None = None) -> dict[str, Any]:
        selected = self._geocode(location, locale)
        forecast = self._forecast(
            selected,
            {
                "current": ",".join(
                    [
                        "temperature_2m",
                        "relative_humidity_2m",
                        "apparent_temperature",
                        "precipitation",
                        "weather_code",
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
        return {
            "location": _location_label(selected),
            "current": normalized,
            "timezone": forecast.get("timezone"),
            "provider_timestamp": normalized.get("time"),
        }

    def forecast(self, location: str, days: int, units: str, locale: str | None = None) -> dict[str, Any]:
        selected = self._geocode(location, locale)
        forecast = self._forecast(
            selected,
            {
                "daily": ",".join(
                    [
                        "weather_code",
                        "temperature_2m_max",
                        "temperature_2m_min",
                        "precipitation_sum",
                        "wind_speed_10m_max",
                    ]
                ),
                "forecast_days": days,
                "timezone": "auto",
                **_unit_params(units),
            },
        )
        daily = forecast.get("daily")
        if not isinstance(daily, dict):
            raise WeatherProviderError("weather provider returned malformed forecast")
        daily_units = forecast.get("daily_units") if isinstance(forecast.get("daily_units"), dict) else {}
        return {
            "location": _location_label(selected),
            "forecast": _normalize_open_meteo_daily(daily, daily_units, days),
            "timezone": forecast.get("timezone"),
        }

    def _geocode(self, location: str, locale: str | None) -> dict[str, Any]:
        params: dict[str, Any] = {"name": location, "count": 1, "format": "json"}
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
    if provider_name in {"", "disabled", "none"}:
        return DisabledWeatherProvider()
    if provider_name in {"open-meteo", "openmeteo"}:
        return OpenMeteoProvider(timeout_seconds=timeout)
    return UnsupportedWeatherProvider(provider_name)


def make_weather_tools(provider: WeatherProvider | None = None) -> dict[str, Any]:
    active_provider = provider or provider_from_env()

    def current(location: str, units: str | None = None, locale: str | None = None) -> dict[str, Any]:
        location_error = _validate_location(location)
        if location_error:
            return _error_payload(active_provider, location_error, configured=_provider_configured(active_provider))
        configured_error = _configuration_error(active_provider)
        if configured_error:
            return configured_error
        resolved_units = _resolve_units(units)
        retrieved_at = datetime.now(UTC).isoformat()
        try:
            raw = active_provider.current_weather(location.strip(), resolved_units, locale)
        except Exception as exc:
            return _provider_error(active_provider, exc)
        return {
            "status": "ok",
            "provider": active_provider.name,
            "location": _display_location(raw, location),
            "units": resolved_units,
            "trust_level": "UNTRUSTED_WEB",
            "retrieved_at": retrieved_at,
            "current": _normalize_mapping(raw.get("current", raw)),
            "_audit": {"network_domains": _provider_domains(active_provider.name)},
        }

    def forecast(
        location: str,
        days: int | None = None,
        units: str | None = None,
        locale: str | None = None,
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
        retrieved_at = datetime.now(UTC).isoformat()
        try:
            raw = active_provider.forecast(location.strip(), clamped_days, resolved_units, locale)
        except Exception as exc:
            return _provider_error(active_provider, exc)
        periods = raw.get("forecast", raw.get("periods", [])) if isinstance(raw, dict) else []
        if not isinstance(periods, list):
            periods = []
        return {
            "status": "ok",
            "provider": active_provider.name,
            "location": _display_location(raw, location),
            "units": resolved_units,
            "days": clamped_days,
            "trust_level": "UNTRUSTED_WEB",
            "retrieved_at": retrieved_at,
            "forecast": [_normalize_mapping(item) for item in periods[:clamped_days] if isinstance(item, dict)],
            "_audit": {"network_domains": _provider_domains(active_provider.name)},
        }

    return {
        "weather.current": current,
        "weather.forecast": forecast,
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
    if provider_name == "open-meteo":
        return ["geocoding-api.open-meteo.com", "api.open-meteo.com"]
    if provider_name in {"disabled", ""}:
        return []
    if provider_name.startswith("unsupported:"):
        return [provider_name]
    return [provider_name]


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
    pieces = [
        str(location.get("name") or "").strip(),
        str(location.get("admin1") or "").strip(),
        str(location.get("country") or "").strip(),
    ]
    return ", ".join(piece for piece in pieces if piece)


def _normalize_open_meteo_current(current: dict[str, Any], units: dict[str, Any]) -> dict[str, Any]:
    return {
        "time": current.get("time"),
        "temperature": current.get("temperature_2m"),
        "temperature_unit": units.get("temperature_2m"),
        "apparent_temperature": current.get("apparent_temperature"),
        "apparent_temperature_unit": units.get("apparent_temperature"),
        "relative_humidity": current.get("relative_humidity_2m"),
        "relative_humidity_unit": units.get("relative_humidity_2m"),
        "precipitation": current.get("precipitation"),
        "precipitation_unit": units.get("precipitation"),
        "weather_code": current.get("weather_code"),
        "wind_speed": current.get("wind_speed_10m"),
        "wind_speed_unit": units.get("wind_speed_10m"),
        "wind_direction": current.get("wind_direction_10m"),
        "wind_direction_unit": units.get("wind_direction_10m"),
        "is_day": current.get("is_day"),
    }


def _normalize_open_meteo_daily(daily: dict[str, Any], units: dict[str, Any], days: int) -> list[dict[str, Any]]:
    dates = daily.get("time")
    if not isinstance(dates, list):
        raise WeatherProviderError("weather provider returned malformed forecast dates")
    normalized: list[dict[str, Any]] = []
    for index, date_value in enumerate(dates[:days]):
        normalized.append(
            {
                "date": date_value,
                "weather_code": _daily_value(daily, "weather_code", index),
                "temperature_max": _daily_value(daily, "temperature_2m_max", index),
                "temperature_max_unit": units.get("temperature_2m_max"),
                "temperature_min": _daily_value(daily, "temperature_2m_min", index),
                "temperature_min_unit": units.get("temperature_2m_min"),
                "precipitation_sum": _daily_value(daily, "precipitation_sum", index),
                "precipitation_sum_unit": units.get("precipitation_sum"),
                "wind_speed_max": _daily_value(daily, "wind_speed_10m_max", index),
                "wind_speed_max_unit": units.get("wind_speed_10m_max"),
            }
        )
    return normalized


def _daily_value(daily: dict[str, Any], key: str, index: int) -> Any:
    values = daily.get(key)
    if not isinstance(values, list) or index >= len(values):
        return None
    return values[index]


WEATHER_SCHEMAS = {
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
                },
                "required": ["location"],
                "additionalProperties": False,
            },
        },
    },
}
