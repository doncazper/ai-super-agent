from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


JsonObject = dict[str, Any]


@dataclass(frozen=True)
class QAApiEnvelope:
    """Stable JSON envelope for QA service/dashboard responses."""

    status: str
    generated_at: str
    read_only: bool
    data: JsonObject = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> JsonObject:
        return asdict(self)


@dataclass(frozen=True)
class QAActionEnvelope:
    """Stable JSON envelope for QA action service responses."""

    status: str
    generated_at: str
    action: str
    safe_only: bool
    data: JsonObject = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> JsonObject:
        return asdict(self)


@dataclass(frozen=True)
class QACommandCoverage:
    total: int
    active: int
    tested_by_qa_reports: int
    untested_active: int
    missing_examples: list[str] = field(default_factory=list)
    missing_tests: list[str] = field(default_factory=list)

    def to_dict(self) -> JsonObject:
        return asdict(self)


@dataclass(frozen=True)
class QAFailureSummary:
    by_severity: dict[str, int]
    failures: list[JsonObject] = field(default_factory=list)

    def to_dict(self) -> JsonObject:
        return asdict(self)


@dataclass(frozen=True)
class QABugSummary:
    open_count: int
    bugs: list[JsonObject] = field(default_factory=list)

    def to_dict(self) -> JsonObject:
        return asdict(self)

