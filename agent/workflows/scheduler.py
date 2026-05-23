from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from agent.config.loader import load_capabilities_config
from agent.config.runtime import RuntimeConfig
from agent.connectors.health import connectors_health_report
from agent.core.orchestrator import new_session_id
from agent.core.tool_broker import ToolBroker
from agent.safety.actions import ActionCenter
from agent.safety.audit import AuditEvent, AuditLogger, new_request_id
from agent.safety.approvals import ApprovalManager
from agent.safety.policy import PolicyEngine, RiskLevel
from agent.safety.trust import TrustLevel
from agent.tools.registry import ToolRegistry, default_registry
from agent.ui.audit_viewer import tail_audit
from agent.ui.evals import EvalOptions, run_eval
from agent.workflows.daily_briefing import daily_briefing_v2


SCHEDULE_PATH = Path("data/schedules.json")
SCHEDULE_PATH_ENV = "SCHEDULE_PATH"
SUPPORTED_WORKFLOWS = {
    "daily_briefing",
    "connector_doctor",
    "eval_safe",
    "memory_cleanup",
    "audit_summary",
    "backup_create",
}
PERSONAL_BRIEFING_SECTIONS = {"calendar", "tasks", "email"}


@dataclass(frozen=True)
class ScheduleRecord:
    schedule_id: str
    name: str
    workflow: str
    schedule: str
    args: dict[str, Any] = field(default_factory=dict)
    status: str = "active"
    created_at: str = ""
    updated_at: str = ""
    run_count: int = 0
    last_run_at: str | None = None
    last_result: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ScheduleStore:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path or os.environ.get(SCHEDULE_PATH_ENV, str(SCHEDULE_PATH)))

    def list(self) -> list[ScheduleRecord]:
        data = self._read()
        return [self._record(item) for item in data.get("schedules", [])]

    def get(self, schedule_id: str) -> ScheduleRecord | None:
        for record in self.list():
            if record.schedule_id == schedule_id:
                return record
        return None

    def create(self, *, workflow: str, name: str | None = None, schedule: str = "manual", args: dict[str, Any] | None = None) -> ScheduleRecord:
        workflow = workflow.strip()
        if workflow not in SUPPORTED_WORKFLOWS:
            raise ValueError(f"unsupported scheduled workflow: {workflow}")
        now = _now()
        record = ScheduleRecord(
            schedule_id=f"sch_{uuid4().hex[:12]}",
            name=(name or workflow).strip(),
            workflow=workflow,
            schedule=schedule.strip() or "manual",
            args=args or {},
            created_at=now,
            updated_at=now,
        )
        records = self.list()
        records.append(record)
        self._write(records)
        return record

    def pause(self, schedule_id: str) -> ScheduleRecord | None:
        return self._update(schedule_id, status="paused")

    def delete(self, schedule_id: str) -> ScheduleRecord | None:
        records = self.list()
        kept = [record for record in records if record.schedule_id != schedule_id]
        if len(kept) == len(records):
            return None
        deleted = next(record for record in records if record.schedule_id == schedule_id)
        self._write(kept)
        return deleted

    def mark_run(self, schedule_id: str, result_status: str) -> ScheduleRecord | None:
        record = self.get(schedule_id)
        if record is None:
            return None
        return self._replace(
            ScheduleRecord(
                **{
                    **record.to_dict(),
                    "updated_at": _now(),
                    "last_run_at": _now(),
                    "last_result": result_status,
                    "run_count": record.run_count + 1,
                }
            )
        )

    def _update(self, schedule_id: str, **updates: Any) -> ScheduleRecord | None:
        record = self.get(schedule_id)
        if record is None:
            return None
        return self._replace(ScheduleRecord(**{**record.to_dict(), **updates, "updated_at": _now()}))

    def _replace(self, updated: ScheduleRecord) -> ScheduleRecord:
        records = [updated if record.schedule_id == updated.schedule_id else record for record in self.list()]
        self._write(records)
        return updated

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"version": 1, "schedules": []}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"schedule store is invalid JSON at {self.path}") from exc

    def _write(self, records: list[ScheduleRecord]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": 1, "schedules": [record.to_dict() for record in records]}
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    @staticmethod
    def _record(item: dict[str, Any]) -> ScheduleRecord:
        return ScheduleRecord(
            schedule_id=str(item.get("schedule_id", "")),
            name=str(item.get("name", "")),
            workflow=str(item.get("workflow", "")),
            schedule=str(item.get("schedule", "manual")),
            args=dict(item.get("args") or {}),
            status=str(item.get("status", "active")),
            created_at=str(item.get("created_at", "")),
            updated_at=str(item.get("updated_at", "")),
            run_count=int(item.get("run_count") or 0),
            last_run_at=item.get("last_run_at"),
            last_result=item.get("last_result"),
        )


def create_schedule(
    *,
    workflow: str,
    name: str | None = None,
    schedule: str = "manual",
    args: dict[str, Any] | None = None,
    store: ScheduleStore | None = None,
    audit_logger: AuditLogger | None = None,
) -> dict[str, Any]:
    active_store = store or ScheduleStore()
    record = active_store.create(workflow=workflow, name=name, schedule=schedule, args=args)
    _audit_schedule_event(audit_logger, "schedule.create", record, f"Created schedule {record.schedule_id}.")
    return {"status": "ok", "schedule": record.to_dict(), "background_persistence": False}


def list_schedules(*, store: ScheduleStore | None = None) -> dict[str, Any]:
    active_store = store or ScheduleStore()
    return {"status": "ok", "background_persistence": False, "schedules": [record.to_dict() for record in active_store.list()]}


def pause_schedule(schedule_id: str, *, store: ScheduleStore | None = None, audit_logger: AuditLogger | None = None) -> dict[str, Any]:
    active_store = store or ScheduleStore()
    record = active_store.pause(schedule_id)
    if record is None:
        return {"status": "error", "error": "schedule not found", "schedule_id": schedule_id}
    _audit_schedule_event(audit_logger, "schedule.pause", record, f"Paused schedule {schedule_id}.")
    return {"status": "ok", "schedule": record.to_dict()}


def delete_schedule(schedule_id: str, *, store: ScheduleStore | None = None, audit_logger: AuditLogger | None = None) -> dict[str, Any]:
    active_store = store or ScheduleStore()
    record = active_store.delete(schedule_id)
    if record is None:
        return {"status": "error", "error": "schedule not found", "schedule_id": schedule_id}
    _audit_schedule_event(audit_logger, "schedule.delete", record, f"Deleted schedule {schedule_id}.")
    return {"status": "ok", "schedule_id": schedule_id}


def run_schedule(
    schedule_id: str,
    *,
    store: ScheduleStore | None = None,
    runtime: RuntimeConfig | None = None,
    registry: ToolRegistry | None = None,
    audit_logger: AuditLogger | None = None,
    eval_runner: Callable[..., dict[str, Any]] = run_eval,
) -> dict[str, Any]:
    active_store = store or ScheduleStore()
    record = active_store.get(schedule_id)
    if record is None:
        return {"status": "error", "error": "schedule not found", "schedule_id": schedule_id}
    if record.status != "active":
        return {"status": "error", "error": "schedule is paused", "schedule_id": schedule_id}

    active_runtime = runtime or RuntimeConfig.from_env()
    active_audit = audit_logger or AuditLogger(active_runtime.audit_log_path)
    broker = _build_broker(active_runtime, registry=registry, audit_logger=active_audit)
    _audit_schedule_event(active_audit, "schedule.run.start", record, f"Started scheduled workflow {record.workflow}.")
    result = _run_workflow(record, broker, active_runtime, active_audit, eval_runner)
    result_status = "ok" if result.get("status") in {"ok", "limited", "dry_run", "skipped"} else "error"
    updated = active_store.mark_run(schedule_id, result_status)
    _audit_schedule_event(active_audit, "schedule.run.finish", record, f"Finished scheduled workflow {record.workflow}: {result_status}.")
    return {
        "status": result_status,
        "schedule": updated.to_dict() if updated else record.to_dict(),
        "workflow_result": result,
        "background_persistence": False,
        "critical_actions_executed": False,
    }


def _run_workflow(
    record: ScheduleRecord,
    broker: ToolBroker,
    runtime: RuntimeConfig,
    audit_logger: AuditLogger,
    eval_runner: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    args = record.args
    if record.workflow == "daily_briefing":
        sections = _sections(args)
        payload = daily_briefing_v2(
            broker,
            sections=sections,
            weather_location=_str_or_none(args.get("weather_location")),
            use_default_weather_location=bool(args.get("weather_default", False)),
            web_topics=_string_list(args.get("web_topics")),
            dry_run=bool(args.get("dry_run", False)),
            action_center=ActionCenter(
                audit_logger=audit_logger,
                session_id=broker.session_id,
                model=broker.model,
                route="schedule_daily_briefing_actions",
            ),
        )
        if PERSONAL_BRIEFING_SECTIONS.intersection(sections):
            payload["personal_sections_requested"] = sorted(PERSONAL_BRIEFING_SECTIONS.intersection(sections))
            payload["approval_required_note"] = "Personal-data sections run only if PolicyEngine and ApprovalManager allow them."
        payload["scheduled_workflow"] = True
        payload["critical_actions_executed"] = False
        return payload
    if record.workflow == "connector_doctor":
        return {
            "status": "ok",
            "workflow": "connector_doctor",
            "scheduled_workflow": True,
            "personal_data_accessed": False,
            "report": connectors_health_report(load_capabilities_config(runtime.capabilities_path), audit_path=runtime.audit_log_path),
        }
    if record.workflow == "eval_safe":
        report = eval_runner(EvalOptions(safe=True))
        report["scheduled_workflow"] = True
        report["personal_data_evals"] = "skipped_by_default"
        return report
    if record.workflow == "memory_cleanup":
        return {
            "status": "ok",
            "workflow": "memory_cleanup",
            "scheduled_workflow": True,
            "memory_deleted": False,
            "summary": "Scheduler v1 does not delete memory automatically. Use `memory clear` manually if cleanup is desired.",
        }
    if record.workflow == "audit_summary":
        events = tail_audit(runtime.audit_log_path, limit=int(args.get("limit", 20) or 20))
        return {
            "status": "ok",
            "workflow": "audit_summary",
            "scheduled_workflow": True,
            "event_count": len(events),
            "recent_events": [
                {
                    "timestamp": event.get("timestamp"),
                    "tool_name": event.get("tool_name"),
                    "policy_decision": event.get("policy_decision"),
                    "approval_result": event.get("approval_result"),
                    "result_summary": event.get("result_summary"),
                }
                for event in events
            ],
        }
    if record.workflow == "backup_create":
        if args.get("redacted") is False:
            return {
                "status": "error",
                "workflow": "backup_create",
                "scheduled_workflow": True,
                "error": "scheduled backup_create supports redacted backups only",
                "critical_actions_executed": False,
            }
        backup_args = {
            "backup_dir": str(args.get("backup_dir") or ""),
            "include_captures": bool(args.get("include_captures", False)),
            "include_audit_metadata": bool(args.get("include_audit_metadata", False)),
            "redacted": True,
        }
        result = broker.execute(
            {
                "id": f"schedule_{record.schedule_id}_backup_create",
                "type": "function",
                "function": {
                    "name": "backup.create",
                    "arguments": json.dumps(backup_args),
                },
            }
        )
        try:
            payload = json.loads(result.content)
        except json.JSONDecodeError:
            payload = {"error": "invalid backup.create response", "raw": result.content}
        return {
            "status": "ok" if result.allowed and payload.get("status") == "ok" else "error",
            "workflow": "backup_create",
            "scheduled_workflow": True,
            "toolbroker_used": True,
            "personal_connectors_read": False,
            "memory_written": False,
            "critical_actions_executed": False,
            "backup": payload,
        }
    return {"status": "error", "error": f"unsupported scheduled workflow: {record.workflow}"}


def _build_broker(runtime: RuntimeConfig, *, registry: ToolRegistry | None, audit_logger: AuditLogger) -> ToolBroker:
    policy_engine = PolicyEngine.from_config(load_capabilities_config(runtime.capabilities_path))
    return ToolBroker(
        registry or default_registry(),
        policy_engine,
        audit_logger,
        session_id=new_session_id(),
        model=runtime.lmstudio_model,
        route="schedule",
        approval_manager=ApprovalManager(),
    )


def _audit_schedule_event(audit_logger: AuditLogger | None, tool_name: str, record: ScheduleRecord, summary: str) -> None:
    if audit_logger is None:
        return
    audit_logger.log(
        AuditEvent(
            session_id="scheduler",
            request_id=new_request_id(),
            route="schedule",
            model="",
            tool_name=tool_name,
            capability="schedule.manage",
            risk_level=RiskLevel.LOW.value,
            trust_level=TrustLevel.TRUSTED_USER.value,
            policy_decision="ALLOW",
            approval_result="not_required",
            sanitized_args={
                "schedule_id": record.schedule_id,
                "workflow": record.workflow,
                "schedule": record.schedule,
                "status": record.status,
            },
            result_summary=summary,
        )
    )


def _sections(args: dict[str, Any]) -> list[str]:
    raw = args.get("sections")
    if raw is None:
        return ["weather"]
    return _string_list(raw)


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [str(value).strip()] if str(value).strip() else []


def _str_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _now() -> str:
    return datetime.now(UTC).isoformat()
