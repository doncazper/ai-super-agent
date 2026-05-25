from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.prompts.evidence import audit_prompt_evidence
from agent.ui.prompts import list_prompt_records, next_prompt


def missed_prompts(project_root: str | Path = ".") -> dict[str, Any]:
    audit = audit_prompt_evidence(project_root)
    missed = [
        item
        for item in audit["evidence"]
        if item["status"] == "queued" and item["classification"] in {"no_evidence", "partial"}
    ]
    return {"status": "ok", "prompts": missed}


def superseded_prompts(project_root: str | Path = ".") -> dict[str, Any]:
    prompts = [record.to_dict() for record in list_prompt_records(project_root) if record.status == "superseded"]
    return {"status": "ok", "prompts": prompts}


def stale_prompts(project_root: str | Path = ".") -> dict[str, Any]:
    audit = audit_prompt_evidence(project_root)
    stale = [item for item in audit["evidence"] if item["classification"] == "stale"]
    return {"status": "ok", "prompts": stale}


def recover_plan(project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    records = list_prompt_records(root)
    prompt_ids = {record.prompt_id for record in records}
    files = sorted(root.glob("prompts/**/*.md"))
    file_ids = {path.stem for path in files}
    orphaned_files = [path.relative_to(root).as_posix() for path in files if path.stem not in prompt_ids]
    ghost_records = [record.to_dict() for record in records if record.path and not (root / record.path).exists()]
    missed = missed_prompts(root)["prompts"]
    stale = stale_prompts(root)["prompts"]
    next_record = next_prompt(root)
    return {
        "status": "ok",
        "next_prompt_id": next_record.prompt_id if next_record else None,
        "orphaned_prompt_files": orphaned_files,
        "ghost_records": ghost_records,
        "missed_prompts": missed,
        "stale_completed_prompts": stale,
        "recommended_actions": _recommendations(orphaned_files, ghost_records, missed, stale),
        "auto_run": False,
    }


def reconcile(project_root: str | Path = ".") -> dict[str, Any]:
    plan = recover_plan(project_root)
    return {
        "status": "needs_review" if plan["recommended_actions"] else "ok",
        "auto_modified": False,
        "message": "reconcile is conservative in v1 and only reports a recovery plan",
        "plan": plan,
    }


def _recommendations(orphaned_files: list[str], ghost_records: list[dict[str, Any]], missed: list[dict[str, Any]], stale: list[dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    if orphaned_files:
        actions.append("Review orphaned prompt files and add ledger/queue records or move them to superseded/skipped.")
    if ghost_records:
        actions.append("Review ghost ledger/queue records whose prompt files are missing before marking complete.")
    if missed:
        actions.append("Run or explicitly skip queued prompts with no completion evidence.")
    if stale:
        actions.append("Add evidence links or downgrade stale completed prompts to needs_review.")
    return actions
