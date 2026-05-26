from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .models import stable_finding_id, utc_now_iso
from .reports import PerformanceReportStore


BROAD_OR_SAFETY_AREAS = {
    "architecture",
    "policy",
    "approval",
    "audit",
    "security",
    "toolbroker",
    "permission",
    "provider status",
}


@dataclass(frozen=True)
class PerformancePatchPlan:
    patch_id: str
    recommendation_id: str
    allowed_to_patch: bool
    reason: str
    risk_level: str
    expected_files: list[str]
    expected_behavior_change: str
    tests_required: list[str]
    docs_required: list[str]
    rollback_plan: str
    human_review_required: bool
    self_heal_compatible: bool
    status: str = "planned"
    applies_patch: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _latest_recommendations_report(store: PerformanceReportStore) -> dict[str, Any]:
    for path in store.list_reports():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if payload.get("report_type") == "recommendations":
            payload["report_path"] = str(path)
            return store.redact_payload(payload)
    return {
        "status": "no_recommendations",
        "message": "No recommendation report found. Run `python smart_agent.py perf suggest-fixes` first.",
        "reports_dir": str(store.reports_dir),
    }


def _expected_files(patch_area: str, docs_required: list[str]) -> list[str]:
    area = patch_area.lower()
    if "docs" in area or "ux" in area:
        return docs_required or ["docs/"]
    if "test" in area or "fixture" in area:
        return ["tests/"]
    if "command registry" in area:
        return ["agent/ui/command_registry.py", "docs/COMMAND_REGISTRY.md", "docs/COMMAND_TEST_MATRIX.md"]
    if "config" in area:
        return ["agent/config/"]
    if "parser" in area:
        return ["agent/"]
    return []


def plan_for_recommendation(recommendation: dict[str, Any]) -> PerformancePatchPlan:
    recommendation_id = str(recommendation.get("recommendation_id") or stable_finding_id(recommendation.get("title")))
    risk_level = str(recommendation.get("risk_level") or "LOW").upper()
    patch_area = str(recommendation.get("patch_area") or "unknown").lower()
    tests_required = [str(item) for item in recommendation.get("tests_required", []) if str(item).strip()]
    docs_required = [str(item) for item in recommendation.get("docs_required", []) if str(item).strip()]
    human_review_required = bool(recommendation.get("human_review_required", True))
    self_heal_compatible = bool(recommendation.get("safe_for_self_heal", False))
    blocked_area = next((area for area in BROAD_OR_SAFETY_AREAS if area in patch_area), "")
    if risk_level not in {"SAFE", "LOW"}:
        allowed = False
        reason = f"risk level {risk_level} requires human review"
    elif blocked_area:
        allowed = False
        reason = f"patch area `{blocked_area}` is broad or safety-sensitive"
    elif human_review_required:
        allowed = False
        reason = "recommendation requires human review"
    elif not self_heal_compatible:
        allowed = False
        reason = "recommendation is not self-heal compatible"
    else:
        allowed = True
        reason = "low-risk self-heal-compatible plan; still not applied by this command"
    return PerformancePatchPlan(
        patch_id=f"patch_{stable_finding_id(recommendation_id, patch_area).removeprefix('perf_')}",
        recommendation_id=recommendation_id,
        allowed_to_patch=allowed,
        reason=reason,
        risk_level=risk_level,
        expected_files=_expected_files(patch_area, docs_required),
        expected_behavior_change=str(recommendation.get("expected_impact") or "unknown"),
        tests_required=tests_required,
        docs_required=docs_required,
        rollback_plan=str(recommendation.get("rollback_plan") or "Revert the scoped optimization patch."),
        human_review_required=human_review_required,
        self_heal_compatible=self_heal_compatible,
        status="planned" if allowed else "blocked",
        applies_patch=False,
    )


def create_patch_plan(project_root: str | Path = ".", *, recommendation_id: str | None = None) -> dict[str, Any]:
    store = PerformanceReportStore(project_root)
    recommendations_report = _latest_recommendations_report(store)
    if recommendations_report.get("status") == "no_recommendations":
        return {**recommendations_report, "patch_plans": [], "applied_patches": 0}
    recommendations = recommendations_report.get("recommendations", [])
    if not isinstance(recommendations, list):
        recommendations = []
    if recommendation_id:
        recommendations = [item for item in recommendations if isinstance(item, dict) and item.get("recommendation_id") == recommendation_id]
    plans = [plan_for_recommendation(item).to_dict() for item in recommendations if isinstance(item, dict)]
    generated_at = utc_now_iso()
    report_id = f"patch_plan_{generated_at.replace(':', '').replace('-', '')}"
    payload = {
        "report_id": report_id,
        "report_type": "patch_plan",
        "generated_at": generated_at,
        "status": "ok",
        "source_report_id": recommendations_report.get("report_id"),
        "patch_plan_count": len(plans),
        "patch_plans": plans,
        "applied_patches": 0,
        "limitations": [
            "Patch plans are metadata only and do not apply patches.",
            "Broad refactors and safety-control changes are blocked by default.",
            "Package installs, commits, pushes, and live provider calls are out of scope.",
        ],
        "redacted": True,
    }
    path = store.report_path(report_id)
    store.ensure_dir()
    path.write_text(json.dumps(store.redact_payload(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    payload["report_path"] = str(path)
    return store.redact_payload(payload)
