from __future__ import annotations

from agent.natural_language.router import route_request


def test_weather_request_maps_to_weather_current() -> None:
    decision = route_request("what's the weather in Phoenix")
    assert decision.intent == "weather.current"
    assert decision.safety_outcome == "show_command_suggestion"
    assert decision.command_suggestions
    assert decision.command_suggestions[0].command_id == "CMD-WEATHER-003"
    assert decision.audit_summary["tools_called"] == []


def test_vague_lookup_requires_clarification() -> None:
    decision = route_request("look this up")
    assert decision.intent == "web.research"
    assert decision.clarification_required is True
    assert decision.safety_outcome == "ask_clarifying_question"
    assert decision.clarification_question is not None


def test_commands_for_memory_maps_to_command_search() -> None:
    decision = route_request("what commands do I have for memory")
    assert decision.intent == "command.search"
    assert decision.safety_outcome == "show_command_suggestion"
    assert any("commands search" in suggestion.command for suggestion in decision.command_suggestions)


def test_fix_last_session_bugs_maps_to_session_review() -> None:
    decision = route_request("fix the last session bugs")
    assert decision.intent == "session.review"
    assert decision.safety_outcome == "show_command_suggestion"
    assert any("session" in suggestion.command for suggestion in decision.command_suggestions)


def test_send_email_requires_preflight_or_approval() -> None:
    decision = route_request("send this email")
    assert decision.intent == "send_or_write.request"
    assert decision.approval_required is True
    assert decision.dry_run_required is True
    assert decision.safety_outcome == "ask_clarifying_question"
    assert decision.clarification_question is not None
    assert decision.clarification_question.clarification_type == "risky_action"
    assert all(not suggestion.safe_to_run_directly for suggestion in decision.command_suggestions)
    assert decision.execution_plan is not None
    assert decision.execution_plan.execution_allowed is False


def test_ambiguous_short_request_asks_clarification() -> None:
    decision = route_request("fix")
    assert decision.intent == "ambiguous"
    assert decision.clarification_required is True
    assert decision.safety_outcome == "ask_clarifying_question"


def test_no_tools_mode_does_not_route_tools() -> None:
    decision = route_request("what's the weather in Phoenix", no_tools=True)
    assert decision.intent == "chat.no_tools"
    assert decision.command_suggestions == ()
    assert decision.safety_outcome == "answer_directly"


def test_exact_command_unaffected_and_not_executed() -> None:
    decision = route_request('python smart_agent.py weather current "Phoenix, AZ"')
    assert decision.intent == "command.exact"
    assert decision.safety_outcome == "show_command_suggestion"
    assert decision.execution_plan is not None
    assert decision.execution_plan.execution_allowed is False


def test_high_risk_request_not_executed() -> None:
    decision = route_request("send a text to Sam")
    assert decision.intent == "send_or_write.request"
    assert decision.risk_level == "CRITICAL"
    assert decision.execution_plan is not None
    assert decision.execution_plan.execution_allowed is False
