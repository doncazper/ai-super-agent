from __future__ import annotations

from pathlib import Path

from agent.performance.baselines import compare_baseline, create_baseline, read_baseline, regression_status
from agent.performance.models import PerformanceBenchmarkResult, PerformanceFinding, PerformanceReport, utc_now_iso
from agent.performance.reports import PerformanceReportStore
from agent.tools.registry import default_registry


def _write_benchmark_report(tmp_path, report_id: str, duration_ms: float) -> None:
    PerformanceReportStore(tmp_path).write_report(
        PerformanceReport(
            report_id=report_id,
            report_type="benchmark",
            generated_at=utc_now_iso(),
            status="ok",
            summary="fixture benchmark",
            benchmark_results=[
                PerformanceBenchmarkResult(
                    benchmark_id=f"{report_id}_bench",
                    command_id="CMD-COMMANDS-005",
                    command="python smart_agent.py commands validate",
                    status="ok",
                    duration_ms=duration_ms,
                    median_duration_ms=duration_ms,
                    returncode=0,
                )
            ],
        )
    )


def test_create_baseline_from_latest_report(tmp_path) -> None:
    _write_benchmark_report(tmp_path, "bench_1", 100.0)
    payload = create_baseline(tmp_path, notes="fixture")
    assert payload["baseline_created"] is True
    assert payload["command_timings"]["CMD-COMMANDS-005"] == 100.0
    assert payload["notes"] == "fixture"
    assert Path(payload["baseline_path"]).exists()
    assert payload["python_version"]
    assert payload["platform"]


def test_compare_baseline_ranks_regression(tmp_path) -> None:
    _write_benchmark_report(tmp_path, "bench_1", 100.0)
    baseline = create_baseline(tmp_path)
    _write_benchmark_report(tmp_path, "bench_2", 160.0)
    payload = compare_baseline(tmp_path, baseline_id=baseline["baseline_id"], tolerance=0.2)
    assert payload["regression_count"] == 1
    assert payload["regressions"][0]["category"] == "command_timing"
    assert payload["regressions"][0]["severity"] == "P2"


def test_compare_baseline_tracks_finding_count(tmp_path) -> None:
    PerformanceReportStore(tmp_path).write_report(
        PerformanceReport(report_id="empty", report_type="static", generated_at=utc_now_iso(), status="ok", summary="empty")
    )
    create_baseline(tmp_path)
    PerformanceReportStore(tmp_path).write_report(
        PerformanceReport(
            report_id="static_2",
            report_type="static",
            generated_at=utc_now_iso(),
            status="ok",
            summary="finding",
            findings=[
                PerformanceFinding(
                    title="Repeated glob",
                    category="glob",
                    severity="P3",
                    summary="Repeated glob in hot path.",
                    likely_cause="Repeated glob.",
                )
            ],
        )
    )
    payload = regression_status(tmp_path)
    assert payload["regressions"][0]["category"] == "finding_count"


def test_baseline_no_report_and_no_baseline_states(tmp_path) -> None:
    created = create_baseline(tmp_path)
    assert created["baseline_created"] is False
    baseline = read_baseline(tmp_path)
    assert baseline["status"] == "no_baseline"
    compared = compare_baseline(tmp_path)
    assert compared["status"] == "no_baseline"


def test_baseline_tools_registered(tmp_path) -> None:
    registry = default_registry(project_root=tmp_path)
    assert registry.get("perf.baseline_create") is not None
    assert registry.get("perf.baseline_compare") is not None
    assert registry.get("perf.regressions") is not None
