from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.qa.service import QAService, next_safe_fix_candidate


def _data(response: dict[str, Any]) -> dict[str, Any]:
    return dict(response.get("data", {}))


def command_qa_dashboard(project_root: str | Path = ".") -> dict[str, Any]:
    service = QAService(project_root)
    status = _data(service.get_qa_status())
    coverage = _data(service.get_command_coverage())
    failures = _data(service.get_failures_by_severity())
    open_bugs = _data(service.get_open_bugs())
    batch = _data(service.get_next_safe_batch(limit=5))
    maturity = _data(service.get_maturity_impact())
    next_fix = _data(service.get_next_safe_fix()).get("candidate", {})
    return {
        "status": "ok",
        "read_only": True,
        "backend_boundary": "agent.qa.service.QAService",
        "command_totals": {
            "total": coverage.get("total", 0),
            "active": coverage.get("active", 0),
            "tested_by_qa_reports": coverage.get("tested_by_qa_reports", 0),
            "untested_active": coverage.get("untested_active", 0),
        },
        "run_counts": _run_counts(project_root),
        "failures_by_severity": failures.get("by_severity", {}),
        "stale_commands": [],
        "commands_missing_examples": coverage.get("missing_examples", []),
        "commands_missing_tests": coverage.get("missing_tests", []),
        "features_needing_live_validation_mentions": _feature_live_validation_mentions(project_root),
        "top_bugs": open_bugs.get("bugs", [])[:10],
        "next_recommended_qa_batch": batch.get("commands", []),
        "next_safe_self_heal_candidate": next_fix,
        "maturity_impact": maturity,
        "service_status": status,
    }


def _run_counts(project_root: str | Path) -> dict[str, int]:
    service = QAService(project_root)
    counts: dict[str, int] = {}
    for record in service._load_qa_records():
        status = str(record.get("status", "unknown"))
        counts[status] = counts.get(status, 0) + 1
    return counts


def _feature_live_validation_mentions(project_root: str | Path) -> int:
    path = Path(project_root) / "docs/FEATURE_MATURITY.md"
    if not path.exists():
        return 0
    maturity_text = path.read_text(encoding="utf-8")
    return maturity_text.count("Live validation") + maturity_text.count("live validation")


def feature_maturity_impact(project_root: str | Path = ".") -> dict[str, Any]:
    return _data(QAService(project_root).get_maturity_impact())

