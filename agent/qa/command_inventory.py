from __future__ import annotations

import ast
from pathlib import Path

from agent.qa.models import CommandInventoryItem
from agent.ui.command_registry import COMMANDS, CommandRecord


def inventory_item_from_record(record: CommandRecord) -> CommandInventoryItem:
    return CommandInventoryItem(
        command_id=record.command_id,
        command=record.command,
        group=record.group,
        description=record.description,
        example=record.example,
        status=record.status,
        risk_level=record.risk_level,
        trust_level=record.trust_level,
        requires_approval=record.requires_approval,
        requires_connector=record.requires_connector,
        requires_provider=record.requires_provider,
        side_effects=record.side_effects,
        toolbroker_path=record.toolbroker_path,
        audit_behavior=record.audit_behavior,
        memory_behavior=record.memory_behavior,
        test_coverage=record.test_coverage,
        manual_qa_status=record.manual_qa_status,
        docs_link=record.docs_link,
    )


def load_command_inventory() -> list[CommandInventoryItem]:
    return [inventory_item_from_record(record) for record in COMMANDS]


def discover_top_level_cli_commands(project_root: str | Path = ".") -> set[str]:
    """Best-effort static discovery from dispatch_cli without importing extras."""

    path = Path(project_root) / "agent/ui/cli_commands.py"
    if not path.exists():
        return set()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    commands: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            left = node.left
            if not (isinstance(left, ast.Name) and left.id == "command"):
                continue
            for comparator in node.comparators:
                if isinstance(comparator, ast.Constant) and isinstance(comparator.value, str):
                    commands.add(comparator.value)
    return commands
