from __future__ import annotations

from agent.natural_language.cli_ux import render_nl_response
from agent.ui.cli_commands import dispatch_cli


def test_exact_command_path_still_dispatches() -> None:
    assert dispatch_cli(["commands", "list", "--status", "active"]) == 0


def test_nl_weather_request_maps_correctly(capsys) -> None:
    assert dispatch_cli(["nl", "what is the weather in Phoenix"]) == 0
    output = capsys.readouterr().out
    assert "Understood intent: weather.current" in output
    assert "python smart_agent.py weather current" in output
    assert "No commands have been executed." in output


def test_ask_help_request_maps_to_command_help(capsys) -> None:
    assert dispatch_cli(["ask", "how do I find memory commands"]) == 0
    output = capsys.readouterr().out
    assert "Understood intent: command.search" in output
    assert "Matched command:" in output
    assert "No commands have been executed." in output


def test_risky_send_request_not_executed(capsys) -> None:
    assert dispatch_cli(["nl", "send this email"]) == 0
    output = capsys.readouterr().out
    assert "risk=CRITICAL" in output
    assert "approval_required=True" in output
    assert "No commands have been executed." in output


def test_ambiguous_request_asks_clarification() -> None:
    output = render_nl_response("fix")
    assert "Understood intent: ambiguous" in output
    assert "clarify" in output.lower()
    assert "No commands have been executed." in output


def test_no_tools_mode_preserved(capsys) -> None:
    assert dispatch_cli(["nl", "--no-tools", "what is the weather in Phoenix"]) == 0
    output = capsys.readouterr().out
    assert "Understood intent: chat.no_tools" in output
    assert "No commands have been executed." in output


def test_help_text_mentions_nl(capsys) -> None:
    assert dispatch_cli(["nl", "--help"]) == 0
    output = capsys.readouterr().out
    assert "preflight" in output
    assert "suggest" in output
