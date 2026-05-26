from __future__ import annotations

from pathlib import Path

from agent.config.runtime import RuntimeConfig
from agent.dogfood.suites import load_all_suites, load_suite
from agent.ui import cli_commands
from agent.ui.evals import EvalOptions, load_eval_cases, run_eval


ROOT = Path(__file__).resolve().parents[2]


def _runtime(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        lmstudio_model="fake-model",
        audit_log_path=str(tmp_path / "audit.jsonl"),
        capabilities_path="config/capabilities.yaml",
    )


def _options(tmp_path: Path, **kwargs) -> EvalOptions:
    return EvalOptions(
        report_path=tmp_path / "docs" / "EVAL_REPORT.md",
        results_path=tmp_path / "logs" / "eval_results.json",
        reports_dir=tmp_path / "reports" / "evals",
        **kwargs,
    )


def test_safe_autonomy_dogfood_suites_exist_and_validate() -> None:
    required = {
        "safe_autonomy_core",
        "channels_gateway",
        "telegram_mobile_scaffolding",
        "skill_proposals",
        "subagent_isolation",
        "sandbox_abstraction",
        "memory_continuity",
        "authorized_web_boundary",
    }
    suites = {suite.suite_id: suite for suite in load_all_suites(project_root=ROOT)}

    assert required.issubset(suites)
    for suite_id in required:
        suite = suites[suite_id]
        assert suite.requires_live_lmstudio is False
        assert suite.requires_web is False
        assert suite.requires_personal_data is False
        assert suite.risk_level == "LOW"
        assert suite.commands
        for command in suite.commands:
            assert command.command.startswith("python smart_agent.py ")
            assert "actions approve" not in command.command
            assert "send --from-action" not in command.command
            assert "live-send-probe" not in command.command
            assert "browser automate" not in command.command.lower()
            assert command.expected_behavior
            assert command.failure_signals


def test_safe_autonomy_core_suite_has_required_checks() -> None:
    suite = load_suite("safe_autonomy_core", project_root=ROOT)
    joined = "\n".join(command.command for command in suite.commands)

    assert "channels status" in joined
    assert "telegram status" in joined
    assert "mobile status" in joined
    assert "schedule dry-run" in joined
    assert "subagents policy" in joined
    assert "sandbox policy" in joined
    assert "brain switch lmstudio --dry-run" in joined
    assert "memory continuity status" in joined
    assert "eval run --safe-autonomy" in joined


def test_safe_autonomy_eval_cases_load() -> None:
    cases = load_eval_cases(ROOT / "eval_cases")
    safe_autonomy = {case.case_id: case for case in cases if case.category == "safe_autonomy"}

    assert "safe_autonomy.gateway_and_mobile_defaults" in safe_autonomy
    assert "safe_autonomy.proposals_scheduler_subagents_sandbox" in safe_autonomy
    assert "safe_autonomy.model_memory_web_boundary" in safe_autonomy
    assert "safe_autonomy.commands_and_registry" in safe_autonomy
    assert all(case.personal_data is False for case in safe_autonomy.values())
    assert all(case.live is False for case in safe_autonomy.values())


def test_safe_autonomy_evals_run_with_fixtures(tmp_path: Path) -> None:
    report = run_eval(_options(tmp_path, safe_autonomy=True), runtime=_runtime(tmp_path))

    by_name = {check["name"]: check for check in report["checks"]}
    assert report["status"] == "ok"
    assert by_name["safe_autonomy.gateway_and_mobile_defaults"]["status"] == "pass"
    assert by_name["safe_autonomy.proposals_scheduler_subagents_sandbox"]["status"] == "pass"
    assert by_name["safe_autonomy.model_memory_web_boundary"]["status"] == "pass"
    assert by_name["safe_autonomy.commands_and_registry"]["status"] == "pass"
    personal = [check for check in report["checks"] if check["personal_data"]]
    assert personal
    assert all(check["status"] == "skipped" for check in personal)


def test_safe_autonomy_eval_cli_flag(monkeypatch, capsys) -> None:
    captured = {}

    def fake_run(options):
        captured["options"] = options
        return {
            "status": "ok",
            "run_id": "safe-autonomy",
            "selected_categories": ["safe_autonomy"],
            "summary": {"pass": 1, "fail": 0, "skipped": 0},
            "checks": [],
            "report_path": "docs/EVAL_REPORT.md",
        }

    monkeypatch.setattr(cli_commands, "run_eval", fake_run)

    assert cli_commands.dispatch_cli(["eval", "run", "--safe-autonomy"], project_root=ROOT) == 0
    assert captured["options"].safe_autonomy is True
    assert "Eval run: safe-autonomy" in capsys.readouterr().out


def test_safe_autonomy_command_registry_entries() -> None:
    from agent.ui.command_registry import get_command

    for command_id in ("CMD-DOGFOOD-AUTONOMY-001", "CMD-EVAL-015", "CMD-EVAL-016"):
        record = get_command(command_id)
        assert record is not None
        assert record.status == "active"
        assert record.risk_level in {"SAFE", "LOW"}
        assert "safe" in record.docs_link.lower() or "autonomy" in record.docs_link.lower()
