from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Callable, Protocol

import httpx

from agent.connectors.cost_policy import (
    ProviderCostConfig,
    ProviderDecision,
    ProviderDecisionStatus,
    select_provider,
    weather_provider_candidates,
)
from agent.config.runtime import env_bool, parse_float, parse_int
from agent.tools.weather.cache import WeatherCache, weather_cache_allowed, weather_cache_key
from agent.tools.weather.models import (
    UnitSystem,
    WeatherAlert,
    WeatherCurrent,
    WeatherDaily,
    WeatherHourly,
    WeatherLocation,
    WeatherProviderError,
    WeatherResult,
    condition_from_weather_code,
    normalize_unit_system,
)
from agent.tools.weather.preferences import configured_default_location, weather_preferences


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

    def alerts(self, location: str, locale: str | None = None) -> dict[str, Any]:
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

    def alerts(self, location: str, locale: str | None = None) -> dict[str, Any]:
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

    def alerts(self, location: str, locale: str | None = None) -> dict[str, Any]:
        return {}


@dataclass(frozen=True)
class UnavailableWeatherProvider:
    name: str
    error: str
    setup_hint: str = ""
    decision: ProviderDecision | None = None

    def is_configured(self) -> bool:
        return False

    def current_weather(self, location: str, units: str, locale: str | None = None) -> dict[str, Any]:
        raise WeatherProviderError(self.error)

    def forecast(
        self,
        location: str,
        days: int,
        units: str,
        locale: str | None = None,
        include_hourly: bool = False,
    ) -> dict[str, Any]:
        raise WeatherProviderError(self.error)

    def alerts(self, location: str, locale: str | None = None) -> dict[str, Any]:
        raise WeatherProviderError(self.error)


@dataclass(frozen=True)
class WeatherKitProvider:
    name: str = "weatherkit"

    def is_configured(self) -> bool:
        return _weatherkit_credentials_configured()

    def current_weather(self, location: str, units: str, locale: str | None = None) -> dict[str, Any]:
        raise WeatherProviderError(_weatherkit_stub_error())

    def forecast(
        self,
        location: str,
        days: int,
        units: str,
        locale: str | None = None,
        include_hourly: bool = False,
    ) -> dict[str, Any]:
        raise WeatherProviderError(_weatherkit_stub_error())

    def alerts(self, location: str, locale: str | None = None) -> dict[str, Any]:
        raise WeatherProviderError(_weatherkit_stub_error())


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

    def alerts(self, location: str, locale: str | None = None) -> dict[str, Any]:
        raise WeatherProviderError("weather alerts are not supported by provider open_meteo")

    def _resolve_location(self, location: str, locale: str | None) -> dict[str, Any]:
        direct = _parse_direct_coordinates(location)
        if direct is not None:
            return direct
        return self._geocode(location, locale)

    def _geocode(self, location: str, locale: str | None) -> dict[str, Any]:
        hint = _city_region_hint(location)
        payload = self._geocode_payload(location, locale)
        results = _geocoding_results(payload)
        results = _prefer_admin1_results(results, hint)
        if not results and hint is not None:
            payload = self._geocode_payload(hint["query"], locale)
            results = _prefer_admin1_results(_geocoding_results(payload), hint)
        if not results:
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

    def _geocode_payload(self, location: str, locale: str | None) -> dict[str, Any]:
        params: dict[str, Any] = {"name": location, "count": 5, "format": "json"}
        language = _language_from_locale(locale)
        if language:
            params["language"] = language
        return self._get_json(self.geocoding_endpoint, params=params)

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


@dataclass(frozen=True)
class NWSProvider:
    timeout_seconds: float = 10
    geocoding_endpoint: str = "https://geocoding-api.open-meteo.com/v1/search"
    points_endpoint_template: str = "https://api.weather.gov/points/{latitude},{longitude}"
    alerts_endpoint: str = "https://api.weather.gov/alerts/active"
    client_factory: Callable[[float], httpx.Client] | None = None
    name: str = "nws"

    def is_configured(self) -> bool:
        return True

    def current_weather(self, location: str, units: str, locale: str | None = None) -> dict[str, Any]:
        selected = self._resolve_location(location, locale)
        points = self._points(selected)
        hourly_url = _nws_property(points, "forecastHourly")
        if not hourly_url:
            raise WeatherProviderError("missing NWS grid data for hourly forecast")
        hourly = self._get_json(hourly_url)
        period = _first_nws_period(hourly)
        current = _normalize_nws_current(period)
        nws_location = _nws_location(selected, points)
        result = WeatherResult(
            status="ok",
            provider=self.name,
            units=UnitSystem.IMPERIAL,
            retrieved_at=datetime.now(UTC).isoformat(),
            location=nws_location,
            current=current,
            timezone=nws_location.timezone,
            provider_timestamp=current.time,
            metadata=_provider_metadata(self.name),
            raw_provider_payload={"points": points, "hourly": hourly},
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
        points = self._points(selected)
        forecast_url = _nws_property(points, "forecast")
        if not forecast_url:
            raise WeatherProviderError("missing NWS grid data for daily forecast")
        forecast = self._get_json(forecast_url)
        periods = _nws_periods(forecast)
        if not periods:
            raise WeatherProviderError("NWS forecast returned no periods")
        hourly_payload = None
        hourly: list[WeatherHourly] = []
        hourly_url = _nws_property(points, "forecastHourly")
        if include_hourly and hourly_url:
            hourly_payload = self._get_json(hourly_url)
            hourly = [_normalize_nws_hourly(period) for period in _nws_periods(hourly_payload)[:24]]
        nws_location = _nws_location(selected, points)
        result = WeatherResult(
            status="ok",
            provider=self.name,
            units=UnitSystem.IMPERIAL,
            retrieved_at=datetime.now(UTC).isoformat(),
            location=nws_location,
            daily=_normalize_nws_daily(periods, days),
            hourly=hourly,
            timezone=nws_location.timezone,
            metadata=_provider_metadata(self.name),
            raw_provider_payload={"points": points, "forecast": forecast, "hourly": hourly_payload},
        )
        return result.to_dict(include_raw=_debug_raw_enabled())

    def alerts(self, location: str, locale: str | None = None) -> dict[str, Any]:
        selected = self._resolve_location(location, locale)
        points = self._points(selected)
        payload = self._get_json(
            self.alerts_endpoint,
            params={"point": f"{selected['latitude']},{selected['longitude']}"},
        )
        features = payload.get("features")
        if not isinstance(features, list):
            raise WeatherProviderError("NWS alerts returned malformed payload")
        nws_location = _nws_location(selected, points)
        result = WeatherResult(
            status="ok",
            provider=self.name,
            units=UnitSystem.IMPERIAL,
            retrieved_at=datetime.now(UTC).isoformat(),
            location=nws_location,
            alerts=[_normalize_nws_alert(feature) for feature in features if isinstance(feature, dict)],
            timezone=nws_location.timezone,
            metadata=_provider_metadata(self.name),
            raw_provider_payload={"points": points, "alerts": payload},
        )
        return result.to_dict(include_raw=_debug_raw_enabled())

    def _resolve_location(self, location: str, locale: str | None) -> dict[str, Any]:
        direct = _parse_direct_coordinates(location)
        if direct is not None:
            return direct
        hint = _city_region_hint(location)
        results = _prefer_admin1_results(_geocoding_results(self._geocode_payload(location, locale)), hint)
        if not results and hint is not None:
            results = _prefer_admin1_results(_geocoding_results(self._geocode_payload(hint["query"], locale)), hint)
        if not results:
            raise WeatherProviderError("location not found")
        selected = results[0]
        if not isinstance(selected, dict):
            raise WeatherProviderError("weather geocoding provider returned malformed result")
        if not _is_us_geocode_result(selected):
            raise WeatherProviderError("unsupported location: NWS supports U.S. locations only")
        if not isinstance(selected.get("latitude"), (int, float)) or not isinstance(selected.get("longitude"), (int, float)):
            raise WeatherProviderError("weather geocoding provider returned malformed coordinates")
        return selected

    def _geocode_payload(self, location: str, locale: str | None) -> dict[str, Any]:
        params: dict[str, Any] = {"name": location, "count": 5, "format": "json"}
        language = _language_from_locale(locale)
        if language:
            params["language"] = language
        return self._get_json(self.geocoding_endpoint, params=params)

    def _points(self, selected_location: dict[str, Any]) -> dict[str, Any]:
        url = self.points_endpoint_template.format(
            latitude=selected_location["latitude"],
            longitude=selected_location["longitude"],
        )
        try:
            return self._get_json(url)
        except WeatherProviderError as exc:
            message = str(exc)
            if "HTTP 404" in message or "HTTP 400" in message:
                raise WeatherProviderError("unsupported location: NWS supports U.S. locations only") from exc
            raise

    def _get_json(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        headers = {
            "Accept": "application/geo+json, application/json",
            "User-Agent": "ai-super-agent/0.1 (local safety-first agent)",
        }
        try:
            with self._client() as client:
                response = client.get(url, params=params or {}, headers=headers)
                response.raise_for_status()
                payload = response.json()
        except httpx.TimeoutException as exc:
            raise WeatherProviderError("retryable weather provider error: NWS request timed out") from exc
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            if status >= 500:
                raise WeatherProviderError(f"retryable weather provider error: NWS returned HTTP {status}") from exc
            raise WeatherProviderError(f"weather provider returned HTTP {status}") from exc
        except httpx.HTTPError as exc:
            raise WeatherProviderError(f"retryable weather provider error: {type(exc).__name__}") from exc
        except ValueError as exc:
            raise WeatherProviderError("weather provider returned malformed JSON") from exc
        if not isinstance(payload, dict):
            raise WeatherProviderError("weather provider returned malformed JSON")
        return payload

    def _client(self) -> httpx.Client:
        if self.client_factory is not None:
            return self.client_factory(self.timeout_seconds)
        return httpx.Client(timeout=self.timeout_seconds)


@dataclass(frozen=True)
class WeatherAPIProvider:
    api_key: str | None = None
    timeout_seconds: float = 10
    base_url: str = "https://api.weatherapi.com/v1"
    client_factory: Callable[[float], httpx.Client] | None = None
    name: str = "weatherapi"

    def is_configured(self) -> bool:
        return bool(self._api_key())

    def current_weather(self, location: str, units: str, locale: str | None = None) -> dict[str, Any]:
        payload = self._get_json(
            "current.json",
            {"q": location, "aqi": "no", **_weatherapi_language_param(locale)},
        )
        result = WeatherResult(
            status="ok",
            provider=self.name,
            units=normalize_unit_system(units),
            retrieved_at=datetime.now(UTC).isoformat(),
            location=_weatherapi_location(payload),
            current=_normalize_weatherapi_current(payload.get("current"), units),
            timezone=_string_or_none(_weatherapi_location_payload(payload).get("tz_id")),
            provider_timestamp=_string_or_none(_weatherapi_current_payload(payload).get("last_updated")),
            metadata=_provider_metadata(self.name),
            raw_provider_payload={"current": payload},
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
        payload = self._get_json(
            "forecast.json",
            {
                "q": location,
                "days": max(1, min(int(days), 10)),
                "aqi": "no",
                "alerts": "yes",
                **_weatherapi_language_param(locale),
            },
        )
        forecast_days = _weatherapi_forecast_days(payload)
        result = WeatherResult(
            status="ok",
            provider=self.name,
            units=normalize_unit_system(units),
            retrieved_at=datetime.now(UTC).isoformat(),
            location=_weatherapi_location(payload),
            daily=[_normalize_weatherapi_daily(day, units) for day in forecast_days[:days]],
            hourly=_normalize_weatherapi_hourly(forecast_days, units) if include_hourly else [],
            alerts=_normalize_weatherapi_alerts(payload),
            timezone=_string_or_none(_weatherapi_location_payload(payload).get("tz_id")),
            metadata=_provider_metadata(self.name),
            raw_provider_payload={"forecast": payload},
        )
        return result.to_dict(include_raw=_debug_raw_enabled())

    def alerts(self, location: str, locale: str | None = None) -> dict[str, Any]:
        payload = self._get_json(
            "forecast.json",
            {"q": location, "days": 1, "aqi": "no", "alerts": "yes", **_weatherapi_language_param(locale)},
        )
        result = WeatherResult(
            status="ok",
            provider=self.name,
            units=UnitSystem.METRIC,
            retrieved_at=datetime.now(UTC).isoformat(),
            location=_weatherapi_location(payload),
            alerts=_normalize_weatherapi_alerts(payload),
            timezone=_string_or_none(_weatherapi_location_payload(payload).get("tz_id")),
            metadata=_provider_metadata(self.name),
            raw_provider_payload={"alerts": payload},
        )
        return result.to_dict(include_raw=_debug_raw_enabled())

    def _api_key(self) -> str:
        return (self.api_key or os.getenv("WEATHERAPI_API_KEY") or os.getenv("WEATHER_API_KEY") or "").strip()

    def _get_json(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        api_key = self._api_key()
        if not api_key:
            raise WeatherProviderError(_weatherapi_setup_hint())
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        safe_params = dict(params)
        safe_params["key"] = api_key
        try:
            with self._client() as client:
                response = client.get(url, params=safe_params)
                response.raise_for_status()
                payload = response.json()
        except httpx.TimeoutException as exc:
            raise WeatherProviderError("retryable weather provider error: WeatherAPI request timed out") from exc
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            if status >= 500:
                raise WeatherProviderError(f"retryable weather provider error: WeatherAPI returned HTTP {status}") from exc
            raise WeatherProviderError(f"weather provider returned HTTP {status}") from exc
        except httpx.HTTPError as exc:
            raise WeatherProviderError(f"retryable weather provider error: {type(exc).__name__}") from exc
        except ValueError as exc:
            raise WeatherProviderError("weather provider returned malformed JSON") from exc
        if not isinstance(payload, dict):
            raise WeatherProviderError("weather provider returned malformed JSON")
        error = payload.get("error")
        if isinstance(error, dict):
            message = _string_or_none(error.get("message")) or "WeatherAPI returned an error"
            raise WeatherProviderError(message)
        return payload

    def _client(self) -> httpx.Client:
        if self.client_factory is not None:
            return self.client_factory(self.timeout_seconds)
        return httpx.Client(timeout=self.timeout_seconds)


@dataclass(frozen=True)
class WeatherProviderSelector:
    timeout_seconds: float = 10
    open_meteo: WeatherProvider | None = None
    nws: WeatherProvider | None = None
    weatherapi: WeatherProvider | None = None
    name: str = "auto"

    def is_configured(self) -> bool:
        return True

    def provider_for_action(
        self,
        action: str,
        *,
        explicit_provider: str | None = None,
        configured_default: str | None = None,
    ) -> tuple[WeatherProvider, ProviderDecision]:
        return _select_weather_provider(
            action,
            explicit_provider=explicit_provider,
            configured_default=configured_default,
            providers={
                "open_meteo": self.open_meteo or OpenMeteoProvider(timeout_seconds=self.timeout_seconds),
                "nws": self.nws or NWSProvider(timeout_seconds=self.timeout_seconds),
                "weatherapi": self.weatherapi or WeatherAPIProvider(timeout_seconds=self.timeout_seconds),
            },
        )

    def current_weather(self, location: str, units: str, locale: str | None = None) -> dict[str, Any]:
        provider, decision = self.provider_for_action("current")
        return _attach_provider_decision(provider.current_weather(location, units, locale), decision)

    def forecast(
        self,
        location: str,
        days: int,
        units: str,
        locale: str | None = None,
        include_hourly: bool = False,
    ) -> dict[str, Any]:
        provider, decision = self.provider_for_action("forecast")
        return _attach_provider_decision(provider.forecast(location, days, units, locale, include_hourly), decision)

    def alerts(self, location: str, locale: str | None = None) -> dict[str, Any]:
        provider, decision = self.provider_for_action("alerts")
        return _attach_provider_decision(provider.alerts(location, locale), decision)


def provider_from_env() -> WeatherProvider:
    provider_name = weather_preferences().provider
    timeout = parse_float(
        "WEATHER_TIMEOUT_SECONDS",
        os.getenv("WEATHER_TIMEOUT_SECONDS", "10"),
        minimum=1,
        maximum=60,
    )
    if provider_name in {"disabled", "none"}:
        return DisabledWeatherProvider()
    if provider_name in {"", "auto"}:
        return WeatherProviderSelector(timeout_seconds=timeout)
    if provider_name in {"open_meteo", "open-meteo", "openmeteo"}:
        return OpenMeteoProvider(timeout_seconds=timeout)
    if provider_name == "nws":
        return NWSProvider(timeout_seconds=timeout)
    if provider_name == "weatherapi":
        provider, _decision = _select_weather_provider("current", configured_default="weatherapi")
        return provider
    if provider_name == "weatherkit":
        return WeatherKitProvider()
    return UnsupportedWeatherProvider(provider_name)


def make_weather_tools(provider: WeatherProvider | None = None) -> dict[str, Any]:
    active_provider = provider or provider_from_env()

    def status() -> dict[str, Any]:
        return weather_provider_status(active_provider)

    def current(
        location: str | None = None,
        units: str | None = None,
        locale: str | None = None,
        no_cache: bool = False,
        provider: str | None = None,
    ) -> dict[str, Any]:
        selected_provider, provider_decision = _provider_for_request(provider, active_provider, "current")
        location, default_audit = _resolve_location_input(location)
        location_error = _validate_location(location)
        if location_error:
            return _attach_provider_decision(
                _error_payload(selected_provider, location_error, configured=_provider_configured(selected_provider)),
                provider_decision,
            )
        configured_error = _configuration_error(selected_provider)
        if configured_error:
            return _attach_provider_decision(configured_error, provider_decision)
        resolved_units = _resolve_units(units)
        cache_allowed = _weather_cache_enabled() and weather_cache_allowed(location)
        cache = WeatherCache(_weather_cache_path())
        cache_key = weather_cache_key(
            provider=selected_provider.name,
            location=location,
            request_type="current",
            units=resolved_units,
        )
        cache_summary = "weather cache miss"
        if not no_cache and cache_allowed:
            cached_entry = cache.get(cache_key)
            if cached_entry is not None and not cached_entry.expired:
                return _with_weather_audit(
                    _attach_provider_decision(
                        _apply_cache_metadata(
                            cached_entry.payload,
                            cached=True,
                            cached_at=cached_entry.cached_at,
                            expires_at=cached_entry.expires_at,
                        ),
                        provider_decision,
                    ),
                    selected_provider,
                    _audit_summary("weather cache hit", default_audit, provider_decision),
                )
            if cached_entry is not None and cached_entry.expired:
                cache_summary = "weather cache expired refresh"
        try:
            raw = selected_provider.current_weather(location.strip(), resolved_units, locale)
        except Exception as exc:
            return _attach_provider_decision(_provider_error(selected_provider, exc), provider_decision)
        if isinstance(raw, dict) and raw.get("status") == "ok":
            if no_cache or not cache_allowed:
                return _with_weather_audit(
                    _attach_provider_decision(_apply_cache_metadata(raw, cached=False, cached_at=None, expires_at=None), provider_decision),
                    selected_provider,
                    _audit_summary(_weather_cache_skip_summary(no_cache, cache_allowed), default_audit, provider_decision),
                )
            cache_entry = cache.set(cache_key, raw, _weather_cache_ttl("current"))
            return _with_weather_audit(
                _attach_provider_decision(
                    _apply_cache_metadata(raw, cached=False, cached_at=cache_entry.cached_at, expires_at=cache_entry.expires_at),
                    provider_decision,
                ),
                selected_provider,
                _audit_summary(cache_summary, default_audit, provider_decision),
            )
        retrieved_at = datetime.now(UTC).isoformat()
        fallback = {
            "status": "ok",
            "provider": selected_provider.name,
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
                _attach_provider_decision(
                    _apply_cache_metadata(fallback, cached=False, cached_at=None, expires_at=None),
                    provider_decision,
                ),
                selected_provider,
                _audit_summary(_weather_cache_skip_summary(no_cache, cache_allowed), default_audit, provider_decision),
            )
        cache_entry = cache.set(cache_key, fallback, _weather_cache_ttl("current"))
        return _with_weather_audit(
            _attach_provider_decision(
                _apply_cache_metadata(fallback, cached=False, cached_at=cache_entry.cached_at, expires_at=cache_entry.expires_at),
                provider_decision,
            ),
            selected_provider,
            _audit_summary(cache_summary, default_audit, provider_decision),
        )

    def forecast(
        location: str | None = None,
        days: int | None = None,
        units: str | None = None,
        locale: str | None = None,
        include_hourly: bool = False,
        no_cache: bool = False,
        provider: str | None = None,
    ) -> dict[str, Any]:
        selected_provider, provider_decision = _provider_for_request(provider, active_provider, "forecast")
        location, default_audit = _resolve_location_input(location)
        location_error = _validate_location(location)
        if location_error:
            return _attach_provider_decision(
                _error_payload(selected_provider, location_error, configured=_provider_configured(selected_provider)),
                provider_decision,
            )
        configured_error = _configuration_error(selected_provider)
        if configured_error:
            return _attach_provider_decision(configured_error, provider_decision)
        resolved_units = _resolve_units(units)
        max_days = parse_int(
            "WEATHER_MAX_FORECAST_DAYS",
            os.getenv("WEATHER_MAX_FORECAST_DAYS", "7"),
            minimum=1,
            maximum=16,
        )
        requested_days = days if days is not None else min(max_days, 3)
        clamped_days = max(1, min(int(requested_days), max_days, 16))
        cache_allowed = _weather_cache_enabled() and weather_cache_allowed(location)
        cache = WeatherCache(_weather_cache_path())
        cache_key = weather_cache_key(
            provider=selected_provider.name,
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
                    _attach_provider_decision(
                        _apply_cache_metadata(
                            payload,
                            cached=True,
                            cached_at=cached_entry.cached_at,
                            expires_at=cached_entry.expires_at,
                        ),
                        provider_decision,
                    ),
                    selected_provider,
                    _audit_summary("weather cache hit", default_audit, provider_decision),
                )
            if cached_entry is not None and cached_entry.expired:
                cache_summary = "weather cache expired refresh"
        try:
            raw = selected_provider.forecast(
                location.strip(),
                clamped_days,
                resolved_units,
                locale,
                bool(include_hourly),
            )
        except Exception as exc:
            return _attach_provider_decision(_provider_error(selected_provider, exc), provider_decision)
        if isinstance(raw, dict) and raw.get("status") == "ok":
            payload = dict(raw)
            payload["days"] = clamped_days
            if no_cache or not cache_allowed:
                return _with_weather_audit(
                    _attach_provider_decision(
                        _apply_cache_metadata(payload, cached=False, cached_at=None, expires_at=None),
                        provider_decision,
                    ),
                    selected_provider,
                    _audit_summary(_weather_cache_skip_summary(no_cache, cache_allowed), default_audit, provider_decision),
                )
            cache_entry = cache.set(cache_key, payload, _weather_cache_ttl("forecast"))
            return _with_weather_audit(
                _attach_provider_decision(
                    _apply_cache_metadata(payload, cached=False, cached_at=cache_entry.cached_at, expires_at=cache_entry.expires_at),
                    provider_decision,
                ),
                selected_provider,
                _audit_summary(cache_summary, default_audit, provider_decision),
            )
        periods = raw.get("forecast", raw.get("periods", [])) if isinstance(raw, dict) else []
        if not isinstance(periods, list):
            periods = []
        retrieved_at = datetime.now(UTC).isoformat()
        fallback = {
            "status": "ok",
            "provider": selected_provider.name,
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
                _attach_provider_decision(
                    _apply_cache_metadata(fallback, cached=False, cached_at=None, expires_at=None),
                    provider_decision,
                ),
                selected_provider,
                _audit_summary(_weather_cache_skip_summary(no_cache, cache_allowed), default_audit, provider_decision),
            )
        cache_entry = cache.set(cache_key, fallback, _weather_cache_ttl("forecast"))
        return _with_weather_audit(
            _attach_provider_decision(
                _apply_cache_metadata(fallback, cached=False, cached_at=cache_entry.cached_at, expires_at=cache_entry.expires_at),
                provider_decision,
            ),
            selected_provider,
            _audit_summary(cache_summary, default_audit, provider_decision),
        )

    def alerts(
        location: str | None = None,
        locale: str | None = None,
        provider: str | None = None,
    ) -> dict[str, Any]:
        selected_provider, provider_decision = _provider_for_request(provider, active_provider, "alerts")
        location, default_audit = _resolve_location_input(location)
        location_error = _validate_location(location)
        if location_error:
            return _attach_provider_decision(
                _error_payload(selected_provider, location_error, configured=_provider_configured(selected_provider)),
                provider_decision,
            )
        configured_error = _configuration_error(selected_provider)
        if configured_error:
            return _attach_provider_decision(configured_error, provider_decision)
        try:
            raw = selected_provider.alerts(location.strip(), locale)
        except Exception as exc:
            return _attach_provider_decision(_provider_error(selected_provider, exc), provider_decision)
        if isinstance(raw, dict) and raw.get("status") == "ok":
            return _with_weather_audit(
                _attach_provider_decision(raw, provider_decision),
                selected_provider,
                _audit_summary("weather alerts provider call", default_audit, provider_decision),
            )
        return _with_weather_audit(
            _attach_provider_decision(
                {
                    "status": "ok",
                    "provider": selected_provider.name,
                    "location": _display_location(raw, location),
                    "trust_level": "UNTRUSTED_WEB",
                    "retrieved_at": datetime.now(UTC).isoformat(),
                    "alerts": raw.get("alerts", []) if isinstance(raw, dict) else [],
                },
                provider_decision,
            ),
            selected_provider,
            _audit_summary("weather alerts provider call", default_audit, provider_decision),
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
        "weather.alerts": alerts,
        "weather.cache_clear": cache_clear,
    }


def weather_provider_status(provider: WeatherProvider | None = None) -> dict[str, Any]:
    active_provider = provider or provider_from_env()
    preferences = weather_preferences()
    configured = _provider_configured(active_provider)
    supported = active_provider.name not in {"disabled"} and not active_provider.name.startswith("unsupported:")
    error = None
    if active_provider.name == "disabled":
        error = "weather provider is not configured"
    elif active_provider.name == "weatherkit" and not configured:
        error = _weatherkit_stub_error()
    elif active_provider.name.startswith("unsupported:"):
        error = "configured weather provider is not supported by this build"
        if not os.getenv("WEATHER_API_KEY", "").strip():
            error += "; WEATHER_API_KEY is not set if this provider requires one"
    elif active_provider.name == "weatherapi" and not configured:
        error = _weatherapi_setup_hint()
    elif isinstance(active_provider, UnavailableWeatherProvider):
        error = active_provider.error
    payload = {
        "status": "ok" if configured and supported else "error",
        "provider": active_provider.name,
        "configured": configured,
        "supported": supported,
        "requires_api_key": active_provider.name in {"weatherkit", "weatherapi"}
        or (active_provider.name != "open_meteo" and active_provider.name.startswith("unsupported:")),
        "api_key_configured": _weatherkit_credentials_configured()
        if active_provider.name == "weatherkit"
        else _weatherapi_credentials_configured(),
        "credentials_configured": _weatherkit_credentials_configured() if active_provider.name == "weatherkit" else None,
        "web_access_enabled": os.getenv("WEB_ACCESS_ENABLED", "true").strip().casefold() not in {"0", "false", "no", "off"},
        "preferences": preferences.to_dict(),
        "trust_level": "UNTRUSTED_WEB",
        "error": error,
    }
    if active_provider.name == "auto":
        payload["providers"] = weather_providers_status()
        payload["decisions"] = {
            action: decision.to_dict()
            for action, decision in {
                "current": _select_weather_provider("current")[1],
                "forecast": _select_weather_provider("forecast")[1],
                "alerts": _select_weather_provider("alerts")[1],
            }.items()
        }
    return payload


def weather_providers_status() -> list[dict[str, Any]]:
    config = ProviderCostConfig.from_env()
    return [
        {
            "name": candidate.name,
            "configured": candidate.configured,
            "no_key_required": candidate.no_key_required,
            "official": candidate.official,
            "paid_api": candidate.paid_api,
            "quota_limited": candidate.quota_limited,
            "default_allowed": select_provider("weather", [candidate], config=config).status == ProviderDecisionStatus.SELECTED,
            "setup_hint": candidate.setup_hint,
        }
        for candidate in weather_provider_candidates()
    ]


def _validate_location(location: str) -> str | None:
    if not isinstance(location, str) or not location.strip():
        return "location is required"
    if len(location.strip()) > 200:
        return "location is too long"
    return None


def _resolve_units(units: str | None) -> str:
    requested = (units or weather_preferences().units).strip().lower()
    if requested in {"metric", "imperial"}:
        return requested
    return "metric"


def _select_weather_provider(
    action: str,
    *,
    explicit_provider: str | None = None,
    configured_default: str | None = None,
    providers: dict[str, WeatherProvider] | None = None,
) -> tuple[WeatherProvider, ProviderDecision]:
    candidates = _weather_candidates_for_action(action)
    env = dict(os.environ)
    if configured_default:
        env["WEATHER_DEFAULT_PROVIDER"] = configured_default
    config = ProviderCostConfig.from_env(env)
    explicit = None if _normalize_weather_provider_name(explicit_provider) == "auto" else explicit_provider
    decision = select_provider("weather", candidates, config=config, explicit_provider=explicit)
    selected = decision.selected_provider
    provider_map = providers or {}
    if decision.status == ProviderDecisionStatus.SELECTED and selected:
        return _weather_provider_by_name(selected, provider_map), decision
    fallback_name = _normalize_weather_provider_name(explicit_provider or configured_default or selected or "auto")
    if fallback_name == "auto":
        fallback_name = "weatherapi" if explicit_provider == "weatherapi" else "auto"
    return (
        UnavailableWeatherProvider(
            fallback_name,
            decision.reason,
            setup_hint=decision.setup_hint,
            decision=decision,
        ),
        decision,
    )


def _weather_candidates_for_action(action: str) -> list[Any]:
    candidates = weather_provider_candidates()
    if action != "alerts":
        return candidates
    adjusted = []
    for candidate in candidates:
        if candidate.name == "open_meteo":
            adjusted.append(
                type(candidate)(
                    candidate.name,
                    candidate.domain,
                    candidate.configured,
                    "Open-Meteo does not provide active alert data; use NOAA/NWS for U.S. official alerts.",
                    no_key_required=candidate.no_key_required,
                    official=candidate.official,
                    local=candidate.local,
                    cached=candidate.cached,
                    user_provided=candidate.user_provided,
                    paid_api=candidate.paid_api,
                    quota_limited=candidate.quota_limited,
                    supports_requested_action=False,
                    metadata=candidate.metadata,
                )
            )
        else:
            adjusted.append(candidate)
    return adjusted


def _weather_provider_by_name(provider_name: str, provider_map: dict[str, WeatherProvider] | None = None) -> WeatherProvider:
    normalized = _normalize_weather_provider_name(provider_name)
    if provider_map and normalized in provider_map:
        return provider_map[normalized]
    timeout = parse_float(
        "WEATHER_TIMEOUT_SECONDS",
        os.getenv("WEATHER_TIMEOUT_SECONDS", "10"),
        minimum=1,
        maximum=60,
    )
    if normalized == "open_meteo":
        return OpenMeteoProvider(timeout_seconds=timeout)
    if normalized == "nws":
        return NWSProvider(timeout_seconds=timeout)
    if normalized == "weatherapi":
        return WeatherAPIProvider(timeout_seconds=timeout)
    if normalized == "weatherkit":
        return WeatherKitProvider()
    if normalized in {"disabled", "none"}:
        return DisabledWeatherProvider()
    return UnsupportedWeatherProvider(normalized)


def _normalize_weather_provider_name(provider_name: str | None) -> str:
    normalized = (provider_name or "").strip().casefold().replace("-", "_")
    if normalized == "openmeteo":
        return "open_meteo"
    return normalized or "auto"


def _configuration_error(provider: WeatherProvider) -> dict[str, Any] | None:
    if provider.name == "disabled":
        return _error_payload(provider, "weather provider is not configured", configured=False)
    unavailable_error = getattr(provider, "error", None)
    if isinstance(unavailable_error, str) and unavailable_error:
        return _error_payload(provider, unavailable_error, configured=False)
    if provider.name.startswith("unsupported:"):
        return _error_payload(provider, "configured weather provider is not supported by this build", configured=False)
    if provider.name == "weatherkit" and not _provider_configured(provider):
        return _error_payload(provider, _weatherkit_stub_error(), configured=False)
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
        "retryable": error.startswith("retryable weather provider error"),
        "configured": _provider_configured(provider),
        "trust_level": "UNTRUSTED_WEB",
        "_audit": {"network_domains": _provider_domains(provider.name)},
    }


def _with_weather_audit(payload: dict[str, Any], provider: WeatherProvider, summary: str = "weather provider call") -> dict[str, Any]:
    result = dict(payload)
    result["_audit"] = {"network_domains": _provider_domains(provider.name), "result_summary": summary}
    return result


def _attach_provider_decision(payload: dict[str, Any], decision: ProviderDecision | None) -> dict[str, Any]:
    if decision is None:
        return payload
    result = dict(payload)
    result["provider_decision"] = decision.to_dict()
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
    global_ttl = weather_preferences().cache_ttl_seconds
    if global_ttl is not None:
        return global_ttl
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
    if not _weather_cache_enabled():
        return "weather cache disabled"
    if not cache_allowed:
        return "weather cache skipped precise location"
    return "weather cache miss"


def _weather_cache_enabled() -> bool:
    return weather_preferences().cache_enabled


def _resolve_location_input(location: str | None) -> tuple[str, dict[str, Any] | None]:
    text = (location or "").strip()
    if text:
        return text, None
    default = configured_default_location()
    if default is None:
        return "", None
    return default.location, {"default_location_used": True, "default_location_source": default.source}


def _audit_summary(
    summary: str,
    default_audit: dict[str, Any] | None,
    provider_decision: ProviderDecision | None = None,
) -> str:
    if provider_decision is not None:
        selected = provider_decision.selected_provider or "unavailable"
        summary = f"{summary}; weather provider selected: {selected} ({provider_decision.reason})"
    if not default_audit:
        return summary
    return f"{summary}; weather default location used from {default_audit['default_location_source']}"


def _error_payload(provider: WeatherProvider, error: str, *, configured: bool) -> dict[str, Any]:
    payload = {
        "status": "error",
        "provider": provider.name,
        "error": error,
        "configured": configured,
        "trust_level": "UNTRUSTED_WEB",
    }
    setup_hint = getattr(provider, "setup_hint", None)
    if isinstance(setup_hint, str) and setup_hint:
        payload["setup_hint"] = setup_hint
    return payload


def _provider_configured(provider: WeatherProvider) -> bool:
    checker = getattr(provider, "is_configured", None)
    if callable(checker):
        return bool(checker())
    return provider.name != "disabled" and not provider.name.startswith("unsupported:")


def _provider_for_request(
    provider_name: str | None,
    default_provider: WeatherProvider,
    action: str,
) -> tuple[WeatherProvider, ProviderDecision | None]:
    requested = (provider_name or "").strip()
    if not requested:
        if isinstance(default_provider, WeatherProviderSelector):
            return default_provider.provider_for_action(action)
        decision = getattr(default_provider, "decision", None)
        if isinstance(decision, ProviderDecision):
            return default_provider, decision
        return default_provider, None
    normalized = _normalize_weather_provider_name(requested)
    if normalized == "auto":
        if isinstance(default_provider, WeatherProviderSelector):
            return default_provider.provider_for_action(action, explicit_provider="auto")
        provider, decision = _select_weather_provider(action, explicit_provider="auto")
        return provider, decision
    if isinstance(default_provider, WeatherProviderSelector):
        return default_provider.provider_for_action(action, explicit_provider=normalized)
    if normalized in {default_provider.name, default_provider.name.replace("-", "_"), default_provider.name.replace("_", "-")}:
        return default_provider, None
    if normalized in {"open_meteo", "open-meteo", "openmeteo"}:
        return _weather_provider_by_name("open_meteo"), None
    if normalized == "nws":
        return _weather_provider_by_name("nws"), None
    if normalized == "weatherapi":
        return _select_weather_provider(action, explicit_provider="weatherapi")
    if normalized == "weatherkit":
        return WeatherKitProvider(), None
    if normalized in {"disabled", "none"}:
        return DisabledWeatherProvider(), None
    return UnsupportedWeatherProvider(normalized), None


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
    if provider_name == "nws":
        return ["geocoding-api.open-meteo.com", "api.weather.gov"]
    if provider_name == "weatherapi":
        return ["api.weatherapi.com"]
    if provider_name == "auto":
        return ["geocoding-api.open-meteo.com", "api.open-meteo.com", "api.weather.gov"]
    if provider_name == "weatherkit":
        return ["weatherkit.apple.com"]
    if provider_name in {"disabled", ""}:
        return []
    if provider_name.startswith("unsupported:"):
        return [provider_name]
    return [provider_name]


def _provider_metadata(provider_name: str) -> dict[str, Any]:
    return {"name": provider_name, "domains": _provider_domains(provider_name)}


def _weatherkit_credentials_configured() -> bool:
    required = (
        "WEATHERKIT_TEAM_ID",
        "WEATHERKIT_SERVICE_ID",
        "WEATHERKIT_KEY_ID",
        "WEATHERKIT_PRIVATE_KEY_PATH",
    )
    return all(os.getenv(name, "").strip() for name in required)


def _weatherapi_credentials_configured() -> bool:
    return bool((os.getenv("WEATHERAPI_API_KEY") or os.getenv("WEATHER_API_KEY") or "").strip())


def _weatherapi_setup_hint() -> str:
    return "weatherapi provider is not configured; set WEATHERAPI_API_KEY or WEATHER_API_KEY"


def _weatherkit_stub_error() -> str:
    if not _weatherkit_credentials_configured():
        return (
            "weatherkit provider is not configured; set WEATHERKIT_TEAM_ID, WEATHERKIT_SERVICE_ID, "
            "WEATHERKIT_KEY_ID, and WEATHERKIT_PRIVATE_KEY_PATH"
        )
    return "weatherkit provider stub only; JWT signing is not implemented until the decision record is approved"


def _debug_raw_enabled() -> bool:
    return env_bool("DEBUG", default=False)


def _language_from_locale(locale: str | None) -> str | None:
    if not locale:
        return None
    language = locale.replace("_", "-").split("-", 1)[0].strip().lower()
    return language or None


_US_STATE_NAMES = {
    "al": "Alabama",
    "ak": "Alaska",
    "az": "Arizona",
    "ar": "Arkansas",
    "ca": "California",
    "co": "Colorado",
    "ct": "Connecticut",
    "de": "Delaware",
    "fl": "Florida",
    "ga": "Georgia",
    "hi": "Hawaii",
    "id": "Idaho",
    "il": "Illinois",
    "in": "Indiana",
    "ia": "Iowa",
    "ks": "Kansas",
    "ky": "Kentucky",
    "la": "Louisiana",
    "me": "Maine",
    "md": "Maryland",
    "ma": "Massachusetts",
    "mi": "Michigan",
    "mn": "Minnesota",
    "ms": "Mississippi",
    "mo": "Missouri",
    "mt": "Montana",
    "ne": "Nebraska",
    "nv": "Nevada",
    "nh": "New Hampshire",
    "nj": "New Jersey",
    "nm": "New Mexico",
    "ny": "New York",
    "nc": "North Carolina",
    "nd": "North Dakota",
    "oh": "Ohio",
    "ok": "Oklahoma",
    "or": "Oregon",
    "pa": "Pennsylvania",
    "ri": "Rhode Island",
    "sc": "South Carolina",
    "sd": "South Dakota",
    "tn": "Tennessee",
    "tx": "Texas",
    "ut": "Utah",
    "vt": "Vermont",
    "va": "Virginia",
    "wa": "Washington",
    "wv": "West Virginia",
    "wi": "Wisconsin",
    "wy": "Wyoming",
    "dc": "District of Columbia",
}


def _city_region_hint(location: str) -> dict[str, str] | None:
    parts = [part.strip() for part in location.split(",")]
    if len(parts) < 2 or not parts[0] or not parts[1]:
        return None
    region = re.sub(r"[^A-Za-z ]", "", parts[1]).strip()
    if not region:
        return None
    return {"query": parts[0], "admin1": _US_STATE_NAMES.get(region.casefold(), region)}


def _geocoding_results(payload: dict[str, Any]) -> list[Any]:
    results = payload.get("results") if isinstance(payload, dict) else None
    return results if isinstance(results, list) else []


def _prefer_admin1_results(results: list[Any], hint: dict[str, str] | None) -> list[Any]:
    if hint is None:
        return results
    expected = hint["admin1"].casefold()
    matches = [
        result
        for result in results
        if isinstance(result, dict) and str(result.get("admin1") or "").casefold() == expected
    ]
    return matches or results


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


def _is_us_geocode_result(location: dict[str, Any]) -> bool:
    country_code = _string_or_none(location.get("country_code"))
    country = (_string_or_none(location.get("country")) or "").casefold()
    if country_code:
        return country_code.upper() in {"US", "USA", "UM", "PR", "VI", "GU", "AS", "MP"}
    return country in {
        "united states",
        "united states of america",
        "puerto rico",
        "u.s. virgin islands",
        "guam",
        "american samoa",
        "northern mariana islands",
    }


def _nws_property(payload: dict[str, Any], key: str) -> str | None:
    properties = payload.get("properties")
    if not isinstance(properties, dict):
        return None
    return _string_or_none(properties.get(key))


def _nws_periods(payload: dict[str, Any]) -> list[dict[str, Any]]:
    properties = payload.get("properties")
    if not isinstance(properties, dict):
        return []
    periods = properties.get("periods")
    if not isinstance(periods, list):
        return []
    return [period for period in periods if isinstance(period, dict)]


def _first_nws_period(payload: dict[str, Any]) -> dict[str, Any]:
    periods = _nws_periods(payload)
    if not periods:
        raise WeatherProviderError("NWS forecast returned no periods")
    return periods[0]


def _nws_location(selected: dict[str, Any], points: dict[str, Any]) -> WeatherLocation:
    properties = points.get("properties")
    if not isinstance(properties, dict):
        properties = {}
    relative = properties.get("relativeLocation")
    relative_props = relative.get("properties") if isinstance(relative, dict) else None
    if not isinstance(relative_props, dict):
        relative_props = {}
    city = _string_or_none(relative_props.get("city"))
    state = _string_or_none(relative_props.get("state"))
    name = ", ".join(part for part in [city, state, "United States"] if part) or _location_label(selected)
    return WeatherLocation(
        name=name,
        latitude=float(selected["latitude"]) if isinstance(selected.get("latitude"), (int, float)) else None,
        longitude=float(selected["longitude"]) if isinstance(selected.get("longitude"), (int, float)) else None,
        timezone=_string_or_none(properties.get("timeZone") or selected.get("timezone")),
        admin1=_string_or_none(selected.get("admin1") or state),
        country=_string_or_none(selected.get("country") or "United States"),
    )


def _normalize_nws_current(period: dict[str, Any]) -> WeatherCurrent:
    return WeatherCurrent(
        time=_string_or_none(period.get("startTime")),
        temperature=period.get("temperature"),
        temperature_unit=_nws_temperature_unit(period.get("temperatureUnit")),
        condition=_string_or_none(period.get("shortForecast")),
        wind_speed=_nws_wind_speed_max(period),
        wind_speed_unit="mph" if _nws_wind_speed_max(period) is not None else None,
        wind_direction=_string_or_none(period.get("windDirection")),
    )


def _normalize_nws_hourly(period: dict[str, Any]) -> WeatherHourly:
    return WeatherHourly(
        time=_string_or_none(period.get("startTime")) or "unknown",
        temperature=period.get("temperature"),
        temperature_unit=_nws_temperature_unit(period.get("temperatureUnit")),
        precipitation_probability=_nws_probability(period),
        precipitation_probability_unit="%" if _nws_probability(period) is not None else None,
        condition=_string_or_none(period.get("shortForecast")),
        wind_speed=_nws_wind_speed_max(period),
        wind_speed_unit="mph" if _nws_wind_speed_max(period) is not None else None,
        wind_direction=_string_or_none(period.get("windDirection")),
    )


def _normalize_nws_daily(periods: list[dict[str, Any]], days: int) -> list[WeatherDaily]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for period in periods:
        date = _nws_period_date(period)
        if date:
            grouped.setdefault(date, []).append(period)
    normalized: list[WeatherDaily] = []
    for date, day_periods in list(grouped.items())[:days]:
        daytime = next((period for period in day_periods if period.get("isDaytime") is True), day_periods[0])
        nighttime = next((period for period in day_periods if period.get("isDaytime") is False), None)
        temperatures = [period.get("temperature") for period in day_periods if isinstance(period.get("temperature"), (int, float))]
        temp_unit = _nws_temperature_unit(daytime.get("temperatureUnit"))
        precip_values = [_nws_probability(period) for period in day_periods]
        wind_values = [_nws_wind_speed_max(period) for period in day_periods]
        normalized.append(
            WeatherDaily(
                date=date,
                condition=_string_or_none(daytime.get("shortForecast")),
                temperature_max=max(temperatures) if temperatures else daytime.get("temperature"),
                temperature_max_unit=temp_unit,
                temperature_min=min(temperatures) if temperatures else (nighttime or daytime).get("temperature"),
                temperature_min_unit=temp_unit,
                precipitation_probability_max=max(value for value in precip_values if value is not None)
                if any(value is not None for value in precip_values)
                else None,
                precipitation_probability_max_unit="%" if any(value is not None for value in precip_values) else None,
                wind_speed_max=max(value for value in wind_values if value is not None)
                if any(value is not None for value in wind_values)
                else None,
                wind_speed_max_unit="mph" if any(value is not None for value in wind_values) else None,
                wind_direction_dominant=_string_or_none(daytime.get("windDirection")),
            )
        )
    return normalized


def _normalize_nws_alert(feature: dict[str, Any]) -> WeatherAlert:
    properties = feature.get("properties")
    if not isinstance(properties, dict):
        properties = {}
    return WeatherAlert(
        title=_string_or_none(properties.get("event")) or "Weather alert",
        severity=_string_or_none(properties.get("severity")),
        starts_at=_string_or_none(properties.get("onset") or properties.get("effective")),
        ends_at=_string_or_none(properties.get("ends") or properties.get("expires")),
        source=_string_or_none(properties.get("senderName")),
        description=_string_or_none(properties.get("description")),
    )


def _weatherapi_language_param(locale: str | None) -> dict[str, str]:
    language = _language_from_locale(locale)
    return {"lang": language} if language else {}


def _weatherapi_location_payload(payload: dict[str, Any]) -> dict[str, Any]:
    location = payload.get("location")
    if not isinstance(location, dict):
        raise WeatherProviderError("WeatherAPI returned malformed location")
    return location


def _weatherapi_current_payload(payload: dict[str, Any]) -> dict[str, Any]:
    current = payload.get("current")
    if not isinstance(current, dict):
        raise WeatherProviderError("WeatherAPI returned malformed current weather")
    return current


def _weatherapi_forecast_days(payload: dict[str, Any]) -> list[dict[str, Any]]:
    forecast = payload.get("forecast")
    if not isinstance(forecast, dict):
        raise WeatherProviderError("WeatherAPI returned malformed forecast")
    forecast_days = forecast.get("forecastday")
    if not isinstance(forecast_days, list):
        raise WeatherProviderError("WeatherAPI returned malformed forecast days")
    return [item for item in forecast_days if isinstance(item, dict)]


def _weatherapi_location(payload: dict[str, Any]) -> WeatherLocation:
    location = _weatherapi_location_payload(payload)
    return WeatherLocation(
        name=", ".join(
            part
            for part in [
                _string_or_none(location.get("name")),
                _string_or_none(location.get("region")),
                _string_or_none(location.get("country")),
            ]
            if part
        )
        or "WeatherAPI location",
        latitude=_float_or_none(location.get("lat")),
        longitude=_float_or_none(location.get("lon")),
        timezone=_string_or_none(location.get("tz_id")),
        admin1=_string_or_none(location.get("region")),
        country=_string_or_none(location.get("country")),
    )


def _normalize_weatherapi_current(current_value: Any, units: str) -> WeatherCurrent:
    if not isinstance(current_value, dict):
        raise WeatherProviderError("WeatherAPI returned malformed current weather")
    imperial = normalize_unit_system(units) == UnitSystem.IMPERIAL
    condition = current_value.get("condition") if isinstance(current_value.get("condition"), dict) else {}
    return WeatherCurrent(
        time=_string_or_none(current_value.get("last_updated")),
        temperature=current_value.get("temp_f" if imperial else "temp_c"),
        temperature_unit="F" if imperial else "C",
        apparent_temperature=current_value.get("feelslike_f" if imperial else "feelslike_c"),
        apparent_temperature_unit="F" if imperial else "C",
        precipitation=current_value.get("precip_in" if imperial else "precip_mm"),
        precipitation_unit="inch" if imperial else "mm",
        wind_speed=current_value.get("wind_mph" if imperial else "wind_kph"),
        wind_speed_unit="mph" if imperial else "km/h",
        wind_direction=current_value.get("wind_degree"),
        wind_direction_unit="degrees",
        humidity=current_value.get("humidity"),
        humidity_unit="%",
        pressure=current_value.get("pressure_in" if imperial else "pressure_mb"),
        pressure_unit="inHg" if imperial else "mb",
        uv_index=current_value.get("uv"),
        weather_code=_int_or_none(condition.get("code")),
        condition=_string_or_none(condition.get("text")),
    )


def _normalize_weatherapi_daily(day_value: dict[str, Any], units: str) -> WeatherDaily:
    day = day_value.get("day")
    if not isinstance(day, dict):
        raise WeatherProviderError("WeatherAPI returned malformed daily forecast")
    imperial = normalize_unit_system(units) == UnitSystem.IMPERIAL
    condition = day.get("condition") if isinstance(day.get("condition"), dict) else {}
    return WeatherDaily(
        date=str(day_value.get("date") or "unknown"),
        weather_code=_int_or_none(condition.get("code")),
        condition=_string_or_none(condition.get("text")),
        temperature_max=day.get("maxtemp_f" if imperial else "maxtemp_c"),
        temperature_max_unit="F" if imperial else "C",
        temperature_min=day.get("mintemp_f" if imperial else "mintemp_c"),
        temperature_min_unit="F" if imperial else "C",
        precipitation_sum=day.get("totalprecip_in" if imperial else "totalprecip_mm"),
        precipitation_sum_unit="inch" if imperial else "mm",
        precipitation_probability_max=day.get("daily_chance_of_rain"),
        precipitation_probability_max_unit="%" if day.get("daily_chance_of_rain") is not None else None,
        wind_speed_max=day.get("maxwind_mph" if imperial else "maxwind_kph"),
        wind_speed_max_unit="mph" if imperial else "km/h",
        uv_index_max=day.get("uv"),
    )


def _normalize_weatherapi_hourly(forecast_days: list[dict[str, Any]], units: str) -> list[WeatherHourly]:
    imperial = normalize_unit_system(units) == UnitSystem.IMPERIAL
    normalized: list[WeatherHourly] = []
    for day in forecast_days:
        hours = day.get("hour")
        if not isinstance(hours, list):
            continue
        for hour in hours[:24]:
            if not isinstance(hour, dict):
                continue
            condition = hour.get("condition") if isinstance(hour.get("condition"), dict) else {}
            normalized.append(
                WeatherHourly(
                    time=str(hour.get("time") or "unknown"),
                    temperature=hour.get("temp_f" if imperial else "temp_c"),
                    temperature_unit="F" if imperial else "C",
                    precipitation_probability=hour.get("chance_of_rain"),
                    precipitation_probability_unit="%" if hour.get("chance_of_rain") is not None else None,
                    precipitation=hour.get("precip_in" if imperial else "precip_mm"),
                    precipitation_unit="inch" if imperial else "mm",
                    wind_speed=hour.get("wind_mph" if imperial else "wind_kph"),
                    wind_speed_unit="mph" if imperial else "km/h",
                    wind_direction=hour.get("wind_degree"),
                    wind_direction_unit="degrees",
                    humidity=hour.get("humidity"),
                    humidity_unit="%",
                    uv_index=hour.get("uv"),
                    weather_code=_int_or_none(condition.get("code")),
                    condition=_string_or_none(condition.get("text")),
                )
            )
    return normalized


def _normalize_weatherapi_alerts(payload: dict[str, Any]) -> list[WeatherAlert]:
    alerts_payload = payload.get("alerts")
    if not isinstance(alerts_payload, dict):
        return []
    alerts = alerts_payload.get("alert")
    if not isinstance(alerts, list):
        return []
    normalized = []
    for item in alerts:
        if not isinstance(item, dict):
            continue
        normalized.append(
            WeatherAlert(
                title=_string_or_none(item.get("headline") or item.get("event")) or "Weather alert",
                severity=_string_or_none(item.get("severity")),
                starts_at=_string_or_none(item.get("effective")),
                ends_at=_string_or_none(item.get("expires")),
                source=_string_or_none(item.get("source")),
                description=_string_or_none(item.get("desc") or item.get("instruction")),
            )
        )
    return normalized


def _nws_period_date(period: dict[str, Any]) -> str | None:
    start = _string_or_none(period.get("startTime"))
    if not start:
        return None
    return start.split("T", 1)[0]


def _nws_temperature_unit(value: Any) -> str | None:
    text = _string_or_none(value)
    if not text:
        return None
    return "F" if text.upper() == "F" else text


def _nws_probability(period: dict[str, Any]) -> float | int | None:
    probability = period.get("probabilityOfPrecipitation")
    if not isinstance(probability, dict):
        return None
    value = probability.get("value")
    return value if isinstance(value, (int, float)) else None


def _nws_wind_speed_max(period: dict[str, Any]) -> int | None:
    text = _string_or_none(period.get("windSpeed"))
    if not text:
        return None
    values = [int(match) for match in re.findall(r"\d+", text)]
    if not values:
        return None
    return max(values)


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


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
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
                    "provider": {"type": "string"},
                },
                "required": [],
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
                    "provider": {"type": "string"},
                },
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    "weather.alerts": {
        "type": "function",
        "function": {
            "name": "weather.alerts",
            "description": "Fetch active weather alerts for a user-provided location when supported by the configured provider.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "locale": {"type": "string"},
                    "provider": {"type": "string"},
                },
                "required": [],
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
