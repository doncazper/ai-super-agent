from __future__ import annotations

from pathlib import Path


PROJECT_STATE_PATH = Path("docs/PROJECT_STATE.md")


def update_prompt_state(
    *,
    project_root: str | Path = ".",
    active_prompt_id: str | None = None,
    next_prompt_id: str | None = None,
    active_prompt_pack: str | None = None,
    prompt_queue_status: str | None = None,
) -> None:
    root = Path(project_root)
    path = root / PROJECT_STATE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("# Project State\n\n## Prompt Tracking\n\n", encoding="utf-8")
    content = path.read_text(encoding="utf-8")
    if "## Prompt Tracking" not in content:
        content = content.rstrip() + "\n\n## Prompt Tracking\n\n"
    replacements = {
        "active_prompt_id": active_prompt_id,
        "next_prompt_id": next_prompt_id,
        "active_prompt_pack": active_prompt_pack,
        "prompt_queue_status": prompt_queue_status,
    }
    for key, value in replacements.items():
        if value is None:
            continue
        content = _replace_bullet(content, key, value)
    path.write_text(content, encoding="utf-8")


def _replace_bullet(content: str, key: str, value: str) -> str:
    prefix = f"- {key}:"
    lines = content.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines[index] = f"{prefix} {value}"
            return "\n".join(lines) + "\n"
    prompt_tracking = "## Prompt Tracking"
    insertion = f"{prefix} {value}"
    marker_index = content.find(prompt_tracking)
    if marker_index == -1:
        return content.rstrip() + f"\n\n## Prompt Tracking\n\n{insertion}\n"
    after = content.find("\n", marker_index)
    if after == -1:
        return content.rstrip() + f"\n\n{insertion}\n"
    return content[: after + 1] + insertion + "\n" + content[after + 1 :]

