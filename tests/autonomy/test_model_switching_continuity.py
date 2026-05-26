from __future__ import annotations

from agent.autonomy.model_switching import build_model_switch_record, model_switch_payload
from agent.autonomy.session_continuity import (
    clear_continuity,
    continuity_status,
    export_redacted_continuity,
    redact_context_summary,
)
from agent.brain.config import BrainRuntimeConfig
from agent.brain.mock_provider import MockBrainProvider
from agent.brain.registry import BrainProviderRegistration, BrainProviderRegistry, make_mock_registration
from agent.ui import cli_commands
from agent.ui.command_registry import COMMANDS


class NoToolProvider(MockBrainProvider):
    def __init__(self, provider_id: str, *, configured: bool = True, available: bool = True) -> None:
        super().__init__(configured=configured, available=available)
        self._provider_id = provider_id

    def provider_id(self) -> str:
        return self._provider_id

    def supports_tool_calls(self) -> bool:
        return False


def test_dry_run_switch_checks_compatibility() -> None:
    payload = model_switch_payload(
        "mock",
        env={"BRAIN_MOCK_PROVIDER_ENABLED": "true", "BRAIN_DEFAULT_PROVIDER": "mock", "BRAIN_PROVIDER_ORDER": "mock"},
        dry_run=True,
    )

    assert payload["status"] == "ok"
    assert payload["dry_run"] is True
    assert payload["persisted_config_changed"] is False
    assert payload["switch_record"]["compatibility_check"]["status"] == "compatible"
    assert payload["switch_record"]["rollback_plan"]["rollback_available"] is True


def test_persistent_switch_is_blocked_without_config_change() -> None:
    payload = model_switch_payload(
        "mock",
        env={"BRAIN_MOCK_PROVIDER_ENABLED": "true", "BRAIN_DEFAULT_PROVIDER": "mock", "BRAIN_PROVIDER_ORDER": "mock"},
        dry_run=False,
    )

    assert payload["status"] == "blocked"
    assert payload["blocked_reason"] == "persistent_model_switch_not_implemented"
    assert payload["persisted_config_changed"] is False
    assert payload["model_call_performed"] is False


def test_switch_blocked_when_provider_unavailable() -> None:
    registry = BrainProviderRegistry(
        [
            BrainProviderRegistration(
                provider_id="missing_runtime",
                provider_name="Missing Runtime",
                factory=lambda: MockBrainProvider(available=False),
            )
        ],
        config=BrainRuntimeConfig(default_provider="missing_runtime", provider_order=("missing_runtime",)),
    )

    record, decision = build_model_switch_record("missing_runtime", registry=registry)

    assert record.status == "blocked"
    assert record.compatibility_check.provider_available is False
    assert decision["reason"] == "provider_unavailable"


def test_tool_call_incompatibility_blocks_tool_required_route() -> None:
    registry = BrainProviderRegistry(
        [
            BrainProviderRegistration(
                provider_id="text_only",
                provider_name="Text Only",
                factory=lambda: NoToolProvider("text_only"),
            )
        ],
        config=BrainRuntimeConfig(default_provider="text_only", provider_order=("text_only",)),
    )

    record, decision = build_model_switch_record("text_only", registry=registry, tool_call_support_required=True)

    assert record.status == "blocked"
    assert record.compatibility_check.tool_call_compatible is False
    assert decision["reason"] == "tool_call_support_required"


def test_cloud_paid_provider_blocked_by_policy() -> None:
    registry = BrainProviderRegistry(
        [
            BrainProviderRegistration(
                provider_id="openai",
                provider_name="OpenAI",
                factory=lambda: MockBrainProvider(),
            )
        ],
        config=BrainRuntimeConfig(default_provider="openai", provider_order=("openai",), allow_cloud_fallback=False),
    )

    record, decision = build_model_switch_record("openai", registry=registry)

    assert record.status == "blocked"
    assert record.compatibility_check.cloud_or_paid_blocked is True
    assert decision["reason"] == "cloud_fallback_disabled"


def test_context_summary_redacted_and_personal_data_not_carried() -> None:
    status = continuity_status(env={"SESSION_CONTINUITY_ENABLED": "true"})
    export = export_redacted_continuity(
        context_summary="email sam@example.com token=abcd1234SECRET",
        env={"SESSION_CONTINUITY_ENABLED": "true"},
    )

    assert status["policy"]["carry_personal_data"] is False
    assert status["memory_written"] is False
    assert "[REDACTED_EMAIL]" in export["export"]["context_summary"]
    assert "abcd1234SECRET" not in export["export"]["context_summary"]
    assert export["memory_written"] is False


def test_redaction_helper_masks_sensitive_context() -> None:
    summary = redact_context_summary("Contact me at person@example.com password=hunter2secret")

    assert "person@example.com" not in summary
    assert "hunter2secret" not in summary


def test_clear_continuity_is_safe_noop_by_default() -> None:
    payload = clear_continuity()

    assert payload["status"] == "ok"
    assert payload["entries_deleted"] == 0
    assert payload["raw_context_deleted"] is False
    assert payload["memory_written"] is False


def test_cli_commands_for_model_switching_and_continuity(capsys) -> None:
    assert cli_commands.dispatch_cli(["brain", "switch", "mock", "--dry-run"]) == 0
    assert cli_commands.dispatch_cli(["brain", "switch", "mock"]) == 0
    assert cli_commands.dispatch_cli(["session", "continuity", "status"]) == 0
    assert cli_commands.dispatch_cli(["session", "continuity", "export", "--redacted"]) == 0
    assert cli_commands.dispatch_cli(["session", "continuity", "clear"]) == 0
    output = capsys.readouterr().out
    assert "persisted_config_changed" in output
    assert "personal_data_carried_by_default" in output


def test_command_registry_updated_for_continuity_commands() -> None:
    commands = {record.command_id: record for record in COMMANDS}

    assert commands["CMD-BRAIN-007"].command == "python smart_agent.py brain switch <provider>"
    assert commands["CMD-SESSION-012"].command == "python smart_agent.py session continuity status"
    assert commands["CMD-SESSION-013"].risk_level == "LOW"
    assert commands["CMD-SESSION-014"].memory_behavior == "no memory write"
