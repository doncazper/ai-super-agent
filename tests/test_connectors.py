from __future__ import annotations

import json

from agent.ui.cli_commands import dispatch_cli
from agent.ui.connectors import connector_status, connectors_doctor, format_connectors_json


def test_weather_configured_status(monkeypatch) -> None:
    monkeypatch.setenv("WEATHER_PROVIDER", "open_meteo")
    monkeypatch.setenv("WEB_ACCESS_ENABLED", "true")
    monkeypatch.delenv("WEATHER_API_KEY", raising=False)

    status = connector_status("weather")

    assert status["name"] == "weather"
    assert status["configured"] is True
    assert status["enabled"] is True
    assert status["default_provider"] == "open_meteo"
    assert status["risk_level"] == "LOW"
    assert status["setup_hint"] == status["docs_setup_hint"]
    assert {item["name"] for item in status["capabilities"]} >= {
        "weather.status",
        "weather.current",
        "weather.forecast",
        "weather.alerts",
    }
    assert status["provider_status"]["requires_api_key"] is False
    assert status["provider_status"]["api_key_configured"] is False


def test_web_missing_provider_status(monkeypatch) -> None:
    monkeypatch.delenv("WEB_SEARCH_PROVIDER", raising=False)
    monkeypatch.delenv("BRAVE_SEARCH_API_KEY", raising=False)

    status = connector_status("web")

    assert status["name"] == "web"
    assert status["configured"] is False
    assert status["default_provider"] == "disabled"
    assert "capabilities" in status
    assert status["rate_limit_state"]["configured"] is True
    assert "BRAVE_SEARCH_API_KEY" in status["docs_setup_hint"]


def test_browser_url_workflow_status_does_not_require_profile_access() -> None:
    status = connector_status("browser")

    assert status["name"] == "browser"
    assert status["configured"] is True
    assert status["default_provider"] == "url_workflow"
    names = {item["name"] for item in status["capabilities"]}
    assert "browser.selected_tab" in names
    assert "browser.read_selected_tab" in names
    assert "history" in status["docs_setup_hint"]
    assert "cookies" in status["docs_setup_hint"]


def test_personal_connectors_disabled_by_default() -> None:
    for name in ("calendar", "contacts", "email", "messages"):
        status = connector_status(name)
        assert status["enabled"] is False
        assert status["risk_level"] in {"HIGH", "CRITICAL"}
        assert status["approval_required"] in {True, "per_action"}


def test_connector_status_redacts_secrets(monkeypatch) -> None:
    monkeypatch.setenv("WEB_SEARCH_PROVIDER", "brave")
    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "super-secret-search-key")
    monkeypatch.setenv("EMAIL_CONNECTOR", "imap")
    monkeypatch.setenv("IMAP_HOST", "imap.example.com")
    monkeypatch.setenv("IMAP_USERNAME", "sam@example.com")
    monkeypatch.setenv("IMAP_PASSWORD", "super-secret-imap-password")

    payload = {
        "web": connector_status("web"),
        "email": connector_status("email"),
    }
    text = format_connectors_json(payload)

    assert "super-secret-search-key" not in text
    assert "super-secret-imap-password" not in text


def test_connectors_doctor_does_not_access_personal_data(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("CALENDAR_CONNECTOR", "applescript")
    monkeypatch.setenv("CONTACTS_CONNECTOR", "applescript")
    monkeypatch.setenv("EMAIL_CONNECTOR", "imap")
    monkeypatch.setenv("MESSAGES_CONNECTOR", "future")
    audit_path = tmp_path / "audit.jsonl"

    report = connectors_doctor(audit_path=audit_path)

    assert report["status"] in {"ok", "warn"}
    assert not audit_path.exists()
    text = json.dumps(report)
    assert "~/Library/Messages" not in text
    assert "~/Library/Mail" not in text
    for connector in report["connectors"]:
        assert "capabilities" in connector
        assert "setup_hint" in connector


def test_connector_status_ignores_successful_dry_run_as_error(tmp_path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    audit_path.write_text(
        json.dumps(
            {
                "timestamp": "2026-05-22T00:00:00+00:00",
                "tool_name": "web.search",
                "policy_decision": "ALLOW",
                "result_summary": "Dry-run evaluated tool call.",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    status = connector_status("web", audit_path=audit_path)

    assert status["last_error"] is None


def test_connectors_cli_status_weather(monkeypatch, capsys) -> None:
    monkeypatch.setenv("WEATHER_PROVIDER", "open_meteo")

    exit_code = dispatch_cli(["connectors", "status", "weather"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["name"] == "weather"
    assert payload["configured"] is True


def test_connectors_cli_list(capsys) -> None:
    exit_code = dispatch_cli(["connectors", "list"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert [item["name"] for item in payload["connectors"]] == [
        "weather",
        "web",
        "browser",
        "calendar",
        "contacts",
        "email",
        "messages",
        "tasks",
    ]
