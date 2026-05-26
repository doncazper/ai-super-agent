from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from agent.qa.command_inventory import discover_top_level_cli_commands, load_command_inventory
from agent.qa.models import QAPlan, QAPlanCommand, utc_now_iso
from agent.qa.safety import classify_qa_tier, missing_metadata, requires_provider_setup


def _plan_id(commands: list[QAPlanCommand]) -> str:
    seed = "|".join(f"{command.command_id}:{command.qa_tier}:{command.safe_to_auto_run}" for command in commands)
    return "qa_plan_" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]


def generate_qa_plan(
    *,
    project_root: str | Path = ".",
    tier: int | None = None,
    group: str | None = None,
    safe_only: bool = False,
    include_non_active: bool = False,
) -> QAPlan:
    inventory = load_command_inventory()
    discovered = discover_top_level_cli_commands(project_root)
    commands: list[QAPlanCommand] = []
    risks: list[str] = []
    setup_required: list[dict[str, Any]] = []

    for item in inventory:
        if group and group.lower() not in item.group.lower() and group.lower() not in item.command.lower():
            continue
        qa_tier, safe_auto, skip_reason = classify_qa_tier(item)
        metadata_gaps = missing_metadata(item)
        if item.status != "active" and not include_non_active:
            safe_auto = False
            skip_reason = skip_reason or f"status_{item.status}"
        if tier is not None and qa_tier != tier:
            continue
        if safe_only and not safe_auto:
            continue
        if metadata_gaps:
            risks.append(f"{item.command_id} missing metadata: {', '.join(metadata_gaps)}")
        provider_setup = requires_provider_setup(item)
        if provider_setup:
            setup_required.append(
                {
                    "command_id": item.command_id,
                    "command": item.command,
                    "requires_connector": item.requires_connector,
                    "requires_provider": item.requires_provider,
                }
            )
        commands.append(
            QAPlanCommand(
                command_id=item.command_id,
                command=item.command,
                group=item.group,
                qa_tier=qa_tier,
                risk_level=item.risk_level,
                status=item.status,
                safe_to_auto_run=safe_auto,
                skip_reason=skip_reason,
                requires_approval=item.requires_approval.lower() not in {"no", "none", "n/a", ""},
                requires_provider_setup=provider_setup,
                requires_disposable_workspace=qa_tier == 3,
                missing_metadata=metadata_gaps,
                docs_link=item.docs_link,
                example=item.example,
            )
        )

    commands.sort(key=lambda command: (command.qa_tier, not command.safe_to_auto_run, command.group, command.command_id))
    safe_count = sum(1 for command in commands if command.safe_to_auto_run)
    skipped_count = sum(1 for command in commands if command.skip_reason)
    blocked_count = sum(1 for command in commands if command.qa_tier in {6, 7} or command.skip_reason)
    by_tier = Counter(str(command.qa_tier) for command in commands)
    by_group = Counter(command.group for command in commands)
    notes = [
        "Plan generation does not execute commands.",
        "HIGH and CRITICAL commands are manual only.",
        "Planned/stubbed/deprecated commands are skipped unless include_non_active is used.",
    ]
    if discovered:
        notes.append(f"Static CLI discovery found {len(discovered)} top-level command groups.")
    return QAPlan(
        plan_id=_plan_id(commands),
        generated_at=utc_now_iso(),
        command_count=len(commands),
        safe_count=safe_count,
        skipped_count=skipped_count,
        blocked_count=blocked_count,
        commands_by_tier=dict(sorted(by_tier.items())),
        commands_by_group=dict(sorted(by_group.items())),
        recommended_first_batch=[command.to_dict() for command in commands if command.safe_to_auto_run and command.qa_tier in {0, 1}][:25],
        setup_required=setup_required[:50],
        risks=risks[:50],
        notes=notes,
        commands=commands,
    )


def format_qa_plan(plan: QAPlan) -> str:
    return json.dumps(plan.to_dict(), indent=2, sort_keys=True)
