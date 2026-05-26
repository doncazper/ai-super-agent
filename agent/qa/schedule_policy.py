from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class QASchedulePolicy:
    scheduler_enabled_by_default: bool
    dry_run_default: bool
    daily_tiers: list[int]
    weekly_tiers: list[int]
    manual_tiers: list[int]
    never_automatic_tiers: list[int]
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def default_schedule_policy() -> QASchedulePolicy:
    return QASchedulePolicy(
        scheduler_enabled_by_default=False,
        dry_run_default=True,
        daily_tiers=[0, 1],
        weekly_tiers=[3],
        manual_tiers=[4, 5],
        never_automatic_tiers=[6, 7],
        notes=[
            "No background scheduler is enabled by default.",
            "Daily/weekly commands are dry-run planning commands unless explicitly wired to a reviewed automation later.",
            "HIGH and CRITICAL commands are never automatic.",
        ],
    )

