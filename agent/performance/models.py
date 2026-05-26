from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

from .severity import normalize_severity


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_finding_id(*parts: object) -> str:
    raw = "|".join(str(part) for part in parts if part is not None)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    return f"perf_{digest}"


def _clean_list(values: list[str] | None) -> list[str]:
    return [str(value) for value in (values or []) if str(value).strip()]


@dataclass
class PerformanceEvidence:
    evidence_type: str
    path: str = ""
    line: int | None = None
    command_id: str = ""
    metric_name: str = ""
    observed_value: float | None = None
    unit: str = ""
    snippet: str = ""
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PerformanceMetric:
    name: str
    value: float
    unit: str
    threshold: float | None = None
    status: str = "observed"
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class OptimizationRecommendation:
    recommendation_id: str
    title: str
    rationale: str
    expected_impact: str
    effort: str = "unknown"
    risk_level: str = "LOW"
    patch_area: str = "unknown"
    tests_required: list[str] = field(default_factory=list)
    docs_required: list[str] = field(default_factory=list)
    rollback_plan: str = "Revert the scoped optimization patch."
    safe_for_self_heal: bool = False
    human_review_required: bool = True
    status: str = "proposed"
    applies_patch: bool = False

    def __post_init__(self) -> None:
        self.tests_required = _clean_list(self.tests_required)
        self.docs_required = _clean_list(self.docs_required)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PerformanceFinding:
    title: str
    category: str
    severity: str
    summary: str
    likely_cause: str
    evidence: list[PerformanceEvidence] = field(default_factory=list)
    recommendations: list[OptimizationRecommendation] = field(default_factory=list)
    finding_id: str = ""
    status: str = "open"
    confidence: str = "medium"
    affected_files: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        self.severity = normalize_severity(self.severity)
        self.affected_files = _clean_list(self.affected_files)
        if not self.finding_id:
            self.finding_id = stable_finding_id(self.category, self.title, self.summary, ",".join(self.affected_files))

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "evidence": [item.to_dict() for item in self.evidence],
            "recommendations": [item.to_dict() for item in self.recommendations],
        }


@dataclass
class PerformanceScanConfig:
    scan_id: str
    scan_type: str
    project_root: str = "."
    include_paths: list[str] = field(default_factory=list)
    exclude_paths: list[str] = field(default_factory=lambda: [".git", ".venv", "__pycache__", ".pytest_cache", "logs", "reports", "media_outputs", ".qa_workspace"])
    max_files: int = 5000
    timeout_seconds: int = 30
    live_providers_allowed: bool = False
    paid_apis_allowed: bool = False
    personal_data_allowed: bool = False

    def __post_init__(self) -> None:
        self.include_paths = _clean_list(self.include_paths)
        self.exclude_paths = _clean_list(self.exclude_paths)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PerformanceScanResult:
    scan_id: str
    status: str
    started_at: str
    completed_at: str
    config: PerformanceScanConfig
    metrics: list[PerformanceMetric] = field(default_factory=list)
    findings: list[PerformanceFinding] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.warnings = _clean_list(self.warnings)

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "config": self.config.to_dict(),
            "metrics": [item.to_dict() for item in self.metrics],
            "findings": [item.to_dict() for item in self.findings],
        }


@dataclass
class PerformanceBenchmarkResult:
    benchmark_id: str
    command_id: str
    command: str
    status: str
    duration_ms: float
    iterations: int = 1
    min_duration_ms: float | None = None
    median_duration_ms: float | None = None
    max_duration_ms: float | None = None
    returncode: int | None = None
    stdout_bytes: int = 0
    stderr_bytes: int = 0
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.min_duration_ms is None:
            self.min_duration_ms = self.duration_ms
        if self.median_duration_ms is None:
            self.median_duration_ms = self.duration_ms
        if self.max_duration_ms is None:
            self.max_duration_ms = self.duration_ms
        self.warnings = _clean_list(self.warnings)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PerformanceBaseline:
    baseline_id: str
    created_at: str
    source_report_id: str
    metrics: list[PerformanceMetric] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "metrics": [item.to_dict() for item in self.metrics],
        }


@dataclass
class PerformanceReport:
    report_id: str
    report_type: str
    generated_at: str
    status: str
    summary: str
    scan_result: PerformanceScanResult | None = None
    benchmark_results: list[PerformanceBenchmarkResult] = field(default_factory=list)
    findings: list[PerformanceFinding] = field(default_factory=list)
    recommendations: list[OptimizationRecommendation] = field(default_factory=list)
    baseline: PerformanceBaseline | None = None
    limitations: list[str] = field(default_factory=list)
    redacted: bool = True

    def __post_init__(self) -> None:
        self.limitations = _clean_list(self.limitations)

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "report_type": self.report_type,
            "generated_at": self.generated_at,
            "status": self.status,
            "summary": self.summary,
            "scan_result": self.scan_result.to_dict() if self.scan_result else None,
            "benchmark_results": [item.to_dict() for item in self.benchmark_results],
            "findings": [item.to_dict() for item in self.findings],
            "recommendations": [item.to_dict() for item in self.recommendations],
            "baseline": self.baseline.to_dict() if self.baseline else None,
            "limitations": list(self.limitations),
            "redacted": self.redacted,
        }
