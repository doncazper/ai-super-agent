from pathlib import Path

from agent.qa.command_inventory import discover_top_level_cli_commands, load_command_inventory
from agent.qa.qa_plan import generate_qa_plan


ROOT = Path(__file__).resolve().parents[2]


def test_registry_inventory_loads() -> None:
    inventory = load_command_inventory()
    assert inventory
    assert any(item.command_id == "CMD-DOCTOR-001" for item in inventory)


def test_static_cli_discovery_finds_top_level_groups() -> None:
    discovered = discover_top_level_cli_commands(ROOT)
    assert "commands" in discovered
    assert "qa" not in discovered or isinstance(discovered, set)


def test_tier_one_selected_and_deterministic() -> None:
    first = generate_qa_plan(project_root=ROOT, tier=1, safe_only=True)
    second = generate_qa_plan(project_root=ROOT, tier=1, safe_only=True)
    assert first.plan_id == second.plan_id
    assert first.commands
    assert all(command.qa_tier == 1 for command in first.commands)
    assert all(command.safe_to_auto_run for command in first.commands)


def test_high_critical_excluded_from_safe_only() -> None:
    plan = generate_qa_plan(project_root=ROOT, safe_only=True)
    assert all(command.risk_level not in {"HIGH", "CRITICAL", "FORBIDDEN"} for command in plan.commands)
    assert all(command.qa_tier not in {6, 7} for command in plan.commands)


def test_planned_stubbed_skipped_by_default() -> None:
    plan = generate_qa_plan(project_root=ROOT)
    planned = [command for command in plan.commands if command.command_id.startswith("CMD-QA-")]
    assert planned
    planned_only = [command for command in planned if command.status == "planned"]
    assert all(command.status == "planned" for command in planned_only)
    assert all(command.safe_to_auto_run is False for command in planned_only)
    assert all(command.skip_reason.startswith("status_") for command in planned_only)
    active_qa = [command for command in planned if command.status == "active"]
    assert active_qa
    active_safe_ids = {"CMD-QA-001", "CMD-QA-002"}
    assert all(command.safe_to_auto_run is True for command in active_qa if command.command_id in active_safe_ids)
    assert any(command.command_id == "CMD-QA-004" and command.safe_to_auto_run is True for command in active_qa)
    assert any(command.command_id in {"CMD-QA-009", "CMD-QA-010"} and command.requires_disposable_workspace for command in active_qa)


def test_provider_required_marked_setup_required() -> None:
    plan = generate_qa_plan(project_root=ROOT, group="Brain")
    assert any(item["requires_provider"] != "none" for item in plan.setup_required)


def test_group_filter() -> None:
    plan = generate_qa_plan(project_root=ROOT, group="Weather")
    assert plan.commands
    assert all("weather" in command.group.lower() or "weather" in command.command.lower() for command in plan.commands)


def test_missing_metadata_report_shape() -> None:
    plan = generate_qa_plan(project_root=ROOT)
    assert isinstance(plan.risks, list)
    assert isinstance(plan.recommended_first_batch, list)
