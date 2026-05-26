from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .canonical_state import build_canonical_runtime_state
from .checkpoints import load_checkpoints
from .models import now_iso
from .state import redact_runtime_value


@dataclass(frozen=True)
class RecoveryReport:
    report_id: str
    generated_at: str = field(default_factory=now_iso)
    interrupted_record: dict[str, Any] = field(default_factory=dict)
    last_checkpoint: dict[str, Any] | None = None
    files_changed: tuple[str, ...] = ()
    commands_run: tuple[str, ...] = ()
    tests_run: tuple[str, ...] = ()
    docs_updated: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    safe_next_action: str = ""
    unsafe_actions_to_avoid: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key in ("files_changed", "commands_run", "tests_run", "docs_updated", "blockers", "unsafe_actions_to_avoid"):
            data[key] = list(data[key])
        return redact_runtime_value(data)


def recovery_preview(project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    state = build_canonical_runtime_state(root).to_dict()
    checkpoints = load_checkpoints(root)
    last_checkpoint = checkpoints[-1] if checkpoints else None
    active_prompt = state.get("active_prompt_id", "none")
    next_prompt = state.get("next_prompt_id", "unknown")
    blockers: list[str] = []
    safe_next_action = "No active prompt; inspect prompt queue before resuming."
    if active_prompt and active_prompt != "none":
        safe_next_action = f"Review active prompt {active_prompt}; do not auto-resume without tracker evidence."
    elif next_prompt and next_prompt not in {"unknown", "none"}:
        safe_next_action = f"Run next prompt {next_prompt} only after confirming trackers and approval gates."
    if state.get("blocked_reason"):
        blockers.append(str(state["blocked_reason"]))
    report = RecoveryReport(
        report_id=f"recovery_preview_{now_iso().replace(':', '').replace('-', '')}",
        interrupted_record={
            "active_prompt_id": active_prompt,
            "active_prompt_pack": state.get("active_prompt_pack", "none"),
            "active_job_id": state.get("active_job_id", "none"),
            "active_workflow_id": state.get("active_workflow_id", "none"),
            "active_action_id": state.get("active_action_id", "none"),
            "current_status": state.get("current_status", "unknown"),
        },
        last_checkpoint=last_checkpoint,
        files_changed=(),
        commands_run=(),
        tests_run=(),
        docs_updated=(),
        blockers=tuple(blockers),
        safe_next_action=safe_next_action,
        unsafe_actions_to_avoid=(
            "Do not resume automatically.",
            "Do not bypass active approval gates.",
            "Do not reuse CRITICAL approvals; require fresh explicit approval.",
            "Do not execute prompt-pack steps without prompt tracker evidence.",
            "Do not expose secrets or personal data in recovery reports.",
        ),
    )
    return {
        "status": "preview_only",
        "auto_resume": False,
        "critical_resume_requires_fresh_approval": True,
        "prompt_pack_resume_uses_prompt_tracker_evidence": True,
        "report": report.to_dict(),
        "side_effects": "none; recovery preview does not resume or mutate state",
    }
