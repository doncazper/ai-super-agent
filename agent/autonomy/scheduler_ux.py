from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from agent.runtime.scheduler import SchedulerPolicy
from agent.workflows.scheduler import ScheduleRecord, ScheduleStore


@dataclass(frozen=True)
class ScheduledWorkflowTemplate:
    workflow_id: str
    workflow_name: str
    description: str
    category: str
    risk_level: str
    required_tools: list[str] = field(default_factory=list)
    approval_requirements: list[str] = field(default_factory=list)
    personal_data_use: str = "none"
    write_send_behavior: str = "none"
    background_execution_allowed: bool = False
    creates_action_center_item: bool = False
    tests_dogfood_status: str = "local tests only; manual QA pending"
    default_enabled: bool = True
    setup_hint: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


TEMPLATES: dict[str, ScheduledWorkflowTemplate] = {
    "connector_doctor": ScheduledWorkflowTemplate(
        workflow_id="connector_doctor",
        workflow_name="Connector doctor",
        description="Review connector/provider configuration metadata.",
        category="diagnostics",
        risk_level="SAFE",
        tests_dogfood_status="covered by scheduler tests; manual QA pending",
        setup_hint="Safe metadata diagnostic. Create a schedule record, then run it manually.",
    ),
    "eval_safe": ScheduledWorkflowTemplate(
        workflow_id="eval_safe",
        workflow_name="Safe eval suite",
        description="Run safe eval fixtures without personal-data or live provider checks.",
        category="evals",
        risk_level="SAFE",
        tests_dogfood_status="covered by scheduler and eval tests; manual QA pending",
        setup_hint="Safe fixture-backed eval. Live/personal-data evals are not included.",
    ),
    "memory_cleanup": ScheduledWorkflowTemplate(
        workflow_id="memory_cleanup",
        workflow_name="Memory cleanup review",
        description="Show manual cleanup guidance without deleting memory automatically.",
        category="maintenance",
        risk_level="LOW",
        tests_dogfood_status="covered by scheduler tests; manual QA pending",
        setup_hint="Manual guidance only. This template does not delete memory.",
    ),
    "audit_summary": ScheduledWorkflowTemplate(
        workflow_id="audit_summary",
        workflow_name="Audit summary",
        description="Show a redacted recent audit event summary.",
        category="diagnostics",
        risk_level="LOW",
        required_tools=["audit tail metadata"],
        tests_dogfood_status="covered by scheduler tests; manual QA pending",
        setup_hint="Manual metadata review only.",
    ),
    "backup_create": ScheduledWorkflowTemplate(
        workflow_id="backup_create",
        workflow_name="Redacted backup",
        description="Create a redacted local backup only when manually run.",
        category="backup",
        risk_level="LOW",
        required_tools=["backup.create"],
        approval_requirements=["user-initiated manual run"],
        write_send_behavior="local redacted backup archive write",
        tests_dogfood_status="covered by scheduler backup tests; manual QA pending",
        setup_hint="Scheduled backup_create forces redacted=true and must still be invoked manually in v1.",
    ),
    "daily_briefing": ScheduledWorkflowTemplate(
        workflow_id="daily_briefing",
        workflow_name="Daily briefing",
        description="Prepare a manual-run briefing; personal sections stay approval-gated.",
        category="briefing",
        risk_level="HIGH",
        required_tools=["weather/web/actions depending on sections"],
        approval_requirements=["personal sections require normal approvals before each run"],
        personal_data_use="disabled by default; calendar/tasks/email sections are personal-data gated",
        creates_action_center_item=True,
        tests_dogfood_status="covered by scheduler tests for approval-required sections; manual QA pending",
        default_enabled=False,
        setup_hint="Use safe sections such as weather by default. Personal sections require explicit approval and do not auto-run.",
    ),
    "email.send_approved": ScheduledWorkflowTemplate(
        workflow_id="email.send_approved",
        workflow_name="Email send",
        description="Forbidden as an automatic scheduled workflow.",
        category="email_send",
        risk_level="CRITICAL",
        required_tools=["email.send_approved"],
        approval_requirements=["CRITICAL exact-preview per-action approval; not schedulable"],
        personal_data_use="email/private recipient data",
        write_send_behavior="send email",
        background_execution_allowed=False,
        creates_action_center_item=True,
        tests_dogfood_status="blocked by scheduler policy; no auto-send dogfood",
        default_enabled=False,
        setup_hint="Create a reviewed Action Center send item manually; do not schedule email sends.",
    ),
    "calendar.write": ScheduledWorkflowTemplate(
        workflow_id="calendar.write",
        workflow_name="Calendar write",
        description="Forbidden as an automatic scheduled workflow.",
        category="calendar_write",
        risk_level="CRITICAL",
        required_tools=["calendar.write"],
        approval_requirements=["CRITICAL exact-preview per-action approval; not schedulable"],
        personal_data_use="calendar/local private data",
        write_send_behavior="calendar write",
        background_execution_allowed=False,
        creates_action_center_item=True,
        tests_dogfood_status="blocked by scheduler policy; no automatic write dogfood",
        default_enabled=False,
        setup_hint="Use a manual Action Center write workflow; do not schedule calendar writes.",
    ),
}


def explain_scheduler() -> dict[str, Any]:
    return {
        "status": "ok",
        "mode": "manual_run_only",
        "dry_run_default": True,
        "background_persistence": False,
        "os_persistence": {
            "cron": False,
            "launch_agent": False,
            "login_item": False,
            "daemon": False,
        },
        "high_critical_auto_run": False,
        "personal_data_default_enabled": False,
        "send_write_auto_run": False,
        "summary": "Scheduler UX can preview and dry-run workflow metadata, but v1 does not install background persistence or run HIGH/CRITICAL actions automatically.",
        "next_safe_action": "Use `schedule templates`, then `schedule preview <workflow_id>`, then create/run an approved manual schedule only if the risk review is acceptable.",
    }


def list_templates() -> dict[str, Any]:
    return {
        "status": "ok",
        "background_persistence": False,
        "templates": [_with_policy(template, last_result=None) for template in TEMPLATES.values() if template.default_enabled],
        "blocked_templates": [_with_policy(template, last_result=None) for template in TEMPLATES.values() if not template.default_enabled],
    }


def preview_workflow(workflow_id: str, *, store: ScheduleStore | None = None) -> dict[str, Any]:
    resolved = _resolve_workflow(workflow_id, store=store)
    if resolved is None:
        return _unknown(workflow_id)
    template, record = resolved
    payload = _with_policy(template, last_result=record.last_result if record else None)
    payload.update(
        {
            "status": "ok",
            "schedule_id": record.schedule_id if record else None,
            "schedule_status": record.status if record else "template",
            "schedule_hint": record.schedule if record else "not scheduled",
            "last_run_result": record.last_result if record else None,
            "next_safe_action": _next_safe_action(template, payload["policy"]),
        }
    )
    return payload


def dry_run_workflow(workflow_id: str, *, store: ScheduleStore | None = None) -> dict[str, Any]:
    preview = preview_workflow(workflow_id, store=store)
    if preview.get("status") != "ok":
        return preview
    allowed = bool(preview["policy"]["allowed"])
    blocked = preview["policy"]["status"] in {"blocked", "approval_required", "unsupported"}
    return {
        **preview,
        "status": "dry_run" if allowed else "blocked",
        "dry_run": True,
        "would_execute_tools": False,
        "tools_executed": [],
        "workflow_executed": False,
        "action_center_item_created": False,
        "background_persistence": False,
        "blocked": blocked,
        "result": "No workflow was run and no tools were executed.",
    }


def workflow_risks(workflow_id: str, *, store: ScheduleStore | None = None) -> dict[str, Any]:
    preview = preview_workflow(workflow_id, store=store)
    if preview.get("status") != "ok":
        return preview
    return {
        "status": "ok",
        "workflow_id": preview["workflow_id"],
        "risk_level": preview["risk_level"],
        "approval_required": preview["policy"]["approval_required"],
        "approval_requirements": preview["approval_requirements"],
        "personal_data_use": preview["personal_data_use"],
        "write_send_behavior": preview["write_send_behavior"],
        "background_execution_allowed": False,
        "blocked_reason": preview["policy"]["reason"] if not preview["policy"]["allowed"] else None,
        "next_safe_action": preview["next_safe_action"],
    }


def review_schedules(*, store: ScheduleStore | None = None) -> dict[str, Any]:
    active_store = store or ScheduleStore()
    records = active_store.list()
    return {
        "status": "ok",
        "background_persistence": False,
        "schedule_count": len(records),
        "schedules": [preview_workflow(record.schedule_id, store=active_store) for record in records],
        "unsupported_records": [
            record.to_dict()
            for record in records
            if record.workflow not in TEMPLATES
        ],
        "next_safe_action": "Pause or delete unsupported/high-risk schedules; use dry-run before manual run.",
    }


def _resolve_workflow(workflow_id: str, *, store: ScheduleStore | None) -> tuple[ScheduledWorkflowTemplate, ScheduleRecord | None] | None:
    active_store = store or ScheduleStore()
    record = active_store.get(workflow_id)
    if record is not None:
        template = TEMPLATES.get(record.workflow)
        return (template, record) if template else None
    template = TEMPLATES.get(workflow_id)
    return (template, None) if template else None


def _with_policy(template: ScheduledWorkflowTemplate, *, last_result: str | None) -> dict[str, Any]:
    policy = SchedulerPolicy().evaluate(
        category=template.category,
        risk_level=template.risk_level,
        personal_data=template.personal_data_use != "none",
        background_persistence=template.background_execution_allowed,
    ).to_dict()
    return {
        **template.to_dict(),
        "approval_required": bool(policy["approval_required"]),
        "policy": policy,
        "last_run_result": last_result,
        "next_safe_action": _next_safe_action(template, policy),
    }


def _next_safe_action(template: ScheduledWorkflowTemplate, policy: dict[str, Any]) -> str:
    if policy["status"] == "manual_run_only":
        return "Preview and dry-run first, then create or manually run only if the user explicitly chooses it."
    if policy["status"] == "approval_required":
        return "Do not auto-run. Create an Action Center review path or choose a safer template."
    if policy["status"] == "blocked":
        return "Do not schedule. Use an explicit one-off Action Center workflow instead."
    return template.setup_hint or "Review setup hints before use."


def _unknown(workflow_id: str) -> dict[str, Any]:
    return {
        "status": "not_found",
        "workflow_id": workflow_id,
        "blocked": True,
        "background_persistence": False,
        "setup_hint": "Run `schedule templates` to see supported scheduler UX templates.",
    }
