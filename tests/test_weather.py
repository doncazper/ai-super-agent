from __future__ import annotations

import json
import sqlite3

import httpx
import pytest

from agent.core.tool_broker import ToolBroker
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry
from agent.tools.weather.formatter import format_weather_answer
from agent.tools.weather.models import convert_temperature
from agent.tools.weather.provider import NWSProvider, OpenMeteoProvider, WeatherKitProvider, provider_from_env
from smart_agent import _run_weather_command


class StaticWeatherProvider:
    name = "static-weather"

    def is_configured(self) -> bool:
        return True

    def current_weather(self, location: str, units: str, locale: str | None = None) -> dict[str, object]:
        return {
            "location": f"Resolved {location}",
            "current": {
                "temperature": 72,
                "condition": f"clear:{units}:{locale}",
                "observed_at": "2026-05-22T12:00:00Z",
            },
        }

    def forecast(
        self,
        location: str,
        days: int,
        units: str,
        locale: str | None = None,
        include_hourly: bool = False,
    ) -> dict[str, object]:
        return {
            "location": f"Resolved {location}",
            "forecast": [
                {"date": f"2026-05-{22 + index:02d}", "high": 70 + index, "low": 50 + index}
                for index in range(days)
            ],
            "hourly": [{"time": "2026-05-22T12:00", "temperature": 72}] if include_hourly else None,
        }

    def alerts(self, location: str, locale: str | None = None) -> dict[str, object]:
        return {
            "status": "ok",
            "provider": self.name,
            "location": f"Resolved {location}",
            "trust_level": "UNTRUSTED_WEB",
            "retrieved_at": "2026-05-22T12:00:00Z",
            "alerts": [],
        }


class TimeoutWeatherProvider(StaticWeatherProvider):
    name = "timeout-weather"

    def current_weather(self, location: str, units: str, locale: str | None = None) -> dict[str, object]:
        raise TimeoutError("too slow")


class CountingWeatherProvider(StaticWeatherProvider):
    name = "counting-weather"

    def __init__(self) -> None:
        self.current_calls = 0
        self.forecast_calls = 0

    def current_weather(self, location: str, units: str, locale: str | None = None) -> dict[str, object]:
        self.current_calls += 1
        payload = super().current_weather(location, units, locale)
        payload["current"]["temperature"] = 70 + self.current_calls
        return payload

    def forecast(
        self,
        location: str,
        days: int,
        units: str,
        locale: str | None = None,
        include_hourly: bool = False,
    ) -> dict[str, object]:
        self.forecast_calls += 1
        return super().forecast(location, days, units, locale, include_hourly)


@pytest.fixture(autouse=True)
def isolate_weather_cache(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEATHER_CACHE_PATH", str(tmp_path / "weather_cache.json"))
    monkeypatch.setenv("WEATHER_PREFERENCES_PATH", str(tmp_path / "weather_preferences.json"))
    monkeypatch.delenv("WEATHER_CURRENT_CACHE_TTL_SECONDS", raising=False)
    monkeypatch.delenv("WEATHER_FORECAST_CACHE_TTL_SECONDS", raising=False)
    monkeypatch.delenv("WEATHER_CACHE_TTL_SECONDS", raising=False)
    monkeypatch.delenv("WEATHER_CACHE_ENABLED", raising=False)
    monkeypatch.delenv("WEATHER_DEFAULT_LOCATION", raising=False)
    monkeypatch.delenv("WEATHER_DEFAULT_LATITUDE", raising=False)
    monkeypatch.delenv("WEATHER_DEFAULT_LONGITUDE", raising=False)
    monkeypatch.delenv("WEATHER_UNITS", raising=False)
    monkeypatch.delenv("WEATHER_DEFAULT_UNITS", raising=False)
    monkeypatch.delenv("WEATHER_PROVIDER", raising=False)
    monkeypatch.delenv("WEATHERKIT_TEAM_ID", raising=False)
    monkeypatch.delenv("WEATHERKIT_SERVICE_ID", raising=False)
    monkeypatch.delenv("WEATHERKIT_KEY_ID", raising=False)
    monkeypatch.delenv("WEATHERKIT_PRIVATE_KEY_PATH", raising=False)


def weather_capabilities(rate_limit: int | None = None) -> dict[str, Capability]:
    metadata: dict[str, object] = {"requires_web_access": True}
    if rate_limit is not None:
        metadata["rate_limit"] = {"requests_per_minute": rate_limit}
    return {
        "weather.status": Capability("weather.status", RiskLevel.LOW),
        "weather.current": Capability("weather.current", RiskLevel.LOW, metadata=metadata),
        "weather.forecast": Capability("weather.forecast", RiskLevel.LOW, metadata=metadata),
        "weather.alerts": Capability("weather.alerts", RiskLevel.LOW, metadata=metadata),
        "weather.cache_clear": Capability("weather.cache_clear", RiskLevel.LOW),
    }


def call(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    return {
        "id": f"call_{tool_name}",
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments)},
    }


def make_broker(tmp_path, weather_provider=None, capabilities: dict[str, Capability] | None = None) -> ToolBroker:
    return ToolBroker(
        default_registry(project_root=tmp_path, weather_provider=weather_provider, memory_path=tmp_path / "memory.sqlite3"),
        PolicyEngine(capabilities or weather_capabilities()),
        AuditLogger(tmp_path / "audit.jsonl"),
        session_id="test-session",
        model="test-model",
        route="test",
    )


def test_weather_provider_explicitly_disabled_returns_clear_error(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEATHER_PROVIDER", "disabled")
    broker = make_broker(tmp_path)

    result = broker.execute(call("weather.current", {"location": "San Francisco"}))

    assert result.allowed is True
    payload = json.loads(result.content)
    assert payload["status"] == "error"
    assert payload["error"] == "weather provider is not configured"
    assert payload["configured"] is False
    assert payload["trust_level"] == "UNTRUSTED_WEB"


def test_weatherkit_not_configured_returns_clear_error(tmp_path) -> None:
    broker = make_broker(tmp_path, weather_provider=WeatherKitProvider())

    result = broker.execute(call("weather.current", {"location": "Phoenix, AZ"}))

    assert result.allowed is True
    payload = json.loads(result.content)
    assert payload["status"] == "error"
    assert payload["provider"] == "weatherkit"
    assert payload["configured"] is False
    assert "WEATHERKIT_TEAM_ID" in payload["error"]


def test_weatherkit_env_presence_check_works(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEATHERKIT_TEAM_ID", "TEAM123456")
    monkeypatch.setenv("WEATHERKIT_SERVICE_ID", "com.example.weather")
    monkeypatch.setenv("WEATHERKIT_KEY_ID", "KEY123456")
    monkeypatch.setenv("WEATHERKIT_PRIVATE_KEY_PATH", str(tmp_path / "AuthKey_KEY123456.p8"))

    provider = WeatherKitProvider()

    assert provider.is_configured() is True


def test_weatherkit_secrets_not_logged_or_returned(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEATHERKIT_TEAM_ID", "SECRETTEAM")
    monkeypatch.setenv("WEATHERKIT_SERVICE_ID", "com.secret.weather")
    monkeypatch.setenv("WEATHERKIT_KEY_ID", "SECRETKEY")
    monkeypatch.setenv("WEATHERKIT_PRIVATE_KEY_PATH", "/secret/AuthKey_SECRETKEY.p8")
    broker = make_broker(tmp_path, weather_provider=WeatherKitProvider())

    result = broker.execute(call("weather.status", {}))

    assert result.allowed is True
    content = result.content
    audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
    assert "SECRETTEAM" not in content
    assert "SECRETKEY" not in content
    assert "com.secret.weather" not in content
    assert "/secret/AuthKey_SECRETKEY.p8" not in content
    assert "SECRETTEAM" not in audit_text
    assert "SECRETKEY" not in audit_text


def test_weatherkit_status_reports_not_configured_without_secret_values(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEATHER_PROVIDER", "weatherkit")
    broker = make_broker(tmp_path)

    result = broker.execute(call("weather.status", {}))

    payload = json.loads(result.content)
    assert payload["provider"] == "weatherkit"
    assert payload["configured"] is False
    assert "WEATHERKIT_TEAM_ID" in payload["error"]
    assert "WEATHERKIT_PRIVATE_KEY_PATH" in payload["error"]


def test_weatherkit_provider_not_used_unless_selected(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEATHERKIT_TEAM_ID", "TEAM123456")
    monkeypatch.setenv("WEATHERKIT_SERVICE_ID", "com.example.weather")
    monkeypatch.setenv("WEATHERKIT_KEY_ID", "KEY123456")
    monkeypatch.setenv("WEATHERKIT_PRIVATE_KEY_PATH", str(tmp_path / "AuthKey_KEY123456.p8"))

    assert provider_from_env().name == "open_meteo"
    monkeypatch.setenv("WEATHER_PROVIDER", "weatherkit")
    assert provider_from_env().name == "weatherkit"


def test_weather_has_no_default_location_by_default(tmp_path) -> None:
    broker = make_broker(tmp_path, weather_provider=StaticWeatherProvider())

    result = broker.execute(call("weather.current", {}))

    assert result.allowed is True
    payload = json.loads(result.content)
    assert payload["status"] == "error"
    assert payload["error"] == "location is required"


def test_weather_default_location_used_when_configured_and_audited(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEATHER_DEFAULT_LOCATION", "Phoenix, AZ")
    broker = make_broker(tmp_path, weather_provider=StaticWeatherProvider())

    result = broker.execute(call("weather.current", {}))

    assert result.allowed is True
    payload = json.loads(result.content)
    assert payload["status"] == "ok"
    assert payload["location"] == "Resolved Phoenix, AZ"
    events = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert events[0]["result_summary"] == "weather cache miss; weather default location used from env:WEATHER_DEFAULT_LOCATION"
    assert events[0]["sanitized_args"] == {}
    assert "Phoenix" not in (tmp_path / "audit.jsonl").read_text(encoding="utf-8")


def test_weather_current_cli_uses_configured_default_location(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("WEATHER_DEFAULT_LOCATION", "Phoenix, AZ")
    broker = make_broker(tmp_path, weather_provider=StaticWeatherProvider())

    exit_code = _run_weather_command(["current", "--json"], broker)

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["location"] == "Resolved Phoenix, AZ"


def test_weather_units_preference_applied(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEATHER_UNITS", "imperial")
    broker = make_broker(tmp_path, weather_provider=StaticWeatherProvider())

    result = broker.execute(call("weather.current", {"location": "Phoenix, AZ"}))

    payload = json.loads(result.content)
    assert payload["status"] == "ok"
    assert payload["units"] == "imperial"
    assert payload["current"]["condition"] == "clear:imperial:None"


def test_weather_cache_can_be_disabled_by_preference(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEATHER_CACHE_ENABLED", "false")
    provider = CountingWeatherProvider()
    broker = make_broker(tmp_path, weather_provider=provider)

    first = broker.execute(call("weather.current", {"location": "Phoenix, AZ"}))
    second = broker.execute(call("weather.current", {"location": "Phoenix, AZ"}))

    assert first.allowed is True
    assert second.allowed is True
    assert provider.current_calls == 2
    assert json.loads(first.content)["cached"] is False
    assert json.loads(second.content)["cached"] is False
    assert not (tmp_path / "weather_cache.json").exists()
    events = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [event["result_summary"] for event in events] == ["weather cache disabled", "weather cache disabled"]


def test_weather_config_cli_set_show_and_clear_default(tmp_path, capsys) -> None:
    broker = make_broker(tmp_path, weather_provider=StaticWeatherProvider())

    set_code = _run_weather_command(["config", "set-default", "Phoenix, AZ"], broker)
    capsys.readouterr()
    show_code = _run_weather_command(["config", "show"], broker)
    show_payload = json.loads(capsys.readouterr().out)
    clear_code = _run_weather_command(["config", "clear-default"], broker)
    clear_payload = json.loads(capsys.readouterr().out)

    assert set_code == 0
    assert show_code == 0
    assert clear_code == 0
    assert show_payload["default_location"] == "Phoenix, AZ"
    assert show_payload["default_location_configured"] is True
    assert show_payload["stored_in_memory"] is False
    assert clear_payload["default_location_configured"] is False


def test_weather_default_location_does_not_write_memory(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEATHER_DEFAULT_LOCATION", "Phoenix, AZ")
    broker = make_broker(tmp_path, weather_provider=StaticWeatherProvider())

    result = broker.execute(call("weather.current", {}))

    assert result.allowed is True
    with sqlite3.connect(tmp_path / "memory.sqlite3") as conn:
        assert conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == 0


def test_open_meteo_is_default_no_key_provider(monkeypatch) -> None:
    monkeypatch.delenv("WEATHER_PROVIDER", raising=False)
    monkeypatch.delenv("WEATHER_API_KEY", raising=False)

    provider = OpenMeteoProvider()
    from agent.tools.weather.provider import provider_from_env, weather_provider_status

    env_provider = provider_from_env()
    status = weather_provider_status(provider)

    assert env_provider.name == "open_meteo"
    assert status["provider"] == "open_meteo"
    assert status["configured"] is True
    assert status["requires_api_key"] is False


def test_configured_provider_returns_normalized_current_weather(tmp_path) -> None:
    broker = make_broker(tmp_path, weather_provider=StaticWeatherProvider())

    result = broker.execute(call("weather.current", {"location": "San Francisco", "units": "imperial"}))

    assert result.allowed is True
    payload = json.loads(result.content)
    assert payload["status"] == "ok"
    assert payload["provider"] == "static-weather"
    assert payload["location"] == "Resolved San Francisco"
    assert payload["units"] == "imperial"
    assert payload["trust_level"] == "UNTRUSTED_WEB"
    assert payload["retrieved_at"]
    assert payload["current"]["temperature"] == 72


def test_configured_provider_returns_normalized_forecast_with_day_limit(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEATHER_MAX_FORECAST_DAYS", "2")
    broker = make_broker(tmp_path, weather_provider=StaticWeatherProvider())

    result = broker.execute(call("weather.forecast", {"location": "San Francisco", "days": 9}))

    assert result.allowed is True
    payload = json.loads(result.content)
    assert payload["status"] == "ok"
    assert payload["days"] == 2
    assert len(payload["forecast"]) == 2
    assert payload["trust_level"] == "UNTRUSTED_WEB"


def test_weather_access_disabled_denies_through_broker(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEB_ACCESS_ENABLED", "false")
    broker = make_broker(tmp_path, weather_provider=StaticWeatherProvider())

    result = broker.execute(call("weather.current", {"location": "San Francisco"}))

    assert result.allowed is False
    assert json.loads(result.content)["error"] == "web access disabled"


def test_weather_rate_limit_enforced(tmp_path) -> None:
    broker = make_broker(
        tmp_path,
        weather_provider=StaticWeatherProvider(),
        capabilities=weather_capabilities(rate_limit=1),
    )

    first = broker.execute(call("weather.current", {"location": "San Francisco"}))
    second = broker.execute(call("weather.current", {"location": "Oakland"}))

    assert first.allowed is True
    assert second.allowed is False
    assert json.loads(second.content)["error"] == "rate limit exceeded"
    events = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert events[-1]["result_summary"] == "Denied by policy: rate limit exceeded"


def test_weather_cache_first_request_hits_provider_second_uses_cache(tmp_path) -> None:
    provider = CountingWeatherProvider()
    broker = make_broker(tmp_path, weather_provider=provider)

    first = broker.execute(call("weather.current", {"location": "Phoenix, AZ"}))
    second = broker.execute(call("weather.current", {"location": "Phoenix, AZ"}))

    first_payload = json.loads(first.content)
    second_payload = json.loads(second.content)
    assert provider.current_calls == 1
    assert first_payload["cached"] is False
    assert second_payload["cached"] is True
    assert second_payload["cached_at"] == first_payload["cached_at"]
    assert second_payload["expires_at"] == first_payload["expires_at"]
    events = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [event["result_summary"] for event in events] == ["weather cache miss", "weather cache hit"]


def test_weather_expired_cache_refreshes(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEATHER_CURRENT_CACHE_TTL_SECONDS", "0")
    provider = CountingWeatherProvider()
    broker = make_broker(tmp_path, weather_provider=provider)

    first = broker.execute(call("weather.current", {"location": "Phoenix, AZ"}))
    second = broker.execute(call("weather.current", {"location": "Phoenix, AZ"}))

    assert provider.current_calls == 2
    assert json.loads(first.content)["cached"] is False
    assert json.loads(second.content)["cached"] is False
    events = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert events[-1]["result_summary"] == "weather cache expired refresh"


def test_weather_no_cache_bypasses_cache(tmp_path) -> None:
    provider = CountingWeatherProvider()
    broker = make_broker(tmp_path, weather_provider=provider)

    first = broker.execute(call("weather.current", {"location": "Phoenix, AZ"}))
    second = broker.execute(call("weather.current", {"location": "Phoenix, AZ", "no_cache": True}))
    third = broker.execute(call("weather.current", {"location": "Phoenix, AZ"}))

    assert provider.current_calls == 2
    assert json.loads(first.content)["cached"] is False
    assert json.loads(second.content)["cached"] is False
    assert json.loads(second.content)["cached_at"] is None
    assert json.loads(third.content)["cached"] is True
    events = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert events[1]["result_summary"] == "weather cache bypass"


def test_weather_no_cache_cli_bypasses_cache(tmp_path, capsys) -> None:
    provider = CountingWeatherProvider()
    broker = make_broker(tmp_path, weather_provider=provider)

    _run_weather_command(["current", "Phoenix, AZ"], broker)
    capsys.readouterr()
    exit_code = _run_weather_command(["current", "Phoenix, AZ", "--no-cache"], broker)

    assert exit_code == 0
    output = capsys.readouterr().out
    assert provider.current_calls == 2
    assert "Weather for Resolved Phoenix, AZ" in output
    assert "Cache: fresh provider result; expires unavailable" in output


def test_weather_cache_clear_works(tmp_path) -> None:
    provider = CountingWeatherProvider()
    broker = make_broker(tmp_path, weather_provider=provider)

    broker.execute(call("weather.current", {"location": "Phoenix, AZ"}))
    clear = broker.execute(call("weather.cache_clear", {}))
    after_clear = broker.execute(call("weather.current", {"location": "Phoenix, AZ"}))

    assert provider.current_calls == 2
    clear_payload = json.loads(clear.content)
    assert clear_payload["status"] == "ok"
    assert clear_payload["cleared_entries"] == 1
    assert json.loads(after_clear.content)["cached"] is False
    events = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert "weather cache cleared" in [event["result_summary"] for event in events]


def test_weather_cache_clear_cli_works(tmp_path, capsys) -> None:
    provider = CountingWeatherProvider()
    broker = make_broker(tmp_path, weather_provider=provider)
    broker.execute(call("weather.current", {"location": "Phoenix, AZ"}))

    exit_code = _run_weather_command(["cache", "clear"], broker)

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["cleared_entries"] == 1


def test_weather_cache_skips_precise_location_payloads(tmp_path) -> None:
    provider = CountingWeatherProvider()
    broker = make_broker(tmp_path, weather_provider=provider)

    first = broker.execute(call("weather.current", {"location": "123 Private Street"}))
    second = broker.execute(call("weather.current", {"location": "123 Private Street"}))

    assert provider.current_calls == 2
    assert json.loads(first.content)["cached"] is False
    assert json.loads(second.content)["cached"] is False
    assert not (tmp_path / "weather_cache.json").exists()
    events = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [event["result_summary"] for event in events] == [
        "weather cache skipped precise location",
        "weather cache skipped precise location",
    ]
    assert "123 Private Street" not in (tmp_path / "audit.jsonl").read_text(encoding="utf-8")


def test_weather_cache_skips_direct_coordinate_payloads(tmp_path) -> None:
    provider = CountingWeatherProvider()
    broker = make_broker(tmp_path, weather_provider=provider)

    result = broker.execute(call("weather.forecast", {"location": "33.4484,-112.0740"}))

    assert result.allowed is True
    assert provider.forecast_calls == 1
    assert json.loads(result.content)["cached"] is False
    assert not (tmp_path / "weather_cache.json").exists()


def test_weather_location_redacted_in_audit_and_no_history_persisted(tmp_path) -> None:
    location = "123 Private Street"
    broker = make_broker(tmp_path, weather_provider=StaticWeatherProvider())

    result = broker.execute(call("weather.current", {"location": location}))

    assert result.allowed is True
    audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
    event = json.loads(audit_text.splitlines()[0])
    assert event["sanitized_args"]["location"] == "[WEATHER_LOCATION_REDACTED]"
    assert event["network_domains"] == ["static-weather"]
    assert event["trust_level"] == "UNTRUSTED_WEB"
    assert location not in audit_text


def test_weather_provider_timeout_returns_structured_error(tmp_path) -> None:
    broker = make_broker(tmp_path, weather_provider=TimeoutWeatherProvider())

    result = broker.execute(call("weather.current", {"location": "San Francisco"}))

    assert result.allowed is True
    payload = json.loads(result.content)
    assert payload["status"] == "error"
    assert payload["error"] == "weather provider failed: TimeoutError"
    assert payload["configured"] is True


def test_unknown_weather_capability_denied(tmp_path) -> None:
    broker = make_broker(tmp_path, weather_provider=StaticWeatherProvider())

    result = broker.execute(call("weather.radar", {"location": "San Francisco"}))

    assert result.allowed is False
    assert json.loads(result.content)["error"] == "unknown tool denied"


def open_meteo_provider(handler) -> OpenMeteoProvider:
    transport = httpx.MockTransport(handler)
    return OpenMeteoProvider(client_factory=lambda timeout: httpx.Client(transport=transport, timeout=timeout))


def nws_provider(handler) -> NWSProvider:
    transport = httpx.MockTransport(handler)
    return NWSProvider(client_factory=lambda timeout: httpx.Client(transport=transport, timeout=timeout))


def geocoding_payload() -> dict[str, object]:
    return {
        "results": [
            {
                "name": "San Francisco",
                "admin1": "California",
                "country": "United States",
                "latitude": 37.7749,
                "longitude": -122.4194,
            }
        ]
    }


def nws_geocoding_payload(country_code: str = "US") -> dict[str, object]:
    country = "United States" if country_code == "US" else "France"
    return {
        "results": [
            {
                "name": "Los Angeles",
                "admin1": "California",
                "country": country,
                "country_code": country_code,
                "latitude": 34.0522,
                "longitude": -118.2437,
                "timezone": "America/Los_Angeles",
            }
        ]
    }


def nws_points_payload() -> dict[str, object]:
    return {
        "properties": {
            "forecast": "https://api.weather.gov/gridpoints/LOX/154,44/forecast",
            "forecastHourly": "https://api.weather.gov/gridpoints/LOX/154,44/forecast/hourly",
            "timeZone": "America/Los_Angeles",
            "relativeLocation": {"properties": {"city": "Los Angeles", "state": "CA"}},
        }
    }


def nws_forecast_payload() -> dict[str, object]:
    return {
        "properties": {
            "periods": [
                {
                    "name": "Today",
                    "startTime": "2026-05-22T06:00:00-07:00",
                    "endTime": "2026-05-22T18:00:00-07:00",
                    "isDaytime": True,
                    "temperature": 72,
                    "temperatureUnit": "F",
                    "windSpeed": "5 to 10 mph",
                    "windDirection": "SW",
                    "shortForecast": "Sunny",
                    "probabilityOfPrecipitation": {"value": 5, "unitCode": "wmoUnit:percent"},
                },
                {
                    "name": "Tonight",
                    "startTime": "2026-05-22T18:00:00-07:00",
                    "endTime": "2026-05-23T06:00:00-07:00",
                    "isDaytime": False,
                    "temperature": 58,
                    "temperatureUnit": "F",
                    "windSpeed": "5 mph",
                    "windDirection": "S",
                    "shortForecast": "Mostly Clear",
                    "probabilityOfPrecipitation": {"value": 10, "unitCode": "wmoUnit:percent"},
                },
            ]
        }
    }


def nws_hourly_payload() -> dict[str, object]:
    return {
        "properties": {
            "periods": [
                {
                    "startTime": "2026-05-22T12:00:00-07:00",
                    "temperature": 70,
                    "temperatureUnit": "F",
                    "windSpeed": "8 mph",
                    "windDirection": "SW",
                    "shortForecast": "Sunny",
                    "probabilityOfPrecipitation": {"value": 5, "unitCode": "wmoUnit:percent"},
                }
            ]
        }
    }


def nws_alerts_payload() -> dict[str, object]:
    return {
        "features": [
            {
                "properties": {
                    "event": "Heat Advisory",
                    "severity": "Moderate",
                    "onset": "2026-05-22T11:00:00-07:00",
                    "ends": "2026-05-22T20:00:00-07:00",
                    "senderName": "NWS Los Angeles/Oxnard",
                    "description": "Hot conditions expected.",
                }
            }
        ]
    }


def ambiguous_geocoding_payload() -> dict[str, object]:
    return {
        "results": [
            {
                "name": "Phoenix",
                "admin1": "Arizona",
                "country": "United States",
                "latitude": 33.4484,
                "longitude": -112.074,
                "timezone": "America/Phoenix",
            },
            {
                "name": "Phoenix",
                "admin1": "Oregon",
                "country": "United States",
                "latitude": 42.2754,
                "longitude": -122.8181,
                "timezone": "America/Los_Angeles",
            },
        ]
    }


def test_open_meteo_current_normalization_and_audit_domains(tmp_path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "geocoding-api.open-meteo.com":
            assert request.url.params["name"] == "San Francisco"
            assert request.url.params["count"] == "5"
            return httpx.Response(200, json=geocoding_payload())
        assert request.url.host == "api.open-meteo.com"
        assert "temperature_2m" in request.url.params["current"]
        return httpx.Response(
            200,
            json={
                "timezone": "America/Los_Angeles",
                "current_units": {
                    "temperature_2m": "F",
                    "apparent_temperature": "F",
                    "relative_humidity_2m": "%",
                    "precipitation": "inch",
                    "rain": "inch",
                    "snowfall": "inch",
                    "pressure_msl": "hPa",
                    "wind_speed_10m": "mp/h",
                    "wind_direction_10m": "deg",
                },
                "current": {
                    "time": "2026-05-22T12:00",
                    "temperature_2m": 65.3,
                    "apparent_temperature": 64.0,
                    "relative_humidity_2m": 72,
                    "precipitation": 0.0,
                    "rain": 0.0,
                    "snowfall": 0.0,
                    "weather_code": 1,
                    "pressure_msl": 1012.4,
                    "wind_speed_10m": 11.2,
                    "wind_direction_10m": 270,
                    "is_day": 1,
                },
            },
        )

    broker = make_broker(tmp_path, weather_provider=open_meteo_provider(handler))

    result = broker.execute(call("weather.current", {"location": "San Francisco", "units": "imperial"}))

    assert result.allowed is True
    payload = json.loads(result.content)
    assert payload["status"] == "ok"
    assert payload["provider"] == "open_meteo"
    assert payload["location"] == "San Francisco, California, United States"
    assert payload["coordinates"] == {"latitude": 37.7749, "longitude": -122.4194}
    assert payload["current"]["temperature"] == 65.3
    assert payload["current"]["temperature_unit"] == "F"
    assert payload["current"]["condition"] == "mainly clear"
    assert payload["current"]["rain"] == 0.0
    assert payload["current"]["snow"] == 0.0
    assert payload["current"]["humidity"] == 72
    assert payload["current"]["pressure"] == 1012.4
    assert "raw_provider_payload" not in payload
    events = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert events[0]["network_domains"] == ["geocoding-api.open-meteo.com", "api.open-meteo.com"]


def test_open_meteo_forecast_normalization(tmp_path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "geocoding-api.open-meteo.com":
            return httpx.Response(200, json=geocoding_payload())
        assert request.url.params["forecast_days"] == "2"
        return httpx.Response(
            200,
            json={
                "timezone": "America/Los_Angeles",
                "daily_units": {
                    "temperature_2m_max": "C",
                    "temperature_2m_min": "C",
                    "precipitation_sum": "mm",
                    "precipitation_probability_max": "%",
                    "rain_sum": "mm",
                    "snowfall_sum": "cm",
                    "wind_speed_10m_max": "km/h",
                    "wind_gusts_10m_max": "km/h",
                    "wind_direction_10m_dominant": "deg",
                    "uv_index_max": "",
                },
                "daily": {
                    "time": ["2026-05-22", "2026-05-23"],
                    "weather_code": [1, 2],
                    "temperature_2m_max": [19.0, 20.0],
                    "temperature_2m_min": [11.0, 12.0],
                    "precipitation_sum": [0.0, 1.2],
                    "precipitation_probability_max": [10, 40],
                    "rain_sum": [0.0, 1.1],
                    "snowfall_sum": [0.0, 0.0],
                    "wind_speed_10m_max": [18.0, 20.0],
                    "wind_gusts_10m_max": [28.0, 30.0],
                    "wind_direction_10m_dominant": [270, 280],
                    "uv_index_max": [6.4, 7.0],
                },
            },
        )

    broker = make_broker(tmp_path, weather_provider=open_meteo_provider(handler))

    result = broker.execute(call("weather.forecast", {"location": "San Francisco", "days": 2}))

    assert result.allowed is True
    payload = json.loads(result.content)
    assert payload["status"] == "ok"
    assert payload["forecast"][0]["date"] == "2026-05-22"
    assert payload["forecast"][0]["condition"] == "mainly clear"
    assert payload["forecast"][0]["temperature_max"] == 19.0
    assert payload["forecast"][0]["temperature_max_unit"] == "C"
    assert payload["forecast"][1]["precipitation_probability_max"] == 40
    assert payload["forecast"][1]["rain_sum"] == 1.1
    assert payload["forecast"][0]["snow_sum"] == 0.0
    assert payload["forecast"][0]["wind_direction_dominant"] == 270
    assert payload["forecast"][0]["uv_index_max"] == 6.4


def test_open_meteo_ambiguous_geocode_returns_disambiguation(tmp_path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "geocoding-api.open-meteo.com":
            return httpx.Response(200, json=ambiguous_geocoding_payload())
        return httpx.Response(
            200,
            json={
                "timezone": "America/Phoenix",
                "current_units": {"temperature_2m": "C"},
                "current": {"time": "2026-05-22T12:00", "temperature_2m": 40.0, "weather_code": 0},
            },
        )

    broker = make_broker(tmp_path, weather_provider=open_meteo_provider(handler))

    result = broker.execute(call("weather.current", {"location": "Phoenix"}))

    payload = json.loads(result.content)
    assert payload["status"] == "ok"
    assert payload["location"] == "Phoenix, Arizona, United States"
    assert payload["disambiguation"]["selected"]["admin1"] == "Arizona"
    assert len(payload["disambiguation"]["alternatives"]) == 2


def test_open_meteo_direct_lat_lon_bypasses_geocoding(tmp_path) -> None:
    hosts: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        hosts.append(str(request.url.host))
        assert request.url.host == "api.open-meteo.com"
        assert request.url.params["latitude"] == "33.4484"
        assert request.url.params["longitude"] == "-112.074"
        return httpx.Response(
            200,
            json={
                "timezone": "America/Phoenix",
                "current_units": {"temperature_2m": "C"},
                "current": {"time": "2026-05-22T12:00", "temperature_2m": 40.0, "weather_code": 0},
            },
        )

    broker = make_broker(tmp_path, weather_provider=open_meteo_provider(handler))

    result = broker.execute(call("weather.current", {"location": "33.4484,-112.0740"}))

    payload = json.loads(result.content)
    assert payload["status"] == "ok"
    assert payload["location"] == "33.448400,-112.074000"
    assert payload["coordinates"] == {"latitude": 33.4484, "longitude": -112.074}
    assert hosts == ["api.open-meteo.com"]


def test_open_meteo_hourly_forecast_optional(tmp_path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "geocoding-api.open-meteo.com":
            return httpx.Response(200, json=geocoding_payload())
        assert "hourly" in request.url.params
        return httpx.Response(
            200,
            json={
                "timezone": "America/Los_Angeles",
                "daily_units": {"temperature_2m_max": "C", "temperature_2m_min": "C"},
                "daily": {
                    "time": ["2026-05-22"],
                    "weather_code": [0],
                    "temperature_2m_max": [20.0],
                    "temperature_2m_min": [12.0],
                },
                "hourly_units": {
                    "temperature_2m": "C",
                    "precipitation_probability": "%",
                    "precipitation": "mm",
                    "rain": "mm",
                    "snowfall": "cm",
                    "wind_speed_10m": "km/h",
                    "wind_direction_10m": "deg",
                    "relative_humidity_2m": "%",
                    "pressure_msl": "hPa",
                },
                "hourly": {
                    "time": ["2026-05-22T00:00"],
                    "temperature_2m": [12.0],
                    "precipitation_probability": [20],
                    "precipitation": [0.2],
                    "rain": [0.2],
                    "snowfall": [0.0],
                    "weather_code": [61],
                    "wind_speed_10m": [10.0],
                    "wind_direction_10m": [180],
                    "relative_humidity_2m": [82],
                    "pressure_msl": [1011],
                    "uv_index": [0.0],
                },
            },
        )

    broker = make_broker(tmp_path, weather_provider=open_meteo_provider(handler))

    result = broker.execute(call("weather.forecast", {"location": "San Francisco", "days": 1, "include_hourly": True}))

    payload = json.loads(result.content)
    assert payload["status"] == "ok"
    assert payload["hourly"][0]["condition"] == "slight rain"
    assert payload["hourly"][0]["precipitation_probability"] == 20
    assert payload["hourly"][0]["snow"] == 0.0
    assert payload["hourly"][0]["humidity"] == 82
    assert payload["hourly"][0]["pressure"] == 1011
    assert payload["hourly"][0]["uv_index"] == 0.0


def test_open_meteo_raw_payload_hidden_by_default_and_debug_opt_in(tmp_path, monkeypatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "geocoding-api.open-meteo.com":
            return httpx.Response(200, json=geocoding_payload())
        return httpx.Response(
            200,
            json={
                "timezone": "America/Los_Angeles",
                "current_units": {"temperature_2m": "C"},
                "current": {"time": "2026-05-22T12:00", "temperature_2m": 20.0, "weather_code": 0},
            },
        )

    broker = make_broker(tmp_path, weather_provider=open_meteo_provider(handler))

    normal = broker.execute(call("weather.current", {"location": "San Francisco"}))
    assert "raw_provider_payload" not in json.loads(normal.content)

    monkeypatch.setenv("DEBUG", "true")
    debug = broker.execute(call("weather.current", {"location": "San Francisco", "no_cache": True}))
    payload = json.loads(debug.content)
    assert payload["raw_provider_payload"]["forecast"]["timezone"] == "America/Los_Angeles"


def test_weather_temperature_conversion_helper() -> None:
    assert convert_temperature(0, "C", "F") == 32.0
    assert convert_temperature(212, "F", "C") == 100.0
    assert convert_temperature(None, "C", "F") is None


def test_open_meteo_geocoding_failure_returns_structured_error(tmp_path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"results": []})

    broker = make_broker(tmp_path, weather_provider=open_meteo_provider(handler))

    result = broker.execute(call("weather.current", {"location": "Nowhere"}))

    assert result.allowed is True
    payload = json.loads(result.content)
    assert payload["status"] == "error"
    assert payload["error"] == "location not found"


def test_open_meteo_timeout_returns_structured_error(tmp_path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("too slow", request=request)

    broker = make_broker(tmp_path, weather_provider=open_meteo_provider(handler))

    result = broker.execute(call("weather.current", {"location": "San Francisco"}))

    assert result.allowed is True
    assert json.loads(result.content)["error"] == "weather provider timed out"


def test_open_meteo_api_error_returns_structured_error(tmp_path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"error": True, "reason": "invalid latitude"})

    broker = make_broker(tmp_path, weather_provider=open_meteo_provider(handler))

    result = broker.execute(call("weather.current", {"location": "San Francisco"}))

    assert result.allowed is True
    payload = json.loads(result.content)
    assert payload["status"] == "error"
    assert payload["error"] == "invalid latitude"


def test_open_meteo_malformed_response_returns_structured_error(tmp_path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "geocoding-api.open-meteo.com":
            return httpx.Response(200, json=geocoding_payload())
        return httpx.Response(200, json={"current": "not-an-object"})

    broker = make_broker(tmp_path, weather_provider=open_meteo_provider(handler))

    result = broker.execute(call("weather.current", {"location": "San Francisco"}))

    assert result.allowed is True
    assert json.loads(result.content)["error"] == "weather provider returned malformed current weather"


def test_nws_current_maps_us_location_to_points_and_hourly_calls(tmp_path) -> None:
    urls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        urls.append(str(request.url))
        if request.url.host == "geocoding-api.open-meteo.com":
            assert request.url.params["name"] == "Los Angeles, CA"
            return httpx.Response(200, json=nws_geocoding_payload())
        if request.url.path.startswith("/points/"):
            assert request.url.path == "/points/34.0522,-118.2437"
            return httpx.Response(200, json=nws_points_payload())
        if request.url.path.endswith("/forecast/hourly"):
            return httpx.Response(200, json=nws_hourly_payload())
        return httpx.Response(404, json={})

    broker = make_broker(tmp_path, weather_provider=nws_provider(handler))

    result = broker.execute(call("weather.current", {"location": "Los Angeles, CA", "provider": "nws"}))

    payload = json.loads(result.content)
    assert result.allowed is True
    assert payload["status"] == "ok"
    assert payload["provider"] == "nws"
    assert payload["location"] == "Los Angeles, CA, United States"
    assert payload["current"]["temperature"] == 70
    assert payload["current"]["condition"] == "Sunny"
    assert payload["current"]["wind_speed"] == 8
    assert any("geocoding-api.open-meteo.com" in url for url in urls)
    assert any("api.weather.gov/points" in url for url in urls)
    assert any("forecast/hourly" in url for url in urls)


def test_nws_non_us_location_returns_unsupported(tmp_path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=nws_geocoding_payload(country_code="FR"))

    broker = make_broker(tmp_path, weather_provider=nws_provider(handler))

    result = broker.execute(call("weather.current", {"location": "Paris, France", "provider": "nws"}))

    payload = json.loads(result.content)
    assert result.allowed is True
    assert payload["status"] == "error"
    assert payload["provider"] == "nws"
    assert payload["error"] == "unsupported location: NWS supports U.S. locations only"


def test_nws_forecast_normalized(tmp_path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "geocoding-api.open-meteo.com":
            return httpx.Response(200, json=nws_geocoding_payload())
        if request.url.path.startswith("/points/"):
            return httpx.Response(200, json=nws_points_payload())
        if request.url.path.endswith("/forecast/hourly"):
            return httpx.Response(200, json=nws_hourly_payload())
        if request.url.path.endswith("/forecast"):
            return httpx.Response(200, json=nws_forecast_payload())
        return httpx.Response(404, json={})

    broker = make_broker(tmp_path, weather_provider=nws_provider(handler))

    result = broker.execute(
        call("weather.forecast", {"location": "Los Angeles, CA", "provider": "nws", "days": 1, "include_hourly": True})
    )

    payload = json.loads(result.content)
    assert result.allowed is True
    assert payload["status"] == "ok"
    assert payload["provider"] == "nws"
    assert payload["units"] == "imperial"
    assert payload["forecast"][0]["date"] == "2026-05-22"
    assert payload["forecast"][0]["temperature_max"] == 72
    assert payload["forecast"][0]["temperature_min"] == 58
    assert payload["forecast"][0]["precipitation_probability_max"] == 10
    assert payload["forecast"][0]["wind_speed_max"] == 10
    assert payload["hourly"][0]["precipitation_probability"] == 5


def test_nws_alerts_normalized_and_cli(tmp_path, capsys) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "geocoding-api.open-meteo.com":
            return httpx.Response(200, json=nws_geocoding_payload())
        if request.url.path.startswith("/points/"):
            return httpx.Response(200, json=nws_points_payload())
        if request.url.path == "/alerts/active":
            assert request.url.params["point"] == "34.0522,-118.2437"
            return httpx.Response(200, json=nws_alerts_payload())
        return httpx.Response(404, json={})

    broker = make_broker(tmp_path, weather_provider=nws_provider(handler))

    exit_code = _run_weather_command(["alerts", "Los Angeles, CA", "--provider", "nws"], broker)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Weather alerts for Los Angeles, CA, United States" in output
    assert "Heat Advisory (Moderate; 2026-05-22T11:00:00-07:00 to 2026-05-22T20:00:00-07:00)" in output
    events = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert events[0]["tool_name"] == "weather.alerts"
    assert events[0]["network_domains"] == ["geocoding-api.open-meteo.com", "api.weather.gov"]


def test_nws_timeout_returns_retryable_structured_error(tmp_path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "geocoding-api.open-meteo.com":
            return httpx.Response(200, json=nws_geocoding_payload())
        raise httpx.TimeoutException("too slow", request=request)

    broker = make_broker(tmp_path, weather_provider=nws_provider(handler))

    result = broker.execute(call("weather.current", {"location": "Los Angeles, CA", "provider": "nws"}))

    payload = json.loads(result.content)
    assert result.allowed is True
    assert payload["status"] == "error"
    assert payload["retryable"] is True
    assert payload["error"] == "retryable weather provider error: NWS request timed out"


def test_nws_missing_grid_data_handled_gracefully(tmp_path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "geocoding-api.open-meteo.com":
            return httpx.Response(200, json=nws_geocoding_payload())
        if request.url.path.startswith("/points/"):
            return httpx.Response(200, json={"properties": {"timeZone": "America/Los_Angeles"}})
        return httpx.Response(404, json={})

    broker = make_broker(tmp_path, weather_provider=nws_provider(handler))

    result = broker.execute(call("weather.forecast", {"location": "Los Angeles, CA", "provider": "nws"}))

    payload = json.loads(result.content)
    assert result.allowed is True
    assert payload["status"] == "error"
    assert payload["error"] == "missing NWS grid data for daily forecast"


def test_weather_doctor_defaults_to_open_meteo_when_no_provider_configured(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.delenv("WEATHER_PROVIDER", raising=False)
    broker = make_broker(tmp_path)

    exit_code = _run_weather_command(["doctor"], broker)

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["provider"] == "open_meteo"
    assert payload["configured"] is True
    assert payload["error"] is None
    assert payload["capabilities"]["weather.current"]["decision"] == "ALLOW"
    events = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert events[0]["tool_name"] == "weather.status"


def test_weather_doctor_with_mocked_provider_configured(tmp_path, capsys) -> None:
    broker = make_broker(tmp_path, weather_provider=StaticWeatherProvider())

    exit_code = _run_weather_command(["doctor"], broker)

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["provider"] == "static-weather"
    assert payload["configured"] is True
    assert payload["status"] == "ok"


def test_weather_doctor_reports_unsupported_provider_and_missing_api_key(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("WEATHER_PROVIDER", "weatherapi")
    monkeypatch.delenv("WEATHER_API_KEY", raising=False)
    broker = make_broker(tmp_path)

    exit_code = _run_weather_command(["doctor"], broker)

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["provider"] == "unsupported:weatherapi"
    assert payload["configured"] is False
    assert "not supported" in payload["error"]
    assert "WEATHER_API_KEY is not set" in payload["error"]


def test_weather_smoke_success_using_mocked_provider(tmp_path, capsys) -> None:
    broker = make_broker(tmp_path, weather_provider=StaticWeatherProvider())

    exit_code = _run_weather_command(["smoke", "Phoenix, AZ", "--days", "3"], broker)

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["provider"] == "static-weather"
    assert payload["configured"] is True
    assert [check["name"] for check in payload["checks"]] == ["weather.current", "weather.forecast"]
    assert payload["current"]["status"] == "ok"
    assert payload["forecast"]["status"] == "ok"
    events = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [event["tool_name"] for event in events] == ["weather.status", "weather.current", "weather.forecast"]


def test_weather_current_cli_success_using_mocked_provider(tmp_path, capsys) -> None:
    broker = make_broker(tmp_path, weather_provider=StaticWeatherProvider())

    exit_code = _run_weather_command(["current", "Phoenix, AZ"], broker)

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Weather for Resolved Phoenix, AZ" in output
    assert "Current: 72C, clear:metric:None" in output
    assert "Source: static-weather; retrieved_at" in output


def test_weather_forecast_cli_success_using_mocked_provider(tmp_path, capsys) -> None:
    broker = make_broker(tmp_path, weather_provider=StaticWeatherProvider())

    exit_code = _run_weather_command(["forecast", "Phoenix, AZ", "--days", "3"], broker)

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Weather forecast for Resolved Phoenix, AZ" in output
    assert "Daily forecast: 2026-05-22 to 2026-05-24" in output
    assert "Source: static-weather; retrieved_at" in output


def test_weather_cli_json_option_preserves_structured_output(tmp_path, capsys) -> None:
    broker = make_broker(tmp_path, weather_provider=StaticWeatherProvider())

    exit_code = _run_weather_command(["current", "Phoenix, AZ", "--json"], broker)

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert payload["provider"] == "static-weather"
    assert payload["location"] == "Resolved Phoenix, AZ"


def test_weather_formatter_recommends_umbrella_from_precipitation_data() -> None:
    text = format_weather_answer(
        {
            "status": "ok",
            "provider": "test-weather",
            "location": "Phoenix",
            "units": "imperial",
            "retrieved_at": "2026-05-22T12:00:00Z",
            "forecast": [
                {
                    "date": "2026-05-22",
                    "temperature_max": 80,
                    "temperature_min": 60,
                    "condition": "rain",
                    "precipitation_probability_max": 70,
                    "precipitation_probability_max_unit": "%",
                    "rain_sum": 0.2,
                    "rain_sum_unit": "inch",
                }
            ],
        },
        mode="forecast",
    )

    assert "Umbrella: bring an umbrella" in text
    assert "70%" in text


def test_weather_formatter_does_not_invent_missing_rain_chance() -> None:
    text = format_weather_answer(
        {
            "status": "ok",
            "provider": "test-weather",
            "location": "Phoenix",
            "units": "imperial",
            "retrieved_at": "2026-05-22T12:00:00Z",
            "current": {"temperature": 75, "condition": "clear"},
        },
        mode="current",
    )

    assert "rain data unavailable; no rain chance invented" in text
    assert "50%" not in text


def test_weather_formatter_displays_cache_metadata() -> None:
    text = format_weather_answer(
        {
            "status": "ok",
            "provider": "test-weather",
            "location": "Phoenix",
            "units": "imperial",
            "retrieved_at": "2026-05-22T12:00:00Z",
            "cached": True,
            "cached_at": "2026-05-22T11:50:00Z",
            "expires_at": "2026-05-22T12:05:00Z",
            "forecast": [{"date": "2026-05-22", "condition": "clear"}],
        },
        mode="forecast",
    )

    assert "Cache: cached result from 2026-05-22T11:50:00Z; expires 2026-05-22T12:05:00Z" in text
    assert "Cached weather may be stale" in text


def test_weather_formatter_reports_unsupported_alerts() -> None:
    text = format_weather_answer(
        {
            "status": "ok",
            "provider": "test-weather",
            "location": "Phoenix",
            "units": "imperial",
            "retrieved_at": "2026-05-22T12:00:00Z",
            "current": {"temperature": 75, "condition": "clear", "rain": 0},
        },
        mode="current",
    )

    assert "Alerts: unavailable; this provider/result does not include alerts" in text


def test_bad_location_handled(tmp_path) -> None:
    broker = make_broker(tmp_path, weather_provider=StaticWeatherProvider())

    result = broker.execute(call("weather.current", {"location": ""}))

    assert result.allowed is True
    payload = json.loads(result.content)
    assert payload["status"] == "error"
    assert payload["error"] == "location is required"


def test_weather_does_not_store_memory_by_default(tmp_path) -> None:
    broker = make_broker(tmp_path, weather_provider=StaticWeatherProvider())

    result = broker.execute(call("weather.current", {"location": "Phoenix, AZ"}))

    assert result.allowed is True
    with sqlite3.connect(tmp_path / "memory.sqlite3") as conn:
        count = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
    assert count == 0
