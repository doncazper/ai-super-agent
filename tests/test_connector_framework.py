from __future__ import annotations

import json

import pytest

from agent.connectors.base import ConnectorConfiguration, ConnectorDefinition
from agent.connectors.errors import UnknownConnectorError
from agent.connectors.health import connectors_health_report
from agent.connectors.registry import default_connector_registry
from agent.connectors.status import build_connector_status, format_status_json
from agent.core.tool_broker import ToolBroker
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry


class StaticWeatherProvider:
    name = "static-weather"

    def is_configured(self) -> bool:
        return True

    def current_weather(self, location: str, units: str, locale: str | None = None) -> dict[str, object]:
        return {
            "status": "ok",
            "provider": self.name,
            "location": location,
            "current": {"temperature": 72},
            "trust_level": "UNTRUSTED_WEB",
        }

    def forecast(
        self,
        location: str,
        days: int,
        units: str,
        locale: str | None = None,
        include_hourly: bool = False,
    ) -> dict[str, object]:
        return {"status": "ok", "provider": self.name, "daily": []}

    def alerts(self, location: str, locale: str | None = None) -> dict[str, object]:
        return {"status": "ok", "provider": self.name, "alerts": []}


def call(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    return {
        "id": f"call_{tool_name}",
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments)},
    }


def weather_capabilities() -> dict[str, Capability]:
    return {
        "weather.status": Capability("weather.status", RiskLevel.LOW),
        "weather.current": Capability("weather.current", RiskLevel.LOW, metadata={"requires_web_access": True}),
        "weather.forecast": Capability("weather.forecast", RiskLevel.LOW, metadata={"requires_web_access": True}),
        "weather.alerts": Capability("weather.alerts", RiskLevel.LOW, metadata={"requires_web_access": True}),
        "weather.cache_clear": Capability("weather.cache_clear", RiskLevel.LOW),
    }


def test_connector_registry_loads() -> None:
    registry = default_connector_registry()

    assert registry.names() == ["weather", "web", "browser", "calendar", "contacts", "email", "messages", "tasks"]
    assert registry.get("weather") is not None


def test_unknown_connector_handled_cleanly() -> None:
    registry = default_connector_registry()

    with pytest.raises(UnknownConnectorError, match="unknown connector: notes"):
        registry.status("notes")


def test_connector_status_redacts_secret_metadata() -> None:
    definition = ConnectorDefinition(
        name="sample",
        capability_prefixes=("sample.",),
        configuration_probe=lambda env: ConnectorConfiguration(
            configured=True,
            provider_name="fixture",
            setup_hint="Set SAMPLE_API_KEY.",
            metadata={"api_key": "real-secret", "nested": {"password": "also-secret"}},
        ),
    )
    config = {
        "tools": {
            "sample.read": {
                "risk_level": "LOW",
                "default_enabled": True,
                "approval_required": False,
            }
        }
    }

    payload = build_connector_status(definition, config, environ={}).to_dict()
    text = format_status_json(payload)

    assert "real-secret" not in text
    assert "also-secret" not in text
    assert "[REDACTED]" in text


def test_health_checks_do_not_access_personal_data() -> None:
    def unsafe_health(env):
        raise AssertionError("personal-data health probe should not run")

    definition = ConnectorDefinition(
        name="calendar",
        capability_prefixes=("calendar.",),
        configuration_probe=lambda env: ConnectorConfiguration(False, "disabled", "setup"),
        health_probe=unsafe_health,
        personal_data=True,
        health_accesses_personal_data=True,
    )
    registry = default_connector_registry().__class__([definition])
    report = connectors_health_report(
        {"tools": {"calendar.read_date_range": {"risk_level": "HIGH", "default_enabled": False, "approval_required": True}}},
        registry=registry,
        environ={},
    )

    assert report["connectors"][0]["name"] == "calendar"
    assert "health" not in report["connectors"][0]


def test_disabled_connector_reports_disabled(monkeypatch) -> None:
    monkeypatch.setenv("WEB_SEARCH_PROVIDER", "disabled")
    monkeypatch.delenv("BRAVE_SEARCH_API_KEY", raising=False)

    status = default_connector_registry().status("web")

    assert status["configured"] is False
    assert status["enabled"] is True
    assert status["default_provider"] == "disabled"
    assert status["status"] == "not_configured"


def test_missing_provider_returns_setup_hint(monkeypatch) -> None:
    monkeypatch.setenv("WEB_SEARCH_PROVIDER", "unknown-provider")
    monkeypatch.delenv("BRAVE_SEARCH_API_KEY", raising=False)

    status = default_connector_registry().status("web")

    assert status["configured"] is False
    assert status["default_provider"] == "unknown-provider"
    assert "not supported" in status["docs_setup_hint"]


def test_existing_weather_connector_still_executes_through_toolbroker(tmp_path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    broker = ToolBroker(
        default_registry(project_root=tmp_path, weather_provider=StaticWeatherProvider(), memory_path=tmp_path / "memory.sqlite3"),
        PolicyEngine(weather_capabilities()),
        AuditLogger(audit_path),
        session_id="connector-framework",
        model="test-model",
        route="test",
    )

    result = broker.execute(call("weather.current", {"location": "Phoenix, AZ"}))

    assert result.allowed is True
    assert json.loads(result.content)["provider"] == "static-weather"
    event = json.loads(audit_path.read_text(encoding="utf-8").splitlines()[0])
    assert event["tool_name"] == "weather.current"
    assert event["policy_decision"] == "ALLOW"
