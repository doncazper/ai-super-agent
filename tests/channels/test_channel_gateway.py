from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent.channels.errors import ChannelDisabledError, ChannelSecurityError, UnknownChannelError
from agent.channels.gateway import ChannelGateway
from agent.channels.registry import ChannelRegistry
from agent.channels.security import redact_metadata
from agent.safety.validation import validate_startup_policy
from agent.ui.cli_commands import dispatch_cli
from agent.ui.command_registry import get_command, validate_command_registry_docs


ROOT = Path(__file__).resolve().parents[2]


def _run_cli(argv: list[str], capsys, monkeypatch, tmp_path: Path) -> tuple[int, dict]:
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))
    code = dispatch_cli(argv, project_root=ROOT)
    captured = capsys.readouterr()
    assert captured.err == ""
    return int(code), json.loads(captured.out)


def test_channel_registry_loads() -> None:
    registry = ChannelRegistry()

    channels = registry.list_channels()
    channel_ids = {channel.channel_id for channel in channels}

    assert "cli" in channel_ids
    assert "telegram" in channel_ids
    assert "mock" in channel_ids
    assert len(channels) == 10


def test_unknown_channel_denied() -> None:
    registry = ChannelRegistry()

    with pytest.raises(UnknownChannelError):
        registry.get("unknown_channel")


def test_mock_channel_submits_safe_request() -> None:
    gateway = ChannelGateway()

    submission = gateway.submit_request(
        channel_id="mock",
        user_ref="fixture-user",
        session_id="session-1",
        message_text="hello",
        correlation_id="audit-1",
        metadata={"telegram_token": "secret-token-value", "safe": "ok"},
    )

    payload = submission.to_dict()
    assert payload["status"] == "submitted"
    assert payload["route_target"] == "orchestrator_runtime"
    assert payload["direct_tool_execution_allowed"] is False
    assert payload["channel_approval_allowed"] is False
    assert payload["personal_data_accessed"] is False
    assert payload["background_persistence_started"] is False
    assert payload["request"]["trust_level"] == "UNTRUSTED_MESSAGE"
    assert payload["request"]["metadata_redacted"]["telegram_token"] == "[REDACTED]"
    assert payload["audit_correlation_id"] == "audit-1"


def test_disabled_remote_channel_rejected() -> None:
    gateway = ChannelGateway()

    with pytest.raises(ChannelDisabledError):
        gateway.submit_request(
            channel_id="telegram",
            user_ref="remote-user",
            session_id="session-1",
            message_text="hello",
            correlation_id="audit-1",
        )


def test_gateway_cannot_execute_tools_or_approve_actions() -> None:
    gateway = ChannelGateway()

    with pytest.raises(ChannelSecurityError, match="cannot execute tools directly"):
        gateway.execute_tool("time.get_current_time", {})
    with pytest.raises(ChannelSecurityError, match="cannot approve"):
        gateway.approve_action("action-1")


def test_correlation_id_required() -> None:
    gateway = ChannelGateway()

    with pytest.raises(ChannelSecurityError, match="correlation id"):
        gateway.submit_request(
            channel_id="mock",
            user_ref="fixture-user",
            session_id="session-1",
            message_text="hello",
            correlation_id="",
        )


def test_secrets_redacted_recursively() -> None:
    payload = redact_metadata(
        {
            "nested": {"api_key": "abc123", "Authorization": "Bearer token"},
            "safe": ["ok", {"refresh_token": "secret"}],
        }
    )

    assert payload["nested"]["api_key"] == "[REDACTED]"
    assert payload["nested"]["Authorization"] == "[REDACTED]"
    assert payload["safe"][1]["refresh_token"] == "[REDACTED]"


def test_channel_cli_list_and_status_are_safe(capsys, monkeypatch, tmp_path: Path) -> None:
    list_code, list_payload = _run_cli(["channels", "list"], capsys, monkeypatch, tmp_path)
    status_code, status_payload = _run_cli(["channels", "status"], capsys, monkeypatch, tmp_path)

    assert list_code == 0
    assert status_code == 0
    assert list_payload["remote_channels_enabled_by_default"] is False
    assert list_payload["direct_tool_execution_supported"] is False
    assert status_payload["send_capable_channels"] == []
    assert status_payload["personal_data_accessed"] is False
    assert status_payload["background_persistence_started"] is False


def test_channel_cli_show_known_and_unknown(capsys, monkeypatch, tmp_path: Path) -> None:
    code, payload = _run_cli(["channels", "show", "telegram"], capsys, monkeypatch, tmp_path)

    assert code == 0
    assert payload["channel"]["channel_id"] == "telegram"
    assert payload["channel"]["default_enabled"] is False
    assert payload["channel"]["remote"] is True

    unknown_code = dispatch_cli(["channels", "show", "unknown"], project_root=ROOT)
    captured = capsys.readouterr()
    assert int(unknown_code) == 2
    assert "unknown channel" in captured.out


def test_channel_capabilities_and_command_registry_validate() -> None:
    validate_startup_policy(ROOT / "config/capabilities.yaml")
    report = validate_command_registry_docs(ROOT)

    assert report["status"] == "ok"
    for command_id in ("CMD-CHANNELS-001", "CMD-CHANNELS-002", "CMD-CHANNELS-003"):
        record = get_command(command_id)
        assert record is not None
        assert record.status == "active"
        assert record.risk_level == "SAFE"
