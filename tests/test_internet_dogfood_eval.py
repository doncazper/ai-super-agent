from __future__ import annotations

import json
from pathlib import Path

from agent.dogfood.suites import load_all_suites, load_suite
from agent.ui import cli_commands
from agent.ui.evals import EvalOptions, load_eval_cases, run_eval


ROOT = Path(__file__).resolve().parents[1]


def test_internet_dogfood_suites_exist_and_validate() -> None:
    required = {
        "internet_core",
        "web_research",
        "web_fetch",
        "web_providers",
        "web_blocked_sources",
    }
    suites = {suite.suite_id: suite for suite in load_all_suites(project_root=ROOT)}

    assert required.issubset(suites)
    for suite_id in required:
        suite = suites[suite_id]
        assert suite.requires_personal_data is False
        assert suite.risk_level in {"LOW", "MEDIUM"}
        assert suite.commands
        assert all(command.command.startswith("python smart_agent.py ") for command in suite.commands)
        assert all(command.failure_signals for command in suite.commands)


def test_live_internet_suites_are_not_default_enabled() -> None:
    for suite_id in ("web_research", "web_fetch", "web_blocked_sources"):
        suite = load_suite(suite_id, project_root=ROOT)
        assert suite.requires_web is True
        assert suite.default_enabled is False

    for suite_id in ("internet_core", "web_providers"):
        suite = load_suite(suite_id, project_root=ROOT)
        assert suite.requires_web is False
        assert suite.default_enabled is True


def test_internet_eval_cases_load_from_subdirectory() -> None:
    cases = load_eval_cases(ROOT / "eval_cases")
    internet_cases = [case for case in cases if case.category == "internet"]

    assert len(internet_cases) >= 5
    assert {case.case_id for case in internet_cases}.issuperset(
        {
            "internet.source_list_and_citations",
            "internet.fetch_failures_reported",
            "internet.prompt_injection_ignored",
            "internet.paid_provider_not_default",
            "internet.audit_network_domains",
        }
    )


def test_internet_eval_fixture_checks_pass(tmp_path: Path) -> None:
    report = run_eval(
        EvalOptions(
            internet=True,
            cases_path=ROOT / "eval_cases",
            report_path=tmp_path / "EVAL_REPORT.md",
            results_path=tmp_path / "eval_results.json",
            reports_dir=tmp_path / "reports",
        )
    )

    assert report["status"] == "ok"
    assert report["selected_categories"] == ["internet"]
    checks = [check for check in report["checks"] if check["category"] == "internet"]
    assert checks
    assert all(check["status"] == "pass" for check in checks)
    assert any(check["name"] == "internet.fetch_failures_reported" for check in checks)
    assert any(check["details"].get("paid_api_used") is False for check in checks)
    assert "Internet evals are fixture-backed" in (tmp_path / "EVAL_REPORT.md").read_text(encoding="utf-8")


def test_eval_cli_accepts_internet_flags(monkeypatch, capsys) -> None:
    seen: dict[str, bool] = {}

    def fake_run_eval(options: EvalOptions):
        seen["internet"] = options.internet
        return {
            "run_id": "eval-test",
            "status": "ok",
            "selected_categories": ["internet"],
            "summary": {"pass": 1, "fail": 0, "skipped": 0},
            "checks": [],
            "report_path": "docs/EVAL_REPORT.md",
        }

    monkeypatch.setattr(cli_commands, "run_eval", fake_run_eval)

    assert cli_commands.dispatch_cli(["eval", "run", "--internet", "--json"], project_root=ROOT) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert seen["internet"] is True

    assert cli_commands.dispatch_cli(["eval", "report", "--internet"], project_root=ROOT) == 0
