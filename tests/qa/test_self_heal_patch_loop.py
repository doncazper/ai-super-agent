from pathlib import Path
import json

from agent.qa.patch_plan import build_patch_plan
from agent.qa.self_heal import plan_self_heal, read_last_self_heal_report, run_self_heal


def _write_bug(tmp_path: Path, **overrides) -> dict:
    bug = {
        "bug_id": "BUG-0001",
        "run_id": "qa_run_test",
        "command_id": "CMD-TEST-001",
        "command": "python smart_agent.py setup",
        "severity": "P3",
        "failure_type": "docs_mismatch",
        "expected_behavior": "Command should match docs.",
        "actual_behavior": "Help text mismatch.",
        "reproduction_command": "python smart_agent.py setup",
        "redacted_stdout_excerpt": "",
        "redacted_stderr_excerpt": "",
        "suspected_area": "CLI",
        "suggested_fix": "Update help docs.",
        "suggested_regression_test": "tests/regressions/test_bug_0001.py",
        "status": "open",
    }
    bug.update(overrides)
    bugs = tmp_path / "bugs"
    bugs.mkdir()
    (bugs / f"{bug['bug_id']}.json").write_text(json.dumps(bug), encoding="utf-8")
    return bug


def test_patch_plan_safe_p3_allowed() -> None:
    plan = build_patch_plan(
        {
            "bug_id": "BUG-LOCAL",
            "severity": "P3",
            "failure_type": "docs_mismatch",
            "actual_behavior": "Help mismatch.",
            "suggested_fix": "Update help docs.",
            "suggested_regression_test": "tests/regressions/test_bug_local.py",
        }
    )
    assert plan.allowed_to_patch is True
    assert plan.human_review_required is True


def test_high_risk_review_required(tmp_path: Path) -> None:
    bug = _write_bug(tmp_path, severity="P0", failure_type="policy_failure")
    plan = build_patch_plan(bug)
    assert plan.allowed_to_patch is False
    assert "human review" in plan.reason.lower()


def test_broad_refactor_blocked(tmp_path: Path) -> None:
    bug = _write_bug(tmp_path, suggested_fix="Requires broad refactor of runtime.")
    plan = build_patch_plan(bug)
    assert plan.allowed_to_patch is False


def test_regression_required(tmp_path: Path) -> None:
    bug = _write_bug(tmp_path, suggested_regression_test="")
    plan = build_patch_plan(bug)
    assert plan.allowed_to_patch is False
    assert "regression" in plan.reason.lower()


def test_plan_and_run_write_reports_without_commit_or_push(tmp_path: Path) -> None:
    _write_bug(tmp_path)
    plan = plan_self_heal(tmp_path, bug_id="BUG-0001")
    assert plan["status"] == "ok"
    assert (tmp_path / plan["path"]).exists()
    result = run_self_heal(tmp_path, bug_id="BUG-0001")
    assert result["patch_applied"] is False
    assert result["commit_created"] is False
    assert result["push_performed"] is False
    assert read_last_self_heal_report(tmp_path)["bug_id"] == "BUG-0001"
