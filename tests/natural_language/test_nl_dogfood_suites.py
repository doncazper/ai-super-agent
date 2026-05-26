from __future__ import annotations

from pathlib import Path

from agent.dogfood.suites import load_all_suites, load_suite
from agent.ui.command_registry import get_command


ROOT = Path(__file__).resolve().parents[2]


def test_natural_language_dogfood_suites_exist_and_validate() -> None:
    suites = {suite.suite_id: suite for suite in load_all_suites(project_root=ROOT)}

    assert {"natural_language_core", "natural_language_risky"}.issubset(suites)
    core = suites["natural_language_core"]
    risky = suites["natural_language_risky"]

    assert core.requires_live_lmstudio is False
    assert core.requires_web is False
    assert core.requires_personal_data is False
    assert core.default_enabled is True
    assert risky.requires_live_lmstudio is False
    assert risky.requires_web is False
    assert risky.requires_personal_data is False
    assert risky.default_enabled is False

    for suite in (core, risky):
        assert suite.commands
        for command in suite.commands:
            assert command.command.startswith("python smart_agent.py ")
            assert command.expected_behavior
            assert command.failure_signals
            assert "natural_language" in command.tags


def test_natural_language_core_suite_covers_required_phrases() -> None:
    suite = load_suite("natural_language_core", project_root=ROOT)
    joined = "\n".join(command.command for command in suite.commands)

    assert "what can you do" in joined
    assert "check if the agent is healthy" in joined
    assert "weather in phoenix" in joined
    assert "current ai coding agent news" in joined
    assert "summarize this file" in joined
    assert "show me my prompt queue" in joined
    assert "review the last session and fix bugs" in joined
    assert "what commands do I have for reddit" in joined


def test_natural_language_risky_suite_is_preflight_only() -> None:
    suite = load_suite("natural_language_risky", project_root=ROOT)

    forbidden_direct_commands = [
        "actions approve",
        "send --from-action",
        "messages send",
        "mail send",
        "calendar write",
        "contacts update",
        "prompts run",
        "work autopilot",
    ]
    for command in suite.commands:
        assert " nl preflight " in command.command
        assert "preflight_only" in command.tags
        lowered = command.command.lower()
        for fragment in forbidden_direct_commands:
            assert fragment not in lowered
        assert "safe_to_execute=true" in command.failure_signals or "safe_to_execute=true" in command.expected_behavior


def test_natural_language_dogfood_command_registry_entries() -> None:
    for command_id in ("CMD-DOGFOOD-NL-001", "CMD-DOGFOOD-NL-002"):
        record = get_command(command_id)
        assert record is not None
        assert record.status == "active"
        assert record.risk_level == "LOW"
        assert "natural_language" in record.command
        assert "NL_DOGFOOD_RUNBOOK" in record.docs_link
