from __future__ import annotations

import json

from agent.config.loader import load_capabilities_config
from agent.core.tool_broker import ToolBroker
from agent.safety.actions import ActionCenter, ActionCenterStore, ActionStatus
from agent.safety.approvals import ApprovalManager, ApprovalStore
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.personal.tasks import MockTasksConnector, TaskItem
from agent.tools.registry import default_registry
from agent.workflows.tasks import TASK_CREATE_ACTION, draft_task_create, execute_task_action


TASK_CAPABILITIES = {
    "tasks.list": Capability("tasks.list", RiskLevel.HIGH, default_enabled=True, approval_required=True),
    "tasks.draft_create": Capability("tasks.draft_create", RiskLevel.MEDIUM, default_enabled=True),
    "tasks.create": Capability(
        "tasks.create",
        RiskLevel.CRITICAL,
        default_enabled=True,
        approval_required="per_action",
        approval_reuse_allowed=False,
    ),
    "tasks.update": Capability(
        "tasks.update",
        RiskLevel.CRITICAL,
        default_enabled=True,
        approval_required="per_action",
        approval_reuse_allowed=False,
    ),
    "tasks.complete": Capability(
        "tasks.complete",
        RiskLevel.CRITICAL,
        default_enabled=True,
        approval_required="per_action",
        approval_reuse_allowed=False,
    ),
    "tasks.delete": Capability(
        "tasks.delete",
        RiskLevel.CRITICAL,
        default_enabled=True,
        approval_required="per_action",
        approval_reuse_allowed=False,
    ),
}


def _center(tmp_path) -> ActionCenter:
    return ActionCenter(
        store=ActionCenterStore(tmp_path / "actions.json"),
        approval_store=ApprovalStore(tmp_path / "approvals.json"),
        audit_logger=AuditLogger(tmp_path / "action-audit.jsonl"),
        session_id="test-session",
        model="test-model",
    )


def _broker(tmp_path, *, approvals: ApprovalManager | None = None, connector: MockTasksConnector | None = None, enabled: bool = True) -> ToolBroker:
    capabilities = {
        name: Capability(
            capability.name,
            capability.risk_level,
            default_enabled=enabled,
            approval_required=capability.approval_required,
            approval_reuse_allowed=capability.approval_reuse_allowed,
        )
        for name, capability in TASK_CAPABILITIES.items()
    }
    return ToolBroker(
        default_registry(project_root=tmp_path, tasks_connector=connector or MockTasksConnector(), action_center=_center(tmp_path)),
        PolicyEngine(capabilities),
        AuditLogger(tmp_path / "broker-audit.jsonl"),
        session_id="broker-session",
        model="test-model",
        route="test",
        approval_manager=approvals,
    )


def _call(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    return {
        "id": f"call_{tool_name}",
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments)},
    }


def test_tasks_module_disabled_denies_access(tmp_path) -> None:
    broker = _broker(tmp_path, enabled=False)

    result = broker.execute(_call("tasks.list", {}))

    assert result.allowed is False
    assert json.loads(result.content)["decision"] == "DENY"


def test_tasks_list_requires_approval(tmp_path) -> None:
    broker = _broker(tmp_path, approvals=ApprovalManager())

    result = broker.execute(_call("tasks.list", {"max_results": 5}))

    assert result.allowed is False
    payload = json.loads(result.content)
    assert payload["approval_result"] == "denied"


def test_tasks_draft_create_creates_action_center_item(tmp_path) -> None:
    action = draft_task_create(
        _center(tmp_path),
        title="Send agenda",
        due="2026-05-23",
        notes="private notes",
        source_workflow="meeting_prep",
        allow_notes=False,
    )

    assert action.status is ActionStatus.PENDING
    assert action.action_type == TASK_CREATE_ACTION
    assert action.source_workflow == "tasks.meeting_prep"
    assert action.sanitized_args["title"] == "Send agenda"
    assert "notes" not in action.sanitized_args
    assert action.sanitized_args["notes_omitted"] is True


def test_tasks_draft_create_routes_through_tool_broker(tmp_path) -> None:
    broker = _broker(tmp_path)

    result = broker.execute(
        _call(
            "tasks.draft_create",
            {
                "title": "Send agenda",
                "due": "2026-05-23",
                "notes": "private notes",
                "source_workflow": "meeting_prep",
                "allow_notes": False,
            },
        )
    )

    payload = json.loads(result.content)
    action = ActionCenterStore(tmp_path / "actions.json").list()[0]
    broker_events = [json.loads(line)["tool_name"] for line in (tmp_path / "broker-audit.jsonl").read_text(encoding="utf-8").splitlines()]
    action_events = [json.loads(line)["tool_name"] for line in (tmp_path / "action-audit.jsonl").read_text(encoding="utf-8").splitlines()]

    assert result.allowed is True
    assert payload["status"] == "ok"
    assert payload["executed"] is False
    assert payload["connector_accessed"] is False
    assert payload["action_id"] == action.action_id
    assert action.action_type == TASK_CREATE_ACTION
    assert "notes" not in action.sanitized_args
    assert "tasks.draft_create" in broker_events
    assert "action.created" in action_events


def test_tasks_create_requires_approval(tmp_path) -> None:
    center = _center(tmp_path)
    action = draft_task_create(center, title="Send agenda")

    report = execute_task_action(_broker(tmp_path), center, action_id=action.action_id)

    assert report["status"] == "error"
    assert report["executed"] is False
    assert "approved" in report["error"]


def test_tasks_complete_requires_approval(tmp_path) -> None:
    connector = MockTasksConnector([TaskItem("task-1", "Agenda")])
    broker = _broker(tmp_path, approvals=ApprovalManager(), connector=connector)

    result = broker.execute(_call("tasks.complete", {"task_id": "task-1"}))

    assert result.allowed is False
    assert json.loads(result.content)["approval_result"] == "denied"
    assert connector.completed == []


def test_tasks_delete_requires_approval(tmp_path) -> None:
    connector = MockTasksConnector([TaskItem("task-1", "Agenda")])
    broker = _broker(tmp_path, approvals=ApprovalManager(), connector=connector)

    result = broker.execute(_call("tasks.delete", {"task_id": "task-1"}))

    assert result.allowed is False
    assert json.loads(result.content)["approval_result"] == "denied"
    assert connector.deleted == []


def test_tasks_mock_provider_list_create_update_complete_delete(tmp_path) -> None:
    connector = MockTasksConnector([TaskItem("task-1", "Agenda")])
    approvals = ApprovalManager(auto_approve={"tasks.list", "tasks.update", "tasks.complete", "tasks.delete"})
    broker = _broker(tmp_path, approvals=approvals, connector=connector)

    listed = broker.execute(_call("tasks.list", {"max_results": 10}))
    updated = broker.execute(_call("tasks.update", {"task_id": "task-1", "changes": {"title": "Agenda updated"}}))
    completed = broker.execute(_call("tasks.complete", {"task_id": "task-1"}))
    deleted = broker.execute(_call("tasks.delete", {"task_id": "task-1"}))

    assert listed.allowed is True
    assert updated.allowed is True
    assert completed.allowed is True
    assert deleted.allowed is True
    assert json.loads(listed.content)["stored_in_memory"] is False
    assert json.loads(updated.content)["stored_in_memory"] is False
    assert connector.deleted == ["task-1"]


def test_approved_task_create_executes_once_and_no_memory_write(tmp_path) -> None:
    center = _center(tmp_path)
    action = draft_task_create(center, title="Send agenda")
    center.approve(action.action_id)
    connector = MockTasksConnector()

    first = execute_task_action(_broker(tmp_path, connector=connector), center, action_id=action.action_id)
    second = execute_task_action(_broker(tmp_path, connector=connector), center, action_id=action.action_id)

    assert first["status"] == "ok"
    assert first["executed"] is True
    assert first["tool_result"]["stored_in_memory"] is False
    assert first["action_status"] == "used"
    assert second["status"] == "error"
    assert second["executed"] is False
    assert len(connector.created) == 1


def test_tasks_audit_logs_access_and_writes(tmp_path) -> None:
    center = _center(tmp_path)
    action = draft_task_create(center, title="Send agenda")
    center.approve(action.action_id)
    connector = MockTasksConnector([TaskItem("task-1", "Agenda")])
    broker = _broker(
        tmp_path,
        approvals=ApprovalManager(auto_approve={"tasks.list", "tasks.complete"}),
        connector=connector,
    )

    broker.execute(_call("tasks.list", {}))
    broker.execute(_call("tasks.complete", {"task_id": "task-1"}))
    execute_task_action(broker, center, action_id=action.action_id)

    action_events = [json.loads(line)["tool_name"] for line in (tmp_path / "action-audit.jsonl").read_text(encoding="utf-8").splitlines()]
    broker_events = [json.loads(line)["tool_name"] for line in (tmp_path / "broker-audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert "action.created" in action_events
    assert "action.approved" in action_events
    assert "action.used" in action_events
    assert "tasks.list" in broker_events
    assert "tasks.complete" in broker_events
    assert "tasks.create" in broker_events


def test_tasks_capabilities_disabled_by_default() -> None:
    tools = load_capabilities_config("config/capabilities.yaml")["tools"]

    assert tools["tasks.draft_create"]["default_enabled"] is True
    assert tools["tasks.draft_create"]["risk_level"] == "MEDIUM"
    assert tools["tasks.list"]["default_enabled"] is False
    assert tools["tasks.list"]["risk_level"] == "HIGH"
    for name in ("tasks.create", "tasks.update", "tasks.complete", "tasks.delete"):
        assert tools[name]["default_enabled"] is False
        assert tools[name]["risk_level"] == "CRITICAL"
        assert tools[name]["approval_required"] == "per_action"
        assert tools[name]["approval_reuse_allowed"] is False
