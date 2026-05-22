from __future__ import annotations

import json
import sqlite3

import httpx

from agent.core.tool_broker import ToolBroker
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry
from agent.tools.weather.provider import OpenMeteoProvider
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

    def forecast(self, location: str, days: int, units: str, locale: str | None = None) -> dict[str, object]:
        return {
            "location": f"Resolved {location}",
            "forecast": [
                {"date": f"2026-05-{22 + index:02d}", "high": 70 + index, "low": 50 + index}
                for index in range(days)
            ],
        }


class TimeoutWeatherProvider(StaticWeatherProvider):
    name = "timeout-weather"

    def current_weather(self, location: str, units: str, locale: str | None = None) -> dict[str, object]:
        raise TimeoutError("too slow")


def weather_capabilities(rate_limit: int | None = None) -> dict[str, Capability]:
    metadata: dict[str, object] = {"requires_web_access": True}
    if rate_limit is not None:
        metadata["rate_limit"] = {"requests_per_minute": rate_limit}
    return {
        "weather.status": Capability("weather.status", RiskLevel.LOW),
        "weather.current": Capability("weather.current", RiskLevel.LOW, metadata=metadata),
        "weather.forecast": Capability("weather.forecast", RiskLevel.LOW, metadata=metadata),
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


def test_weather_provider_missing_returns_clear_error(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("WEATHER_PROVIDER", raising=False)
    broker = make_broker(tmp_path)

    result = broker.execute(call("weather.current", {"location": "San Francisco"}))

    assert result.allowed is True
    payload = json.loads(result.content)
    assert payload["status"] == "error"
    assert payload["error"] == "weather provider is not configured"
    assert payload["configured"] is False
    assert payload["trust_level"] == "UNTRUSTED_WEB"


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

    result = broker.execute(call("weather.alerts", {"location": "San Francisco"}))

    assert result.allowed is False
    assert json.loads(result.content)["error"] == "unknown tool denied"


def open_meteo_provider(handler) -> OpenMeteoProvider:
    transport = httpx.MockTransport(handler)
    return OpenMeteoProvider(client_factory=lambda timeout: httpx.Client(transport=transport, timeout=timeout))


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


def test_open_meteo_current_normalization_and_audit_domains(tmp_path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "geocoding-api.open-meteo.com":
            assert request.url.params["name"] == "San Francisco"
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
                    "wind_speed_10m": "mp/h",
                    "wind_direction_10m": "deg",
                },
                "current": {
                    "time": "2026-05-22T12:00",
                    "temperature_2m": 65.3,
                    "apparent_temperature": 64.0,
                    "relative_humidity_2m": 72,
                    "precipitation": 0.0,
                    "weather_code": 1,
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
    assert payload["provider"] == "open-meteo"
    assert payload["location"] == "San Francisco, California, United States"
    assert payload["current"]["temperature"] == 65.3
    assert payload["current"]["temperature_unit"] == "F"
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
                    "wind_speed_10m_max": "km/h",
                },
                "daily": {
                    "time": ["2026-05-22", "2026-05-23"],
                    "weather_code": [1, 2],
                    "temperature_2m_max": [19.0, 20.0],
                    "temperature_2m_min": [11.0, 12.0],
                    "precipitation_sum": [0.0, 1.2],
                    "wind_speed_10m_max": [18.0, 20.0],
                },
            },
        )

    broker = make_broker(tmp_path, weather_provider=open_meteo_provider(handler))

    result = broker.execute(call("weather.forecast", {"location": "San Francisco", "days": 2}))

    assert result.allowed is True
    payload = json.loads(result.content)
    assert payload["status"] == "ok"
    assert payload["forecast"][0]["date"] == "2026-05-22"
    assert payload["forecast"][0]["temperature_max"] == 19.0
    assert payload["forecast"][0]["temperature_max_unit"] == "C"


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


def test_open_meteo_malformed_response_returns_structured_error(tmp_path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "geocoding-api.open-meteo.com":
            return httpx.Response(200, json=geocoding_payload())
        return httpx.Response(200, json={"current": "not-an-object"})

    broker = make_broker(tmp_path, weather_provider=open_meteo_provider(handler))

    result = broker.execute(call("weather.current", {"location": "San Francisco"}))

    assert result.allowed is True
    assert json.loads(result.content)["error"] == "weather provider returned malformed current weather"


def test_weather_doctor_with_no_provider_configured(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.delenv("WEATHER_PROVIDER", raising=False)
    broker = make_broker(tmp_path)

    exit_code = _run_weather_command(["doctor"], broker)

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["provider"] == "disabled"
    assert payload["configured"] is False
    assert payload["error"] == "weather provider is not configured"
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
