from __future__ import annotations

from agent.natural_language.clarification import build_clarification
from agent.natural_language.models import CommandSuggestion, IntentCandidate
from agent.natural_language.preview import format_clarification_preview
from agent.natural_language.router import route_request


def test_missing_location_asks_for_location() -> None:
    decision = route_request("weather")
    question = decision.clarification_question
    assert question is not None
    assert question.clarification_type == "missing_required_argument"
    assert "location" in question.question.lower()
    assert decision.execution_plan is not None
    assert decision.execution_plan.execution_allowed is False


def test_multiple_command_matches_offer_choices() -> None:
    suggestions = (
        CommandSuggestion("CMD-A", "python smart_agent.py a", "A", "SAFE", "no", "active", True, False),
        CommandSuggestion("CMD-B", "python smart_agent.py b", "B", "SAFE", "no", "active", True, False),
    )
    question = build_clarification(IntentCandidate("unknown", 0.5, "multiple matches", ("fallback",)), suggestions)
    assert question.clarification_type == "multiple_matching_commands"
    assert "python smart_agent.py a" in question.choices
    assert "python smart_agent.py b" in question.choices


def test_provider_missing_suggests_doctor_or_setup() -> None:
    suggestions = (
        CommandSuggestion(
            "CMD-WEB",
            "python smart_agent.py web search",
            "Search",
            "LOW",
            "no",
            "active",
            True,
            False,
            setup_hint="Requires configured web provider; use web providers first.",
        ),
    )
    question = build_clarification(IntentCandidate("web.research", 0.7, "provider setup", ("search",)), suggestions)
    assert question.clarification_type == "provider_missing"
    assert "doctor" in " ".join(question.choices).lower() or "setup" in question.setup_hint.lower()


def test_deprecated_command_suggests_replacement() -> None:
    suggestions = (
        CommandSuggestion(
            "CMD-OLD",
            "python smart_agent.py old",
            "Old",
            "LOW",
            "no",
            "deprecated",
            False,
            False,
            replacement="python smart_agent.py new",
        ),
    )
    question = build_clarification(IntentCandidate("command.search", 0.6, "deprecated", ("old",)), suggestions)
    assert question.clarification_type == "command_is_deprecated"
    assert "python smart_agent.py new" in question.choices


def test_personal_data_request_says_approval_setup_required() -> None:
    decision = route_request("read my email")
    question = decision.clarification_question
    assert question is not None
    assert question.clarification_type == "personal_data_request"
    assert question.approval_required is True
    assert question.dry_run_required is True
    assert decision.execution_plan is not None
    assert decision.execution_plan.execution_allowed is False


def test_risky_send_write_request_does_not_execute() -> None:
    decision = route_request("send this email")
    preview = format_clarification_preview(decision)
    assert "No commands have been executed." in preview
    assert decision.execution_plan is not None
    assert decision.execution_plan.execution_allowed is False
    assert decision.clarification_question is not None
    assert decision.clarification_question.clarification_type == "risky_action"
