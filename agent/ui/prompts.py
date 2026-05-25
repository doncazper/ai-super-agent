from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROMPT_STATUSES = {
    "queued",
    "active",
    "completed",
    "skipped",
    "failed",
    "superseded",
    "blocked",
    "approval_required",
    "needs_review",
}
PROMPT_DIRS = {
    "queued": "prompts/queued",
    "active": "prompts/active",
    "completed": "prompts/completed",
    "skipped": "prompts/skipped",
    "failed": "prompts/failed",
    "superseded": "prompts/superseded",
    "blocked": "prompts/blocked",
    "approval_required": "prompts/approval_required",
    "needs_review": "prompts/needs_review",
}
LEDGER_PATH = Path("docs/PROMPT_LEDGER.md")
QUEUE_PATH = Path("docs/PROMPT_QUEUE.md")
AUDIT_PATH = Path("docs/PROMPT_AUDIT.md")
EVIDENCE_PATHS = (
    Path("CHANGELOG.md"),
    Path("docs/COMPLETION_REPORT.md"),
    Path("docs/FEATURE_REGISTRY.md"),
    Path("docs/FEATURE_MATURITY.md"),
    Path("docs/PROJECT_STATE.md"),
)


@dataclass(frozen=True)
class PromptRecord:
    prompt_id: str
    title: str
    category: str
    status: str
    source: str = "reconstructed"
    path: str = ""
    notes: str = ""
    dependencies: str = ""
    approval_gate: str = ""
    risk_level: str = ""
    pack_id: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "prompt_id": self.prompt_id,
            "title": self.title,
            "category": self.category,
            "status": self.status,
            "source": self.source,
            "path": self.path,
            "notes": self.notes,
            "dependencies": self.dependencies,
            "approval_gate": self.approval_gate,
            "risk_level": self.risk_level,
            "pack_id": self.pack_id,
        }


def list_prompt_records(project_root: str | Path = ".") -> list[PromptRecord]:
    root = Path(project_root)
    rows: dict[str, PromptRecord] = {}
    for path in (LEDGER_PATH, QUEUE_PATH):
        for record in _records_from_markdown_table(root / path, path.as_posix()):
            rows[record.prompt_id] = record
    for record in _records_from_prompt_dirs(root):
        rows[record.prompt_id] = record
    return sorted(rows.values(), key=lambda item: item.prompt_id)


def next_prompt(project_root: str | Path = ".") -> PromptRecord | None:
    root = Path(project_root)
    status_by_id = {record.prompt_id: record.status for record in list_prompt_records(root)}
    for record in _records_from_markdown_table(root / QUEUE_PATH, QUEUE_PATH.as_posix()):
        effective_status = status_by_id.get(record.prompt_id, record.status)
        if (
            effective_status == "queued"
            and record.status == "queued"
            and _dependencies_complete(record.dependencies, status_by_id)
            and not _approval_gate_blocks(record.approval_gate)
        ):
            return record
    return None


def show_prompt(prompt_id: str, project_root: str | Path = ".") -> dict[str, Any] | None:
    root = Path(project_root)
    record_path = _find_record_file(prompt_id, root)
    records = {record.prompt_id: record for record in list_prompt_records(root)}
    record = records.get(prompt_id)
    if record_path is None and record is None:
        return None
    payload: dict[str, Any] = {"prompt_id": prompt_id}
    if record is not None:
        payload.update(record.to_dict())
    if record_path is not None:
        payload["path"] = str(record_path.relative_to(root))
        payload["content"] = record_path.read_text(encoding="utf-8")
    return payload


def add_prompt_record(source: str, project_root: str | Path = ".") -> dict[str, str]:
    root = Path(project_root)
    _ensure_dirs(root)
    source_path = root / source
    if source_path.exists() and source_path.is_file():
        content = source_path.read_text(encoding="utf-8")
        prompt_id = _prompt_id_from_content(content) or _slug(source_path.stem)
        title = _prompt_title_from_content(content) or source_path.stem.replace("_", " ").replace("-", " ").title()
    else:
        prompt_id = _slug(source)
        title = source.replace("_", " ").replace("-", " ").title()
        content = _new_record_content(prompt_id=prompt_id, title=title, status="queued")
    target = root / PROMPT_DIRS["queued"] / f"{prompt_id}.md"
    if source_path.exists() and source_path.resolve() != target.resolve():
        shutil.copyfile(source_path, target)
        _rewrite_field(target, "status", "queued")
    else:
        target.write_text(content, encoding="utf-8")
    return {"prompt_id": prompt_id, "status": "queued", "path": str(target.relative_to(root))}


def mark_prompt(
    prompt_id: str,
    status: str,
    *,
    project_root: str | Path = ".",
    test_result: str | None = None,
    docs_updated: str | None = None,
    unknown: bool = False,
    notes: str | None = None,
    superseded_by: str | None = None,
) -> dict[str, str]:
    if status not in PROMPT_STATUSES:
        raise ValueError(f"invalid prompt status: {status}")
    if status == "completed" and not unknown and (not test_result or not docs_updated):
        raise ValueError("mark-complete requires --test-result and --docs-updated, or --unknown")
    if status == "failed" and not notes:
        raise ValueError("mark-failed requires --notes with a failure reason")
    if status == "active":
        active = [record.prompt_id for record in list_prompt_records(project_root) if record.status == "active" and record.prompt_id != prompt_id]
        if active:
            raise ValueError(f"cannot mark {prompt_id} active while another prompt is active: {', '.join(active)}")
    root = Path(project_root)
    _ensure_dirs(root)
    source = _find_record_file(prompt_id, root)
    if source is None:
        source = root / PROMPT_DIRS.get(status, PROMPT_DIRS["queued"]) / f"{prompt_id}.md"
        source.write_text(_new_record_content(prompt_id=prompt_id, title=prompt_id, status=status), encoding="utf-8")
    target_dir = root / PROMPT_DIRS.get(status, PROMPT_DIRS["queued"])
    target = target_dir / source.name
    if source != target:
        shutil.move(str(source), str(target))
    _rewrite_field(target, "status", status)
    now = _now_iso()
    if status == "active":
        _rewrite_field(target, "started_at", now)
    if status in {"completed", "skipped", "failed", "superseded", "blocked"}:
        _rewrite_field(target, "completed_at", now)
    if test_result is not None:
        _rewrite_field(target, "test_result", test_result)
    if docs_updated is not None:
        _rewrite_field(target, "docs_updated", docs_updated)
    if notes is not None:
        _rewrite_field(target, "notes", notes)
    if superseded_by is not None:
        _rewrite_field(target, "superseded_by", superseded_by)
    _update_tracking_tables(
        root,
        prompt_id,
        {
            "status": status,
            "started_at": now if status == "active" else None,
            "completed_at": now if status in {"completed", "skipped", "failed", "superseded", "blocked", "needs_review"} else None,
            "test_result": test_result or ("unknown" if unknown and status == "completed" else None),
            "docs_updated": docs_updated or ("unknown" if unknown and status == "completed" else None),
            "notes": notes,
            "blockers": notes if status in {"failed", "blocked", "needs_review"} else None,
            "superseded_by": superseded_by,
        },
    )
    return {"prompt_id": prompt_id, "status": status, "path": str(target.relative_to(root))}


def audit_prompts(project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    records = list_prompt_records(root)
    active = [record.prompt_id for record in records if record.status == "active"]
    evidence_text = _evidence_text(root)
    definitely_complete = [
        record.prompt_id
        for record in records
        if record.status == "completed" and _has_evidence(record, evidence_text)
    ]
    missing_evidence = [
        record.prompt_id
        for record in records
        if record.status == "completed" and not _has_evidence(record, evidence_text)
    ]
    queued_without_evidence = [
        record.prompt_id
        for record in records
        if record.status == "queued" and not _has_evidence(record, evidence_text)
    ]
    return {
        "total": len(records),
        "active_prompt_ids": active,
        "active_count": len(active),
        "queued_count": sum(1 for record in records if record.status == "queued"),
        "completed_count": sum(1 for record in records if record.status == "completed"),
        "blocked_count": sum(1 for record in records if record.status == "blocked"),
        "superseded_count": sum(1 for record in records if record.status == "superseded"),
        "definitely_complete": definitely_complete,
        "completed_missing_evidence": missing_evidence,
        "queued_without_evidence": queued_without_evidence,
        "next_prompt_id": next_prompt(root).prompt_id if next_prompt(root) else None,
    }


def missing_prompts(project_root: str | Path = ".") -> list[PromptRecord]:
    root = Path(project_root)
    evidence_text = _evidence_text(root)
    return [record for record in list_prompt_records(root) if record.status == "queued" and not _has_evidence(record, evidence_text)]


def search_prompt_records(query: str, project_root: str | Path = ".") -> list[PromptRecord]:
    terms = [term.lower() for term in query.split() if term.strip()]
    if not terms:
        return []
    matches: list[PromptRecord] = []
    for record in list_prompt_records(project_root):
        haystack = " ".join(
            [
                record.prompt_id,
                record.title,
                record.category,
                record.status,
                record.notes,
                record.path,
                record.risk_level,
                record.pack_id,
            ]
        ).lower()
        if all(term in haystack for term in terms):
            matches.append(record)
    return matches


def format_prompt_records(records: list[PromptRecord]) -> str:
    return json.dumps({"prompts": [record.to_dict() for record in records]}, indent=2, sort_keys=True)


def format_prompt_record(record: PromptRecord | dict[str, Any] | None) -> str:
    if record is None:
        return json.dumps({"status": "not_found"}, indent=2, sort_keys=True)
    if isinstance(record, PromptRecord):
        payload = record.to_dict()
    else:
        payload = record
    return json.dumps(payload, indent=2, sort_keys=True)


def _records_from_markdown_table(path: Path, source_path: str) -> list[PromptRecord]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    records: list[PromptRecord] = []
    for index, line in enumerate(lines):
        if not line.startswith("|") or "prompt_id" not in line:
            continue
        headers = [_clean_cell(cell) for cell in line.strip("|").split("|")]
        if "prompt_id" not in headers or "status" not in headers:
            continue
        for row in lines[index + 2 :]:
            if not row.startswith("|"):
                break
            cells = [_clean_cell(cell) for cell in row.strip("|").split("|")]
            if len(cells) != len(headers):
                continue
            payload = dict(zip(headers, cells))
            prompt_id = payload.get("prompt_id", "")
            status = payload.get("status", "")
            if prompt_id and status in PROMPT_STATUSES:
                records.append(
                    PromptRecord(
                        prompt_id=prompt_id,
                        title=payload.get("title") or payload.get("prompt_group") or prompt_id,
                        category=payload.get("category", ""),
                        status=status,
                        source=payload.get("source", "reconstructed"),
                        path=source_path,
                        notes=payload.get("notes", ""),
                        dependencies=payload.get("prerequisite_prompt_ids", "") or payload.get("depends_on", ""),
                        approval_gate=payload.get("approval_gate", ""),
                        risk_level=payload.get("risk_level", ""),
                        pack_id=payload.get("pack_id", ""),
                    )
                )
        break
    return records


def _records_from_prompt_dirs(root: Path) -> list[PromptRecord]:
    records: list[PromptRecord] = []
    for status, directory in PROMPT_DIRS.items():
        for path in sorted((root / directory).glob("*.md")):
            content = path.read_text(encoding="utf-8")
            prompt_id = _prompt_id_from_content(content) or path.stem
            title = _prompt_title_from_content(content) or prompt_id
            file_status = _field_from_content(content, "status") or status
            if file_status not in PROMPT_STATUSES:
                file_status = status
            records.append(
                PromptRecord(
                    prompt_id=prompt_id,
                    title=title,
                    category=_field_from_content(content, "category") or "",
                    status=file_status,
                    source=_field_from_content(content, "source") or "user",
                    path=str(path.relative_to(root)),
                    notes=_field_from_content(content, "notes") or "",
                    dependencies=_field_from_content(content, "depends_on") or "",
                    approval_gate=_field_from_content(content, "approval_gate") or "",
                    risk_level=_field_from_content(content, "risk_level") or "",
                    pack_id=_field_from_content(content, "pack_id") or "",
                )
            )
    return records


def _find_record_file(prompt_id: str, root: Path) -> Path | None:
    for directory in PROMPT_DIRS.values():
        candidate = root / directory / f"{prompt_id}.md"
        if candidate.exists():
            return candidate
    for directory in PROMPT_DIRS.values():
        for path in (root / directory).glob("*.md"):
            if _prompt_id_from_content(path.read_text(encoding="utf-8")) == prompt_id:
                return path
    return None


def _new_record_content(*, prompt_id: str, title: str, status: str) -> str:
    now = _now_iso()
    return f"""# Prompt Record: {title}

prompt_id: {prompt_id}
title: {title}
category: uncategorized
pack_id:
risk_level: LOW
approval_gate: false
depends_on: []
status: {status}
source: user
created_at: {now}
pasted_to_codex: unknown
started_at:
completed_at:
branch:
commit_hash:
related_feature_ids:
related_files:
files_expected:
files_changed:
expected_outputs:
commands_expected:
commands_run:
tests_expected:
tests_run:
test_result:
docs_updated:
changelog_updated:
feature_registry_updated:
feature_maturity_updated:
command_registry_updated:
completion_report_updated:
evidence_links:
blockers:
next_prompt_id:
supersedes:
superseded_by:
notes:
"""


def _rewrite_field(path: Path, field: str, value: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    prefix = f"{field}:"
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines[index] = f"{prefix} {value}"
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    lines.append(f"{prefix} {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _update_tracking_tables(root: Path, prompt_id: str, updates: dict[str, str | None]) -> None:
    for path in (root / LEDGER_PATH, root / QUEUE_PATH):
        if path.exists():
            _update_markdown_table_row(path, prompt_id, updates)


def _update_markdown_table_row(path: Path, prompt_id: str, updates: dict[str, str | None]) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    in_table = False
    headers: list[str] = []
    changed = False
    for index, line in enumerate(lines):
        if not line.startswith("|"):
            if in_table:
                break
            continue
        cells = [_clean_cell(cell) for cell in line.strip("|").split("|")]
        if "prompt_id" in cells:
            headers = cells
            in_table = True
            continue
        if not in_table or "---" in line:
            continue
        row = [_clean_cell(cell) for cell in line.strip("|").split("|")]
        if len(row) != len(headers):
            continue
        payload = dict(zip(headers, row))
        if payload.get("prompt_id") != prompt_id:
            continue
        for field, value in updates.items():
            if value is not None and field in payload:
                payload[field] = str(value)
        lines[index] = "| " + " | ".join(payload.get(header, "") for header in headers) + " |"
        changed = True
        break
    if changed:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _prompt_id_from_content(content: str) -> str | None:
    return _field_from_content(content, "prompt_id")


def _prompt_title_from_content(content: str) -> str | None:
    return _field_from_content(content, "title")


def _field_from_content(content: str, field: str) -> str | None:
    match = re.search(rf"^{re.escape(field)}:\s*(.+?)\s*$", content, flags=re.MULTILINE)
    return match.group(1).strip() if match else None


def _has_evidence(record: PromptRecord, evidence_text: str) -> bool:
    title_terms = [term for term in re.split(r"[\s/_+-]+", record.title.lower()) if len(term) >= 5]
    if record.prompt_id.lower() in evidence_text:
        return True
    return bool(title_terms and sum(1 for term in title_terms if term in evidence_text) >= min(2, len(title_terms)))


def _dependencies_complete(value: str, status_by_id: dict[str, str]) -> bool:
    dependencies = [part.strip().strip('"').strip("'") for part in re.split(r"[,\[\]]+", value) if part.strip()]
    return all(status_by_id.get(dependency) == "completed" for dependency in dependencies)


def _approval_gate_blocks(value: str) -> bool:
    normalized = value.strip().lower()
    return normalized in {"true", "yes", "approval required", "blocked"}


def _evidence_text(root: Path) -> str:
    chunks: list[str] = []
    for path in EVIDENCE_PATHS:
        candidate = root / path
        if candidate.exists():
            chunks.append(candidate.read_text(encoding="utf-8", errors="ignore").lower())
    return "\n".join(chunks)


def _clean_cell(value: str) -> str:
    return value.strip().replace("`", "")


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "prompt"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _ensure_dirs(root: Path) -> None:
    for directory in PROMPT_DIRS.values():
        (root / directory).mkdir(parents=True, exist_ok=True)
