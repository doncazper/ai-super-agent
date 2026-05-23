from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent.promptops.clipboard import ClipboardUnavailable, read_clipboard, write_clipboard
from agent.promptops.importer import import_file, import_text
from agent.promptops.models import WorkbenchImportResult, WorkbenchNextResult
from agent.promptops.state import update_prompt_state
from agent.ui.prompts import (
    audit_prompts,
    format_prompt_record,
    list_prompt_records,
    mark_prompt,
    next_prompt,
    show_prompt,
)


def import_from_stdin(text: str, *, project_root: str | Path = ".", pack_id: str | None = None, single: bool = False, prompt_id: str | None = None) -> WorkbenchImportResult:
    return import_text(text, project_root=project_root, pack_id=pack_id, single=single, prompt_id=prompt_id)


def import_from_clipboard(*, project_root: str | Path = ".", pack_id: str | None = None, single: bool = False, prompt_id: str | None = None) -> WorkbenchImportResult:
    text = read_clipboard()
    return import_text(text, project_root=project_root, pack_id=pack_id, single=single, prompt_id=prompt_id)


def import_from_file(path: str | Path, *, project_root: str | Path = ".", pack_id: str | None = None) -> WorkbenchImportResult:
    return import_file(path, project_root=project_root, pack_id=pack_id)


def next_work(*, project_root: str | Path = ".") -> WorkbenchNextResult:
    record = next_prompt(project_root)
    if record is None:
        return WorkbenchNextResult("empty", None, None, None, None, None, None, None, None, error="no queued prompt is currently runnable")
    payload = show_prompt(record.prompt_id, project_root) or {}
    risk = _field_from_content(payload.get("content", ""), "risk_level") or "LOW"
    path = payload.get("path") or record.path
    return WorkbenchNextResult(
        status="ok",
        prompt_id=record.prompt_id,
        title=record.title,
        category=record.category,
        risk_level=risk,
        approval_gate=record.approval_gate or "false",
        prerequisites=record.dependencies,
        path=path,
        command=f"python smart_agent.py work show-next",
    )


def show_next(*, project_root: str | Path = ".") -> dict[str, Any]:
    result = next_work(project_root=project_root)
    if result.prompt_id is None:
        return result.to_dict()
    return show_prompt(result.prompt_id, project_root) or result.to_dict()


def copy_next(*, project_root: str | Path = ".", mark_active: bool = False) -> dict[str, Any]:
    payload = show_next(project_root=project_root)
    content = payload.get("content")
    if not content:
        return {"status": "empty", "copied": False, "error": "no prompt content available"}
    copied = False
    error = None
    try:
        write_clipboard(content)
        copied = True
    except ClipboardUnavailable as exc:
        error = str(exc)
    if mark_active and payload.get("prompt_id"):
        mark_prompt(payload["prompt_id"], "active", project_root=project_root, notes="Marked active by PromptOps copy-next.")
        update_prompt_state(project_root=project_root, active_prompt_id=payload["prompt_id"])
    return {
        "status": "ok" if copied else "fallback",
        "copied": copied,
        "prompt_id": payload.get("prompt_id"),
        "path": payload.get("path"),
        "error": error,
        "content": None if copied else content,
    }


def resume(*, project_root: str | Path = ".") -> dict[str, Any]:
    records = list_prompt_records(project_root)
    active = [record.to_dict() for record in records if record.status == "active"]
    next_result = next_work(project_root=project_root).to_dict()
    return {"active": active, "next": next_result}


def status(*, project_root: str | Path = ".") -> dict[str, Any]:
    records = list_prompt_records(project_root)
    return {
        "total": len(records),
        "queued": sum(1 for record in records if record.status == "queued"),
        "active": sum(1 for record in records if record.status == "active"),
        "completed": sum(1 for record in records if record.status == "completed"),
        "failed": sum(1 for record in records if record.status == "failed"),
        "blocked": sum(1 for record in records if record.status == "blocked"),
        "next": next_work(project_root=project_root).to_dict(),
    }


def review(*, project_root: str | Path = ".") -> dict[str, Any]:
    audit = audit_prompts(project_root)
    return {
        "status": status(project_root=project_root),
        "audit": audit,
        "active": resume(project_root=project_root)["active"],
    }


def audit(*, project_root: str | Path = ".") -> dict[str, Any]:
    return audit_prompts(project_root)


def mark_active(prompt_id: str, *, project_root: str | Path = ".") -> dict[str, str]:
    result = mark_prompt(prompt_id, "active", project_root=project_root, notes="Marked active by PromptOps Workbench.")
    update_prompt_state(project_root=project_root, active_prompt_id=prompt_id)
    return result


def mark_failed(prompt_id: str, *, project_root: str | Path = ".", notes: str | None = None) -> dict[str, str]:
    result = mark_prompt(prompt_id, "failed", project_root=project_root, notes=notes or "Marked failed by PromptOps Workbench.")
    next_record = next_prompt(project_root)
    update_prompt_state(project_root=project_root, active_prompt_id="none", next_prompt_id=next_record.prompt_id if next_record else "none")
    return result


def mark_complete(
    prompt_id: str,
    *,
    project_root: str | Path = ".",
    test_result: str | None = None,
    docs_updated: str | None = None,
    unknown: bool = False,
    notes: str | None = None,
) -> dict[str, str]:
    result = mark_prompt(
        prompt_id,
        "completed",
        project_root=project_root,
        test_result=test_result,
        docs_updated=docs_updated,
        unknown=unknown,
        notes=notes or "Marked complete by PromptOps Workbench.",
    )
    next_record = next_prompt(project_root)
    update_prompt_state(project_root=project_root, active_prompt_id="none", next_prompt_id=next_record.prompt_id if next_record else "none")
    return result


def format_json(payload: Any) -> str:
    if hasattr(payload, "to_dict"):
        payload = payload.to_dict()
    return json.dumps(payload, indent=2, sort_keys=True)


def format_readable_next(payload: WorkbenchNextResult) -> str:
    if payload.prompt_id is None:
        return payload.error or "No queued prompt is currently runnable."
    return (
        f"Next prompt: {payload.prompt_id}\n"
        f"Title: {payload.title}\n"
        f"Category: {payload.category}\n"
        f"Risk: {payload.risk_level}\n"
        f"Approval gate: {payload.approval_gate}\n"
        f"Prerequisites: {payload.prerequisites or 'none'}\n"
        f"Path: {payload.path}\n"
        f"Show: {payload.command}\n"
    )


def _field_from_content(content: str, field: str) -> str | None:
    prefix = f"{field}:"
    for line in content.splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return None

