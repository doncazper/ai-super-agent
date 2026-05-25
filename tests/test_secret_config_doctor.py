from __future__ import annotations

import json
import subprocess

from agent.config.loader import load_capabilities_config
from agent.connectors.secret_doctor import gmail_doctor, gmail_scopes, secrets_doctor, telegram_doctor
from agent.ui.cli_commands import dispatch_cli
from agent.ui.connectors import connector_status, format_connectors_json


SERP_SECRET = "serp-" + "secret-value"
WEATHER_SECRET = "weather-" + "secret-value"
GMAIL_SECRET = "gmail-" + "secret-value"
TELEGRAM_SECRET = "telegram-" + "secret-value"


def test_all_secrets_redacted(tmp_path) -> None:
    env = {
        "SERPAPI_API_KEY": SERP_SECRET,
        "WEATHERAPI_API_KEY": WEATHER_SECRET,
        "GMAIL_USER": "user@example.com",
        "GMAIL_CLIENT_ID": "gmail-client-id",
        "GMAIL_CLIENT_SECRET": GMAIL_SECRET,
        "GMAIL_TOKEN_PATH": str(tmp_path / "token.json"),
        "TELEGRAM_BOT_TOKEN": TELEGRAM_SECRET,
        "TELEGRAM_DEFAULT_CHAT_ID": "12345",
    }

    report = secrets_doctor(project_root=tmp_path, environ=env)
    text = json.dumps(report)

    for secret in (SERP_SECRET, WEATHER_SECRET, GMAIL_SECRET, TELEGRAM_SECRET, "user@example.com"):
        assert secret not in text
    assert report["no_api_calls_made"] is True
    assert report["no_personal_data_reads"] is True


def test_missing_credentials_show_setup_hints(tmp_path) -> None:
    report = secrets_doctor(project_root=tmp_path, environ={})

    providers = {item["name"]: item for item in report["providers"]}
    assert providers["serpapi"]["configured"] is False
    assert "SERPAPI_API_KEY" in providers["serpapi"]["setup_hint"]
    assert providers["gmail"]["configured"] is False
    assert "Gmail OAuth" in providers["gmail"]["setup_hint"]


def test_env_tracked_warning_works(tmp_path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, stdout=subprocess.DEVNULL)
    (tmp_path / ".env").write_text("SERPAPI_" + "API_KEY=example\n", encoding="utf-8")
    subprocess.run(["git", "add", ".env"], cwd=tmp_path, check=True, stdout=subprocess.DEVNULL)

    report = secrets_doctor(project_root=tmp_path, environ={})

    assert any(warning["code"] == "env_tracked" for warning in report["warnings"])


def test_token_path_warning_works(tmp_path) -> None:
    token_path = tmp_path / "gmail-token.json"
    token_path.write_text("{}", encoding="utf-8")

    report = secrets_doctor(project_root=tmp_path, environ={"GMAIL_TOKEN_PATH": str(token_path)})

    assert any(warning["code"] == "token_path_inside_repo" for warning in report["warnings"])


def test_gmail_scope_warning_works(tmp_path) -> None:
    env = {
        "GMAIL_SCOPES": "https://www.googleapis.com/auth/gmail.metadata https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/gmail.send",
    }

    scopes = gmail_scopes(environ=env)
    doctor = gmail_doctor(project_root=tmp_path, environ=env)

    warning_codes = {warning["code"] for warning in scopes["warnings"]}
    assert "gmail_broad_scope" in warning_codes
    assert "gmail_send_scope" in warning_codes
    assert doctor["no_api_calls_made"] is True
    assert doctor["no_inbox_read"] is True
    assert doctor["no_email_sent"] is True
    assert doctor["send_capability"]["risk_level"] == "CRITICAL"
    assert doctor["send_capability"]["default_enabled"] is False


def test_telegram_doctor_warns_without_default_chat() -> None:
    report = telegram_doctor(
        environ={
            "TELEGRAM_BOT_TOKEN": TELEGRAM_SECRET,
            "TELEGRAM_ALLOWED_CHAT_IDS": "12345,67890",
        }
    )
    text = json.dumps(report)

    assert TELEGRAM_SECRET not in text
    assert report["no_api_calls_made"] is True
    assert report["no_chat_reads"] is True
    assert report["no_messages_sent"] is True
    assert any(warning["code"] == "telegram_default_chat_missing" for warning in report["warnings"])
    assert report["credential_status"]["metadata"]["allowed_chat_count"] == 2
    assert report["send_capability"]["risk_level"] == "CRITICAL"
    assert report["send_capability"]["default_enabled"] is False


def test_docs_tests_config_secret_scan_warning(tmp_path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    fake_secret = "real-looking-" + "secret-value"
    (docs / "sample.md").write_text("GMAIL_CLIENT_" + "SECRET=" + fake_secret + "\n", encoding="utf-8")

    report = secrets_doctor(project_root=tmp_path, environ={})

    assert any(warning["code"] == "possible_secret_in_repo_text" for warning in report["warnings"])
    assert fake_secret not in json.dumps(report)


def test_paid_provider_disabled_under_free_first(tmp_path) -> None:
    env = {"SERPAPI_API_KEY": SERP_SECRET, "PROVIDER_COST_MODE": "free_first", "ALLOW_PAID_APIS": "false"}

    report = secrets_doctor(project_root=tmp_path, environ=env)
    serpapi = {item["name"]: item for item in report["providers"]}["serpapi"]

    assert serpapi["configured"] is True
    assert serpapi["allowed"] is False
    assert serpapi["disabled_by_cost_policy"] is True
    assert report["cost_policy"]["paid_providers_default_disabled"] is True


def test_connector_status_does_not_reveal_secrets(monkeypatch) -> None:
    monkeypatch.setenv("SERPAPI_API_KEY", SERP_SECRET)
    monkeypatch.setenv("WEATHERAPI_API_KEY", WEATHER_SECRET)
    monkeypatch.setenv("GMAIL_CLIENT_SECRET", GMAIL_SECRET)
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TELEGRAM_SECRET)

    payload = {
        "serpapi": connector_status("serpapi"),
        "weatherapi": connector_status("weatherapi"),
        "gmail": connector_status("gmail"),
        "telegram": connector_status("telegram"),
    }
    text = format_connectors_json(payload)

    for secret in (SERP_SECRET, WEATHER_SECRET, GMAIL_SECRET, TELEGRAM_SECRET):
        assert secret not in text
    assert payload["serpapi"]["disabled_by_cost_policy"] is True


def test_secrets_cli_status_and_doctor(capsys, monkeypatch) -> None:
    monkeypatch.setenv("SERPAPI_API_KEY", SERP_SECRET)

    assert dispatch_cli(["secrets", "status"]) == 0
    status = json.loads(capsys.readouterr().out)
    assert status["no_api_calls_made"] is True
    assert "serpapi" in status["configured_providers"]

    assert dispatch_cli(["secrets", "doctor"]) == 0
    doctor = json.loads(capsys.readouterr().out)
    assert doctor["no_personal_data_reads"] is True
    assert SERP_SECRET not in json.dumps(doctor)


def test_gmail_and_telegram_cli_doctors(capsys, monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("GMAIL_CLIENT_SECRET", GMAIL_SECRET)
    monkeypatch.setenv("GMAIL_SCOPES", "https://mail.google.com/")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TELEGRAM_SECRET)
    monkeypatch.setenv("TELEGRAM_ALLOWED_CHAT_IDS", "12345")

    assert dispatch_cli(["gmail", "doctor"], project_root=tmp_path) == 0
    gmail_report = json.loads(capsys.readouterr().out)
    assert gmail_report["no_inbox_read"] is True
    assert gmail_report["send_capability"]["risk_level"] == "CRITICAL"
    assert GMAIL_SECRET not in json.dumps(gmail_report)

    assert dispatch_cli(["gmail", "scopes"], project_root=tmp_path) == 0
    scopes_report = json.loads(capsys.readouterr().out)
    assert any(warning["code"] == "gmail_send_scope" for warning in scopes_report["warnings"])

    assert dispatch_cli(["telegram", "doctor"], project_root=tmp_path) == 0
    telegram_report = json.loads(capsys.readouterr().out)
    assert telegram_report["no_messages_sent"] is True
    assert TELEGRAM_SECRET not in json.dumps(telegram_report)

    assert dispatch_cli(["telegram", "status"], project_root=tmp_path) == 0
    telegram_status = json.loads(capsys.readouterr().out)
    assert telegram_status["no_chat_reads"] is True
    assert telegram_status["send_capability"]["approval_reuse_allowed"] is False


def test_sends_and_personal_tools_remain_disabled_by_default() -> None:
    capabilities = load_capabilities_config()["tools"]

    for name in ("email.send", "email.send_approved", "messages.send", "messages.send_approved"):
        capability = capabilities[name]
        assert capability["risk_level"] == "CRITICAL"
        assert capability["default_enabled"] is False
        assert capability["approval_required"] == "per_action"
        assert capability["approval_reuse_allowed"] is False

    personal_connectors = {"calendar", "contacts", "email", "messages", "tasks"}
    for name, capability in capabilities.items():
        if capability.get("connector_name") in personal_connectors:
            assert capability["default_enabled"] is False, name
