from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent.qa.models import QAPlan, QAPlanCommand, utc_now_iso
from agent.qa.service import QAService
from agent.qa.errors import CommandQAUnsafeError
from agent.ui import cli_commands


def _plan(command: QAPlanCommand) -> QAPlan:
    return QAPlan(
        plan_id="qa_plan_test",
        generated_at=utc_now_iso(),
        command_count=1,
        safe_count=1 if command.safe_to_auto_run else 0,
        skipped_count=0,
        blocked_count=0,
        commands_by_tier={str(command.qa_tier): 1},
        commands_by_group={command.group: 1},
        recommended_first_batch=[command.to_dict()],
        setup_required=[],
        risks=[],
        notes=[],
        commands=[command],
    )


def _command(**overrides: object) -> QAPlanCommand:
    values = {
        "command_id": "CMD-QA-TEST",
        "command": "python smart_agent.py qa status",
        "group": "Command QA",
        "qa_tier": 1,
        "risk_level": "SAFE",
        "status": "active",
        "safe_to_auto_run": True,
        "skip_reason": "",
        "requires_approval": False,
        "requires_provider_setup": False,
        "requires_disposable_workspace": False,
        "missing_metadata": [],
        "docs_link": "docs/qa/COMMAND_QA_DASHBOARD.md",
        "example": "python smart_agent.py qa status",
    }
    values.update(overrides)
    return QAPlanCommand(**values)  # type: ignore[arg-type]


def test_service_status_returns_json_serializable_output(tmp_path: Path) -> None:
    result = QAService(tmp_path).get_qa_status()

    json.dumps(result)
    assert result["status"] == "ok"
    assert result["read_only"] is True
    assert result["data"]["boundary"] == "service"


def test_dashboard_read_only_methods_do_not_execute_commands(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_runner(**_: object) -> dict[str, object]:
        raise AssertionError("read-only dashboard must not execute commands")

    monkeypatch.setattr("agent.qa.service.run_safe_commands", fail_runner)

    service = QAService(tmp_path)
    json.dumps(service.get_qa_status())
    json.dumps(service.get_command_coverage())
    json.dumps(service.get_next_safe_batch())


def test_action_method_respects_safe_only_tier(tmp_path: Path) -> None:
    with pytest.raises(CommandQAUnsafeError):
        QAService(tmp_path).run_safe_batch(tier=2)


def test_high_and_critical_commands_are_blocked(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    high_command = _command(risk_level="HIGH", command="python smart_agent.py email metadata")
    monkeypatch.setattr("agent.qa.service.generate_qa_plan", lambda **_: _plan(high_command))

    with pytest.raises(CommandQAUnsafeError):
        QAService(tmp_path).run_safe_batch(tier=1)


def test_personal_data_commands_are_blocked(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    personal_command = _command(command_id="CMD-PERSONAL", command="python smart_agent.py calendar read", group="Calendar")
    monkeypatch.setattr("agent.qa.service.generate_qa_plan", lambda **_: _plan(personal_command))

    with pytest.raises(CommandQAUnsafeError):
        QAService(tmp_path).run_safe_batch(tier=1)


def test_safe_action_delegates_to_runner_with_safe_boundary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    safe_command = _command()
    monkeypatch.setattr("agent.qa.service.generate_qa_plan", lambda **_: _plan(safe_command))
    called: dict[str, object] = {}

    def fake_runner(**kwargs: object) -> dict[str, object]:
        called.update(kwargs)
        return {"run_id": "qa_run_fake", "records": [], "report": {"record_count": 0}}

    monkeypatch.setattr("agent.qa.service.run_safe_commands", fake_runner)

    result = QAService(tmp_path).run_safe_batch(tier=1, limit=1)

    assert result["action"] == "run_safe_batch"
    assert result["safe_only"] is True
    assert called["safe_only"] is True
    assert called["limit"] == 1


def test_service_redacts_secrets_from_summaries(tmp_path: Path) -> None:
    bugs = tmp_path / "bugs"
    bugs.mkdir()
    (bugs / "BUG-0001.json").write_text(
        json.dumps(
            {
                "bug_id": "BUG-0001",
                "status": "open",
                "severity": "P3",
                "actual_behavior": "token=sk-abc1234567890",
                "suggested_regression_test": "tests/regressions/test_bug.py",
            }
        ),
        encoding="utf-8",
    )

    result = QAService(tmp_path).get_open_bugs()
    payload = json.dumps(result)

    assert "sk-abc1234567890" not in payload
    assert "[REDACTED" in payload


def test_cli_dashboard_uses_service_layer(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli_commands.dispatch_cli(["qa", "dashboard"], project_root=tmp_path)
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output["read_only"] is True
    assert output["backend_boundary"] == "agent.qa.service.QAService"


def test_future_frontend_contract_docs_exist() -> None:
    root = Path(__file__).resolve().parents[2]
    assert (root / "docs/qa/QA_FRONTEND_BACKEND_BOUNDARY.md").exists()
    assert (root / "docs/qa/QA_DASHBOARD_API_CONTRACT.md").exists()
