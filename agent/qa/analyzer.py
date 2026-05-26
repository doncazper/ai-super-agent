from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent.qa.logging import REPORTS_DIR, read_last_report
from agent.qa.redaction import redact_text


FAILURE_TYPES = {
    "command_not_found",
    "import_error",
    "usage_error",
    "bad_help",
    "bad_output",
    "timeout",
    "exception",
    "policy_failure",
    "approval_failure",
    "audit_failure",
    "redaction_failure",
    "provider_missing_bad_error",
    "docs_mismatch",
    "command_registry_mismatch",
    "test_gap",
    "flaky",
    "unknown",
    "nonzero_exit",
    "blocked_by_policy",
    "manual_arguments_required",
}

P0_FAILURES = {"policy_failure", "approval_failure", "audit_failure", "redaction_failure"}
P1_FAILURES = {"command_not_found", "import_error", "exception"}
P3_FAILURES = {"usage_error", "bad_help", "docs_mismatch", "command_registry_mismatch", "test_gap"}


def _report_path(project_root: str | Path, *, run_id: str | None = None, report_id: str | None = None, last: bool = False) -> Path:
    root = Path(project_root)
    if last:
        latest = read_last_report(root)
        jsonl_path = latest.get("jsonl_path")
        if not jsonl_path:
            raise FileNotFoundError("No latest QA report is available.")
        return root / jsonl_path
    selected = report_id or run_id
    if not selected:
        raise ValueError("run_id, report_id, or last=True is required")
    if selected.endswith(".jsonl"):
        path = Path(selected)
        return path if path.is_absolute() else root / path
    return root / REPORTS_DIR / f"{selected}.jsonl"


def load_run_records(project_root: str | Path = ".", *, run_id: str | None = None, report_id: str | None = None, last: bool = False) -> list[dict[str, Any]]:
    path = _report_path(project_root, run_id=run_id, report_id=report_id, last=last)
    if not path.exists():
        raise FileNotFoundError(f"QA report not found: {path}")
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        records.append(redact_record(payload))
    return records


def redact_record(record: dict[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in record.items():
        redacted[key] = redact_text(value) if isinstance(value, str) else value
    return redacted


def rank_failure(record: dict[str, Any]) -> dict[str, Any]:
    failure_type = str(record.get("failure_type") or "unknown")
    if failure_type not in FAILURE_TYPES:
        failure_type = "unknown"
    command = str(record.get("command_string") or "")
    group = str(record.get("suspected_area") or "")
    status = str(record.get("status") or "")
    if status == "passed":
        severity = "P4"
    elif failure_type in P0_FAILURES or any(word in f"{command} {group}".lower() for word in ("secret", "policy bypass", "approval bypass", "data leak")):
        severity = "P0"
    elif failure_type in P1_FAILURES or any(word in group.lower() for word in ("core", "runtime", "toolbroker", "policy")):
        severity = "P1"
    elif failure_type in P3_FAILURES:
        severity = "P3"
    elif failure_type in {"flaky"}:
        severity = "P4"
    else:
        severity = "P2"
    ranked = dict(record)
    ranked["failure_type"] = failure_type
    ranked["severity"] = severity
    ranked["rank_score"] = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}[severity]
    return ranked


def rank_failures(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    failures = [rank_failure(record) for record in records if record.get("status") != "passed"]
    return sorted(failures, key=lambda record: (record["rank_score"], record.get("command_id", "")))


def rank_last_report(project_root: str | Path = ".") -> dict[str, Any]:
    records = load_run_records(project_root, last=True)
    ranked = rank_failures(records)
    return {
        "status": "ok",
        "failure_count": len(ranked),
        "ranked_failures": ranked,
    }

