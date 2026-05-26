from __future__ import annotations

from pathlib import Path

from agent.performance.models import OptimizationRecommendation, PerformanceReport, utc_now_iso
from agent.performance.patch_planner import create_patch_plan, plan_for_recommendation
from agent.performance.reports import PerformanceReportStore
from agent.tools.registry import default_registry


def _write_recommendations(tmp_path, recommendations) -> None:
    PerformanceReportStore(tmp_path).write_report(
        PerformanceReport(
            report_id="recommendations_fixture",
            report_type="recommendations",
            generated_at=utc_now_iso(),
            status="ok",
            summary="fixture",
            recommendations=recommendations,
        )
    )


def test_patch_plan_allows_only_low_risk_self_heal_compatible_recommendation() -> None:
    recommendation = OptimizationRecommendation(
        recommendation_id="rec_docs",
        title="Improve docs",
        rationale="docs only",
        expected_impact="clearer setup",
        risk_level="SAFE",
        patch_area="docs/ux",
        docs_required=["docs/performance/README.md"],
        safe_for_self_heal=True,
        human_review_required=False,
    ).to_dict()
    plan = plan_for_recommendation(recommendation)
    assert plan.allowed_to_patch is True
    assert plan.applies_patch is False
    assert plan.expected_files == ["docs/performance/README.md"]


def test_patch_plan_blocks_architecture_and_safety_sensitive_recommendations() -> None:
    recommendation = OptimizationRecommendation(
        recommendation_id="rec_arch",
        title="Rework architecture",
        rationale="broad",
        expected_impact="unknown",
        risk_level="MEDIUM",
        patch_area="architecture",
    ).to_dict()
    plan = plan_for_recommendation(recommendation)
    assert plan.allowed_to_patch is False
    assert plan.human_review_required is True
    assert "risk level" in plan.reason or "architecture" in plan.reason


def test_create_patch_plan_writes_report_without_applying_patches(tmp_path) -> None:
    recommendation = OptimizationRecommendation(
        recommendation_id="rec_test_target",
        title="Narrow test target",
        rationale="fixture",
        expected_impact="faster iteration",
        risk_level="LOW",
        patch_area="test selection",
        tests_required=["targeted test"],
        safe_for_self_heal=True,
        human_review_required=False,
    )
    _write_recommendations(tmp_path, [recommendation])
    payload = create_patch_plan(tmp_path)
    assert payload["patch_plan_count"] == 1
    assert payload["applied_patches"] == 0
    assert payload["patch_plans"][0]["allowed_to_patch"] is True
    assert Path(payload["report_path"]).exists()


def test_create_patch_plan_filters_recommendation_id(tmp_path) -> None:
    _write_recommendations(
        tmp_path,
        [
            OptimizationRecommendation("rec_a", "A", "r", "impact", safe_for_self_heal=True, human_review_required=False),
            OptimizationRecommendation("rec_b", "B", "r", "impact", safe_for_self_heal=True, human_review_required=False),
        ],
    )
    payload = create_patch_plan(tmp_path, recommendation_id="rec_b")
    assert payload["patch_plan_count"] == 1
    assert payload["patch_plans"][0]["recommendation_id"] == "rec_b"


def test_create_patch_plan_no_recommendations_state(tmp_path) -> None:
    payload = create_patch_plan(tmp_path)
    assert payload["status"] == "no_recommendations"
    assert payload["applied_patches"] == 0


def test_patch_plan_tool_registered(tmp_path) -> None:
    registry = default_registry(project_root=tmp_path)
    assert registry.get("perf.patch_plan") is not None
