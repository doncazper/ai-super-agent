from __future__ import annotations

from pathlib import Path

from agent.prompts.pack_models import PromptPack, now_iso


AUDIT_PATH = Path("docs/PROMPT_AUDIT.md")


def append_import_audit(pack: PromptPack, *, project_root: str | Path = ".") -> None:
    path = Path(project_root) / AUDIT_PATH
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Prompt Audit\n\n", encoding="utf-8")
    existing = path.read_text(encoding="utf-8")
    prompt_ids = ", ".join(prompt.prompt_id for prompt in sorted(pack.prompts, key=lambda item: item.order))
    entry = (
        "\n## Prompt Pack Import\n\n"
        f"- imported_at: {now_iso()}\n"
        f"- pack_id: {pack.pack_id}\n"
        f"- pack_title: {pack.pack_title}\n"
        f"- mode: {pack.mode}\n"
        f"- prompt_count: {len(pack.prompts)}\n"
        f"- prompt_ids: {prompt_ids}\n"
        "- execution: import_only; no prompt executed automatically.\n"
    )
    path.write_text(existing.rstrip() + entry + "\n", encoding="utf-8")
