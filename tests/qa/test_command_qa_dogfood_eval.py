from pathlib import Path

from agent.dogfood.suites import load_suite
from agent.config.runtime import RuntimeConfig
from agent.ui import cli_commands
from agent.ui.evals import EvalOptions, load_eval_cases, run_eval


ROOT = Path(__file__).resolve().parents[2]


def test_command_qa_dogfood_suites_validate() -> None:
    for suite_id in ("command_qa_core", "command_qa_sandbox", "command_qa_self_heal"):
        suite = load_suite(suite_id, project_root=ROOT)
        assert suite.risk_level == "LOW"
        assert suite.requires_live_lmstudio is False
        assert suite.requires_web is False
        assert suite.requires_personal_data is False
        assert suite.commands
        for command in suite.commands:
            assert command.command.startswith("python smart_agent.py qa ")
            assert "approve" not in command.command
            assert "commit" not in command.command
            assert "push" not in command.command
            assert command.expected_behavior
            assert command.failure_signals


def test_command_qa_eval_fixtures_load() -> None:
    cases = [case for case in load_eval_cases(ROOT / "eval_cases") if case.category == "command_qa"]
    assert {case.case_id for case in cases} >= {
        "command_qa.safe_plan_boundaries",
        "command_qa.sandbox_boundaries",
        "command_qa.self_heal_conservative",
    }
    assert all(case.personal_data is False for case in cases)
    assert all(case.live is False for case in cases)


def test_command_qa_eval_run_with_fixtures(tmp_path: Path) -> None:
    report = run_eval(
        EvalOptions(
            command_qa=True,
            report_path=tmp_path / "docs/EVAL_REPORT.md",
            results_path=tmp_path / "logs/eval_results.json",
            reports_dir=tmp_path / "reports/evals",
        ),
        runtime=RuntimeConfig(
            lmstudio_model="fake-model",
            audit_log_path=str(tmp_path / "audit.jsonl"),
            capabilities_path="config/capabilities.yaml",
        ),
    )
    assert report["status"] == "ok"
    assert report["selected_categories"] == ["command_qa"]
    assert report["summary"]["fail"] == 0


def test_command_qa_eval_cli_flag(monkeypatch, capsys) -> None:
    captured = {}

    def fake_run(options):
        captured["options"] = options
        return {
            "status": "ok",
            "run_id": "command-qa",
            "selected_categories": ["command_qa"],
            "summary": {"pass": 1, "fail": 0, "skipped": 0},
            "checks": [],
            "report_path": "docs/EVAL_REPORT.md",
        }

    monkeypatch.setattr(cli_commands, "run_eval", fake_run)
    assert cli_commands.dispatch_cli(["eval", "run", "--command-qa"], project_root=ROOT) == 0
    assert captured["options"].command_qa is True
    assert "Eval run: command-qa" in capsys.readouterr().out
