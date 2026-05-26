from __future__ import annotations

from agent.performance.dashboard import build_dashboard, next_fix, performance_status, trends
from agent.performance.models import OptimizationRecommendation, PerformanceBenchmarkResult, PerformanceReport, utc_now_iso
from agent.performance.patch_planner import PerformancePatchPlan
from agent.performance.reports import PerformanceReportStore
from agent.tools.registry import default_registry


def _write_fixture_reports(tmp_path) -> None:
    store = PerformanceReportStore(tmp_path)
    store.write_report(
        PerformanceReport(
            report_id="benchmark_fixture",
            report_type="benchmark",
            generated_at=utc_now_iso(),
            status="ok",
            summary="benchmark",
            benchmark_results=[
                PerformanceBenchmarkResult("bench_1", "CMD-COMMANDS-005", "python smart_agent.py commands validate", "ok", 120.0),
            ],
        )
    )
    store.write_report(
        PerformanceReport(
            report_id="recommendations_fixture",
            report_type="recommendations",
            generated_at=utc_now_iso(),
            status="ok",
            summary="recommendations",
            recommendations=[
                OptimizationRecommendation(
                    "rec_docs",
                    "Improve docs",
                    "rationale",
                    "clearer setup",
                    risk_level="SAFE",
                    patch_area="docs/ux",
                    safe_for_self_heal=True,
                    human_review_required=False,
                )
            ],
        )
    )
    patch_report = {
        "report_id": "patch_fixture",
        "report_type": "patch_plan",
        "generated_at": utc_now_iso(),
        "status": "ok",
        "patch_plans": [
            PerformancePatchPlan(
                patch_id="patch_1",
                recommendation_id="rec_docs",
                allowed_to_patch=True,
                reason="fixture",
                risk_level="SAFE",
                expected_files=["docs/"],
                expected_behavior_change="clearer setup",
                tests_required=["docs validation"],
                docs_required=["docs/performance/PERFORMANCE_DASHBOARD.md"],
                rollback_plan="revert",
                human_review_required=False,
                self_heal_compatible=True,
            ).to_dict()
        ],
    }
    path = store.report_path("patch_fixture")
    store.ensure_dir()
    path.write_text(__import__("json").dumps(patch_report), encoding="utf-8")


def test_dashboard_reads_reports_without_executing_commands(tmp_path) -> None:
    _write_fixture_reports(tmp_path)
    payload = build_dashboard(tmp_path)
    assert payload["read_only"] is True
    assert payload["commands_executed"] == []
    assert payload["slowest_safe_commands"][0]["command_id"] == "CMD-COMMANDS-005"
    assert payload["recommendations"][0]["recommendation_id"] == "rec_docs"
    assert payload["patch_plan_candidates"][0]["patch_id"] == "patch_1"


def test_status_next_fix_and_trends_are_read_only(tmp_path) -> None:
    _write_fixture_reports(tmp_path)
    status = performance_status(tmp_path)
    action = next_fix(tmp_path)
    trend = trends(tmp_path)
    assert status["read_only"] is True
    assert action["read_only"] is True
    assert trend["read_only"] is True
    assert action["next_safe_action"]


def test_dashboard_tools_registered(tmp_path) -> None:
    registry = default_registry(project_root=tmp_path)
    assert registry.get("perf.dashboard") is not None
    assert registry.get("perf.status") is not None
    assert registry.get("perf.next_fix") is not None
    assert registry.get("perf.trends") is not None
