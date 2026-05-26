from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import OptimizationRecommendation, PerformanceReport, stable_finding_id, utc_now_iso
from .reports import PerformanceReportStore


@dataclass(frozen=True)
class RecommendationRule:
    category: str
    keywords: tuple[str, ...]
    title: str
    expected_impact: str
    effort: str
    risk_level: str
    patch_area: str
    tests_required: tuple[str, ...]
    docs_required: tuple[str, ...] = ()
    rollback_plan: str = "Revert the scoped optimization patch."
    safe_for_self_heal: bool = False
    human_review_required: bool = True


RULES: tuple[RecommendationRule, ...] = (
    RecommendationRule("lazy imports", ("heavy import", "startup import", "module-level import", "lazy import"), "Defer optional imports out of startup paths", "Lower CLI startup latency.", "medium", "LOW", "imports/startup", ("startup/import timing test",)),
    RecommendationRule("add timeout", ("without timeout", "requests.", "httpx.", "subprocess without timeout"), "Add an explicit timeout", "Prevent hangs and reduce tail latency.", "small", "LOW", "network/subprocess boundary", ("timeout regression test",)),
    RecommendationRule("bound file scan", ("os.walk", "rglob", "unbounded file", "scan"), "Bound file scanning scope", "Reduce worst-case local filesystem latency.", "medium", "LOW", "filesystem scan", ("scan limit test",)),
    RecommendationRule("cache parsed config", ("config", "parse", "load_capabilities", "yaml"), "Cache parsed config metadata", "Reduce repeated config parsing in hot paths.", "medium", "LOW", "config loader", ("cache invalidation test",)),
    RecommendationRule("cache command registry", ("command registry", "commands list", "registry"), "Cache derived command registry indexes", "Reduce repeated command metadata construction.", "medium", "LOW", "command registry", ("command registry cache test",)),
    RecommendationRule("avoid repeated glob", ("glob", "repeated glob"), "Avoid repeated glob expansion", "Lower repeated local filesystem work.", "small", "LOW", "filesystem helpers", ("glob regression test",)),
    RecommendationRule("avoid full tracker read in hot path", ("tracker", "feature maturity", "project_state", "completion_report"), "Avoid full tracker reads in hot paths", "Keep status/dashboard commands responsive.", "medium", "LOW", "tracker readers", ("status command fixture test",)),
    RecommendationRule("use streaming/chunking", ("read_text", "read_bytes", "large read", "chunk"), "Use streaming or chunked reads", "Reduce memory spikes and improve large-file behavior.", "medium", "LOW", "file IO", ("large fixture test",)),
    RecommendationRule("TTL cache", ("ttl cache", "cache ttl", "repeated provider status"), "Use a TTL cache for repeated metadata", "Reduce repeated safe metadata work while preserving freshness.", "medium", "LOW", "metadata cache", ("ttl expiry test",)),
    RecommendationRule("compile regex once", ("re.compile", "regex", "regular expression"), "Compile regex patterns once", "Reduce repeated parsing overhead.", "small", "LOW", "parser", ("parser regression test",)),
    RecommendationRule("narrow test target", ("pytest", "full suite", "test_profile", "duration"), "Narrow the profiled test target", "Improve iteration speed while preserving full-suite release gates.", "small", "LOW", "test selection", ("targeted test",), ("docs/TEST_PLAN.md",), safe_for_self_heal=True, human_review_required=False),
    RecommendationRule("add fixture", ("setup", "fixture"), "Add or narrow test fixtures", "Reduce test setup overhead without hiding failures.", "medium", "LOW", "tests/fixtures", ("fixture behavior test",)),
    RecommendationRule("defer live provider check", ("live provider", "provider check", "doctor"), "Defer live provider checks from status paths", "Keep doctor/status commands safe and fast by default.", "medium", "LOW", "provider status", ("doctor/status no-live test",), ("provider docs",)),
    RecommendationRule("docs/UX only", ("setup hint", "help text", "docs", "ux"), "Improve docs or setup hints", "Reduce user confusion without runtime risk.", "small", "SAFE", "docs/ux", ("docs validation",), ("relevant docs",), safe_for_self_heal=True, human_review_required=False),
)

ARCHITECTURE_REVIEW = RecommendationRule(
    "needs architecture review",
    (),
    "Review architecture before optimizing",
    "Avoid broad rewrites or safety regressions from premature optimization.",
    "unknown",
    "MEDIUM",
    "architecture",
    ("focused regression tests",),
    ("architecture/risk docs",),
    "Do not apply until a reviewed design exists; revert any exploratory patch.",
    safe_for_self_heal=False,
    human_review_required=True,
)


def _text_from_finding(finding: dict[str, Any]) -> str:
    evidence = finding.get("evidence", [])
    evidence_text = " ".join(str(item) for item in evidence if isinstance(item, dict))
    return " ".join(
        [
            str(finding.get("title", "")),
            str(finding.get("category", "")),
            str(finding.get("summary", "")),
            str(finding.get("likely_cause", "")),
            evidence_text,
        ]
    ).lower()


def _rule_for_finding(finding: dict[str, Any]) -> RecommendationRule:
    if str(finding.get("category", "")).lower() == "test_profile":
        return next(rule for rule in RULES if rule.category == "narrow test target")
    text = _text_from_finding(finding)
    for rule in RULES:
        if any(keyword in text for keyword in rule.keywords):
            return rule
    return ARCHITECTURE_REVIEW


def recommendation_from_finding(finding: dict[str, Any]) -> OptimizationRecommendation:
    rule = _rule_for_finding(finding)
    finding_id = str(finding.get("finding_id") or stable_finding_id(finding.get("title"), finding.get("summary")))
    return OptimizationRecommendation(
        recommendation_id=f"rec_{stable_finding_id(finding_id, rule.category).removeprefix('perf_')}",
        title=rule.title,
        rationale=f"Finding `{finding_id}` matches category `{rule.category}`. {finding.get('summary', '')}".strip(),
        expected_impact=rule.expected_impact,
        effort=rule.effort,
        risk_level=rule.risk_level,
        patch_area=rule.patch_area,
        tests_required=list(rule.tests_required),
        docs_required=list(rule.docs_required),
        rollback_plan=rule.rollback_plan,
        safe_for_self_heal=rule.safe_for_self_heal,
        human_review_required=rule.human_review_required,
        status="proposed",
        applies_patch=False,
    )


def _findings_from_report(report: dict[str, Any]) -> list[dict[str, Any]]:
    findings = report.get("findings")
    if isinstance(findings, list) and findings:
        return [item for item in findings if isinstance(item, dict)]
    scan_result = report.get("scan_result")
    if isinstance(scan_result, dict):
        nested = scan_result.get("findings")
        if isinstance(nested, list):
            return [item for item in nested if isinstance(item, dict)]
    durations = report.get("durations")
    if isinstance(durations, list) and durations:
        return [
            {
                "finding_id": "pytest_duration_profile",
                "title": "Pytest duration profile has slow entries",
                "category": "test_profile",
                "summary": "Pytest --durations output identified local test timing entries.",
                "likely_cause": "Test setup, fixture scope, or broad target selection may be contributing.",
                "evidence": durations[:10],
            }
        ]
    return []


def build_recommendations(report: dict[str, Any]) -> list[OptimizationRecommendation]:
    recommendations: list[OptimizationRecommendation] = []
    seen: set[str] = set()
    for finding in _findings_from_report(report):
        recommendation = recommendation_from_finding(finding)
        if recommendation.recommendation_id in seen:
            continue
        seen.add(recommendation.recommendation_id)
        recommendations.append(recommendation)
    recommendations.sort(key=lambda item: (item.human_review_required, item.risk_level, item.effort, item.title))
    return recommendations


def _latest_source_report(store: PerformanceReportStore) -> dict[str, Any]:
    for path in store.list_reports():
        try:
            payload = store.redact_payload(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        if payload.get("report_type") == "recommendations":
            continue
        if payload.get("report_type") == "test_profile":
            profile_path = store.report_path(str(payload.get("report_id", "")), suffix=".profile.json")
            if profile_path.exists():
                try:
                    profile_payload = store.redact_payload(json.loads(profile_path.read_text(encoding="utf-8")))
                    if isinstance(profile_payload, dict):
                        payload.update(profile_payload)
                except Exception:
                    pass
        payload["report_path"] = str(path)
        return payload
    return store.read_latest_report()


def suggest_fixes(project_root: str | Path = ".") -> dict[str, Any]:
    store = PerformanceReportStore(project_root)
    source_report = _latest_source_report(store)
    if source_report.get("status") == "no_report":
        return {
            **source_report,
            "recommendations": [],
            "message": "No performance report is available for recommendation generation.",
        }
    recommendations = build_recommendations(source_report)
    generated_at = utc_now_iso()
    report = PerformanceReport(
        report_id=f"recommendations_{generated_at.replace(':', '').replace('-', '')}",
        report_type="recommendations",
        generated_at=generated_at,
        status="ok",
        summary=f"Generated {len(recommendations)} optimization recommendation(s) from {source_report.get('report_id', 'latest report')}.",
        recommendations=recommendations,
        limitations=[
            "Recommendations are advisory only and do not apply patches.",
            "Safety, policy, approval, audit, and test behavior must not be weakened for speed.",
            "Human review is required unless a future approved self-heal flow explicitly accepts a low-risk recommendation.",
        ],
    )
    report_path = store.write_report(report)
    markdown_path = store.write_markdown(report)
    return store.redact_payload(
        {
            **report.to_dict(),
            "source_report_id": source_report.get("report_id"),
            "source_report_type": source_report.get("report_type"),
            "recommendation_count": len(recommendations),
            "report_path": str(report_path),
            "markdown_path": str(markdown_path),
            "applied_patches": 0,
        }
    )
