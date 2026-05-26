from __future__ import annotations

from agent.brain.config import BrainRuntimeConfig
from agent.brain.mock_provider import MockBrainProvider
from agent.brain.provider_router import BrainProviderRouter, BrainRouteRequest
from agent.brain.registry import BrainProviderRegistration, BrainProviderRegistry, make_mock_registration
from agent.brain.status import brain_fallback_status, brain_route_message, brain_switch_dry_run
from agent.ui import cli_commands
from agent.ui.command_registry import COMMANDS


class NoToolMockProvider(MockBrainProvider):
    def __init__(self, provider_id: str, *, configured: bool = True, available: bool = True) -> None:
        super().__init__(configured=configured, available=available)
        self._provider_id = provider_id

    def provider_id(self) -> str:
        return self._provider_id

    def supports_tool_calls(self) -> bool:
        return False


def registry_for_tests(config: BrainRuntimeConfig) -> BrainProviderRegistry:
    return BrainProviderRegistry(
        [
            BrainProviderRegistration(
                provider_id="primary",
                provider_name="Primary",
                factory=lambda: NoToolMockProvider("primary", available=False),
                setup_hint="primary test provider",
            ),
            BrainProviderRegistration(
                provider_id="secondary",
                provider_name="Secondary",
                factory=lambda: NoToolMockProvider("secondary"),
                setup_hint="secondary test provider",
            ),
            make_mock_registration(MockBrainProvider()),
        ],
        config=config,
    )


def test_explicit_provider_selected() -> None:
    registry = registry_for_tests(
        BrainRuntimeConfig(default_provider="mock", provider_order=("mock", "primary", "secondary"), mock_provider_enabled=True)
    )

    decision = BrainProviderRouter(registry).route(BrainRouteRequest(requested_provider="mock", user_override=True))

    assert decision.status == "selected"
    assert decision.selected_provider == "mock"
    assert decision.fallback_used is False
    assert decision.audit_event["model_call_performed"] is False


def test_fallback_disabled_blocks_fallback() -> None:
    registry = registry_for_tests(
        BrainRuntimeConfig(default_provider="primary", provider_order=("primary", "secondary"), fallback_enabled=False)
    )

    decision = BrainProviderRouter(registry).route(BrainRouteRequest(requested_provider="primary", user_override=True))

    assert decision.status == "blocked"
    assert decision.selected_provider is None
    assert decision.attempts[0].reason == "provider_unavailable"
    assert len(decision.attempts) == 1


def test_fallback_enabled_selects_next_healthy_provider() -> None:
    registry = registry_for_tests(
        BrainRuntimeConfig(
            default_provider="primary",
            provider_order=("primary", "secondary"),
            fallback_enabled=True,
            max_fallback_attempts=1,
        )
    )

    decision = BrainProviderRouter(registry).route(BrainRouteRequest(requested_provider="primary", user_override=True))

    assert decision.status == "selected"
    assert decision.selected_provider == "secondary"
    assert decision.fallback_used is True
    assert [attempt.provider_id for attempt in decision.attempts] == ["primary", "secondary"]


def test_tool_call_task_rejects_provider_without_tool_support() -> None:
    registry = registry_for_tests(
        BrainRuntimeConfig(default_provider="secondary", provider_order=("secondary",), require_tool_call_support_for_tools=True)
    )

    decision = BrainProviderRouter(registry).route(
        BrainRouteRequest(requested_provider="secondary", requires_tool_calls=True, user_override=True)
    )

    assert decision.status == "blocked"
    assert decision.attempts[0].reason == "tool_call_support_required"


def test_no_tools_task_allows_provider_without_tool_support() -> None:
    registry = registry_for_tests(BrainRuntimeConfig(default_provider="secondary", provider_order=("secondary",)))

    decision = BrainProviderRouter(registry).route(
        BrainRouteRequest(requested_provider="secondary", requires_tool_calls=False, no_tools=True, user_override=True)
    )

    assert decision.status == "selected"
    assert decision.selected_provider == "secondary"


def test_cloud_fallback_blocked() -> None:
    registry = BrainProviderRegistry(
        [
            BrainProviderRegistration(
                provider_id="openai",
                provider_name="OpenAI cloud",
                factory=lambda: MockBrainProvider(),
                setup_hint="cloud test provider",
            )
        ],
        config=BrainRuntimeConfig(default_provider="openai", provider_order=("openai",), allow_cloud_fallback=False),
    )

    decision = BrainProviderRouter(registry).route(BrainRouteRequest(requested_provider="openai", user_override=True))

    assert decision.status == "blocked"
    assert decision.attempts[0].reason == "cloud_fallback_disabled"


def test_status_helpers_return_recorded_decisions() -> None:
    env = {"BRAIN_DEFAULT_PROVIDER": "mock", "BRAIN_MOCK_PROVIDER_ENABLED": "true", "BRAIN_PROVIDER_ORDER": "mock"}

    route = brain_route_message("hello", env=env)
    switch = brain_switch_dry_run("mock", env=env)
    status = brain_fallback_status(env=env)

    assert route["decision"]["selected_provider"] == "mock"
    assert switch["dry_run"] is True
    assert status["fallback_enabled"] is False


def test_brain_router_cli_commands(capsys) -> None:
    assert cli_commands.dispatch_cli(["brain", "fallback-status"]) == 0
    assert cli_commands.dispatch_cli(["brain", "switch", "lmstudio", "--dry-run"]) == 0
    assert cli_commands.dispatch_cli(["brain", "route", "hello"]) == 0
    output = capsys.readouterr().out
    assert "model_call_performed" in output


def test_command_registry_updated_for_router_commands() -> None:
    commands = {record.command_id: record for record in COMMANDS}

    assert commands["CMD-BRAIN-007"].status == "active"
    assert commands["CMD-BRAIN-008"].status == "active"
    assert commands["CMD-BRAIN-011"].command == "python smart_agent.py brain route"
