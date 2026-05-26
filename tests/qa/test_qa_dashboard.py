from pathlib import Path
import json

from agent.qa.dashboard import command_qa_dashboard, feature_maturity_impact, next_safe_fix_candidate


def test_dashboard_handles_no_reports(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/FEATURE_MATURITY.md").write_text("No live validation yet.\n", encoding="utf-8")
    result = command_qa_dashboard(tmp_path)
    assert result["status"] == "ok"
    assert result["read_only"] is True
    assert result["command_totals"]["total"] > 0


def test_dashboard_renders_counts(tmp_path: Path) -> None:
    reports = tmp_path / "reports/qa"
    reports.mkdir(parents=True)
    record = {"run_id": "qa_run_test", "command_id": "CMD-QA-002", "status": "failed", "failure_type": "timeout", "severity": "P2"}
    (reports / "qa_run_test.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")
    result = command_qa_dashboard(tmp_path)
    assert result["run_counts"]["failed"] == 1
    assert result["failures_by_severity"]["P2"] == 1


def test_next_fix_selects_highest_safe_bug() -> None:
    result = next_safe_fix_candidate(
        [
            {"bug_id": "BUG-1", "severity": "P1", "suggested_regression_test": "tests/regressions/test_bug_1.py"},
            {"bug_id": "BUG-2", "severity": "P3", "suggested_regression_test": "tests/regressions/test_bug_2.py"},
            {"bug_id": "BUG-3", "severity": "P2", "suggested_regression_test": "tests/regressions/test_bug_3.py"},
        ]
    )
    assert result["bug_id"] == "BUG-3"


def test_maturity_impact_conservative(tmp_path: Path) -> None:
    result = feature_maturity_impact(tmp_path)
    assert result["conservative"] is True
    assert "not live validation" in result["reason"]

