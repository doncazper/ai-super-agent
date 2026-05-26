from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent.qa.models import utc_now_iso
from agent.qa.qa_plan import generate_qa_plan
from agent.qa.schedule_policy import default_schedule_policy


def _write_progress_report(project_root: str | Path, name: str, payload: dict[str, Any]) -> dict[str, Any]:
    reports = Path(project_root) / "reports/qa"
    reports.mkdir(parents=True, exist_ok=True)
    path = reports / f"{name}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload = dict(payload)
    payload["report_path"] = path.relative_to(Path(project_root)).as_posix()
    return payload


def next_batch(project_root: str | Path = ".", *, limit: int = 10) -> dict[str, Any]:
    plan = generate_qa_plan(project_root=project_root, tier=1, safe_only=True)
    commands = plan.commands[:limit]
    return {
        "status": "ok",
        "generated_at": utc_now_iso(),
        "dry_run": True,
        "selection_basis": "Tier 1 safe active commands from command registry order; historical run age is not tracked yet.",
        "commands": [command.to_dict() for command in commands],
    }


def daily_dry_run(project_root: str | Path = ".", *, limit: int = 25) -> dict[str, Any]:
    policy = default_schedule_policy()
    commands = []
    for tier in policy.daily_tiers:
        commands.extend(generate_qa_plan(project_root=project_root, tier=tier, safe_only=True).commands)
    payload = {
        "status": "ok",
        "generated_at": utc_now_iso(),
        "cadence": "daily",
        "dry_run": True,
        "tiers": policy.daily_tiers,
        "commands": [command.to_dict() for command in commands[:limit]],
        "excluded": "Tier 2+ provider/sandbox/personal/high-risk commands are excluded from daily dry-run.",
    }
    return _write_progress_report(project_root, "daily_dry_run", payload)


def weekly_dry_run(project_root: str | Path = ".", *, limit: int = 25) -> dict[str, Any]:
    policy = default_schedule_policy()
    plan = generate_qa_plan(project_root=project_root, tier=3, safe_only=False)
    commands = [
        command
        for command in plan.commands
        if command.requires_disposable_workspace and command.qa_tier == 3 and "personal" not in command.skip_reason.lower()
    ][:limit]
    payload = {
        "status": "ok",
        "generated_at": utc_now_iso(),
        "cadence": "weekly",
        "dry_run": True,
        "tiers": policy.weekly_tiers,
        "requires_sandbox": True,
        "commands": [command.to_dict() for command in commands],
        "todo": "Review this plan before wiring any scheduled automation. No scheduler is enabled by default.",
    }
    return _write_progress_report(project_root, "weekly_dry_run", payload)


def depth_status(project_root: str | Path = ".") -> dict[str, Any]:
    policy = default_schedule_policy()
    return {
        "status": "ok",
        "generated_at": utc_now_iso(),
        "policy": policy.to_dict(),
        "scheduler_enabled": False,
        "action_center_item_created": False,
        "todo": "Create a reviewed Action Center item only after manual approval of the schedule.",
    }

