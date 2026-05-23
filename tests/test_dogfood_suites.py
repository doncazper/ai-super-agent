from __future__ import annotations

import json
from pathlib import Path

from agent.dogfood.runner import CommandExecution, parse_agent_command, run_suite
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


def test_dogfood_suite_yaml_validates() -> None:
    suites = load_all_suites(project_root=ROOT)

    assert len(suites) >= 9
    for suite in suites:
        assert suite.suite_id
        assert suite.commands
        for command in suite.commands:
            assert command.id
            assert command.command.startswith("python smart_agent.py ")
            assert command.expected_behavior
            assert command.failure_signals


def test_all_safe_contains_no_personal_data_commands() -> None:
    suite = load_suite("all_safe", project_root=ROOT)

    assert suite.requires_personal_data is False
    for command in suite.commands:
        assert "personal_data" not in command.tags
        assert "calendar" not in command.command
        assert "contacts" not in command.command
        assert "email" not in command.command
        assert "messages" not in command.command


def test_personal_dry_run_uses_preflight_only() -> None:
    suite = load_suite("personal_dry_run", project_root=ROOT)

    assert suite.requires_personal_data is False
    assert suite.default_enabled is False
    for command in suite.commands:
        assert command.command.startswith('python smart_agent.py preflight "')


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
