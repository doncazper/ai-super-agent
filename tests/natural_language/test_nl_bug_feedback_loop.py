from __future__ import annotations

import json
from pathlib import Path

from agent.session_logs.feedback import VALID_FEEDBACK_TAGS
from agent.session_logs.review import BugStore
from agent.ui import cli_commands
from agent.ui.evals import load_eval_cases
from agent.ui.command_registry import get_command


def _write_agent_script(tmp_path: Path) -> None:
    (tmp_path / "smart_agent.py").write_text("print('nl command output password=hunter2 sam@example.com')\n", encoding="utf-8")


def _create_nl_bug(tmp_path: Path, capsys) -> str:
    _write_agent_script(tmp_path)
    assert cli_commands.dispatch_cli(["session", "start", "--name", "nl-bug"], project_root=tmp_path) == 0
    capsys.readouterr()
    assert (
        cli_commands.dispatch_cli(
            ["session", "run", "--", "nl", "weather for password=hunter2 sam@example.com"],
            project_root=tmp_path,
        )
        == 0
    )
    capsys.readouterr()
    assert (
        cli_commands.dispatch_cli(
            [
                "feedback",
                "nl-bug",
                "--last",
                "--expected-intent",
                "weather.current",
                "--expected-safety-outcome",
                "clarify",
                "--tag",
                "should_have_clarified",
                "--note",
                "wrong command for password=hunter2 sam@example.com",
            ],
            project_root=tmp_path,
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    return str(payload["bug"]["bug_id"])


def test_natural_language_feedback_tags_are_accepted() -> None:
    expected = {
        "misunderstood_intent",
        "wrong_command_suggested",
        "should_have_clarified",
        "should_have_denied",
        "should_have_required_approval",
        "executed_when_should_not",
        "failed_to_find_command",
        "poor_natural_language_answer",
    }

    assert expected <= VALID_FEEDBACK_TAGS


def test_feedback_nl_bug_creates_redacted_bug(tmp_path: Path, capsys) -> None:
    bug_id = _create_nl_bug(tmp_path, capsys)
    bug = BugStore(project_root=tmp_path).get(bug_id)

    assert bug is not None
    assert bug.feature == "natural_language"
    assert bug.command_id
    assert "weather.current" in bug.expected_behavior
    text = json.dumps(bug.to_dict())
    assert "hunter2" not in text
    assert "sam@example.com" not in text
    assert "<REDACTED_SECRET>" in text
    assert "<REDACTED_EMAIL>" in text


def test_create_nl_regression_generates_fixture_that_loads(tmp_path: Path, capsys) -> None:
    bug_id = _create_nl_bug(tmp_path, capsys)

    assert cli_commands.dispatch_cli(["bugs", "create-nl-regression", bug_id], project_root=tmp_path) == 0
    result = json.loads(capsys.readouterr().out)
    fixture_path = tmp_path / result["fixture_path"]
    assert fixture_path.exists()

    cases = load_eval_cases(tmp_path / "eval_cases")
    generated = {case.case_id: case for case in cases}
    case_id = result["case_id"]
    assert case_id in generated
    case = generated[case_id]
    assert case.category == "natural_language"
    assert case.expect["expected_intent"] == "weather.current"
    assert case.expect["should_execute"] is False
    serialized = json.dumps(case.__dict__)
    assert "hunter2" not in serialized
    assert "sam@example.com" not in serialized


def test_nl_regressions_list_and_command_registry(tmp_path: Path, capsys) -> None:
    bug_id = _create_nl_bug(tmp_path, capsys)
    assert cli_commands.dispatch_cli(["bugs", "create-nl-regression", bug_id], project_root=tmp_path) == 0
    capsys.readouterr()

    assert cli_commands.dispatch_cli(["nl", "regressions", "list"], project_root=tmp_path) == 0
    listed = json.loads(capsys.readouterr().out)
    assert listed["count"] == 1
    assert listed["cases"][0]["id"].startswith("nl.regression.")

    for command_id in ("CMD-FEEDBACK-011", "CMD-BUGS-009", "CMD-NL-006"):
        record = get_command(command_id)
        assert record is not None
        assert record.status == "active"
        assert record.risk_level in {"SAFE", "LOW"}
        assert "NL_BUG_TRIAGE" in record.docs_link
