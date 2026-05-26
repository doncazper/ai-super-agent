from __future__ import annotations

from dataclasses import dataclass

from agent.commands.intent_index import build_intent_index, suggest_commands


@dataclass(frozen=True)
class FixtureCommand:
    command_id: str
    command: str
    group: str
    description: str
    example: str
    status: str
    risk_level: str
    requires_approval: str
    requires_provider: str
    requires_connector: str
    docs_link: str = "docs/example.md"
    side_effects: str = "none"
    notes: str = ""


def _fixture_registry() -> list[FixtureCommand]:
    return [
        FixtureCommand(
            "CMD-WEATHER-003",
            'python smart_agent.py weather current "<location>"',
            "Weather",
            "Get current weather.",
            'python smart_agent.py weather current "Phoenix, AZ"',
            "active",
            "LOW",
            "no",
            "open_meteo",
            "weather",
        ),
        FixtureCommand(
            "CMD-EMAIL-999",
            "python smart_agent.py email send --from-action <action_id>",
            "Email",
            "Send approved email.",
            "python smart_agent.py email send --from-action act_123",
            "active",
            "CRITICAL",
            "Action Center",
            "mock email provider",
            "email",
        ),
        FixtureCommand(
            "CMD-OLD-001",
            "python smart_agent.py old-weather",
            "Weather",
            "Deprecated weather command.",
            "python smart_agent.py old-weather",
            "deprecated",
            "LOW",
            "no",
            "",
            "",
        ),
        FixtureCommand(
            "CMD-NEWS-001",
            'python smart_agent.py news top',
            "News",
            "Planned top headlines.",
            "python smart_agent.py news top",
            "stubbed",
            "LOW",
            "no",
            "news provider",
            "news",
        ),
    ]


def test_index_builds_from_fixture_registry() -> None:
    index = build_intent_index(_fixture_registry())
    assert {entry.command_id for entry in index} >= {"CMD-WEATHER-003", "CMD-EMAIL-999"}
    weather = next(entry for entry in index if entry.command_id == "CMD-WEATHER-003")
    assert "weather.current" in weather.intent_ids
    assert weather.examples
    assert "weather" in weather.aliases


def test_active_command_suggested_from_natural_terms() -> None:
    suggestions = suggest_commands("what is the weather in phoenix", records=_fixture_registry())
    assert suggestions
    assert suggestions[0].entry.command_id == "CMD-WEATHER-003"
    assert suggestions[0].primary is True


def test_deprecated_command_not_primary() -> None:
    suggestions = suggest_commands("old weather", records=_fixture_registry())
    deprecated = next(item for item in suggestions if item.entry.command_id == "CMD-OLD-001")
    assert deprecated.primary is False
    assert "deprecated" in deprecated.safety_note


def test_stubbed_command_labeled_and_provider_hint_present() -> None:
    index = build_intent_index(_fixture_registry())
    news = next(entry for entry in index if entry.command_id == "CMD-NEWS-001")
    assert news.status == "stubbed"
    assert news.safe_to_run_directly is False
    assert "Requires configured" in news.setup_hint


def test_high_risk_command_is_dry_run_or_approval_only() -> None:
    index = build_intent_index(_fixture_registry())
    email = next(entry for entry in index if entry.command_id == "CMD-EMAIL-999")
    assert email.safe_to_run_directly is False
    assert email.dry_run_available is True
    assert "send_or_write.request" in email.intent_ids
