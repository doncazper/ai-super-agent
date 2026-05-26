from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .baselines import read_baseline
from .reports import PerformanceReportStore


REPORT_TYPES = ("static", "startup", "benchmark", "test_profile", "recommendations", "regressions", "patch_plan")


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _latest_reports(store: PerformanceReportStore) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for path in store.list_reports():
        payload = _read_json(path)
        if not payload:
            continue
        report_type = str(payload.get("report_type", ""))
        if report_type == "test_profile":
            profile_path = store.report_path(str(payload.get("report_id", "")), suffix=".profile.json")
            if profile_path.exists():
                profile_payload = _read_json(profile_path)
                if profile_payload:
                    payload.update(profile_payload)
        if report_type in REPORT_TYPES and report_type not in latest:
            payload["report_path"] = str(path)
            latest[report_type] = store.redact_payload(payload)
    return latest


def _top_findings(report: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not report:
        return []
    findings = report.get("findings", [])
    if not findings and isinstance(report.get("scan_result"), dict):
        findings = report["scan_result"].get("findings", [])
    if not isinstance(findings, list):
        return []
    return [
        {
            "finding_id": item.get("finding_id"),
            "severity": item.get("severity"),
            "title": item.get("title"),
            "category": item.get("category"),
        }
        for item in findings[:10]
        if isinstance(item, dict)
    ]


def _slowest_commands(report: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not report or not isinstance(report.get("benchmark_results"), list):
        return []
    rows = [item for item in report["benchmark_results"] if isinstance(item, dict)]
    rows.sort(key=lambda item: float(item.get("median_duration_ms") or item.get("duration_ms") or 0), reverse=True)
    return [
        {
            "command_id": item.get("command_id"),
            "command": item.get("command"),
            "median_duration_ms": item.get("median_duration_ms", item.get("duration_ms")),
            "status": item.get("status"),
        }
        for item in rows[:10]
    ]


def _slowest_tests(report: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not report or not isinstance(report.get("durations"), list):
        return []
    rows = [item for item in report["durations"] if isinstance(item, dict)]
    rows.sort(key=lambda item: float(item.get("seconds") or 0), reverse=True)
    return rows[:10]


def _recommendations(report: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not report or not isinstance(report.get("recommendations"), list):
        return []
    return [
        {
            "recommendation_id": item.get("recommendation_id"),
            "title": item.get("title"),
            "risk_level": item.get("risk_level"),
            "patch_area": item.get("patch_area"),
            "human_review_required": item.get("human_review_required"),
            "safe_for_self_heal": item.get("safe_for_self_heal"),
        }
        for item in report["recommendations"][:10]
        if isinstance(item, dict)
    ]


def _patch_candidates(report: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not report or not isinstance(report.get("patch_plans"), list):
        return []
    return [
        {
            "patch_id": item.get("patch_id"),
            "recommendation_id": item.get("recommendation_id"),
            "allowed_to_patch": item.get("allowed_to_patch"),
            "reason": item.get("reason"),
            "status": item.get("status"),
        }
        for item in report["patch_plans"][:10]
        if isinstance(item, dict)
    ]


def build_dashboard(project_root: str | Path = ".") -> dict[str, Any]:
    store = PerformanceReportStore(project_root)
    latest = _latest_reports(store)
    baseline = read_baseline(project_root)
    regressions = latest.get("regressions", {})
    patch_candidates = _patch_candidates(latest.get("patch_plan"))
    recommendations = _recommendations(latest.get("recommendations"))
    next_action = "Run `python smart_agent.py perf scan --static --max-files 500` to create initial local evidence."
    if regressions.get("regression_count", 0):
        next_action = "Review `python smart_agent.py perf regressions` and inspect the highest-severity regression."
    elif recommendations:
        next_action = "Review `python smart_agent.py perf patch-plan` for metadata-only next steps."
    elif baseline.get("status") == "no_baseline":
        next_action = "Create a baseline with `python smart_agent.py perf baseline create` after reviewing the latest report."
    return {
        "status": "ok",
        "dashboard_kind": "performance",
        "report_counts": {report_type: int(report_type in latest) for report_type in REPORT_TYPES},
        "latest_reports": {key: value.get("report_id") for key, value in latest.items()},
        "latest_scan_summary": (latest.get("static") or latest.get("startup") or {}).get("summary", ""),
        "top_bottlenecks": _top_findings(latest.get("static")),
        "slowest_safe_commands": _slowest_commands(latest.get("benchmark")),
        "slowest_tests": _slowest_tests(latest.get("test_profile")),
        "regression_warnings": regressions.get("regressions", [])[:10] if isinstance(regressions.get("regressions"), list) else [],
        "baseline_status": baseline.get("status", "ok"),
        "baseline_id": baseline.get("baseline_id", ""),
        "recommendations": recommendations,
        "patch_plan_candidates": patch_candidates,
        "feature_maturity_impact": {
            "feature": "Performance Bottleneck Scanner and Optimization Advisor",
            "impact": "Adds local evidence for maturity/release hardening; does not prove live validation.",
        },
        "next_safe_action": next_action,
        "read_only": True,
        "commands_executed": [],
    }


def performance_status(project_root: str | Path = ".") -> dict[str, Any]:
    dashboard = build_dashboard(project_root)
    return {
        "status": dashboard["status"],
        "baseline_status": dashboard["baseline_status"],
        "baseline_id": dashboard["baseline_id"],
        "report_counts": dashboard["report_counts"],
        "regression_warning_count": len(dashboard["regression_warnings"]),
        "recommendation_count": len(dashboard["recommendations"]),
        "patch_plan_candidate_count": len(dashboard["patch_plan_candidates"]),
        "read_only": True,
        "commands_executed": [],
    }


def next_fix(project_root: str | Path = ".") -> dict[str, Any]:
    dashboard = build_dashboard(project_root)
    return {
        "status": "ok",
        "next_safe_action": dashboard["next_safe_action"],
        "top_recommendation": dashboard["recommendations"][0] if dashboard["recommendations"] else None,
        "top_patch_plan_candidate": dashboard["patch_plan_candidates"][0] if dashboard["patch_plan_candidates"] else None,
        "read_only": True,
        "commands_executed": [],
    }


def trends(project_root: str | Path = ".") -> dict[str, Any]:
    dashboard = build_dashboard(project_root)
    return {
        "status": "ok",
        "baseline_status": dashboard["baseline_status"],
        "baseline_id": dashboard["baseline_id"],
        "regression_warnings": dashboard["regression_warnings"],
        "slowest_safe_commands": dashboard["slowest_safe_commands"],
        "slowest_tests": dashboard["slowest_tests"],
        "read_only": True,
        "commands_executed": [],
    }
