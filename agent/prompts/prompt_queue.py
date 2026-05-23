from __future__ import annotations

from pathlib import Path

from agent.prompts.pack_models import PromptPack, now_iso
from agent.ui.prompts import PromptRecord, list_prompt_records


LEDGER_PATH = Path("docs/PROMPT_LEDGER.md")
QUEUE_PATH = Path("docs/PROMPT_QUEUE.md")


def append_pack_to_ledger(pack: PromptPack, *, project_root: str | Path = ".") -> None:
    path = Path(project_root) / LEDGER_PATH
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_ledger_header(), encoding="utf-8")
    existing = path.read_text(encoding="utf-8")
    lines = []
    for prompt in sorted(pack.prompts, key=lambda item: item.order):
        if f"| {prompt.prompt_id} |" in existing:
            continue
        lines.append(
            "| "
            + " | ".join(
                [
                    prompt.prompt_id,
                    _cell(prompt.title),
                    _cell(prompt.category),
                    prompt.status,
                    f"pack:{pack.pack_id}",
                    now_iso(),
                    "yes",
                    "",
                    "",
                    "main",
                    "",
                    "",
                    "Imported prompt pack split file",
                    "TBD",
                    "no",
                    "not run",
                    "no",
                    "no",
                    "no",
                    "no",
                    "no",
                    "approval gate" if prompt.approval_gate else "none",
                    "",
                    "",
                    "",
                    f"Imported from {pack.pack_id}",
                ]
            )
            + " |"
        )
    if lines:
        path.write_text(existing.rstrip() + "\n" + "\n".join(lines) + "\n", encoding="utf-8")


def append_pack_to_queue(pack: PromptPack, *, project_root: str | Path = ".") -> None:
    path = Path(project_root) / QUEUE_PATH
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_queue_header(), encoding="utf-8")
    existing = path.read_text(encoding="utf-8")
    lines = []
    for prompt in sorted(pack.prompts, key=lambda item: item.order):
        if f"| {prompt.prompt_id} |" in existing:
            continue
        approval_gate = "true" if prompt.approval_gate else "false"
        lines.append(
            "| "
            + " | ".join(
                [
                    prompt.prompt_id,
                    _cell(prompt.title),
                    _cell(prompt.category),
                    prompt.status,
                    ", ".join(prompt.depends_on),
                    approval_gate,
                    "Run exactly one imported prompt through the mini-SDLC",
                    "Relevant tests, docs validation, startup policy, capability manifest validation",
                    f"Imported from {pack.pack_id}; risk {prompt.risk_level}",
                ]
            )
            + " |"
        )
    if lines:
        path.write_text(existing.rstrip() + "\n" + "\n".join(lines) + "\n", encoding="utf-8")


def next_queued_prompt(project_root: str | Path = ".") -> PromptRecord | None:
    records = list_prompt_records(project_root)
    by_id = {record.prompt_id: record for record in records}
    for record in records:
        effective = by_id.get(record.prompt_id)
        if record.status != "queued" or (effective and effective.status != "queued"):
            continue
        if _approval_blocks(record.approval_gate):
            continue
        dependencies = [part.strip() for part in record.dependencies.split(",") if part.strip()]
        if all(by_id.get(dependency) and by_id[dependency].status == "completed" for dependency in dependencies):
            return record
    return None


def _approval_blocks(value: str) -> bool:
    normalized = value.lower()
    return normalized in {"true", "yes", "approval required", "blocked"}


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def _ledger_header() -> str:
    return """# Prompt Ledger

| prompt_id | title | category | status | source | created_at | pasted_to_codex | started_at | completed_at | branch | commit_hash | related_feature_ids | expected_outputs | commands_expected | tests_run | test_result | docs_updated | changelog_updated | feature_registry_updated | feature_maturity_updated | completion_report_updated | blockers | next_prompt_id | supersedes | superseded_by | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
"""


def _queue_header() -> str:
    return """# Prompt Queue

| prompt_id | title | category | status | prerequisite_prompt_ids | approval_gate | expected_outputs | tests_expected | notes |
|---|---|---|---|---|---|---|---|---|
"""
