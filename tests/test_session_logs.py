from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from agent.session_logs.recorder import SessionRecorder
from agent.session_logs.redaction import redact_text
from agent.session_logs.review import BugStore, SessionReviewer
from agent.session_logs.store import SessionLogStore
from agent.ui import cli_commands


def make_recorder(tmp_path: Path) -> SessionRecorder:
    return SessionRecorder(SessionLogStore(tmp_path / "reports" / "sessions", project_root=tmp_path), project_root=tmp_path)


def write_agent_script(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "smart_agent.py"
    script.write_text(body, encoding="utf-8")
    return script


def test_start_end_list_show_and_replay_work(tmp_path: Path) -> None:
    recorder = make_recorder(tmp_path)

    session = recorder.start(name="manual-test", tags=["smoke"])
    assert session.status == "active"
    assert recorder.status()["active"]["session_id"] == session.session_id

    ended = recorder.end()
    assert ended.status == "ended"
    assert recorder.list()[0]["session_id"] == session.session_id
    shown = recorder.show(session.session_id)
    assert shown["session"]["name"] == "manual-test"
    replay = recorder.replay(session.session_id)
    assert "Session Replay: manual-test" in replay


def test_session_run_captures_stdout_stderr_and_exit_code(tmp_path: Path) -> None:
    recorder = make_recorder(tmp_path)
    recorder.start(name="capture")
    script = write_agent_script(
        tmp_path,
        "import sys\nprint('hello stdout')\nprint('oops stderr', file=sys.stderr)\nsys.exit(3)\n",
    )

    record = recorder.run_command(["demo"], agent_script=script, python_executable=sys.executable)

    assert record.exit_code == 3
    assert "hello stdout" in record.stdout_preview
    assert "oops stderr" in record.stderr_preview
    stored = tmp_path / str(record.full_output_path)
    assert stored.exists()
    assert "hello stdout" in stored.read_text(encoding="utf-8")
    assert recorder.store.get_active().failure_count == 1


def test_secrets_and_personal_identifiers_are_redacted(tmp_path: Path) -> None:
    recorder = make_recorder(tmp_path)
    recorder.start(name="redaction")
    script = write_agent_script(
        tmp_path,
        "print('API_KEY=not-a-real-secret-value email person@example.invalid phone 202-555-0100')\n",
    )

    record = recorder.run_command(["--api-key", "not-a-real-command-secret", "demo"], agent_script=script, python_executable=sys.executable)
    output = (tmp_path / str(record.full_output_path)).read_text(encoding="utf-8")

    assert "not-a-real-secret-value" not in record.stdout_preview
    assert "person@example.invalid" not in record.stdout_preview
    assert "202-555-0100" not in record.stdout_preview
    assert "not-a-real-command-secret" not in record.sanitized_command_line
    assert "<REDACTED_SECRET>" in output
    assert "<REDACTED_EMAIL>" in output
    assert "<REDACTED_PHONE>" in output


def test_linked_audit_ids_stored_when_present(tmp_path: Path) -> None:
    recorder = make_recorder(tmp_path)
    recorder.start(name="audit-link")
    script = write_agent_script(tmp_path, 'print(\'{"audit_id": "audit_123456", "tool_call_id": "call_abcdef"}\')\n')

    record = recorder.run_command(["doctor"], agent_script=script, python_executable=sys.executable)

    assert "audit_123456" in record.linked_audit_ids
    assert "call_abcdef" in record.linked_audit_ids
    assert recorder.store.get_active().linked_audit_ids


def test_large_output_is_truncated_in_preview_and_stored_separately(tmp_path: Path) -> None:
    recorder = make_recorder(tmp_path)
    recorder.start(name="large-output")
    script = write_agent_script(tmp_path, "print('x' * 5000)\n")

    record = recorder.run_command(["demo"], agent_script=script, python_executable=sys.executable)

    assert "...[truncated]" in record.stdout_preview
    assert len(record.stdout_preview) < 4100
    assert record.full_output_path
    assert len((tmp_path / str(record.full_output_path)).read_text(encoding="utf-8")) > 5000


def test_malformed_session_file_is_skipped(tmp_path: Path) -> None:
    store = SessionLogStore(tmp_path / "reports" / "sessions", project_root=tmp_path)
    bad_dir = store.root / "sess_bad"
    bad_dir.mkdir(parents=True)
    (bad_dir / "session.json").write_text("{not json", encoding="utf-8")

    assert store.list_sessions() == []


def test_gitignore_protects_raw_session_reports() -> None:
    text = Path(".gitignore").read_text(encoding="utf-8")

    assert "reports/sessions/*" in text
    assert "!reports/sessions/.gitkeep" in text
    assert "reports/session_reviews/*" in text
    assert "!reports/session_reviews/.gitkeep" in text
    assert "bugs/*.json" in text
    assert "!bugs/.gitkeep" in text


def test_session_cli_start_run_end(tmp_path: Path, capsys) -> None:
    write_agent_script(tmp_path, "print('cli ok')\n")

    assert cli_commands.dispatch_cli(["session", "start", "--name", "cli-test"], project_root=tmp_path) == 0
    started = json.loads(capsys.readouterr().out)
    assert started["name"] == "cli-test"

    assert cli_commands.dispatch_cli(["session", "run", "--", "doctor"], project_root=tmp_path) == 0
    run = json.loads(capsys.readouterr().out)
    assert run["exit_code"] == 0
    assert "cli ok" in run["stdout_preview"]

    assert cli_commands.dispatch_cli(["session", "replay", "--last"], project_root=tmp_path) == 0
    replay = capsys.readouterr().out
    assert "Session Replay: cli-test" in replay

    assert cli_commands.dispatch_cli(["session", "end"], project_root=tmp_path) == 0
    ended = json.loads(capsys.readouterr().out)
    assert ended["status"] == "ended"


def test_feedback_attaches_to_last_command_and_replay(tmp_path: Path, capsys) -> None:
    write_agent_script(tmp_path, "print('cli ok')\n")
    assert cli_commands.dispatch_cli(["session", "start", "--name", "feedback-test"], project_root=tmp_path) == 0
    capsys.readouterr()
    assert cli_commands.dispatch_cli(["session", "run", "--", "doctor"], project_root=tmp_path) == 0
    command = json.loads(capsys.readouterr().out)

    assert cli_commands.dispatch_cli(["feedback", "good", "--last"], project_root=tmp_path) == 0
    feedback = json.loads(capsys.readouterr().out)
    assert feedback["command_id"] == command["command_id"]
    assert feedback["rating"] == 5
    assert feedback["redaction_status"] == "redacted"

    assert cli_commands.dispatch_cli(["session", "show", feedback["session_id"]], project_root=tmp_path) == 0
    shown = json.loads(capsys.readouterr().out)
    assert shown["session"]["feedback_count"] == 1
    assert shown["commands"][0]["user_rating"] == 5
    assert shown["feedback"][0]["feedback_id"] == feedback["feedback_id"]

    assert cli_commands.dispatch_cli(["session", "replay", "--last"], project_root=tmp_path) == 0
    replay = capsys.readouterr().out
    assert "feedback:" in replay
    assert "rating=5" in replay


def test_feedback_attaches_to_specific_command_and_lists(tmp_path: Path, capsys) -> None:
    write_agent_script(tmp_path, "print('cli ok')\n")
    assert cli_commands.dispatch_cli(["session", "start", "--name", "specific-feedback"], project_root=tmp_path) == 0
    capsys.readouterr()
    assert cli_commands.dispatch_cli(["session", "run", "--", "doctor"], project_root=tmp_path) == 0
    first = json.loads(capsys.readouterr().out)
    assert cli_commands.dispatch_cli(["session", "run", "--", "tools", "list"], project_root=tmp_path) == 0
    second = json.loads(capsys.readouterr().out)
    assert first["command_id"] != second["command_id"]

    assert cli_commands.dispatch_cli(
        ["feedback", "add", first["command_id"], "--tag", "poor_response", "--note", "wrong answer"],
        project_root=tmp_path,
    ) == 0
    record = json.loads(capsys.readouterr().out)
    assert record["command_id"] == first["command_id"]

    assert cli_commands.dispatch_cli(["feedback", "list", "--session", record["session_id"]], project_root=tmp_path) == 0
    listed = json.loads(capsys.readouterr().out)
    assert listed["feedback"][0]["tags"] == ["poor_response"]


def test_feedback_invalid_score_rejected(tmp_path: Path, capsys) -> None:
    write_agent_script(tmp_path, "print('cli ok')\n")
    assert cli_commands.dispatch_cli(["session", "start", "--name", "bad-score"], project_root=tmp_path) == 0
    capsys.readouterr()
    assert cli_commands.dispatch_cli(["session", "run", "--", "doctor"], project_root=tmp_path) == 0
    capsys.readouterr()

    assert cli_commands.dispatch_cli(["feedback", "rate", "--last", "--score", "6"], project_root=tmp_path) == 2


def test_feedback_unsafe_escalates_severity_and_redacts(tmp_path: Path, capsys) -> None:
    write_agent_script(tmp_path, "print('cli ok')\n")
    assert cli_commands.dispatch_cli(["session", "start", "--name", "unsafe-feedback"], project_root=tmp_path) == 0
    capsys.readouterr()
    assert cli_commands.dispatch_cli(["session", "run", "--", "doctor"], project_root=tmp_path) == 0
    capsys.readouterr()

    assert cli_commands.dispatch_cli(
        ["feedback", "unsafe", "--last", "--reason", "leaked password=hunter2 to sam@example.com"],
        project_root=tmp_path,
    ) == 0
    feedback = json.loads(capsys.readouterr().out)
    assert feedback["severity"] == "high"
    assert "unsafe_behavior" in feedback["tags"]
    assert "hunter2" not in feedback["reason"]
    assert "sam@example.com" not in feedback["reason"]
    assert "<REDACTED_SECRET>" in feedback["reason"]
    assert "<REDACTED_EMAIL>" in feedback["reason"]
    assert not (tmp_path / "data" / "memory.sqlite").exists()


def test_nested_session_run_is_rejected(tmp_path: Path) -> None:
    recorder = make_recorder(tmp_path)
    recorder.start(name="nested")

    with pytest.raises(ValueError, match="nested session"):
        recorder.run_command(["session", "status"])


def test_redact_text_masks_common_secret_forms() -> None:
    text = redact_text("Authorization: Bearer abcdefghijk password: hunter2 user test@example.com")

    assert "abcdefghijk" not in text
    assert "hunter2" not in text
    assert "test@example.com" not in text


def test_session_review_summarizes_clean_session(tmp_path: Path, capsys) -> None:
    write_agent_script(tmp_path, "print('clean ok')\n")
    assert cli_commands.dispatch_cli(["session", "start", "--name", "clean-review"], project_root=tmp_path) == 0
    capsys.readouterr()
    assert cli_commands.dispatch_cli(["session", "run", "--", "doctor"], project_root=tmp_path) == 0
    capsys.readouterr()

    assert cli_commands.dispatch_cli(["session", "review", "--last"], project_root=tmp_path) == 0
    review = json.loads(capsys.readouterr().out)

    assert review["pass_fail_summary"]["total"] == 1
    assert review["pass_fail_summary"]["failed"] == 0
    assert review["suspected_bugs"] == []
    assert (tmp_path / review["review_path"]).exists()


def test_session_review_identifies_failed_command(tmp_path: Path, capsys) -> None:
    write_agent_script(tmp_path, "import sys\nprint('boom', file=sys.stderr)\nsys.exit(7)\n")
    assert cli_commands.dispatch_cli(["session", "start", "--name", "failed-review"], project_root=tmp_path) == 0
    capsys.readouterr()
    assert cli_commands.dispatch_cli(["session", "run", "--", "weather", "doctor"], project_root=tmp_path) == 7
    capsys.readouterr()

    assert cli_commands.dispatch_cli(["session", "review", "--last"], project_root=tmp_path) == 0
    review = json.loads(capsys.readouterr().out)

    assert review["pass_fail_summary"]["failed"] == 1
    assert review["suspected_bugs"][0]["severity"] == "P1"
    assert "weather" in review["suspected_bugs"][0]["feature"]
    assert "Add CLI regression coverage" in review["suggested_regression_tests"][0]


def test_session_review_uses_user_feedback_flags(tmp_path: Path, capsys) -> None:
    write_agent_script(tmp_path, "print('route ok but answer bad')\n")
    assert cli_commands.dispatch_cli(["session", "start", "--name", "feedback-review"], project_root=tmp_path) == 0
    capsys.readouterr()
    assert cli_commands.dispatch_cli(["session", "run", "--", "--no-tools", "hello"], project_root=tmp_path) == 0
    command = json.loads(capsys.readouterr().out)
    assert cli_commands.dispatch_cli(
        ["feedback", "add", command["command_id"], "--tag", "bad_routing", "--note", "wrong tool path"],
        project_root=tmp_path,
    ) == 0
    capsys.readouterr()

    assert cli_commands.dispatch_cli(["session", "review", "--last"], project_root=tmp_path) == 0
    review = json.loads(capsys.readouterr().out)

    assert review["feedback_summary"]["tag_counts"]["bad_routing"] == 1
    assert review["routing_failures"][0]["tags"] == ["bad_routing"]
    assert review["suspected_bugs"][0]["severity"] == "P2"


def test_session_review_create_bugs_and_bugs_cli(tmp_path: Path, capsys) -> None:
    write_agent_script(tmp_path, "import sys\nprint('failed command', file=sys.stderr)\nsys.exit(2)\n")
    assert cli_commands.dispatch_cli(["session", "start", "--name", "bug-create"], project_root=tmp_path) == 0
    capsys.readouterr()
    assert cli_commands.dispatch_cli(["session", "run", "--", "doctor"], project_root=tmp_path) == 2
    capsys.readouterr()

    assert cli_commands.dispatch_cli(["session", "review", "--last", "--create-bugs"], project_root=tmp_path) == 0
    review = json.loads(capsys.readouterr().out)

    assert review["created_bugs"][0]["bug_id"] == "BUG-0001"
    assert (tmp_path / "bugs" / "BUG-0001.json").exists()
    assert cli_commands.dispatch_cli(["bugs", "list"], project_root=tmp_path) == 0
    listed = json.loads(capsys.readouterr().out)
    assert listed["bugs"][0]["bug_id"] == "BUG-0001"
    assert cli_commands.dispatch_cli(["bugs", "show", "BUG-0001"], project_root=tmp_path) == 0
    shown = json.loads(capsys.readouterr().out)
    assert shown["status"] == "open"
    assert cli_commands.dispatch_cli(["bugs", "export"], project_root=tmp_path) == 0
    exported = json.loads(capsys.readouterr().out)
    assert exported["bugs"][0]["bug_id"] == "BUG-0001"


def test_bug_ids_are_stable_and_incrementing(tmp_path: Path) -> None:
    store = BugStore(project_root=tmp_path)

    first = store.create_bug({"title": "one", "severity": "P3"})
    second = store.create_bug({"title": "two", "severity": "P2"})

    assert first.bug_id == "BUG-0001"
    assert second.bug_id == "BUG-0002"
    assert [bug.bug_id for bug in store.list_bugs()] == ["BUG-0002", "BUG-0001"]


def test_bug_reports_redact_secrets_and_personal_content(tmp_path: Path, capsys) -> None:
    write_agent_script(
        tmp_path,
        "import sys\nprint('password: hunter2 user sam@example.com phone 415-555-1212', file=sys.stderr)\nsys.exit(3)\n",
    )
    assert cli_commands.dispatch_cli(["session", "start", "--name", "redacted-bug"], project_root=tmp_path) == 0
    capsys.readouterr()
    assert cli_commands.dispatch_cli(["session", "run", "--", "doctor"], project_root=tmp_path) == 3
    capsys.readouterr()

    assert cli_commands.dispatch_cli(["session", "review", "--last", "--create-bugs"], project_root=tmp_path) == 0
    capsys.readouterr()
    bug_text = (tmp_path / "bugs" / "BUG-0001.json").read_text(encoding="utf-8")

    assert "hunter2" not in bug_text
    assert "sam@example.com" not in bug_text
    assert "415-555-1212" not in bug_text
    assert "<REDACTED_SECRET>" in bug_text
    assert "<REDACTED_EMAIL>" in bug_text
    assert "<REDACTED_PHONE>" in bug_text


def test_session_review_classifies_policy_bypass_as_p0(tmp_path: Path, capsys) -> None:
    write_agent_script(tmp_path, "print('policy bypass caused personal data leak')\n")
    assert cli_commands.dispatch_cli(["session", "start", "--name", "p0-review"], project_root=tmp_path) == 0
    capsys.readouterr()
    assert cli_commands.dispatch_cli(["session", "run", "--", "doctor"], project_root=tmp_path) == 0
    capsys.readouterr()
    assert cli_commands.dispatch_cli(
        ["feedback", "unsafe", "--last", "--reason", "ToolBroker bypass leaked personal data"],
        project_root=tmp_path,
    ) == 0
    capsys.readouterr()

    assert cli_commands.dispatch_cli(["session", "review", "--last", "--create-bugs"], project_root=tmp_path) == 0
    review = json.loads(capsys.readouterr().out)

    assert review["suspected_bugs"][0]["severity"] == "P0"
    assert review["created_bugs"][0]["severity"] == "P0"
    assert not (tmp_path / "data" / "memory.sqlite").exists()
