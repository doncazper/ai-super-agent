from __future__ import annotations

from agent.performance.models import PerformanceFinding, PerformanceReport, utc_now_iso
from agent.performance.recommendations import build_recommendations, recommendation_from_finding, suggest_fixes
from agent.performance.reports import PerformanceReportStore
from agent.tools.registry import default_registry


def test_recommendation_from_finding_maps_cache_command_registry() -> None:
    finding = PerformanceFinding(
        title="Repeated command registry construction",
        category="command registry",
        severity="P2",
        summary="The command registry is built repeatedly in a hot path.",
        likely_cause="No cached derived index.",
    ).to_dict()
    recommendation = recommendation_from_finding(finding)
    assert recommendation.patch_area == "command registry"
    assert recommendation.applies_patch is False
    assert recommendation.human_review_required is True
    assert "command registry" in recommendation.title.lower()


def test_recommendation_defaults_to_architecture_review() -> None:
    finding = PerformanceFinding(
        title="Ambiguous bottleneck",
        category="unknown",
        severity="P2",
        summary="The cause is unclear.",
        likely_cause="Unknown.",
    ).to_dict()
    recommendation = recommendation_from_finding(finding)
    assert recommendation.patch_area == "architecture"
    assert recommendation.human_review_required is True
    assert recommendation.safe_for_self_heal is False


def test_build_recommendations_from_test_profile_duration() -> None:
    report = {
        "report_id": "profile_1",
        "report_type": "test_profile",
        "durations": [
            {"seconds": 1.2, "phase": "setup", "nodeid": "tests/test_a.py::test_slow"},
        ],
    }
    recommendations = build_recommendations(report)
    assert recommendations
    assert recommendations[0].applies_patch is False
    assert recommendations[0].status == "proposed"


def test_suggest_fixes_writes_recommendation_report(tmp_path) -> None:
    store = PerformanceReportStore(tmp_path)
    finding = PerformanceFinding(
        title="Requests call without timeout",
        category="network",
        severity="P2",
        summary="A requests call has no timeout.",
        likely_cause="Missing timeout.",
    )
    store.write_report(
        PerformanceReport(
            report_id="static_fixture",
            report_type="static",
            generated_at=utc_now_iso(),
            status="ok",
            summary="fixture",
            findings=[finding],
        )
    )
    payload = suggest_fixes(tmp_path)
    assert payload["report_type"] == "recommendations"
    assert payload["recommendation_count"] == 1
    assert payload["applied_patches"] == 0
    assert payload["recommendations"][0]["applies_patch"] is False


def test_suggest_fixes_no_report_state(tmp_path) -> None:
    payload = suggest_fixes(tmp_path)
    assert payload["status"] == "no_report"
    assert payload["recommendations"] == []


def test_suggest_fixes_tool_registered(tmp_path) -> None:
    registry = default_registry(project_root=tmp_path)
    assert registry.get("perf.suggest_fixes") is not None
