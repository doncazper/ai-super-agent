from __future__ import annotations

import json
from pathlib import Path

from agent.dogfood.suites import load_suite
from agent.native_skills.test_harness import run_skill_test
from agent.ui import cli_commands
from agent.ui.command_registry import COMMANDS
from agent.ui.evals import EvalOptions, load_eval_cases, run_eval
from smart_agent import _run_skills_command
from tests.test_native_skill_manifests import manifest_data, write_project


ROOT = Path(__file__).resolve().parents[2]


def test_safe_skill_test_passes(tmp_path: Path) -> None:
    write_project(tmp_path, manifest_data(skill_id="safe_doc", category="documents"))

    report = run_skill_test(tmp_path, skill_id="safe_doc")

    assert report["status"] == "ok", report
    assert report["summary"]["fail"] == 0
    assert any(check["category"] == "prompt_injection fixture" for check in report["checks"])
    assert any(check["category"] == "secret fixture" for check in report["checks"])


def test_high_risk_skill_skipped_by_default(tmp_path: Path) -> None:
    write_project(tmp_path, manifest_data(skill_id="high_skill", risk_level="HIGH", approval_required=True))

    report = run_skill_test(tmp_path, skill_id="high_skill")

    assert report["status"] == "ok"
    assert report["summary"]["skipped"] == 1
    assert "HIGH skill skipped" in report["checks"][0]["reason"]


def test_personal_data_skill_skipped_by_default(tmp_path: Path) -> None:
    write_project(
        tmp_path,
        manifest_data(
            skill_id="personal_skill",
            risk_level="HIGH",
            trust_level="LOCAL_PRIVATE_DATA",
            approval_required=True,
            status="disabled",
        ),
    )

    report = run_skill_test(tmp_path, skill_id="personal_skill")

    assert report["status"] == "ok"
    assert report["summary"]["skipped"] == 1


def test_missing_dependency_reported_as_skipped(tmp_path: Path) -> None:
    write_project(tmp_path, manifest_data(skill_id="needs_setup", required_env=["MISSING_NATIVE_SKILL_TOKEN"]))

    report = run_skill_test(tmp_path, skill_id="needs_setup")
    dependency = next(check for check in report["checks"] if check["category"] == "dependency gating")

    assert dependency["status"] == "skipped"
    assert dependency["details"]["dependency_status"] == "requires_setup"


def test_prompt_injection_and_secret_fixtures_caught(tmp_path: Path) -> None:
    write_project(tmp_path, manifest_data(skill_id="fixture_skill"))

    report = run_skill_test(tmp_path, skill_id="fixture_skill")
    checks = {check["category"]: check for check in report["checks"]}

    assert checks["prompt_injection fixture"]["status"] == "pass"
    assert checks["secret fixture"]["status"] == "pass"


def test_skill_test_cli_and_dogfood_cli(tmp_path: Path, monkeypatch, capsys) -> None:
    write_project(tmp_path, manifest_data(skill_id="cli_skill"))
    monkeypatch.chdir(tmp_path)

    assert _run_skills_command(["test", "cli_skill"], broker=None) == 0  # type: ignore[arg-type]
    tested = json.loads(capsys.readouterr().out)
    assert tested["status"] == "ok"

    assert _run_skills_command(["test", "--all-safe"], broker=None) == 0  # type: ignore[arg-type]
    all_safe = json.loads(capsys.readouterr().out)
    assert all_safe["skill_id"] == "all-safe"

    assert _run_skills_command(["dogfood", "cli_skill"], broker=None) == 0  # type: ignore[arg-type]
    dogfood = json.loads(capsys.readouterr().out)
    assert dogfood["status"] == "ok"
    assert "python smart_agent.py skills test cli_skill" in dogfood["commands"]


def test_native_skill_dogfood_suite_yaml_validates() -> None:
    core = load_suite("native_skills_core", project_root=ROOT)
    vetting = load_suite("native_skill_vetting", project_root=ROOT)

    assert core.default_enabled is True
    assert vetting.requires_personal_data is False
    assert all(command.command.startswith("python smart_agent.py ") for command in core.commands + vetting.commands)


def test_native_skill_eval_cases_and_report_generated(tmp_path: Path) -> None:
    cases = load_eval_cases(ROOT / "eval_cases")
    native_cases = [case for case in cases if case.category == "native_skills"]

    assert {case.case_id for case in native_cases}.issuperset(
        {
            "native_skills.safe_harness_defaults",
            "native_skills.fixtures_caught",
            "native_skills.dogfood_and_registry",
        }
    )

    report = run_eval(
        EvalOptions(
            native_skills=True,
            cases_path=ROOT / "eval_cases",
            report_path=tmp_path / "EVAL_REPORT.md",
            results_path=tmp_path / "eval_results.json",
            reports_dir=tmp_path / "reports",
        )
    )

    assert report["status"] == "ok"
    assert report["selected_categories"] == ["native_skills"]
    assert all(check["status"] == "pass" for check in report["checks"] if check["category"] == "native_skills")


def test_eval_cli_accepts_native_skills_flag(monkeypatch, capsys) -> None:
    seen: dict[str, bool] = {}

    def fake_run_eval(options: EvalOptions):
        seen["native_skills"] = options.native_skills
        return {
            "run_id": "eval-native-skills-test",
            "status": "ok",
            "selected_categories": ["native_skills"],
            "summary": {"pass": 1, "fail": 0, "skipped": 0},
            "checks": [],
            "report_path": "docs/EVAL_REPORT.md",
        }

    monkeypatch.setattr(cli_commands, "run_eval", fake_run_eval)

    assert cli_commands.dispatch_cli(["eval", "run", "--native-skills", "--json"], project_root=ROOT) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "ok"
    assert seen["native_skills"] is True


def test_command_registry_updated_for_native_skill_harness() -> None:
    commands = {record.command for record in COMMANDS}

    assert "python smart_agent.py skills test <skill_id>" in commands
    assert "python smart_agent.py skills test --all-safe" in commands
    assert "python smart_agent.py skills dogfood <skill_id>" in commands
    assert "python smart_agent.py eval run --native-skills" in commands
    assert "python smart_agent.py dogfood run native_skills_core --session" in commands
