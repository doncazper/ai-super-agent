from pathlib import Path
import json

from agent.qa.analyzer import rank_failures
from agent.qa.bug_generator import create_bugs_from_run
from agent.qa.regression_generator import create_regression_from_bug


def _write_run(tmp_path: Path, run_id: str, records: list[dict]) -> None:
    reports = tmp_path / "reports/qa"
    reports.mkdir(parents=True)
    (reports / f"{run_id}.jsonl").write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")


def _failure(**overrides) -> dict:
    data = {
        "run_id": "qa_run_test",
        "command_id": "CMD-TEST-001",
        "command_string": "python smart_agent.py setup",
        "qa_tier": 1,
        "risk_level": "SAFE",
        "start_time": "2026-05-25T00:00:00+00:00",
        "duration_ms": 12,
        "exit_code": 1,
        "redacted_stdout_excerpt": "token=secret-value user@example.com",
        "redacted_stderr_excerpt": "bad output",
        "full_log_path": "reports/qa/test.log",
        "status": "failed",
        "failure_type": "nonzero_exit",
        "severity": "",
        "suspected_area": "Doctor/status/config",
        "linked_bug_id": "",
        "regression_test_path": "",
        "feature_id": "",
        "maturity_impact": "needs_review",
        "audit_ids": [],
        "notes": "",
    }
    data.update(overrides)
    return data


def test_rank_failures_prioritizes_safety() -> None:
    ranked = rank_failures([
        _failure(command_id="CMD-P2", failure_type="timeout"),
        _failure(command_id="CMD-P0", failure_type="policy_failure"),
    ])
    assert ranked[0]["command_id"] == "CMD-P0"
    assert ranked[0]["severity"] == "P0"


def test_generate_bug_from_failed_run_redacts_secrets(tmp_path: Path) -> None:
    _write_run(tmp_path, "qa_run_test", [_failure()])
    result = create_bugs_from_run(tmp_path, run_id="qa_run_test")
    assert result["created_count"] == 1
    bug_path = tmp_path / result["bugs"][0]["path"]
    text = bug_path.read_text(encoding="utf-8")
    assert "secret-value" not in text
    assert "user@example.com" not in text
    bug = json.loads(text)
    assert bug["status"] == "open"
    assert bug["failure_type"] == "nonzero_exit"


def test_generate_regression_stub_from_bug(tmp_path: Path) -> None:
    _write_run(tmp_path, "qa_run_test", [_failure()])
    bugs = create_bugs_from_run(tmp_path, run_id="qa_run_test")
    bug_id = bugs["bugs"][0]["bug_id"]
    result = create_regression_from_bug(tmp_path, bug_id=bug_id)
    path = tmp_path / result["regression_test_path"]
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "pytest.mark.skip" in content
    assert "secret-value" not in content


def test_docs_mismatch_ranked_p3() -> None:
    ranked = rank_failures([_failure(failure_type="docs_mismatch")])
    assert ranked[0]["severity"] == "P3"

