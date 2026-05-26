from __future__ import annotations

import json
from pathlib import Path

from agent.autonomy.scheduler_ux import dry_run_workflow, list_templates, preview_workflow, workflow_risks
from agent.ui import cli_commands
from agent.ui.command_registry import get_command
from agent.workflows.scheduler import ScheduleStore, create_schedule


def test_schedule_templates_list_safe_templates() -> None:
    report = list_templates()

    workflow_ids = {item["workflow_id"] for item in report["templates"]}
    blocked_ids = {item["workflow_id"] for item in report["blocked_templates"]}
    assert "connector_doctor" in workflow_ids
    assert "backup_create" in workflow_ids
    assert "email.send_approved" in blocked_ids
    assert report["background_persistence"] is False


def test_preview_shows_risk_and_approval_for_safe_workflow() -> None:
    preview = preview_workflow("backup_create")

    assert preview["status"] == "ok"
    assert preview["workflow_id"] == "backup_create"
    assert preview["risk_level"] == "LOW"
    assert preview["approval_required"] is False
    assert preview["background_execution_allowed"] is False
    assert "backup.create" in preview["required_tools"]


def test_dry_run_executes_no_tools(tmp_path: Path) -> None:
    store = ScheduleStore(tmp_path / "schedules.json")
    schedule = create_schedule(workflow="connector_doctor", store=store)["schedule"]

    report = dry_run_workflow(schedule["schedule_id"], store=store)

    assert report["status"] == "dry_run"
    assert report["would_execute_tools"] is False
    assert report["tools_executed"] == []
    assert report["workflow_executed"] is False
    assert report["background_persistence"] is False
    assert schedule["run_count"] == 0
    assert store.get(schedule["schedule_id"]).run_count == 0


def test_high_risk_workflow_is_approval_required() -> None:
    risks = workflow_risks("daily_briefing")

    assert risks["status"] == "ok"
    assert risks["risk_level"] == "HIGH"
    assert risks["approval_required"] is True
    assert "Personal-data" in risks["blocked_reason"]


def test_critical_workflow_never_auto_runs() -> None:
    report = dry_run_workflow("email.send_approved")

    assert report["status"] == "blocked"
    assert report["risk_level"] == "CRITICAL"
    assert report["would_execute_tools"] is False
    assert report["workflow_executed"] is False
    assert report["policy"]["status"] == "blocked"
    assert report["background_execution_allowed"] is False


def test_personal_workflow_disabled_by_default() -> None:
    preview = preview_workflow("daily_briefing")

    assert preview["default_enabled"] is False
    assert preview["approval_required"] is True
    assert "disabled by default" in preview["personal_data_use"]
    assert preview["creates_action_center_item"] is True


def test_schedule_ux_cli_commands(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("SCHEDULE_PATH", str(tmp_path / "schedules.json"))
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))

    assert cli_commands.dispatch_cli(["schedule", "templates"], project_root=tmp_path) == 0
    templates = json.loads(capsys.readouterr().out)
    assert templates["templates"]

    assert cli_commands.dispatch_cli(["schedule", "preview", "connector_doctor"], project_root=tmp_path) == 0
    preview = json.loads(capsys.readouterr().out)
    assert preview["workflow_id"] == "connector_doctor"

    assert cli_commands.dispatch_cli(["schedule", "dry-run", "connector_doctor"], project_root=tmp_path) == 0
    dry_run = json.loads(capsys.readouterr().out)
    assert dry_run["would_execute_tools"] is False

    assert cli_commands.dispatch_cli(["schedule", "risks", "email.send_approved"], project_root=tmp_path) == 0
    risks = json.loads(capsys.readouterr().out)
    assert risks["approval_required"] is True

    assert cli_commands.dispatch_cli(["schedule", "review"], project_root=tmp_path) == 0
    review = json.loads(capsys.readouterr().out)
    assert review["background_persistence"] is False


def test_command_registry_tracks_scheduler_ux_commands() -> None:
    command = get_command("CMD-SCHEDULE-006")

    assert command is not None
    assert command.command == "python smart_agent.py schedule explain"
    assert command.risk_level == "SAFE"
    assert command.example
