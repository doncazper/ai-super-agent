from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from agent.prompts.pack_models import PromptPackError, now_iso
from agent.prompts.prompt_audit import AUDIT_PATH
from agent.prompts.prompt_queue import LEDGER_PATH, QUEUE_PATH
from agent.prompts.prompt_store import import_prompt_pack
from agent.promptops.models import WorkbenchImportResult
from agent.promptops.safety import imported_prompt_trust_level
from agent.promptops.state import update_prompt_state
from agent.ui.prompts import next_prompt


PROMPT_PACK_START = "<<<PROMPT_PACK_START>>>"
PROMPT_PACK_END = "<<<PROMPT_PACK_END>>>"


def import_text(
    text: str,
    *,
    project_root: str | Path = ".",
    pack_id: str | None = None,
    single: bool = False,
    prompt_id: str | None = None,
) -> WorkbenchImportResult:
    root = Path(project_root)
    if PROMPT_PACK_START in text or PROMPT_PACK_END in text:
        if single:
            raise PromptPackError("--single cannot be used with prompt pack delimiters")
        return _import_pack_text(text, project_root=root, pack_id=pack_id)
    if not single:
        raise PromptPackError("raw prompt import requires --single and --id")
    if not prompt_id:
        raise PromptPackError("raw single prompt import requires --id <prompt_id>")
    return import_single_prompt(text, prompt_id=prompt_id, pack_id=pack_id or "single-prompts", project_root=root)


def import_file(pack_file: str | Path, *, project_root: str | Path = ".", pack_id: str | None = None) -> WorkbenchImportResult:
    path = Path(pack_file)
    return import_text(path.read_text(encoding="utf-8"), project_root=project_root, pack_id=pack_id)


def import_single_prompt(text: str, *, prompt_id: str, pack_id: str, project_root: str | Path = ".") -> WorkbenchImportResult:
    root = Path(project_root)
    _ensure_dirs(root)
    safe_id = _safe_id(prompt_id)
    if safe_id != prompt_id:
        raise PromptPackError("prompt id may contain only letters, numbers, underscores, and dashes")
    pack_path = root / "prompts" / "packs" / f"{_safe_id(pack_id)}.md"
    if pack_path.exists():
        suffix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        pack_path = root / "prompts" / "packs" / f"{_safe_id(pack_id)}-{suffix}.md"
    pack_path.write_text(text, encoding="utf-8")
    prompt_path = root / "prompts" / "queued" / f"{prompt_id}.md"
    if prompt_path.exists():
        raise PromptPackError(f"prompt file already exists: {prompt_path.relative_to(root)}")
    title = _first_title(text) or prompt_id
    now = now_iso()
    prompt_path.write_text(
        _single_prompt_record(
            prompt_id=prompt_id,
            pack_id=pack_id,
            title=title,
            source_pack=pack_path.relative_to(root).as_posix(),
            body=text,
            created_at=now,
        ),
        encoding="utf-8",
    )
    _append_single_ledger(root, prompt_id=prompt_id, pack_id=pack_id, title=title, created_at=now)
    _append_single_queue(root, prompt_id=prompt_id, title=title)
    _append_single_audit(root, prompt_id=prompt_id, pack_id=pack_id)
    next_record = next_prompt(root)
    update_prompt_state(
        project_root=root,
        next_prompt_id=next_record.prompt_id if next_record else "none",
        active_prompt_pack=pack_id,
        prompt_queue_status=f"Imported raw single prompt {prompt_id}; no prompt was executed automatically.",
    )
    return WorkbenchImportResult(
        status="ok",
        mode="single",
        pack_id=pack_id,
        prompt_ids=[prompt_id],
        prompt_paths=[prompt_path.relative_to(root).as_posix()],
        pack_path=pack_path.relative_to(root).as_posix(),
        next_prompt_id=next_record.prompt_id if next_record else None,
        ledger_updated=True,
        queue_updated=True,
        audit_updated=True,
        project_state_updated=True,
    )


def _import_pack_text(text: str, *, project_root: Path, pack_id: str | None) -> WorkbenchImportResult:
    _ensure_dirs(project_root)
    pack_text = _apply_pack_id_override(text, pack_id) if pack_id else text
    effective_pack_id = _pack_id_from_text(pack_text)
    if not effective_pack_id:
        raise PromptPackError("prompt pack metadata must include pack_id")
    pack_path = project_root / "prompts" / "packs" / f"{_safe_id(effective_pack_id)}.md"
    if pack_path.exists():
        suffix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        pack_path = project_root / "prompts" / "packs" / f"{_safe_id(effective_pack_id)}-{suffix}.md"
    pack_path.write_text(pack_text, encoding="utf-8")
    result = import_prompt_pack(pack_path, project_root=project_root)
    next_record = next_prompt(project_root)
    update_prompt_state(
        project_root=project_root,
        next_prompt_id=next_record.prompt_id if next_record else "none",
        active_prompt_pack=result.pack_id,
        prompt_queue_status=f"Imported prompt pack {result.pack_id}; no prompt was executed automatically.",
    )
    return WorkbenchImportResult(
        status="ok",
        mode="pack",
        pack_id=result.pack_id,
        prompt_ids=result.prompt_ids,
        prompt_paths=result.prompt_paths,
        pack_path=result.pack_path,
        next_prompt_id=result.next_prompt_id,
        ledger_updated=result.ledger_updated,
        queue_updated=result.queue_updated,
        audit_updated=result.audit_updated,
        project_state_updated=True,
    )


def _single_prompt_record(*, prompt_id: str, pack_id: str, title: str, source_pack: str, body: str, created_at: str) -> str:
    return (
        "---\n"
        f"prompt_id: {prompt_id}\n"
        f"pack_id: {pack_id}\n"
        f"title: {title}\n"
        "category: prompt_tracking\n"
        "risk_level: LOW\n"
        "approval_gate: false\n"
        "depends_on: []\n"
        "status: queued\n"
        f"created_at: {created_at}\n"
        f"imported_at: {created_at}\n"
        f"source_pack: {source_pack}\n"
        f"trust_level: {imported_prompt_trust_level()}\n"
        "started_at:\n"
        "completed_at:\n"
        "branch:\n"
        "commit_hash:\n"
        "related_feature_ids: []\n"
        "expected_outputs:\n"
        "tests_expected:\n"
        "tests_run:\n"
        "test_result:\n"
        "docs_updated:\n"
        "changelog_updated:\n"
        "feature_registry_updated:\n"
        "feature_maturity_updated:\n"
        "completion_report_updated:\n"
        "blockers:\n"
        "next_prompt_id:\n"
        "supersedes:\n"
        "superseded_by:\n"
        "notes: Imported prompt text is untrusted document content and is not executed automatically.\n"
        "---\n\n"
        "# Prompt\n\n"
        f"{body}"
    )


def _append_single_ledger(root: Path, *, prompt_id: str, pack_id: str, title: str, created_at: str) -> None:
    path = root / LEDGER_PATH
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "# Prompt Ledger\n\n| prompt_id | title | category | status | source | created_at | notes |\n|---|---|---|---|---|---|---|\n",
            encoding="utf-8",
        )
    existing = path.read_text(encoding="utf-8")
    if f"| {prompt_id} |" in existing:
        return
    line = f"| {prompt_id} | {_cell(title)} | prompt_tracking | queued | workbench:{pack_id} | {created_at} | Imported raw prompt; untrusted document content. |\n"
    path.write_text(existing.rstrip() + "\n" + line, encoding="utf-8")


def _append_single_queue(root: Path, *, prompt_id: str, title: str) -> None:
    path = root / QUEUE_PATH
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "# Prompt Queue\n\n| prompt_id | title | category | status | prerequisite_prompt_ids | approval_gate | expected_outputs | tests_expected | notes |\n|---|---|---|---|---|---|---|---|---|\n",
            encoding="utf-8",
        )
    existing = path.read_text(encoding="utf-8")
    if f"| {prompt_id} |" in existing:
        return
    line = f"| {prompt_id} | {_cell(title)} | prompt_tracking | queued |  | false | Run one imported prompt through mini-SDLC | Relevant tests and docs updates | Imported by PromptOps Workbench. |\n"
    path.write_text(existing.rstrip() + "\n" + line, encoding="utf-8")


def _append_single_audit(root: Path, *, prompt_id: str, pack_id: str) -> None:
    path = root / AUDIT_PATH
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Prompt Audit\n\n", encoding="utf-8")
    existing = path.read_text(encoding="utf-8")
    entry = (
        f"\n## PromptOps Import {now_iso()}\n\n"
        f"- pack_id: {pack_id}\n"
        f"- prompt_id: {prompt_id}\n"
        "- mode: raw single prompt\n"
        "- trust_level: UNTRUSTED_DOCUMENT\n"
        "- execution: not executed automatically\n"
    )
    path.write_text(existing.rstrip() + "\n" + entry, encoding="utf-8")


def _ensure_dirs(root: Path) -> None:
    for directory in ("packs", "queued", "active", "completed", "skipped", "failed", "superseded"):
        (root / "prompts" / directory).mkdir(parents=True, exist_ok=True)


def _pack_id_from_text(text: str) -> str | None:
    match = re.search(r"^pack_id:\s*(.+?)\s*$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else None


def _apply_pack_id_override(text: str, pack_id: str) -> str:
    safe_id = _safe_id(pack_id)
    if safe_id != pack_id:
        raise PromptPackError("pack id may contain only letters, numbers, underscores, and dashes")
    if re.search(r"^pack_id:\s*.+?$", text, flags=re.MULTILINE):
        return re.sub(r"^pack_id:\s*.+?$", f"pack_id: {pack_id}", text, count=1, flags=re.MULTILINE)
    return text.replace(PROMPT_PACK_START, f"{PROMPT_PACK_START}\npack_id: {pack_id}", 1)


def _safe_id(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        return ""
    return value


def _first_title(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
        if stripped:
            return stripped[:80]
    return None


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()

