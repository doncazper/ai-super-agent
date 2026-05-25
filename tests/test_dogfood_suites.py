from __future__ import annotations

import json
from pathlib import Path

from agent.dogfood.runner import CommandExecution, parse_agent_command, run_suite
from agent.dogfood.planner import dogfood_next
from agent.dogfood.suites import load_all_suites, load_suite
from agent.session_logs.recorder import SessionRecorder
from agent.session_logs.store import SessionLogStore
from agent.ui import cli_commands


ROOT = Path(__file__).resolve().parents[1]


def test_dogfood_cli_list_and_show(capsys) -> None:
    assert cli_commands.dispatch_cli(["dogfood", "list"], project_root=ROOT) == 0
    listed = json.loads(capsys.readouterr().out)
    suite_ids = {suite["suite_id"] for suite in listed["suites"]}
    assert {"core", "weather", "all_safe", "personal_dry_run"}.issubset(suite_ids)

    assert cli_commands.dispatch_cli(["dogfood", "show", "core"], project_root=ROOT) == 0
    shown = json.loads(capsys.readouterr().out)
    assert shown["suite_id"] == "core"
    assert shown["commands"]


def test_dogfood_plan_next_and_checklist_cli(capsys) -> None:
    assert cli_commands.dispatch_cli(["dogfood", "plan"], project_root=ROOT) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["recommended_next"]["next_type"]
    assert any(step["title"] == "Start session" for step in plan["daily_safe_smoke"])

    assert cli_commands.dispatch_cli(["dogfood", "next"], project_root=ROOT) == 0
    next_step = json.loads(capsys.readouterr().out)
    assert "commands" in next_step
    assert "maturity_notes" in next_step

    assert cli_commands.dispatch_cli(["dogfood", "checklist"], project_root=ROOT) == 0
    checklist = json.loads(capsys.readouterr().out)
    assert checklist["daily"]
    assert checklist["weekly"]


def test_dogfood_next_considers_maturity_and_last_session(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "FEATURE_MATURITY.md").write_text(
        "Manual Dogfood Command Suites: first real manual dogfood session still pending",
        encoding="utf-8",
    )
    next_step = dogfood_next(project_root=tmp_path)
    assert next_step["next_type"] == "start_daily_session"
    assert next_step["suite"] == "all_safe"
    assert "first real manual dogfood session still pending" in next_step["maturity_notes"]

    recorder = SessionRecorder(SessionLogStore(tmp_path / "reports" / "sessions", project_root=tmp_path), project_root=tmp_path)
    session = recorder.start(name="active-dogfood")
    active_next = dogfood_next(project_root=tmp_path)
    assert active_next["next_type"] == "continue_active_session"
    assert active_next["session_id"] == session.session_id


def test_dogfood_suite_yaml_validates() -> None:
    suites = load_all_suites(project_root=ROOT)

    assert len(suites) >= 15
    for suite in suites:
        assert suite.suite_id
        assert suite.commands
        for command in suite.commands:
            assert command.id
            assert command.command.startswith("python smart_agent.py ")
            assert command.expected_behavior
            assert command.failure_signals


def test_messaging_dogfood_suites_exist_and_validate() -> None:
    required = {
        "messaging_core",
        "messaging_handoff",
        "messaging_ios_compose",
        "messaging_macos_probe",
        "messaging_send_dry_run",
        "lead_response",
    }
    suites = {suite.suite_id: suite for suite in load_all_suites(project_root=ROOT)}

    assert required.issubset(suites)
    for suite_id in required:
        suite = suites[suite_id]
        assert suite.requires_personal_data is False
        assert suite.default_enabled is False
        assert suite.risk_level in {"LOW", "MEDIUM"}
        assert all(command.failure_signals for command in suite.commands)


def test_all_safe_contains_no_personal_data_commands() -> None:
    suite = load_suite("all_safe", project_root=ROOT)

    assert suite.requires_personal_data is False
    for command in suite.commands:
        assert "personal_data" not in command.tags
        assert "calendar" not in command.command
        assert "contacts" not in command.command
        assert "email" not in command.command
        assert "messages" not in command.command
        assert "live-send-probe" not in command.command
        assert "send --from-action" not in command.command


def test_personal_dry_run_uses_preflight_only() -> None:
    suite = load_suite("personal_dry_run", project_root=ROOT)

    assert suite.requires_personal_data is False
    assert suite.default_enabled is False
    for command in suite.commands:
        assert command.command.startswith('python smart_agent.py preflight "')


def test_messaging_dry_run_suites_do_not_execute_live_sends() -> None:
    for suite_id in ("messaging_macos_probe", "messaging_send_dry_run", "lead_response"):
        suite = load_suite(suite_id, project_root=ROOT)
        for command in suite.commands:
            assert "live-send-probe" not in command.command
            if " send --from-action " in command.command:
                assert command.command.startswith('python smart_agent.py preflight "')
            assert "actions approve" not in command.command


def test_lead_response_suite_uses_mock_or_preflight_data() -> None:
    suite = load_suite("lead_response", project_root=ROOT)

    joined = "\n".join(command.command for command in suite.commands)
    assert "apple-business mock-inbound" in joined
    assert "mock-lead-001" in joined
    assert "preflight \"leads create-send-action" in joined
    assert "leads send" not in joined


def test_dogfood_run_with_mock_executor_records_results(tmp_path: Path) -> None:
    _write_suite(tmp_path, "mini", ["python smart_agent.py doctor", "python smart_agent.py tools list"])

    def executor(args, command):
        return CommandExecution(0, f"ok {command.id}", "", 5)

    report = run_suite("mini", project_root=tmp_path, executor=executor)

    assert report["status"] == "ok"
    assert report["summary"] == {"total": 2, "passed": 2, "failed": 0, "skipped": 0}
    assert report["results"][0]["stdout_preview"] == "ok cmd_1"


def test_dogfood_run_continues_and_records_failed_command(tmp_path: Path) -> None:
    _write_suite(tmp_path, "mini", ["python smart_agent.py doctor", "python smart_agent.py tools list"])

    def executor(args, command):
        exit_code = 3 if command.id == "cmd_1" else 0
        return CommandExecution(exit_code, "", "boom", 5)

    report = run_suite("mini", project_root=tmp_path, executor=executor)

    assert report["status"] == "failed"
    assert report["summary"]["failed"] == 1
    assert [result["status"] for result in report["results"]] == ["failed", "passed"]


def test_dogfood_session_integration_records_commands(tmp_path: Path) -> None:
    _write_suite(tmp_path, "mini", ["python smart_agent.py doctor"])
    (tmp_path / "smart_agent.py").write_text("print('session dogfood ok')\n", encoding="utf-8")
    recorder = SessionRecorder(SessionLogStore(tmp_path / "reports" / "sessions", project_root=tmp_path), project_root=tmp_path)
    recorder.start(name="dogfood")

    report = run_suite(
        "mini",
        project_root=tmp_path,
        use_session=True,
        session_recorder=recorder,
    )

    assert report["status"] == "ok"
    active = recorder.store.get_active()
    assert active is not None
    assert active.command_count == 1


def test_parse_agent_command_rejects_non_agent_commands() -> None:
    assert parse_agent_command("python smart_agent.py doctor") == ["doctor"]

    try:
        parse_agent_command("sh -c 'echo nope'")
    except ValueError as exc:
        assert "smart_agent.py" in str(exc)
    else:
        raise AssertionError("expected command validation failure")


def test_live_test_runbook_docs_exist_and_reference_session_review() -> None:
    required = [
        ROOT / "docs" / "dogfood" / "LIVE_TEST_RUNBOOK.md",
        ROOT / "docs" / "dogfood" / "DAILY_DOGFOOD_CHECKLIST.md",
        ROOT / "docs" / "dogfood" / "WEEKLY_RELEASE_CHECK.md",
        ROOT / "docs" / "templates" / "dogfood_session_notes.md",
    ]
    for path in required:
        assert path.exists(), path
    daily = (ROOT / "docs" / "dogfood" / "DAILY_DOGFOOD_CHECKLIST.md").read_text(encoding="utf-8")
    assert "session start" in daily
    assert "session review" in daily
    assert "session log" in daily.lower()


def _write_suite(tmp_path: Path, suite_id: str, commands: list[str]) -> None:
    suites_dir = tmp_path / "dogfood_suites"
    suites_dir.mkdir()
    command_yaml = "\n".join(
        f"""  - id: cmd_{index}
    description: Command {index}
    command: {json.dumps(command)}
    expected_behavior: Expected behavior {index}
    failure_signals: Failure {index}
    tags: [test]
"""
        for index, command in enumerate(commands, start=1)
    )
    (suites_dir / f"{suite_id}.yaml").write_text(
        f"""suite_id: {suite_id}
name: Mini
description: Mini suite
risk_level: LOW
requires_live_lmstudio: false
requires_web: false
requires_personal_data: false
default_enabled: true
commands:
{command_yaml}""",
        encoding="utf-8",
    )
