from __future__ import annotations

from typing import Any


def format_weather_answer(payload: dict[str, Any], *, mode: str = "auto") -> str:
    """Format structured weather payloads for direct CLI display only."""
    if payload.get("status") != "ok":
        return _format_error(payload)
    if mode == "current" or (mode == "auto" and isinstance(payload.get("current"), dict)):
        return _format_current(payload)
    if mode == "forecast" or (mode == "auto" and isinstance(payload.get("forecast"), list)):
        return _format_forecast(payload)
    return _format_error({**payload, "error": "weather data unavailable"})


def _format_current(payload: dict[str, Any]) -> str:
    current = _mapping(payload.get("current"))
    lines = [
        f"Weather for {_value(payload.get('location'))}",
        f"Current: {_current_summary(current, payload)}",
        f"Umbrella: {_umbrella_recommendation(payload)}",
        f"Clothing: {_clothing_recommendation(current, payload)}",
        _alerts_summary(payload),
        _cache_summary(payload),
        _uncertainty_note(payload),
        _source_note(payload),
    ]
    return "\n".join(line for line in lines if line)


def _format_forecast(payload: dict[str, Any]) -> str:
    forecast = payload.get("forecast")
    days = forecast if isinstance(forecast, list) else []
    lines = [
        f"Weather forecast for {_value(payload.get('location'))}",
        f"Daily forecast: {_forecast_span(days)}",
    ]
    if days:
        for day in days[:7]:
            if isinstance(day, dict):
                lines.append(f"- {_daily_summary(day, payload)}")
    else:
        lines.append("- unavailable")
    lines.extend(
        [
            f"Umbrella: {_umbrella_recommendation(payload)}",
            _alerts_summary(payload),
            _cache_summary(payload),
            _uncertainty_note(payload),
            _source_note(payload),
        ]
    )
    return "\n".join(line for line in lines if line)


def _format_error(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Weather unavailable",
            f"Provider: {_value(payload.get('provider'))}",
            f"Error: {_value(payload.get('error'))}",
        ]
    )


def _current_summary(current: dict[str, Any], payload: dict[str, Any]) -> str:
    temperature = _number_with_unit(
        current.get("temperature"),
        current.get("temperature_unit") or _temperature_unit(payload.get("units")),
    )
    apparent = _number_with_unit(
        current.get("apparent_temperature"),
        current.get("apparent_temperature_unit") or _temperature_unit(payload.get("units")),
    )
    condition = _value(current.get("condition"))
    wind = _number_with_unit(current.get("wind_speed"), current.get("wind_speed_unit"))
    pieces = [f"{temperature}, {condition}"]
    if apparent != "unavailable":
        pieces.append(f"feels like {apparent}")
    if wind != "unavailable":
        pieces.append(f"wind {wind}")
    return "; ".join(pieces)


def _daily_summary(day: dict[str, Any], payload: dict[str, Any]) -> str:
    unit = _temperature_unit(payload.get("units"))
    high = _number_with_unit(day.get("temperature_max") or day.get("high"), day.get("temperature_max_unit") or unit)
    low = _number_with_unit(day.get("temperature_min") or day.get("low"), day.get("temperature_min_unit") or unit)
    condition = _value(day.get("condition"))
    rain = _rain_summary(day)
    wind = _number_with_unit(day.get("wind_speed_max"), day.get("wind_speed_max_unit"))
    pieces = [
        f"{_value(day.get('date'))}: high {high}, low {low}, {condition}",
        f"rain {rain}",
    ]
    if wind != "unavailable":
        pieces.append(f"wind up to {wind}")
    return "; ".join(pieces)


def _umbrella_recommendation(payload: dict[str, Any]) -> str:
    values = _precipitation_signals(payload)
    if not values:
        return "rain data unavailable; no rain chance invented"
    if any(value >= 50 for value in values["probabilities"]):
        return "bring an umbrella; precipitation probability is elevated"
    if any(value > 0 for value in values["amounts"]):
        return "bring an umbrella; measurable precipitation is reported"
    return "probably not needed based on available precipitation data"


def _clothing_recommendation(current: dict[str, Any], payload: dict[str, Any]) -> str:
    temperature = _to_float(current.get("apparent_temperature") or current.get("temperature"))
    if temperature is None:
        return "temperature data unavailable"
    units = str(payload.get("units") or "").lower()
    fahrenheit = temperature if units == "imperial" else (temperature * 9 / 5) + 32
    if fahrenheit >= 90:
        return "light, breathable clothing; consider sun protection and water"
    if fahrenheit >= 75:
        return "light clothing should be comfortable"
    if fahrenheit >= 60:
        return "a light layer may be useful"
    if fahrenheit >= 45:
        return "wear a jacket or warmer layer"
    return "dress warmly with a coat or insulated layer"


def _alerts_summary(payload: dict[str, Any]) -> str:
    alerts = payload.get("alerts")
    if not isinstance(alerts, list):
        return "Alerts: unavailable; this provider/result does not include alerts"
    if not alerts:
        return "Alerts: no active alerts reported by provider"
    summaries = []
    for alert in alerts[:3]:
        if isinstance(alert, dict):
            title = _value(alert.get("title"))
            severity = _value(alert.get("severity"))
            timing = " to ".join(part for part in [_string(alert.get("starts_at")), _string(alert.get("ends_at"))] if part)
            summaries.append(f"{title} ({severity}; {timing or 'timing unavailable'})")
    return "Alerts: " + ("; ".join(summaries) if summaries else "unavailable")


def _cache_summary(payload: dict[str, Any]) -> str:
    if payload.get("cached") is True:
        return (
            "Cache: cached result from "
            f"{_value(payload.get('cached_at'))}; expires {_value(payload.get('expires_at'))}. "
            "Cached weather may be stale; use --no-cache for a fresh provider call."
        )
    if "cached" in payload:
        return f"Cache: fresh provider result; expires {_value(payload.get('expires_at'))}"
    return ""


def _uncertainty_note(payload: dict[str, Any]) -> str:
    note = "Uncertainty: weather can change; use provider data as a cautious estimate"
    if payload.get("cached") is True:
        note += ", especially because this result came from cache"
    return note


def _source_note(payload: dict[str, Any]) -> str:
    return f"Source: {_value(payload.get('provider'))}; retrieved_at {_value(payload.get('retrieved_at'))}"


def _forecast_span(days: list[Any]) -> str:
    if not days:
        return "unavailable"
    first = days[0].get("date") if isinstance(days[0], dict) else None
    last = days[-1].get("date") if isinstance(days[-1], dict) else None
    if first and last and first != last:
        return f"{first} to {last}"
    return _value(first or last)


def _rain_summary(day: dict[str, Any]) -> str:
    probability = day.get("precipitation_probability_max")
    amount = day.get("rain_sum")
    if amount is None:
        amount = day.get("precipitation_sum")
    pieces = []
    if probability is not None:
        pieces.append(_number_with_unit(probability, day.get("precipitation_probability_max_unit") or "%"))
    if amount is not None:
        pieces.append(_number_with_unit(amount, day.get("rain_sum_unit") or day.get("precipitation_sum_unit")))
    return ", ".join(pieces) if pieces else "unavailable"


def _precipitation_signals(payload: dict[str, Any]) -> dict[str, list[float]] | None:
    probabilities: list[float] = []
    amounts: list[float] = []
    current = _mapping(payload.get("current"))
    for key in ("rain", "precipitation", "snow"):
        value = _to_float(current.get(key))
        if value is not None:
            amounts.append(value)
    forecast = payload.get("forecast")
    if isinstance(forecast, list):
        for day in forecast:
            if not isinstance(day, dict):
                continue
            probability = _to_float(day.get("precipitation_probability_max"))
            if probability is not None:
                probabilities.append(probability)
            for key in ("rain_sum", "precipitation_sum", "snow_sum"):
                amount = _to_float(day.get(key))
                if amount is not None:
                    amounts.append(amount)
    if not probabilities and not amounts:
        return None
    return {"probabilities": probabilities, "amounts": amounts}


def _number_with_unit(value: Any, unit: Any = None) -> str:
    if value is None:
        return "unavailable"
    suffix = _string(unit)
    return f"{value}{suffix or ''}"


def _temperature_unit(units: Any) -> str:
    return "F" if str(units).lower() == "imperial" else "C"


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _value(value: Any) -> str:
    text = _string(value)
    return text if text else "unavailable"


def _string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _to_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None
