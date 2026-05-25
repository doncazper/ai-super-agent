from __future__ import annotations

import json
import re
from pathlib import Path

from agent.dogfood.suites import load_all_suites, load_suite
from agent.ui import cli_commands
from agent.ui.command_registry import COMMANDS
from agent.ui.evals import EvalOptions, load_eval_cases, run_eval


ROOT = Path(__file__).resolve().parents[1]


def test_forum_dogfood_suites_exist_and_validate() -> None:
    required = {
        "reddit_core",
        "reddit_research",
        "forum_multilingual",
        "v2ex",
        "chinese_forum_discovery",
    }
    suites = {suite.suite_id: suite for suite in load_all_suites(project_root=ROOT)}

    assert required.issubset(suites)
    for suite_id in required:
        suite = suites[suite_id]
        assert suite.requires_personal_data is False
        assert suite.risk_level == "MEDIUM"
        assert suite.commands
        assert all(command.command.startswith("python smart_agent.py ") for command in suite.commands)
        assert all(command.failure_signals for command in suite.commands)


def test_forum_dogfood_live_provider_suites_are_default_disabled() -> None:
    for suite_id in ("reddit_core", "reddit_research", "v2ex", "chinese_forum_discovery"):
        suite = load_suite(suite_id, project_root=ROOT)
        assert suite.requires_web is True
        assert suite.default_enabled is False

    multilingual = load_suite("forum_multilingual", project_root=ROOT)
    assert multilingual.requires_web is False
    assert multilingual.default_enabled is False


def test_all_safe_excludes_live_reddit_and_forum_provider_commands() -> None:
    suite = load_suite("all_safe", project_root=ROOT)
    joined = "\n".join(command.command for command in suite.commands)

    assert "reddit search" not in joined
    assert "reddit post" not in joined
    assert "reddit summarize" not in joined
    assert "v2ex latest" not in joined
    assert "cn-forums search" not in joined


def test_forum_eval_cases_load_from_subdirectory_and_are_sanitized() -> None:
    cases = load_eval_cases(ROOT / "eval_cases")
    forum_cases = [case for case in cases if case.category == "forums"]

    assert len(forum_cases) >= 5
    assert {case.case_id for case in forum_cases}.issuperset(
        {
            "forums.no_fabricated_sources",
            "forums.translation_labeled_generated",
            "forums.prompt_injection_ignored",
            "forums.no_scraping_or_paid_defaults",
            "forums.retention_policy_enforced",
        }
    )

    raw_fixture_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((ROOT / "eval_cases" / "forums").glob("*.json"))
    )
    assert not re.search(r"[\w.+-]+@[\w.-]+\.\w+", raw_fixture_text)
    assert not re.search(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b", raw_fixture_text)
    assert "author_display" not in raw_fixture_text
    assert "\"author\"" not in raw_fixture_text


def test_forum_eval_fixture_checks_pass(tmp_path: Path) -> None:
    report = run_eval(
        EvalOptions(
            forums=True,
            cases_path=ROOT / "eval_cases",
            report_path=tmp_path / "EVAL_REPORT.md",
            results_path=tmp_path / "eval_results.json",
            reports_dir=tmp_path / "reports",
        )
    )

    assert report["status"] == "ok"
    assert report["selected_categories"] == ["forums"]
    checks = [check for check in report["checks"] if check["category"] == "forums"]
    assert checks
    assert all(check["status"] == "pass" for check in checks)
    assert any(check["name"] == "forums.translation_labeled_generated" for check in checks)
    assert any(check["details"].get("unavailable_count") for check in checks)
    assert "Forum evals are fixture-backed" in (tmp_path / "EVAL_REPORT.md").read_text(encoding="utf-8")


def test_eval_cli_accepts_forum_flags(monkeypatch, capsys) -> None:
    seen: dict[str, bool] = {}

    def fake_run_eval(options: EvalOptions):
        seen["forums"] = options.forums
        return {
            "run_id": "eval-forums-test",
            "status": "ok",
            "selected_categories": ["forums"],
            "summary": {"pass": 1, "fail": 0, "skipped": 0},
            "checks": [],
            "report_path": "docs/EVAL_REPORT.md",
        }

    monkeypatch.setattr(cli_commands, "run_eval", fake_run_eval)

    assert cli_commands.dispatch_cli(["eval", "run", "--forums", "--json"], project_root=ROOT) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert seen["forums"] is True

    assert cli_commands.dispatch_cli(["eval", "report", "--forums"], project_root=ROOT) == 0


def test_forum_eval_and_dogfood_commands_are_registered() -> None:
    commands = {record.command for record in COMMANDS}

    assert "python smart_agent.py eval run --forums" in commands
    assert "python smart_agent.py eval report --forums" in commands
    assert "python smart_agent.py dogfood run reddit_core --session" in commands
    assert "python smart_agent.py dogfood run reddit_research --session" in commands
    assert "python smart_agent.py dogfood run forum_multilingual --session" in commands
