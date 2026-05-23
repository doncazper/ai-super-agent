from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent.config.runtime import RuntimeConfig
from agent.safety.audit import AuditLogger
from agent.tools.registry import default_registry
from agent.ui import cli_commands
from agent.workflows.scheduler import (
    ScheduleStore,
    create_schedule,
    delete_schedule,
    list_schedules,
    pause_schedule,
    run_schedule,
)


pytestmark = pytest.mark.unit


def runtime(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        lmstudio_model="test-model",
        audit_log_path=str(tmp_path / "logs" / "audit.jsonl"),
        capabilities_path="config/capabilities.yaml",
    )


def registry(tmp_path: Path):
    return default_registry(project_root=tmp_path, memory_path=tmp_path / "memory.sqlite3")


def audit_events(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_schedule_create_and_list_work(tmp_path: Path) -> None:
    store = ScheduleStore(tmp_path / "schedules.json")
    audit = AuditLogger(tmp_path / "audit.jsonl")

    created = create_schedule(
        workflow="connector_doctor",
        name="Connector check",
        schedule="daily@08:00",
        store=store,
        audit_logger=audit,
    )
    listed = list_schedules(store=store)

    assert created["status"] == "ok"
    assert created["background_persistence"] is False
    assert listed["schedules"][0]["workflow"] == "connector_doctor"
    assert listed["schedules"][0]["schedule"] == "daily@08:00"


def test_schedule_run_executes_safe_workflow_and_audits(tmp_path: Path) -> None:
    store = ScheduleStore(tmp_path / "schedules.json")
    audit_path = tmp_path / "logs" / "audit.jsonl"
    audit = AuditLogger(audit_path)
    schedule = create_schedule(workflow="connector_doctor", store=store, audit_logger=audit)["schedule"]

    result = run_schedule(
        schedule["schedule_id"],
        store=store,
        runtime=runtime(tmp_path),
        registry=registry(tmp_path),
        audit_logger=audit,
    )

    assert result["status"] == "ok"
    assert result["workflow_result"]["workflow"] == "connector_doctor"
    assert result["workflow_result"]["personal_data_accessed"] is False
    assert result["critical_actions_executed"] is False
    events = audit_events(audit_path)
    assert any(event["tool_name"] == "schedule.run.start" for event in events)
    assert any(event["tool_name"] == "schedule.run.finish" for event in events)


def test_scheduled_personal_workflow_requires_approval(tmp_path: Path) -> None:
    store = ScheduleStore(tmp_path / "schedules.json")
    audit = AuditLogger(tmp_path / "logs" / "audit.jsonl")
    schedule = create_schedule(
        workflow="daily_briefing",
        args={"sections": ["calendar"]},
        store=store,
        audit_logger=audit,
    )["schedule"]

    result = run_schedule(
        schedule["schedule_id"],
        store=store,
        runtime=runtime(tmp_path),
        registry=registry(tmp_path),
        audit_logger=audit,
    )

    payload = result["workflow_result"]
    assert result["critical_actions_executed"] is False
    assert payload["personal_sections_requested"] == ["calendar"]
    calendar_section = next(section for section in payload["sections"] if section["name"] == "calendar")
    assert calendar_section["status"] in {"error", "skipped"}
    assert "approval" in json.dumps(calendar_section).lower()


def test_scheduled_critical_action_not_supported_or_executed(tmp_path: Path) -> None:
    store = ScheduleStore(tmp_path / "schedules.json")
    audit = AuditLogger(tmp_path / "logs" / "audit.jsonl")

    with pytest.raises(ValueError):
        create_schedule(workflow="email.send_approved", store=store, audit_logger=audit)

    schedule = create_schedule(
        workflow="daily_briefing",
        args={"sections": ["suggested_actions"]},
        store=store,
        audit_logger=audit,
    )["schedule"]
    result = run_schedule(
        schedule["schedule_id"],
        store=store,
        runtime=runtime(tmp_path),
        registry=registry(tmp_path),
        audit_logger=audit,
    )

    assert result["critical_actions_executed"] is False
    assert result["workflow_result"]["writes_or_sends"] is False


def test_schedule_pause_and_delete_work(tmp_path: Path) -> None:
    store = ScheduleStore(tmp_path / "schedules.json")
    audit = AuditLogger(tmp_path / "audit.jsonl")
    schedule = create_schedule(workflow="audit_summary", store=store, audit_logger=audit)["schedule"]

    paused = pause_schedule(schedule["schedule_id"], store=store, audit_logger=audit)
    run_result = run_schedule(schedule["schedule_id"], store=store, runtime=runtime(tmp_path), registry=registry(tmp_path), audit_logger=audit)
    deleted = delete_schedule(schedule["schedule_id"], store=store, audit_logger=audit)

    assert paused["schedule"]["status"] == "paused"
    assert run_result["status"] == "error"
    assert run_result["error"] == "schedule is paused"
    assert deleted["status"] == "ok"
    assert list_schedules(store=store)["schedules"] == []


def test_scheduler_creates_no_hidden_persistence(tmp_path: Path) -> None:
    store = ScheduleStore(tmp_path / "data" / "schedules.json")
    created = create_schedule(workflow="memory_cleanup", store=store)

    assert created["background_persistence"] is False
    assert store.path.exists()
    assert not (tmp_path / "Library" / "LaunchAgents").exists()
    assert not (tmp_path / "cron").exists()


def test_schedule_backup_create_runs_through_broker_and_audits(tmp_path: Path) -> None:
    store = ScheduleStore(tmp_path / "schedules.json")
    audit_path = tmp_path / "logs" / "audit.jsonl"
    audit = AuditLogger(audit_path)
    schedule = create_schedule(
        workflow="backup_create",
        args={"backup_dir": str(tmp_path / "workspace" / "scheduled_backups")},
        store=store,
        audit_logger=audit,
    )["schedule"]

    result = run_schedule(
        schedule["schedule_id"],
        store=store,
        runtime=runtime(tmp_path),
        registry=registry(tmp_path),
        audit_logger=audit,
    )

    assert result["status"] == "ok"
    payload = result["workflow_result"]
    assert payload["workflow"] == "backup_create"
    assert payload["toolbroker_used"] is True
    assert payload["personal_connectors_read"] is False
    assert payload["memory_written"] is False
    assert payload["critical_actions_executed"] is False
    assert payload["backup"]["status"] == "ok"
    assert payload["backup"]["redacted"] is True
    events = audit_events(audit_path)
    assert any(event["tool_name"] == "backup.create" for event in events)
    assert any(event["tool_name"] == "schedule.run.finish" for event in events)


def test_schedule_backup_create_rejects_unredacted_arg(tmp_path: Path) -> None:
    store = ScheduleStore(tmp_path / "schedules.json")
    audit = AuditLogger(tmp_path / "logs" / "audit.jsonl")
    schedule = create_schedule(
        workflow="backup_create",
        args={"redacted": False},
        store=store,
        audit_logger=audit,
    )["schedule"]

    result = run_schedule(
        schedule["schedule_id"],
        store=store,
        runtime=runtime(tmp_path),
        registry=registry(tmp_path),
        audit_logger=audit,
    )

    assert result["status"] == "error"
    assert "redacted backups only" in result["workflow_result"]["error"]
    assert result["critical_actions_executed"] is False


def test_schedule_cli_uses_local_store_and_lists(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("SCHEDULE_PATH", str(tmp_path / "schedules.json"))
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))

    assert cli_commands.dispatch_cli(["schedule", "create", "--workflow", "connector_doctor", "--name", "Doctor"], project_root=tmp_path) == 0
    created = json.loads(capsys.readouterr().out)
    assert created["schedule"]["workflow"] == "connector_doctor"

    assert cli_commands.dispatch_cli(["schedule", "list"], project_root=tmp_path) == 0
    listed = json.loads(capsys.readouterr().out)
    assert listed["schedules"][0]["schedule_id"] == created["schedule"]["schedule_id"]
