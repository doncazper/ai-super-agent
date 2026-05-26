from __future__ import annotations

import json
from pathlib import Path

from agent.channels.mobile import mobile_pairing_status, mobile_status
from agent.channels.telegram import telegram_access_status
from agent.connectors.secret_doctor import telegram_doctor, telegram_status
from agent.safety.validation import validate_startup_policy
from agent.ui.cli_commands import dispatch_cli
from agent.ui.command_registry import get_command, validate_command_registry_docs


ROOT = Path(__file__).resolve().parents[2]
TELEGRAM_SECRET = "telegram-" + "secret-value"


def _run_cli(argv: list[str], capsys, monkeypatch, tmp_path: Path) -> tuple[int, dict]:
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))
    code = dispatch_cli(argv, project_root=ROOT)
    captured = capsys.readouterr()
    assert captured.err == ""
    return int(code), json.loads(captured.out)


def test_missing_token_setup_hint() -> None:
    report = telegram_access_status({})

    assert report["enabled"] is False
    assert report["token_present"] is False
    assert report["no_network_calls_made"] is True
    assert any(warning["code"] == "telegram_token_missing" for warning in report["warnings"])


def test_token_redacted_and_allowlist_required() -> None:
    env = {"TELEGRAM_ENABLED": "true", "TELEGRAM_BOT_TOKEN": TELEGRAM_SECRET}

    report = telegram_access_status(env)
    text = json.dumps(report)

    assert TELEGRAM_SECRET not in text
    assert report["token_present"] is True
    assert report["allowed_chat_ids_configured"] is False
    assert report["future_send_ready"] is False
    assert report["send_enabled_now"] is False


def test_telegram_disabled_send_polling_and_webhook_by_default() -> None:
    report = telegram_status(environ={})

    assert report["enabled"] is False
    assert report["allow_send"] is False
    assert report["allow_polling"] is False
    assert report["allow_webhook"] is False
    assert report["polling_started"] is False
    assert report["webhook_server_started"] is False
    assert report["no_background_service"] is True
    assert report["no_messages_sent"] is True


def test_allowed_chat_ids_required_before_future_send_ready() -> None:
    without_allowlist = telegram_access_status(
        {
            "TELEGRAM_ENABLED": "true",
            "TELEGRAM_BOT_TOKEN": TELEGRAM_SECRET,
            "TELEGRAM_ALLOW_SEND": "true",
        }
    )
    with_allowlist = telegram_access_status(
        {
            "TELEGRAM_ENABLED": "true",
            "TELEGRAM_BOT_TOKEN": TELEGRAM_SECRET,
            "TELEGRAM_ALLOWED_CHAT_IDS": "12345,67890",
            "TELEGRAM_ALLOW_SEND": "true",
        }
    )

    assert without_allowlist["future_send_ready"] is False
    assert with_allowlist["future_send_ready"] is True
    assert with_allowlist["send_enabled_now"] is False
    assert with_allowlist["allowed_chat_count"] == 2


def test_telegram_doctor_reports_no_api_or_message_access() -> None:
    report = telegram_doctor(environ={"TELEGRAM_BOT_TOKEN": TELEGRAM_SECRET})
    text = json.dumps(report)

    assert TELEGRAM_SECRET not in text
    assert report["no_api_calls_made"] is True
    assert report["no_chat_reads"] is True
    assert report["no_messages_sent"] is True
    assert report["polling_started"] is False
    assert report["webhook_server_started"] is False


def test_mobile_disabled_by_default() -> None:
    report = mobile_status({})
    pairing = mobile_pairing_status({})

    assert report["enabled"] is False
    assert report["mobile_approvals_enabled"] is False
    assert report["paired"] is False
    assert report["approval_manager_required"] is True
    assert report["frontend_cannot_self_approve"] is True
    assert report["no_network_calls_made"] is True
    assert pairing["status"] == "unpaired"


def test_telegram_and_mobile_cli_commands_are_brokered_and_safe(capsys, monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TELEGRAM_SECRET)

    telegram_code, telegram_payload = _run_cli(["telegram", "status"], capsys, monkeypatch, tmp_path)
    mobile_code, mobile_payload = _run_cli(["mobile", "status"], capsys, monkeypatch, tmp_path)
    pairing_code, pairing_payload = _run_cli(["mobile", "pairing-status"], capsys, monkeypatch, tmp_path)

    assert telegram_code == 0
    assert mobile_code == 0
    assert pairing_code == 0
    assert TELEGRAM_SECRET not in json.dumps(telegram_payload)
    assert telegram_payload["no_api_calls_made"] is True
    assert telegram_payload["no_messages_sent"] is True
    assert mobile_payload["no_personal_data_accessed"] is True
    assert pairing_payload["approval_manager_required"] is True


def test_telegram_mobile_capabilities_and_command_registry_validate() -> None:
    validate_startup_policy(ROOT / "config/capabilities.yaml")
    report = validate_command_registry_docs(ROOT)

    assert report["status"] == "ok"
    for command_id in ("CMD-TELEGRAM-001", "CMD-TELEGRAM-002", "CMD-MOBILE-001", "CMD-MOBILE-002"):
        record = get_command(command_id)
        assert record is not None
        assert record.status == "active"
        assert record.risk_level == "SAFE"
