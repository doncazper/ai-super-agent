from pathlib import Path
import subprocess

import pytest

from agent.qa import runner
from agent.qa.errors import CommandQAUnsafeError
from agent.qa.logging import read_last_report
from agent.qa.models import QAPlan, QAPlanCommand, utc_now_iso
from agent.qa.redaction import redact_text
from agent.qa.runner import run_safe_commands, validate_runner_command
from agent.ui import cli_commands


ROOT = Path(__file__).resolve().parents[2]


def _command(**overrides) -> QAPlanCommand:
    data = {
        "command_id": "CMD-TEST-001",
        "command": "python smart_agent.py setup",
        "group": "Doctor/status/config",
        "qa_tier": 1,
        "risk_level": "SAFE",
        "status": "active",
        "safe_to_auto_run": True,
        "skip_reason": "",
        "requires_approval": False,
        "requires_provider_setup": False,
        "requires_disposable_workspace": False,
        "example": "python smart_agent.py setup",
        "docs_link": "README.md",
    }
    data.update(overrides)
    return QAPlanCommand(**data)


def test_secret_redaction() -> None:
    text = "SERPAPI_API_KEY=secret-value email me at person@example.com sk-abc123456789XYZ"
    redacted = redact_text(text)
    assert "secret-value" not in redacted
    assert "person@example.com" not in redacted
    assert "sk-abc" not in redacted


def test_disallowed_command_blocked() -> None:
    with pytest.raises(CommandQAUnsafeError):
        validate_runner_command(_command(safe_to_auto_run=False, skip_reason="blocked"))


def test_high_critical_denied() -> None:
    with pytest.raises(CommandQAUnsafeError):
        validate_runner_command(_command(qa_tier=7, risk_level="CRITICAL"))


def test_placeholder_command_skipped() -> None:
    with pytest.raises(CommandQAUnsafeError):
        validate_runner_command(_command(example="python smart_agent.py commands show <command_id>"))


def test_shell_control_syntax_rejected() -> None:
    with pytest.raises(CommandQAUnsafeError):
        validate_runner_command(_command(example="python smart_agent.py setup; rm -rf workspace"))


def test_safe_command_runs_and_report_written(tmp_path: Path) -> None:
    result = run_safe_commands(project_root=ROOT, tier=1, group="Command QA", limit=1)
    assert result["run_id"]
    records = result["records"]
    assert records
    assert records[0]["command_id"].startswith("CMD-QA-")
    assert records[0]["status"] == "passed"
    report = result["report"]
    assert (ROOT / report["jsonl_path"]).exists()
    assert (ROOT / report["markdown_path"]).exists()
    assert read_last_report(ROOT)["run_id"] == result["run_id"]


def test_tier_zero_runs_registry_validation() -> None:
    result = run_safe_commands(project_root=ROOT, tier=0, limit=1)
    records = result["records"]
    assert records
    assert records[0]["qa_tier"] == 0
    assert records[0]["status"] in {"passed", "skipped"}


def test_tier_two_rejected() -> None:
    with pytest.raises(CommandQAUnsafeError):
        run_safe_commands(project_root=ROOT, tier=2)


def test_timeout_handled(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    command = _command()
    plan = QAPlan(
        plan_id="qa_plan_test",
        generated_at=utc_now_iso(),
        command_count=1,
        safe_count=1,
        skipped_count=0,
        blocked_count=0,
        commands_by_tier={"1": 1},
        commands_by_group={"Doctor/status/config": 1},
        recommended_first_batch=[command.to_dict()],
        setup_required=[],
        risks=[],
        notes=[],
        commands=[command],
    )

    def fake_generate_qa_plan(**kwargs):
        return plan

    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=["python"], timeout=1, output="token=secret-value", stderr="oops")

    monkeypatch.setattr(runner, "generate_qa_plan", fake_generate_qa_plan)
    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    result = run_safe_commands(project_root=tmp_path, tier=1, limit=1, timeout_seconds=1)
    record = result["records"][0]
    assert record["status"] == "failed"
    assert record["failure_type"] == "timeout"
    assert "secret-value" not in record["redacted_stdout_excerpt"]


def test_qa_commands_run_and_report_cli(capsys) -> None:
    assert cli_commands.dispatch_cli(["qa", "commands", "run", "--tier", "0", "--limit", "1"], project_root=ROOT) == 0
    payload = capsys.readouterr().out
    assert "qa_run_" in payload
    assert cli_commands.dispatch_cli(["qa", "commands", "report", "--last"], project_root=ROOT) == 0
    report = capsys.readouterr().out
    assert "jsonl_path" in report
