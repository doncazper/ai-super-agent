from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


REPORTS_DIR = Path("reports/qa")


@dataclass(frozen=True)
class CommandRunRecord:
    run_id: str
    command_id: str
    command_string: str
    qa_tier: int
    risk_level: str
    start_time: str
    duration_ms: int
    exit_code: int | None
    redacted_stdout_excerpt: str
    redacted_stderr_excerpt: str
    full_log_path: str
    status: str
    failure_type: str
    severity: str
    suspected_area: str
    linked_bug_id: str
    regression_test_path: str
    feature_id: str
    maturity_impact: str
    audit_ids: list[str]
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def ensure_reports_dir(project_root: str | Path = ".") -> Path:
    path = Path(project_root) / REPORTS_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_run_report(
    records: list[CommandRunRecord],
    *,
    run_id: str,
    project_root: str | Path = ".",
    notes: list[str] | None = None,
    sandbox_path: str = "",
) -> dict[str, Any]:
    reports_dir = ensure_reports_dir(project_root)
    jsonl_path = reports_dir / f"{run_id}.jsonl"
    markdown_path = reports_dir / f"{run_id}.md"
    payloads = [record.to_dict() for record in records]
    jsonl_path.write_text("\n".join(json.dumps(payload, sort_keys=True) for payload in payloads) + ("\n" if payloads else ""), encoding="utf-8")
    lines = [
        f"# Command QA Run {run_id}",
        "",
        f"- Records: {len(records)}",
        f"- Passed: {sum(1 for r in records if r.status == 'passed')}",
        f"- Failed: {sum(1 for r in records if r.status == 'failed')}",
        f"- Skipped: {sum(1 for r in records if r.status == 'skipped')}",
        f"- Blocked: {sum(1 for r in records if r.status == 'blocked')}",
        f"- Sandbox: {sandbox_path or 'not used'}",
        "",
        "## Notes",
    ]
    for note in notes or []:
        lines.append(f"- {note}")
    lines.extend(["", "## Records", ""])
    for record in records:
        lines.append(f"- `{record.command_id}` tier {record.qa_tier}: {record.status} ({record.failure_type or 'none'})")
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    latest_path = reports_dir / "last_run.json"
    latest_payload = {
        "run_id": run_id,
        "jsonl_path": jsonl_path.relative_to(Path(project_root)).as_posix(),
        "markdown_path": markdown_path.relative_to(Path(project_root)).as_posix(),
        "record_count": len(records),
        "sandbox_path": sandbox_path,
    }
    latest_path.write_text(json.dumps(latest_payload, indent=2, sort_keys=True), encoding="utf-8")
    return latest_payload


def read_last_report(project_root: str | Path = ".") -> dict[str, Any]:
    path = Path(project_root) / REPORTS_DIR / "last_run.json"
    if not path.exists():
        return {"status": "not_found", "message": "No command QA run report exists yet."}
    return json.loads(path.read_text(encoding="utf-8"))
