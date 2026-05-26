from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path

from agent.ui import cli_commands
from agent.ui.command_registry import COMMANDS, get_command, qa_run, validate_command_registry_docs


ROOT = Path(__file__).resolve().parents[1]


def test_command_registry_docs_exist_and_validate() -> None:
    for path in (
        "docs/COMMAND_REGISTRY.md",
        "docs/COMMAND_TEST_MATRIX.md",
        "docs/COMMAND_LEGACY.md",
        "docs/COMMAND_QA_RUNBOOK.md",
        "docs/templates/command_record_template.md",
        "docs/templates/command_test_record_template.md",
    ):
        assert (ROOT / path).exists(), path
    report = validate_command_registry_docs(ROOT)
    assert report["status"] == "ok", report
    assert report["command_count"] >= 100


def test_every_command_has_required_metadata() -> None:
    valid_statuses = {"active", "experimental", "stubbed", "deprecated", "legacy", "removed", "blocked", "planned"}
    valid_risk_parts = {"SAFE", "LOW", "MEDIUM", "HIGH", "CRITICAL", "FORBIDDEN"}
    for record in COMMANDS:
        assert record.command_id
        assert record.command
        assert record.group
        assert record.description
        assert record.example
        assert record.status in valid_statuses
        assert all(part in valid_risk_parts for part in record.risk_level.split("/"))
        if record.status in {"deprecated", "legacy", "removed"}:
            assert record.replacement != "n/a" or record.notes


def test_command_registry_cli_list_show_search_and_legacy(capsys) -> None:
    assert cli_commands.dispatch_cli(["commands", "list"], project_root=ROOT) == 0
    listed = json.loads(capsys.readouterr().out)
    assert any(item["command_id"] == "CMD-WEATHER-003" for item in listed["commands"])

    assert cli_commands.dispatch_cli(["commands", "show", "CMD-WEATHER-003"], project_root=ROOT) == 0
    shown = json.loads(capsys.readouterr().out)
    assert shown["command"] == "python smart_agent.py weather current \"<location>\""

    assert cli_commands.dispatch_cli(["commands", "search", "PromptOps"], project_root=ROOT) == 0
    searched = json.loads(capsys.readouterr().out)
    assert any(item["command_id"].startswith("CMD-WORK") for item in searched["commands"])

    assert cli_commands.dispatch_cli(["commands", "legacy"], project_root=ROOT) == 0
    legacy = json.loads(capsys.readouterr().out)
    assert any(item["status"] in {"legacy", "blocked"} for item in legacy["commands"])


def test_command_registry_cli_validate_and_qa_plan(capsys) -> None:
    assert cli_commands.dispatch_cli(["commands", "validate"], project_root=ROOT) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "ok"

    assert cli_commands.dispatch_cli(["commands", "qa-plan"], project_root=ROOT) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["commands"]


def test_command_registry_list_handles_closed_pipe_without_traceback() -> None:
    command = f"set -o pipefail; {shlex.quote(sys.executable)} smart_agent.py commands list | head -5"
    result = subprocess.run(
        ["bash", "-lc", command],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "BrokenPipeError" not in result.stderr


def test_command_qa_run_prints_only_safe_low_active_commands() -> None:
    commands = qa_run("Weather")
    assert commands
    for item in commands:
        record = get_command(item["command_id"])
        assert record is not None
        assert record.status == "active"
        assert record.risk_level in {"SAFE", "LOW"}
