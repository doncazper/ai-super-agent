from __future__ import annotations

from agent.natural_language.execution_plan import build_execution_plan
from agent.natural_language.preflight import explain_request, suggest_request


def test_safe_weather_request_creates_safe_plan() -> None:
    plan = build_execution_plan("what is the weather in Phoenix")
    assert plan.intent == "weather.current"
    assert plan.command_id == "CMD-WEATHER-003"
    assert plan.safe_to_execute is True
    assert plan.approval_required is False
    assert plan.audit_preview["tools_called"] == []
    assert plan.args == ("Phoenix",)


def test_web_research_plan_shows_provider_requirement() -> None:
    plan = build_execution_plan("look up latest python release")
    assert plan.intent == "web.research"
    assert plan.safe_to_execute is False
    assert plan.provider_requirements
    assert "configured web/search provider or local web index" in plan.missing_requirements


def test_email_send_plan_requires_approval_and_is_not_safe() -> None:
    plan = build_execution_plan("send this email")
    assert plan.intent == "send_or_write.request"
    assert plan.risk_level == "CRITICAL"
    assert plan.approval_required is True
    assert plan.dry_run_required is True
    assert plan.safe_to_execute is False


def test_file_write_plan_requires_approval_preview() -> None:
    plan = build_execution_plan("write hello to a workspace file")
    assert plan.intent == "file.write"
    assert plan.command_id == "CMD-FILES-005"
    assert plan.approval_required is True
    assert plan.dry_run_required is True
    assert plan.safe_to_execute is False
    assert "workspace write" in " ".join(plan.expected_side_effects)


def test_unknown_command_denied_and_suggests_help() -> None:
    plan = build_execution_plan("frobnicate quasar gently")
    assert plan.intent == "unknown"
    assert plan.safe_to_execute is False
    assert "deterministic intent or exact command" in plan.missing_requirements
    assert "commands search" in plan.command or plan.command_id


def test_preflight_exposes_no_tool_execution() -> None:
    plan = build_execution_plan("send a text to Sam")
    assert plan.audit_preview["tools_called"] == []
    assert plan.audit_preview["commands_executed"] == []
    assert plan.audit_preview["personal_data_accessed"] is False


def test_explain_and_suggest_are_metadata_only() -> None:
    explanation = explain_request("what is the weather in Phoenix")
    suggestion = suggest_request("what is the weather in Phoenix")
    assert explanation["safe_to_execute"] is True
    assert suggestion["command_id"] == "CMD-WEATHER-003"
    assert suggestion["safe_to_execute"] is True
