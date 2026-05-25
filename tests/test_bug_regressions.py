from __future__ import annotations

import json
from pathlib import Path

from agent.session_logs.review import BugStore
from agent.ui import cli_commands


def _create_bug(tmp_path: Path, **overrides) -> str:
    payload = {
        "title": "P2 command failed",
        "severity": "P2",
        "feature": "doctor",
        "command_id": "cmd_001",
        "session_id": "sess_test",
        "reproduction_command": "python smart_agent.py doctor",
        "expected_behavior": "Command should return a clear status report.",
        "actual_behavior": "Command exited with 2.",
        "stdout_stderr_excerpt": "[stderr]\nfailed",
        "suggested_regression_test": "Add CLI regression coverage for doctor.",
    }
    payload.update(overrides)
    return BugStore(project_root=tmp_path).create_bug(payload).bug_id


def test_create_regression_stub_for_command_failure(tmp_path: Path, capsys) -> None:
    bug_id = _create_bug(tmp_path)

    assert cli_commands.dispatch_cli(["bugs", "create-regression", bug_id], project_root=tmp_path) == 0
    result = json.loads(capsys.readouterr().out)

    test_path = tmp_path / result["test_path"]
    assert test_path.exists()
    text = test_path.read_text(encoding="utf-8")
    assert "Reproduction command" in text
    assert "python smart_agent.py doctor" in text
    assert "pytest.skip" in text
    bug = BugStore(project_root=tmp_path).get(bug_id)
    assert bug is not None
    assert bug.status == "regression_added"
    assert result["test_path"] in bug.linked_tests


def test_create_regression_marks_live_provider_stub(tmp_path: Path, capsys) -> None:
    bug_id = _create_bug(
        tmp_path,
        feature="web",
        title="Live provider failure",
        actual_behavior="Requires live provider with configured provider.",
        suggested_regression_test="Create live provider regression only when configured.",
    )

    assert cli_commands.dispatch_cli(["bugs", "create-regression", bug_id], project_root=tmp_path) == 0
    result = json.loads(capsys.readouterr().out)
    text = (tmp_path / result["test_path"]).read_text(encoding="utf-8")

    assert "@pytest.mark.integration" in text
    assert "live-provider regression scaffold" in text


def test_regression_stub_redacts_secrets_and_personal_identifiers(tmp_path: Path, capsys) -> None:
    bug_id = _create_bug(
        tmp_path,
        actual_behavior="password: hunter2 user person@example.invalid phone 202-555-0100",
        stdout_stderr_excerpt="token=not-a-real-secret-value person@example.invalid",
    )

    assert cli_commands.dispatch_cli(["bugs", "create-regression", bug_id], project_root=tmp_path) == 0
    result = json.loads(capsys.readouterr().out)
    text = (tmp_path / result["test_path"]).read_text(encoding="utf-8")

    assert "hunter2" not in text
    assert "person@example.invalid" not in text
    assert "202-555-0100" not in text
    assert "<REDACTED_SECRET>" in text
    assert "<REDACTED_EMAIL>" in text


def test_personal_data_bug_creates_skipped_personal_data_stub(tmp_path: Path, capsys) -> None:
    bug_id = _create_bug(
        tmp_path,
        feature="email",
        title="Email metadata issue",
        actual_behavior="UNTRUSTED_EMAIL selected thread failed without sanitized fixture.",
    )

    assert cli_commands.dispatch_cli(["bugs", "create-regression", bug_id], project_root=tmp_path) == 0
    result = json.loads(capsys.readouterr().out)
    text = (tmp_path / result["test_path"]).read_text(encoding="utf-8")

    assert "@pytest.mark.personal_data" in text
    assert "personal-data regression requires a sanitized fixture" in text


def test_create_regressions_for_session(tmp_path: Path, capsys) -> None:
    first = _create_bug(tmp_path, title="one", session_id="sess_batch")
    second = _create_bug(tmp_path, title="two", session_id="sess_batch")
    _create_bug(tmp_path, title="other", session_id="other_session")

    assert cli_commands.dispatch_cli(["bugs", "create-regressions", "--session", "sess_batch"], project_root=tmp_path) == 0
    result = json.loads(capsys.readouterr().out)

    assert [item["bug_id"] for item in result["regressions"]] == [first, second]
    assert (tmp_path / "tests" / "regressions" / "test_bug_0001.py").exists()
    assert (tmp_path / "tests" / "regressions" / "test_bug_0002.py").exists()


def test_mark_fixed_requires_linked_test_or_explicit_reason(tmp_path: Path, capsys) -> None:
    bug_id = _create_bug(tmp_path)

    assert cli_commands.dispatch_cli(["bugs", "mark-fixed", bug_id], project_root=tmp_path) == 2
    assert cli_commands.dispatch_cli(["bugs", "mark-fixed", bug_id, "--reason", "Covered by manual verification"], project_root=tmp_path) == 0
    fixed = json.loads(capsys.readouterr().out)
    assert fixed["status"] == "fixed"


def test_link_test_and_mark_wontfix_update_status(tmp_path: Path, capsys) -> None:
    bug_id = _create_bug(tmp_path)

    assert cli_commands.dispatch_cli(["bugs", "link-test", bug_id, "tests/regressions/test_bug_custom.py"], project_root=tmp_path) == 0
    linked = json.loads(capsys.readouterr().out)
    assert "tests/regressions/test_bug_custom.py" in linked["linked_tests"]

    assert cli_commands.dispatch_cli(["bugs", "mark-wontfix", bug_id, "--reason", "Duplicate"], project_root=tmp_path) == 0
    wontfix = json.loads(capsys.readouterr().out)
    assert wontfix["status"] == "wontfix"
    assert wontfix["resolution_note"] == "Duplicate"


def test_feature_maturity_mentions_regression_coverage() -> None:
    text = Path("docs/FEATURE_MATURITY.md").read_text(encoding="utf-8")

    assert "Session Review and Bug Generator" in text
