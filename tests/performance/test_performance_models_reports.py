from __future__ import annotations

import json

from agent.performance.models import (
    OptimizationRecommendation,
    PerformanceEvidence,
    PerformanceFinding,
    PerformanceMetric,
    PerformanceReport,
    PerformanceScanConfig,
    PerformanceScanResult,
    utc_now_iso,
)
from agent.performance.reports import PerformanceReportStore
from agent.tools.registry import default_registry


def _sample_report() -> PerformanceReport:
    finding = PerformanceFinding(
        title="Repeated command registry load",
        category="Command registry loading",
        severity="P2",
        summary="Command metadata is loaded repeatedly in a tight path.",
        likely_cause="No cached read-only index.",
        affected_files=["agent/ui/command_registry.py"],
        evidence=[
            PerformanceEvidence(
                evidence_type="static",
                path="agent/ui/command_registry.py",
                line=73,
                snippet="api_key=sk-abcdefghijklmnopqrstuvwxyz",
            )
        ],
        recommendations=[
            OptimizationRecommendation(
                recommendation_id="rec_cache_index",
                title="Cache derived registry index",
                rationale="Avoid repeated derived metadata construction.",
                expected_impact="Lower CLI metadata latency.",
                tests_required=["tests/test_command_registry.py"],
            )
        ],
    )
    config = PerformanceScanConfig(scan_id="scan_1", scan_type="static", project_root=".")
    result = PerformanceScanResult(
        scan_id="scan_1",
        status="ok",
        started_at=utc_now_iso(),
        completed_at=utc_now_iso(),
        config=config,
        metrics=[PerformanceMetric(name="files_scanned", value=10, unit="count")],
        findings=[finding],
    )
    return PerformanceReport(
        report_id="report_1",
        report_type="static",
        generated_at=utc_now_iso(),
        status="ok",
        summary="api_key=sk-abcdefghijklmnopqrstuvwxyz",
        scan_result=result,
        findings=[finding],
        recommendations=finding.recommendations,
        limitations=["fixture report"],
    )


def test_performance_models_are_json_serializable_and_have_stable_ids() -> None:
    first = PerformanceFinding(
        title="Slow startup import",
        category="Startup/import overhead",
        severity="p2",
        summary="Import path does extra work.",
        likely_cause="Eager optional imports.",
        affected_files=["smart_agent.py"],
    )
    second = PerformanceFinding(
        title="Slow startup import",
        category="Startup/import overhead",
        severity="P2",
        summary="Import path does extra work.",
        likely_cause="Eager optional imports.",
        affected_files=["smart_agent.py"],
    )
    assert first.finding_id == second.finding_id
    payload = first.to_dict()
    assert payload["severity"] == "P2"
    json.dumps(payload)


def test_report_store_writes_redacted_json_and_markdown(tmp_path) -> None:
    store = PerformanceReportStore(tmp_path)
    report = _sample_report()
    json_path = store.write_report(report)
    md_path = store.write_markdown(report)

    raw_json = json_path.read_text(encoding="utf-8")
    raw_md = md_path.read_text(encoding="utf-8")
    assert "sk-abcdefghijklmnopqrstuvwxyz" not in raw_json
    assert "[REDACTED]" in raw_json
    assert "Performance Report" in raw_md
    assert report.findings[0].finding_id in raw_md


def test_report_store_handles_no_report_state(tmp_path) -> None:
    payload = PerformanceReportStore(tmp_path).read_latest_report()
    assert payload["status"] == "no_report"
    assert payload["reports_dir"].endswith("reports/performance")


def test_report_store_reads_latest_findings(tmp_path) -> None:
    store = PerformanceReportStore(tmp_path)
    store.write_report(_sample_report())
    payload = store.read_latest_findings()
    assert payload["status"] == "ok"
    assert payload["finding_count"] == 1
    assert payload["findings"][0]["title"] == "Repeated command registry load"


def test_performance_tools_registered_without_running_scans(tmp_path) -> None:
    registry = default_registry(project_root=tmp_path)
    assert registry.get("perf.report") is not None
    assert registry.get("perf.findings") is not None
    report = registry.get("perf.report").handler()
    findings = registry.get("perf.findings").handler()
    assert report["status"] == "no_report"
    assert findings["findings"] == []
