from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class UnitSystem(str, Enum):
    METRIC = "metric"
    IMPERIAL = "imperial"


class WeatherCondition(str, Enum):
    CLEAR = "clear sky"
    MAINLY_CLEAR = "mainly clear"
    PARTLY_CLOUDY = "partly cloudy"
    OVERCAST = "overcast"
    FOG = "fog"
    DRIZZLE = "drizzle"
    FREEZING_DRIZZLE = "freezing drizzle"
    RAIN = "rain"
    FREEZING_RAIN = "freezing rain"
    SNOW = "snow"
    RAIN_SHOWERS = "rain showers"
    SNOW_SHOWERS = "snow showers"
    THUNDERSTORM = "thunderstorm"
    UNKNOWN = "unknown"


class WeatherProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class WeatherLocation:
    name: str
    latitude: float | None = None
    longitude: float | None = None
    timezone: str | None = None
    admin1: str | None = None
    country: str | None = None
    disambiguation: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = _compact(
            {
                "name": self.name,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "timezone": self.timezone,
                "admin1": self.admin1,
                "country": self.country,
                "disambiguation": self.disambiguation,
            }
        )
        if self.latitude is not None and self.longitude is not None:
            payload["coordinates"] = {"latitude": self.latitude, "longitude": self.longitude}
        return payload


@dataclass(frozen=True)
class WeatherCurrent:
    time: str | None = None
    temperature: float | int | None = None
    temperature_unit: str | None = None
    apparent_temperature: float | int | None = None
    apparent_temperature_unit: str | None = None
    precipitation: float | int | None = None
    precipitation_unit: str | None = None
    rain: float | int | None = None
    rain_unit: str | None = None
    snow: float | int | None = None
    snow_unit: str | None = None
    wind_speed: float | int | None = None
    wind_speed_unit: str | None = None
    wind_direction: float | int | None = None
    wind_direction_unit: str | None = None
    humidity: float | int | None = None
    humidity_unit: str | None = None
    pressure: float | int | None = None
    pressure_unit: str | None = None
    uv_index: float | int | None = None
    weather_code: int | None = None
    condition: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return _compact(self.__dict__)


@dataclass(frozen=True)
class WeatherHourly:
    time: str
    temperature: float | int | None = None
    temperature_unit: str | None = None
    precipitation_probability: float | int | None = None
    precipitation_probability_unit: str | None = None
    precipitation: float | int | None = None
    precipitation_unit: str | None = None
    rain: float | int | None = None
    rain_unit: str | None = None
    snow: float | int | None = None
    snow_unit: str | None = None
    wind_speed: float | int | None = None
    wind_speed_unit: str | None = None
    wind_direction: float | int | None = None
    wind_direction_unit: str | None = None
    humidity: float | int | None = None
    humidity_unit: str | None = None
    pressure: float | int | None = None
    pressure_unit: str | None = None
    uv_index: float | int | None = None
    weather_code: int | None = None
    condition: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return _compact(self.__dict__)


@dataclass(frozen=True)
class WeatherDaily:
    date: str
    weather_code: int | None = None
    condition: str | None = None
    temperature_max: float | int | None = None
    temperature_max_unit: str | None = None
    temperature_min: float | int | None = None
    temperature_min_unit: str | None = None
    precipitation_sum: float | int | None = None
    precipitation_sum_unit: str | None = None
    precipitation_probability_max: float | int | None = None
    precipitation_probability_max_unit: str | None = None
    rain_sum: float | int | None = None
    rain_sum_unit: str | None = None
    snow_sum: float | int | None = None
    snow_sum_unit: str | None = None
    wind_speed_max: float | int | None = None
    wind_speed_max_unit: str | None = None
    wind_gusts_max: float | int | None = None
    wind_gusts_max_unit: str | None = None
    wind_direction_dominant: float | int | None = None
    wind_direction_dominant_unit: str | None = None
    uv_index_max: float | int | None = None

    def to_dict(self) -> dict[str, Any]:
        return _compact(self.__dict__)


@dataclass(frozen=True)
class WeatherAlert:
    title: str
    severity: str | None = None
    starts_at: str | None = None
    ends_at: str | None = None
    source: str | None = None
    description: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return _compact(self.__dict__)


@dataclass(frozen=True)
class WeatherResult:
    status: str
    provider: str
    units: UnitSystem
    retrieved_at: str
    location: WeatherLocation | None = None
    current: WeatherCurrent | None = None
    hourly: list[WeatherHourly] = field(default_factory=list)
    daily: list[WeatherDaily] = field(default_factory=list)
    alerts: list[WeatherAlert] = field(default_factory=list)
    timezone: str | None = None
    provider_timestamp: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    raw_provider_payload: dict[str, Any] | None = None

    def to_dict(self, *, include_raw: bool = False) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self.status,
            "provider": self.provider,
            "units": self.units.value,
            "retrieved_at": self.retrieved_at,
            "timezone": self.timezone,
            "provider_timestamp": self.provider_timestamp,
            "location": self.location.name if self.location else None,
            "location_details": self.location.to_dict() if self.location else None,
            "coordinates": (
                {"latitude": self.location.latitude, "longitude": self.location.longitude}
                if self.location and self.location.latitude is not None and self.location.longitude is not None
                else None
            ),
            "disambiguation": self.location.disambiguation if self.location else None,
            "current": self.current.to_dict() if self.current else None,
            "forecast": [item.to_dict() for item in self.daily],
            "daily": [item.to_dict() for item in self.daily],
            "hourly": [item.to_dict() for item in self.hourly] if self.hourly else None,
            "alerts": [item.to_dict() for item in self.alerts] if self.alerts else None,
            "provider_metadata": self.metadata or None,
        }
        if include_raw and self.raw_provider_payload is not None:
            payload["raw_provider_payload"] = self.raw_provider_payload
        return _compact(payload)


def normalize_unit_system(value: str | UnitSystem | None) -> UnitSystem:
    if isinstance(value, UnitSystem):
        return value
    normalized = (value or UnitSystem.METRIC.value).strip().lower()
    if normalized == UnitSystem.IMPERIAL.value:
        return UnitSystem.IMPERIAL
    return UnitSystem.METRIC


def convert_temperature(value: float | int | None, from_unit: str, to_unit: str) -> float | int | None:
    if value is None:
        return None
    source = from_unit.strip().upper()
    target = to_unit.strip().upper()
    if source == target:
        return value
    if source in {"C", "CELSIUS"} and target in {"F", "FAHRENHEIT"}:
        return round((float(value) * 9 / 5) + 32, 2)
    if source in {"F", "FAHRENHEIT"} and target in {"C", "CELSIUS"}:
        return round((float(value) - 32) * 5 / 9, 2)
    raise WeatherProviderError(f"unsupported temperature conversion: {from_unit} to {to_unit}")


def condition_from_weather_code(code: Any) -> str | None:
    try:
        normalized = int(code)
    except (TypeError, ValueError):
        return None
    return OPEN_METEO_CONDITION_LABELS.get(normalized, f"unknown weather code {normalized}")


def _compact(value: dict[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in value.items() if item is not None}


OPEN_METEO_CONDITION_LABELS = {
    0: WeatherCondition.CLEAR.value,
    1: WeatherCondition.MAINLY_CLEAR.value,
    2: WeatherCondition.PARTLY_CLOUDY.value,
    3: WeatherCondition.OVERCAST.value,
    45: WeatherCondition.FOG.value,
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    56: "light freezing drizzle",
    57: "dense freezing drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    66: "light freezing rain",
    67: "heavy freezing rain",
    71: "slight snow fall",
    73: "moderate snow fall",
    75: "heavy snow fall",
    77: "snow grains",
    80: "slight rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    85: "slight snow showers",
    86: "heavy snow showers",
    95: WeatherCondition.THUNDERSTORM.value,
    96: "thunderstorm with slight hail",
    99: "thunderstorm with heavy hail",
}
