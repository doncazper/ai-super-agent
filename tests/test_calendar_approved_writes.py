from __future__ import annotations

import base64
import json

from agent.config.loader import load_capabilities_config
from agent.core.tool_broker import ToolBroker
from agent.safety.actions import ActionCenter, ActionCenterStore, ActionStatus
from agent.safety.approvals import ApprovalStore
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry
from agent.workflows.calendar_writes import (
    CALENDAR_CREATE_ACTION,
    CALENDAR_DELETE_ACTION,
    CALENDAR_UPDATE_ACTION,
    draft_calendar_create,
    draft_calendar_delete,
    draft_calendar_update,
    execute_calendar_action,
)


def _center(tmp_path) -> ActionCenter:
    return ActionCenter(
        store=ActionCenterStore(tmp_path / "actions.json"),
        approval_store=ApprovalStore(tmp_path / "approvals.json"),
        audit_logger=AuditLogger(tmp_path / "audit.jsonl"),
        session_id="test-session",
        model="test-model",
    )


def _broker(tmp_path, *, enabled: bool = True) -> ToolBroker:
    capabilities = {
        name: Capability(
            name,
            RiskLevel.CRITICAL,
            default_enabled=enabled,
            approval_required="per_action",
            approval_reuse_allowed=False,
        )
        for name in (CALENDAR_CREATE_ACTION, CALENDAR_UPDATE_ACTION, CALENDAR_DELETE_ACTION)
    }
    return ToolBroker(
        default_registry(project_root=tmp_path),
        PolicyEngine(capabilities),
        AuditLogger(tmp_path / "broker-audit.jsonl"),
        session_id="broker-session",
        model="test-model",
        route="test",
    )


def _event_token() -> str:
    payload = {
        "title": "Planning",
        "start": "2026-05-22T10:00:00",
        "end": "2026-05-22T10:30:00",
        "calendar_name": "Work",
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "calevt_" + base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def test_calendar_create_draft_produces_pending_action_not_event(tmp_path) -> None:
    action = draft_calendar_create(
        _center(tmp_path),
        title="Planning",
        start="2026-05-22T10:00:00",
        end="2026-05-22T10:30:00",
        calendar_name="Work",
        attendees=["a@example.com"],
        location="Room 1",
    )

    assert action.status is ActionStatus.PENDING
    assert action.action_type == CALENDAR_CREATE_ACTION
    assert action.preview["title"] == "Calendar event"
    assert action.sanitized_args["send_invites"] is False
    assert "event_id" not in action.sanitized_args


def test_calendar_create_requires_approval(tmp_path) -> None:
    center = _center(tmp_path)
    action = draft_calendar_create(center, title="Planning", start="2026-05-22T10:00", end="2026-05-22T10:30")

    report = execute_calendar_action(_broker(tmp_path), center, action_id=action.action_id, expected_action_type=CALENDAR_CREATE_ACTION)

    assert report["status"] == "error"
    assert report["executed"] is False
    assert "approved" in report["error"]


def test_calendar_update_requires_approval(tmp_path) -> None:
    center = _center(tmp_path)
    action = draft_calendar_update(center, event_id=_event_token(), changes={"title": "New title"})

    report = execute_calendar_action(_broker(tmp_path), center, action_id=action.action_id, expected_action_type=CALENDAR_UPDATE_ACTION)

    assert report["status"] == "error"
    assert report["executed"] is False


def test_calendar_delete_requires_approval(tmp_path) -> None:
    center = _center(tmp_path)
    action = draft_calendar_delete(center, event_id=_event_token())

    report = execute_calendar_action(_broker(tmp_path), center, action_id=action.action_id, expected_action_type=CALENDAR_DELETE_ACTION)

    assert report["status"] == "error"
    assert report["executed"] is False


def test_denial_prevents_calendar_write(tmp_path) -> None:
    center = _center(tmp_path)
    action = draft_calendar_create(center, title="Planning", start="2026-05-22T10:00", end="2026-05-22T10:30")
    center.deny(action.action_id)

    report = execute_calendar_action(_broker(tmp_path), center, action_id=action.action_id, expected_action_type=CALENDAR_CREATE_ACTION)

    assert report["status"] == "error"
    assert report["executed"] is False
    assert report["action_status"] == "denied"


def test_approved_calendar_create_executes_once(tmp_path) -> None:
    center = _center(tmp_path)
    action = draft_calendar_create(center, title="Planning", start="2026-05-22T10:00", end="2026-05-22T10:30")
    center.approve(action.action_id)

    first = execute_calendar_action(_broker(tmp_path), center, action_id=action.action_id, expected_action_type=CALENDAR_CREATE_ACTION)
    second = execute_calendar_action(_broker(tmp_path), center, action_id=action.action_id, expected_action_type=CALENDAR_CREATE_ACTION)

    assert first["status"] == "ok"
    assert first["executed"] is True
    assert first["tool_result"]["executed"] is False
    assert first["tool_result"]["connector_configured"] is False
    assert first["action_status"] == "used"
    assert second["status"] == "error"
    assert second["executed"] is False


def test_calendar_update_rollback_data_captured_where_possible(tmp_path) -> None:
    action = draft_calendar_update(_center(tmp_path), event_id=_event_token(), changes={"title": "New title"})

    assert action.sanitized_args["rollback_data"]["title"] == "Planning"
    assert action.rollback_availability is True


def test_event_notes_body_not_included_unless_allowed(tmp_path) -> None:
    without_notes = draft_calendar_create(
        _center(tmp_path),
        title="Planning",
        start="2026-05-22T10:00",
        end="2026-05-22T10:30",
        notes="private notes",
        allow_notes=False,
    )
    with_notes = draft_calendar_create(
        _center(tmp_path),
        title="Planning 2",
        start="2026-05-22T11:00",
        end="2026-05-22T11:30",
        notes="approved notes",
        allow_notes=True,
    )

    assert "notes" not in without_notes.sanitized_args
    assert without_notes.sanitized_args["notes_omitted"] is True
    assert with_notes.sanitized_args["notes"] == "approved notes"


def test_calendar_write_audits_draft_approval_execution_and_failure(tmp_path) -> None:
    center = _center(tmp_path)
    pending = draft_calendar_create(center, title="Pending", start="2026-05-22T09:00", end="2026-05-22T09:30")
    execute_calendar_action(_broker(tmp_path), center, action_id=pending.action_id, expected_action_type=CALENDAR_CREATE_ACTION)
    approved = draft_calendar_create(center, title="Approved", start="2026-05-22T10:00", end="2026-05-22T10:30")
    center.approve(approved.action_id)
    execute_calendar_action(_broker(tmp_path), center, action_id=approved.action_id, expected_action_type=CALENDAR_CREATE_ACTION)

    action_events = [json.loads(line)["tool_name"] for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    broker_events = [json.loads(line)["tool_name"] for line in (tmp_path / "broker-audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert "action.created" in action_events
    assert "action.approved" in action_events
    assert "action.execution_failed" in action_events
    assert "action.used" in action_events
    assert "calendar.create_event" in broker_events


def test_calendar_write_capabilities_disabled_by_default() -> None:
    tools = load_capabilities_config("config/capabilities.yaml")["tools"]

    for name in (CALENDAR_CREATE_ACTION, CALENDAR_UPDATE_ACTION, CALENDAR_DELETE_ACTION):
        assert tools[name]["default_enabled"] is False
        assert tools[name]["approval_required"] == "per_action"
        assert tools[name]["approval_reuse_allowed"] is False
