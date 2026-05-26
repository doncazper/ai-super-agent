from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .models import now_iso
from .state import redact_runtime_value


@dataclass(frozen=True)
class RuntimeCheckpoint:
    checkpoint_id: str
    record_id: str
    created_at: str = field(default_factory=now_iso)
    kind: str = "prompt_pack"
    state_hash: str = ""
    input_hash: str = ""
    output_hash: str = ""
    artifact_hashes: dict[str, str] = field(default_factory=dict)
    current_step: str = ""
    completed_steps: tuple[str, ...] = ()
    remaining_steps: tuple[str, ...] = ()
    approval_state: str = "none"
    audit_ids: tuple[str, ...] = ()
    resume_command: str = ""
    rollback_plan: str = ""
    safe_to_resume: bool = False
    human_review_required: bool = True
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.checkpoint_id:
            raise ValueError("checkpoint_id is required")
        if not self.record_id:
            raise ValueError("record_id is required")
        if self.approval_state == "critical_action_pending" and self.safe_to_resume:
            raise ValueError("CRITICAL action checkpoints cannot be safe_to_resume without fresh approval")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["completed_steps"] = list(self.completed_steps)
        data["remaining_steps"] = list(self.remaining_steps)
        data["audit_ids"] = list(self.audit_ids)
        return redact_runtime_value(data)


def load_checkpoints(project_root: str | Path = ".") -> list[dict[str, Any]]:
    checkpoints_dir = Path(project_root) / "reports" / "runtime" / "checkpoints"
    if not checkpoints_dir.exists():
        return []
    checkpoints: list[dict[str, Any]] = []
    for path in sorted(checkpoints_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {"checkpoint_id": path.stem, "record_id": "unknown", "load_error": True}
        if isinstance(payload, dict):
            payload["source_path"] = str(path)
            checkpoints.append(redact_runtime_value(payload))
    return checkpoints


def list_checkpoints(project_root: str | Path = ".") -> dict[str, Any]:
    checkpoints = load_checkpoints(project_root)
    return {
        "status": "ok",
        "checkpoint_count": len(checkpoints),
        "checkpoints": checkpoints,
        "storage_path": "reports/runtime/checkpoints",
        "side_effects": "none; read-only checkpoint listing",
    }


def show_checkpoint(checkpoint_id: str, project_root: str | Path = ".") -> dict[str, Any]:
    for checkpoint in load_checkpoints(project_root):
        if checkpoint.get("checkpoint_id") == checkpoint_id:
            return {"status": "ok", "checkpoint": checkpoint, "side_effects": "none; read-only checkpoint lookup"}
    return {"status": "not_found", "checkpoint_id": checkpoint_id, "side_effects": "none; read-only checkpoint lookup"}
