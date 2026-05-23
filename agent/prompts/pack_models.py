from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RISK_LEVELS = {"SAFE", "LOW", "MEDIUM", "HIGH", "CRITICAL", "FORBIDDEN"}
IMPORT_STATUSES = {"queued", "blocked", "skipped", "superseded"}


@dataclass(frozen=True)
class PackedPrompt:
    prompt_id: str
    order: int
    title: str
    category: str
    risk_level: str
    approval_gate: bool
    depends_on: list[str]
    status: str
    body: str
    metadata: dict[str, str]


@dataclass(frozen=True)
class PromptPack:
    pack_id: str
    pack_title: str
    mode: str
    default_execution: str
    requires_sdlc: bool
    requires_prompt_ledger: bool
    requires_feature_maturity_update: bool
    prompts: list[PackedPrompt]
    metadata: dict[str, str]
    raw_text: str


@dataclass(frozen=True)
class PromptImportResult:
    pack_id: str
    pack_path: str
    prompt_paths: list[str]
    prompt_ids: list[str]
    queue_updated: bool
    ledger_updated: bool
    audit_updated: bool
    next_prompt_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "pack_id": self.pack_id,
            "pack_path": self.pack_path,
            "prompt_paths": self.prompt_paths,
            "prompt_ids": self.prompt_ids,
            "queue_updated": self.queue_updated,
            "ledger_updated": self.ledger_updated,
            "audit_updated": self.audit_updated,
            "next_prompt_id": self.next_prompt_id,
        }


class PromptPackError(ValueError):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def safe_pack_path(project_root: str | Path, pack_id: str) -> Path:
    return Path(project_root) / "prompts" / "packs" / f"{pack_id}.md"
