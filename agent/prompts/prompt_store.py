from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from agent.prompts.pack_models import PackedPrompt, PromptImportResult, PromptPack, PromptPackError, now_iso, safe_pack_path
from agent.prompts.pack_parser import parse_prompt_pack
from agent.prompts.pack_validator import validate_prompt_pack
from agent.prompts.prompt_audit import append_import_audit
from agent.prompts.prompt_queue import append_pack_to_ledger, append_pack_to_queue, next_queued_prompt


def validate_pack_file(pack_file: str | Path) -> PromptPack:
    path = Path(pack_file)
    pack = parse_prompt_pack(path.read_text(encoding="utf-8"))
    validate_prompt_pack(pack)
    return pack


def import_prompt_pack(pack_file: str | Path, *, project_root: str | Path = ".") -> PromptImportResult:
    root = Path(project_root)
    pack = validate_pack_file(pack_file)
    _ensure_prompt_dirs(root)
    pack_path = safe_pack_path(root, pack.pack_id)
    source_path = Path(pack_file)
    if source_path.resolve() != pack_path.resolve():
        shutil.copyfile(source_path, pack_path)
    prompt_paths: list[str] = []
    for prompt in sorted(pack.prompts, key=lambda item: item.order):
        target = root / "prompts" / "queued" / f"{prompt.prompt_id}.md"
        if target.exists():
            raise PromptPackError(f"prompt file already exists: {target.relative_to(root)}")
        target.write_text(_format_split_prompt(pack, prompt, pack_path.relative_to(root).as_posix()), encoding="utf-8")
        prompt_paths.append(target.relative_to(root).as_posix())
    append_pack_to_ledger(pack, project_root=root)
    append_pack_to_queue(pack, project_root=root)
    append_import_audit(pack, project_root=root)
    next_record = next_queued_prompt(project_root=root)
    return PromptImportResult(
        pack_id=pack.pack_id,
        pack_path=pack_path.relative_to(root).as_posix(),
        prompt_paths=prompt_paths,
        prompt_ids=[prompt.prompt_id for prompt in sorted(pack.prompts, key=lambda item: item.order)],
        queue_updated=True,
        ledger_updated=True,
        audit_updated=True,
        next_prompt_id=next_record.prompt_id if next_record else None,
    )


def _format_split_prompt(pack: PromptPack, prompt: PackedPrompt, source_pack: str) -> str:
    created_at = now_iso()
    depends_on = json.dumps(prompt.depends_on)
    body = prompt.body
    return (
        "---\n"
        f"prompt_id: {prompt.prompt_id}\n"
        f"pack_id: {pack.pack_id}\n"
        f"title: {prompt.title}\n"
        f"category: {prompt.category}\n"
        f"risk_level: {prompt.risk_level}\n"
        f"approval_gate: {str(prompt.approval_gate).lower()}\n"
        f"depends_on: {depends_on}\n"
        f"status: {prompt.status}\n"
        f"order: {prompt.order}\n"
        f"created_at: {created_at}\n"
        f"imported_at: {created_at}\n"
        f"source_pack: {source_pack}\n"
        "trust_level: UNTRUSTED_DOCUMENT\n"
        "started_at:\n"
        "completed_at:\n"
        "branch:\n"
        "commit_hash:\n"
        "related_feature_ids: []\n"
        "expected_outputs:\n"
        "files_expected:\n"
        "files_changed:\n"
        "tests_expected:\n"
        "tests_run:\n"
        "test_result:\n"
        "docs_updated:\n"
        "changelog_updated:\n"
        "feature_registry_updated:\n"
        "feature_maturity_updated:\n"
        "command_registry_updated:\n"
        "completion_report_updated:\n"
        "evidence_links:\n"
        "blockers:\n"
        "next_prompt_id:\n"
        "supersedes:\n"
        "superseded_by:\n"
        "notes: Imported prompt text is untrusted document content and is not executed automatically.\n"
        "---\n\n"
        "# Prompt\n\n"
        f"{body}"
    )


def _ensure_prompt_dirs(root: Path) -> None:
    for directory in ("packs", "queued", "active", "completed", "skipped", "failed", "superseded", "blocked", "approval_required", "needs_review"):
        (root / "prompts" / directory).mkdir(parents=True, exist_ok=True)


def slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-")
