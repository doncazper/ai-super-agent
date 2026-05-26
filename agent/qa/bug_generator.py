from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from agent.qa.analyzer import load_run_records, rank_failures
from agent.qa.redaction import redact_text
from agent.qa.models import utc_now_iso


def _bugs_dir(project_root: str | Path = ".") -> Path:
    path = Path(project_root) / "bugs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _next_bug_id(project_root: str | Path = ".") -> str:
    highest = 0
    for path in _bugs_dir(project_root).glob("BUG-*.json"):
        match = re.match(r"BUG-(\d+)\.json", path.name)
        if match:
            highest = max(highest, int(match.group(1)))
    return f"BUG-{highest + 1:04d}"


def bug_from_failure(failure: dict[str, Any], *, bug_id: str | None = None) -> dict[str, Any]:
    selected_bug_id = bug_id or "BUG-0000"
    command = redact_text(str(failure.get("command_string") or ""))
    stdout = redact_text(str(failure.get("redacted_stdout_excerpt") or ""))
    stderr = redact_text(str(failure.get("redacted_stderr_excerpt") or ""))
    actual = "\n".join(part for part in (stdout, stderr, str(failure.get("notes") or "")) if part)
    return {
        "bug_id": selected_bug_id,
        "run_id": failure.get("run_id", ""),
        "command_id": failure.get("command_id", ""),
        "command": command,
        "severity": failure.get("severity", "P2"),
        "failure_type": failure.get("failure_type", "unknown"),
        "expected_behavior": "Command should match documented behavior without unsafe side effects.",
        "actual_behavior": redact_text(actual or "No redacted output excerpt captured."),
        "reproduction_command": command,
        "redacted_stdout_excerpt": stdout,
        "redacted_stderr_excerpt": stderr,
        "suspected_area": failure.get("suspected_area", ""),
        "suggested_fix": "Review the command implementation, docs, and tests before applying a scoped fix.",
        "suggested_regression_test": f"Add fixture-backed regression coverage for {failure.get('command_id', 'the affected command')}.",
        "status": "open",
        "created_at": utc_now_iso(),
        "source": "command_qa",
    }


def write_bug_report(project_root: str | Path, bug: dict[str, Any]) -> Path:
    path = _bugs_dir(project_root) / f"{bug['bug_id']}.json"
    path.write_text(json.dumps(bug, indent=2, sort_keys=True), encoding="utf-8")
    return path


def create_bugs_from_records(project_root: str | Path, records: list[dict[str, Any]]) -> dict[str, Any]:
    ranked = rank_failures(records)
    created: list[dict[str, Any]] = []
    for failure in ranked:
        bug_id = _next_bug_id(project_root)
        bug = bug_from_failure(failure, bug_id=bug_id)
        path = write_bug_report(project_root, bug)
        created.append({"bug_id": bug_id, "path": path.relative_to(Path(project_root)).as_posix(), "severity": bug["severity"]})
    return {"status": "ok", "created_count": len(created), "bugs": created}


def create_bugs_from_run(project_root: str | Path = ".", *, run_id: str | None = None, report_id: str | None = None) -> dict[str, Any]:
    records = load_run_records(project_root, run_id=run_id, report_id=report_id)
    return create_bugs_from_records(project_root, records)

