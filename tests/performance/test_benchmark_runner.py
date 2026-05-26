from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from agent.performance.benchmark_runner import find_benchmark_candidate, is_benchmark_safe, run_safe_benchmarks
from agent.performance.reports import PerformanceReportStore
from agent.tools.registry import default_registry
from agent.ui.command_registry import get_command


def _fake_runner(argv: list[str], cwd: Path, timeout_seconds: int) -> subprocess.CompletedProcess[str]:
    assert cwd.exists()
    assert timeout_seconds == 3
    return subprocess.CompletedProcess(argv, 0, stdout="RAW_OUTPUT_PAYLOAD", stderr="")


def test_benchmark_command_must_match_registry() -> None:
    with pytest.raises(ValueError, match="command registry"):
        find_benchmark_candidate("echo unsafe")


def test_benchmark_rejects_high_or_approval_commands() -> None:
    record = get_command("CMD-APPROVAL-003")
    assert record is not None
    allowed, reason = is_benchmark_safe(record)
    assert not allowed
    assert "risk level" in reason or "approval" in reason


def test_benchmark_rejects_placeholder_commands() -> None:
    record = get_command("CMD-CORE-001")
    assert record is not None
    allowed, reason = is_benchmark_safe(record)
    assert not allowed
    assert "placeholder" in reason or "model call" in reason


def test_safe_benchmark_records_median_min_max_without_raw_output(tmp_path) -> None:
    payload = run_safe_benchmarks(
        tmp_path,
        command="python smart_agent.py commands validate",
        iterations=3,
        timeout_seconds=3,
        runner=_fake_runner,
        write_report=False,
    )
    result = payload["benchmark_results"][0]
    assert result["command_id"] == "CMD-COMMANDS-005"
    assert result["iterations"] == 3
    assert result["min_duration_ms"] <= result["median_duration_ms"] <= result["max_duration_ms"]
    assert result["stdout_bytes"] == 54
    serialized = json.dumps(payload)
    assert "RAW_OUTPUT_PAYLOAD" not in serialized


def test_safe_benchmark_writes_redacted_report(tmp_path) -> None:
    payload = run_safe_benchmarks(
        tmp_path,
        command="python smart_agent.py commands validate",
        iterations=1,
        timeout_seconds=3,
        runner=_fake_runner,
    )
    report_path = Path(payload["report_path"])
    assert report_path.exists()
    latest = PerformanceReportStore(tmp_path).read_latest_report()
    assert latest["report_type"] == "benchmark"


def test_benchmark_tool_registered(tmp_path) -> None:
    registry = default_registry(project_root=tmp_path)
    assert registry.get("perf.benchmark") is not None
