from __future__ import annotations

import json

from agent.autonomy.subagents import dry_run_subagent, list_subagents, show_subagent, subagent_policy
from agent.ui import cli_commands
from agent.ui.command_registry import get_command


def test_default_subagents_have_no_personal_data_access() -> None:
    report = list_subagents(network_enabled=False)

    assert report["execution_enabled"] is False
    assert report["mock_only"] is True
    assert all(profile["can_access_personal_data"] is False for profile in report["subagents"])


def test_critical_execution_denied_for_all_profiles() -> None:
    policy = subagent_policy(network_enabled=False)

    assert all(profile["critical_execution_denied"] is True for profile in policy["profiles"])


def test_write_permissions_disabled_by_default() -> None:
    report = list_subagents(network_enabled=False)

    assert all(profile["can_write_files"] is False for profile in report["subagents"])


def test_locked_down_has_no_tools() -> None:
    report = show_subagent("locked_down", network_enabled=False)

    subagent = report["subagent"]
    assert subagent["allowed_tools"] == []
    assert subagent["blocked_tools"] == ["*"]
    assert report["policy"]["direct_tool_bypass_denied"] is True


def test_researcher_network_allowed_only_if_configured() -> None:
    disabled = show_subagent("researcher", network_enabled=False)["subagent"]
    enabled = show_subagent("researcher", network_enabled=True)["subagent"]

    assert disabled["can_access_network"] is False
    assert disabled["allowed_tools"] == []
    assert enabled["can_access_network"] is True
    assert "web.search" in enabled["allowed_tools"]


def test_coder_cannot_bypass_toolbroker() -> None:
    report = dry_run_subagent("coder", "draft a patch", network_enabled=False)

    assert report["status"] == "dry_run"
    assert report["toolbroker_required"] is True
    assert report["direct_tool_calls_allowed"] is False
    assert report["approval_bypass_allowed"] is False
    assert report["tools_executed"] == []
    assert report["writes_allowed"] is False


def test_dry_run_mock_works() -> None:
    report = dry_run_subagent("planner", "split this into safe prompts", network_enabled=False)

    assert report["mock_only"] is True
    assert report["execution_enabled"] is False
    assert report["output_trust_level"] == "MODEL_OUTPUT"
    assert report["result"] == "No subagent was launched and no tools were executed."


def test_subagent_cli_commands(capsys) -> None:
    assert cli_commands.dispatch_cli(["subagents", "list"]) == 0
    list_payload = json.loads(capsys.readouterr().out)
    assert list_payload["subagents"]

    assert cli_commands.dispatch_cli(["subagents", "show", "researcher"]) == 0
    show_payload = json.loads(capsys.readouterr().out)
    assert show_payload["subagent"]["profile"] == "researcher"

    assert cli_commands.dispatch_cli(["subagents", "policy"]) == 0
    policy_payload = json.loads(capsys.readouterr().out)
    assert "Subagents cannot call tools directly." in policy_payload["rules"]

    assert cli_commands.dispatch_cli(["subagents", "dry-run", "coder", "inspect tests"]) == 0
    dry_run_payload = json.loads(capsys.readouterr().out)
    assert dry_run_payload["tools_executed"] == []


def test_command_registry_tracks_subagent_commands() -> None:
    command = get_command("CMD-SUBAGENTS-001")

    assert command is not None
    assert command.command == "python smart_agent.py subagents list"
    assert command.risk_level == "SAFE"
    assert command.example
