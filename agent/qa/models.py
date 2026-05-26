from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class CommandInventoryItem:
    command_id: str
    command: str
    group: str
    description: str
    example: str
    status: str
    risk_level: str
    trust_level: str
    requires_approval: str
    requires_connector: str
    requires_provider: str
    side_effects: str
    toolbroker_path: str
    audit_behavior: str
    memory_behavior: str
    test_coverage: str
    manual_qa_status: str
    docs_link: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class QAPlanCommand:
    command_id: str
    command: str
    group: str
    qa_tier: int
    risk_level: str
    status: str
    safe_to_auto_run: bool
    skip_reason: str
    requires_approval: bool
    requires_provider_setup: bool
    requires_disposable_workspace: bool
    missing_metadata: list[str] = field(default_factory=list)
    docs_link: str = ""
    example: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class QAPlan:
    plan_id: str
    generated_at: str
    command_count: int
    safe_count: int
    skipped_count: int
    blocked_count: int
    commands_by_tier: dict[str, int]
    commands_by_group: dict[str, int]
    recommended_first_batch: list[dict[str, Any]]
    setup_required: list[dict[str, Any]]
    risks: list[str]
    notes: list[str]
    commands: list[QAPlanCommand]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["commands"] = [command.to_dict() for command in self.commands]
        return payload
