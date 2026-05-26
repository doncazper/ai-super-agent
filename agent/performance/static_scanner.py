from __future__ import annotations

import ast
from pathlib import Path

from .models import (
    OptimizationRecommendation,
    PerformanceEvidence,
    PerformanceFinding,
    PerformanceReport,
    PerformanceScanConfig,
    PerformanceScanResult,
    utc_now_iso,
)
from .patterns import DEFAULT_EXCLUDES, HEAVY_OPTIONAL_IMPORTS, STATIC_PATTERNS, StaticPattern
from .reports import PerformanceReportStore


STARTUP_PATHS = {"smart_agent.py", "agent/ui/cli_commands.py", "agent/tools/registry.py"}


def should_exclude(path: Path, root: Path, excludes: tuple[str, ...] = DEFAULT_EXCLUDES) -> bool:
    try:
        relative_parts = path.relative_to(root).parts
    except ValueError:
        return True
    return any(part in excludes for part in relative_parts)


def iter_python_files(root: Path, *, max_files: int, excludes: tuple[str, ...] = DEFAULT_EXCLUDES) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.py"):
        if should_exclude(path, root, excludes):
            continue
        files.append(path)
        if len(files) >= max_files:
            break
    return files


def _recommendation(pattern: StaticPattern) -> OptimizationRecommendation:
    return OptimizationRecommendation(
        recommendation_id=f"rec_{pattern.pattern_id}",
        title=pattern.recommendation,
        rationale=pattern.likely_cause,
        expected_impact="Reduce latency or hang risk in affected paths.",
        effort="small/medium",
        risk_level="LOW",
        tests_required=["targeted regression test for the affected path"],
        docs_required=["update performance notes if user-facing behavior changes"],
        applies_patch=False,
    )


def _finding_for_pattern(pattern: StaticPattern, path: Path, root: Path, line_number: int, line: str) -> PerformanceFinding:
    relative = str(path.relative_to(root))
    return PerformanceFinding(
        title=pattern.title,
        category=pattern.category,
        severity=pattern.severity,
        summary=f"{pattern.title} in {relative}:{line_number}",
        likely_cause=pattern.likely_cause,
        affected_files=[relative],
        evidence=[
            PerformanceEvidence(
                evidence_type="static",
                path=relative,
                line=line_number,
                snippet=line.strip()[:240],
            )
        ],
        recommendations=[_recommendation(pattern)],
    )


def _heavy_import_findings(path: Path, root: Path, text: str) -> list[PerformanceFinding]:
    relative = str(path.relative_to(root))
    if relative not in STARTUP_PATHS:
        return []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    findings: list[PerformanceFinding] = []
    for node in ast.walk(tree):
        module = ""
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name.split(".")[0]
                if module in HEAVY_OPTIONAL_IMPORTS:
                    break
        elif isinstance(node, ast.ImportFrom):
            module = (node.module or "").split(".")[0]
        if module not in HEAVY_OPTIONAL_IMPORTS:
            continue
        findings.append(
            PerformanceFinding(
                title="Optional heavy import in startup path",
                category="Startup/import overhead",
                severity="P2",
                summary=f"Startup path imports optional heavy module `{module}` in {relative}:{getattr(node, 'lineno', 1)}",
                likely_cause="Optional provider or data libraries imported at startup can slow CLI launch.",
                affected_files=[relative],
                evidence=[
                    PerformanceEvidence(
                        evidence_type="static",
                        path=relative,
                        line=getattr(node, "lineno", None),
                        snippet=f"import {module}",
                    )
                ],
                recommendations=[
                    OptimizationRecommendation(
                        recommendation_id="rec_lazy_optional_import",
                        title="Lazy-load optional heavy imports",
                        rationale="CLI startup should not import optional provider runtimes.",
                        expected_impact="Lower startup overhead and fewer optional dependency failures.",
                        effort="medium",
                        risk_level="LOW",
                        tests_required=["startup import guard test"],
                        docs_required=["update performance overhead policy"],
                    )
                ],
            )
        )
    return findings


def scan_static(project_root: str | Path = ".", *, max_files: int = 5000, write_report: bool = True) -> dict[str, object]:
    root = Path(project_root).resolve()
    scan_id = f"static_{utc_now_iso().replace(':', '').replace('-', '')}"
    config = PerformanceScanConfig(
        scan_id=scan_id,
        scan_type="static",
        project_root=str(root),
        exclude_paths=list(DEFAULT_EXCLUDES),
        max_files=max_files,
        live_providers_allowed=False,
        paid_apis_allowed=False,
        personal_data_allowed=False,
    )
    started_at = utc_now_iso()
    findings: list[PerformanceFinding] = []
    warnings: list[str] = []
    files = iter_python_files(root, max_files=max_files)
    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            warnings.append(f"could not read {path}: {exc}")
            continue
        findings.extend(_heavy_import_findings(path, root, text))
        lines = text.splitlines()
        loop_window: list[int] = []
        for index, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith(("for ", "while ")):
                loop_window.append(index)
            loop_window = [line_number for line_number in loop_window if index - line_number <= 25]
            for pattern in STATIC_PATTERNS:
                if not pattern.regex.search(line):
                    continue
                findings.append(_finding_for_pattern(pattern, path, root, index, line))
            if loop_window and ("load_capabilities_config(" in stripped or "RuntimeConfig.from_env(" in stripped):
                findings.append(
                    PerformanceFinding(
                        title="Repeated config load in loop candidate",
                        category="Repeated config loads in loops",
                        severity="P2",
                        summary=f"Config/runtime load appears inside or near a loop in {path.relative_to(root)}:{index}",
                        likely_cause="Repeated config parsing in loops can dominate command latency.",
                        affected_files=[str(path.relative_to(root))],
                        evidence=[PerformanceEvidence(evidence_type="static", path=str(path.relative_to(root)), line=index, snippet=stripped[:240])],
                        recommendations=[
                            OptimizationRecommendation(
                                recommendation_id="rec_cache_config_for_loop",
                                title="Load config once before the loop",
                                rationale="Config parsing is usually invariant inside a loop.",
                                expected_impact="Reduce repeated IO and parsing overhead.",
                                effort="small",
                                risk_level="LOW",
                            )
                        ],
                    )
                )
            relative_name = str(path.relative_to(root)).lower()
            if ("status" in relative_name or "dashboard" in relative_name) and (".read_text()" in stripped or ".read()" in stripped):
                findings.append(
                    PerformanceFinding(
                        title="Large read candidate in status/dashboard path",
                        category="Status/dashboard large reads",
                        severity="P3",
                        summary=f"Status/dashboard path may read whole files in {path.relative_to(root)}:{index}",
                        likely_cause="Read-only status surfaces should avoid expensive whole-file reads.",
                        affected_files=[str(path.relative_to(root))],
                        evidence=[PerformanceEvidence(evidence_type="static", path=str(path.relative_to(root)), line=index, snippet=stripped[:240])],
                        recommendations=[
                            OptimizationRecommendation(
                                recommendation_id="rec_bound_status_dashboard_reads",
                                title="Bound status/dashboard reads",
                                rationale="Status surfaces should remain cheap and predictable.",
                                expected_impact="Lower status/dashboard latency on large artifacts.",
                                effort="small",
                                risk_level="LOW",
                            )
                        ],
                    )
                )
            if ("doctor" in path.name or "status" in path.name) and ("requests." in stripped or "httpx." in stripped):
                findings.append(
                    PerformanceFinding(
                        title="Possible live provider call in status/doctor path",
                        category="Doctor/status live call",
                        severity="P2",
                        summary=f"Status/doctor-like file may call a live provider in {path.relative_to(root)}:{index}",
                        likely_cause="Doctor/status paths should prefer config-only or explicit health checks.",
                        affected_files=[str(path.relative_to(root))],
                        evidence=[PerformanceEvidence(evidence_type="static", path=str(path.relative_to(root)), line=index, snippet=stripped[:240])],
                        recommendations=[
                            OptimizationRecommendation(
                                recommendation_id="rec_status_no_live_provider",
                                title="Move live provider checks behind explicit health commands",
                                rationale="Status commands should be cheap and unavailable-safe.",
                                expected_impact="Avoid slow or surprising network calls in diagnostics.",
                                effort="medium",
                                risk_level="LOW",
                            )
                        ],
                    )
                )
    completed_at = utc_now_iso()
    result = PerformanceScanResult(
        scan_id=scan_id,
        status="ok",
        started_at=started_at,
        completed_at=completed_at,
        config=config,
        findings=findings,
        warnings=warnings,
    )
    report = PerformanceReport(
        report_id=scan_id,
        report_type="static",
        generated_at=completed_at,
        status="ok",
        summary=f"Static scan inspected {len(files)} Python files and found {len(findings)} heuristic findings.",
        scan_result=result,
        findings=findings,
        recommendations=[recommendation for finding in findings for recommendation in finding.recommendations],
        limitations=[
            "Heuristic static findings require human review.",
            "The scanner does not execute scanned code.",
            "The scanner does not call live providers or paid APIs.",
        ],
    )
    output: dict[str, object] = report.to_dict()
    output["files_scanned"] = len(files)
    output["excluded_paths"] = list(DEFAULT_EXCLUDES)
    if write_report:
        store = PerformanceReportStore(root)
        json_path = store.write_report(report)
        markdown_path = store.write_markdown(report)
        output["report_path"] = str(json_path)
        output["markdown_path"] = str(markdown_path)
    return PerformanceReportStore(root).redact_payload(output)
