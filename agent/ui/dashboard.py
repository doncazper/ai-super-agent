from __future__ import annotations

import json
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from agent.config.loader import load_capabilities_config
from agent.config.runtime import RuntimeConfig, RuntimeConfigError
from agent.connectors.registry import default_connector_registry
from agent.safety.approvals import ApprovalRequest, ApprovalStatus, ApprovalStore
from agent.safety.redaction import SecretRedactor
from agent.tools.registry import default_registry
from agent.ui.audit_viewer import tail_audit
from agent.ui.doctor import DoctorCheck, run_doctor
from agent.ui.permissions_dashboard import PermissionStore


PERSONAL_CONNECTORS = {"calendar", "contacts", "email", "messages", "browser"}


def build_dashboard(
    *,
    project_root: str | Path = ".",
    audit_limit: int = 10,
    runtime: RuntimeConfig | None = None,
    doctor_checks: list[DoctorCheck] | None = None,
    connectors: list[dict[str, Any]] | None = None,
    approvals: list[ApprovalRequest] | None = None,
    permissions: list[str] | None = None,
    audit_events: list[dict[str, Any]] | None = None,
    memory_path: str | Path = "data/memory.sqlite3",
) -> dict[str, Any]:
    redactor = SecretRedactor()
    root = Path(project_root)
    runtime_error = ""
    try:
        active_runtime = runtime or RuntimeConfig.from_env()
    except RuntimeConfigError as exc:
        active_runtime = RuntimeConfig()
        runtime_error = str(exc)

    capabilities = load_capabilities_config(active_runtime.capabilities_path)
    checks = doctor_checks if doctor_checks is not None else run_doctor(config=active_runtime)
    connector_statuses = (
        connectors
        if connectors is not None
        else default_connector_registry().list_statuses(capabilities, audit_path=active_runtime.audit_log_path)
    )
    approval_requests = approvals if approvals is not None else ApprovalStore().list()
    permission_grants = permissions if permissions is not None else PermissionStore().show()
    recent_events = (
        audit_events
        if audit_events is not None
        else tail_audit(active_runtime.audit_log_path, limit=max(1, min(audit_limit, 50)))
    )

    report = {
        "status": "ok" if not any(check.status == "fail" for check in checks) and not runtime_error else "warn",
        "read_only": True,
        "accesses_personal_data": False,
        "background_actions": False,
        "runtime": _runtime_section(active_runtime, runtime_error),
        "lmstudio": _lmstudio_section(checks),
        "tools": _tools_section(project_root=root, capabilities=capabilities),
        "connectors": [_connector_summary(status) for status in connector_statuses],
        "permissions": {"grants": permission_grants, "grant_count": len(permission_grants)},
        "approvals": _approvals_section(approval_requests),
        "audit": {
            "path": active_runtime.audit_log_path,
            "recent_events": [_safe_audit_event(event) for event in recent_events],
        },
        "memory": _memory_summary(memory_path),
        "risk_settings": _risk_settings(capabilities),
        "last_test_run": _last_test_run(root / "docs" / "PROJECT_STATE.md"),
        "setup_hints": _setup_hints(checks, connector_statuses),
        "safety_notes": [
            "Dashboard is metadata/status only and does not execute connector actions.",
            "No permissions are granted and no approvals are used by viewing the dashboard.",
            "Personal connectors are displayed from configuration/status metadata only.",
        ],
    }
    return redactor.redact(report)


def format_dashboard(report: dict[str, Any]) -> str:
    lines = [
        "Agent Dashboard v1",
        f"Status: {report.get('status')}",
        f"Read-only: {report.get('read_only')} | Personal data accessed: {report.get('accesses_personal_data')}",
        "",
        "Runtime",
        f"- Model: {report.get('runtime', {}).get('model') or '(not set)'}",
        f"- Base URL: {report.get('runtime', {}).get('base_url')}",
        f"- Tool mode: {report.get('runtime', {}).get('tool_mode')}",
        f"- Audit log: {report.get('runtime', {}).get('audit_log_path')}",
        "",
        "LM Studio",
        f"- Server: {report.get('lmstudio', {}).get('server_status')} ({report.get('lmstudio', {}).get('server_detail')})",
        f"- Model configured: {report.get('lmstudio', {}).get('model_status')}",
        "",
        "Tools",
        f"- Registered: {report.get('tools', {}).get('registered_count')}",
        f"- Enabled by default: {report.get('tools', {}).get('enabled_count')}",
        f"- Enabled tools: {', '.join(report.get('tools', {}).get('enabled_tools', [])[:16])}",
        "",
        "Connectors",
    ]
    for connector in report.get("connectors", []):
        lines.append(
            f"- {connector.get('name')}: configured={connector.get('configured')} "
            f"enabled={connector.get('enabled')} provider={connector.get('default_provider')} "
            f"risk={connector.get('risk_level')} approval={connector.get('approval_required')}"
        )
    lines.extend(
        [
            "",
            "Permissions",
            f"- Grants: {', '.join(report.get('permissions', {}).get('grants', [])) or '(none)'}",
            "",
            "Pending Approvals",
        ]
    )
    pending = report.get("approvals", {}).get("pending", [])
    if pending:
        for request in pending:
            lines.append(f"- {request.get('request_id')}: {request.get('capability')} [{request.get('risk_level')}]")
    else:
        lines.append("- (none)")
    lines.extend(
        [
            "",
            "Recent Audit Events",
        ]
    )
    for event in report.get("audit", {}).get("recent_events", []):
        lines.append(
            f"- {event.get('timestamp', '')} {event.get('tool_name')} "
            f"{event.get('policy_decision')} {event.get('approval_result')} {event.get('result_summary', '')}".rstrip()
        )
    if not report.get("audit", {}).get("recent_events"):
        lines.append("- (none)")
    memory = report.get("memory", {})
    lines.extend(
        [
            "",
            "Memory",
            f"- Records: {memory.get('total_records')} | Categories: {memory.get('by_category')}",
            "",
            "Risk Settings",
            f"- By risk: {report.get('risk_settings', {}).get('by_risk')}",
            f"- Personal defaults disabled: {report.get('risk_settings', {}).get('personal_defaults_disabled')}",
            f"- Critical defaults disabled: {report.get('risk_settings', {}).get('critical_defaults_disabled')}",
            "",
            "Last Test Run",
            f"- {report.get('last_test_run', {}).get('summary')}",
            "",
            "Setup Hints",
        ]
    )
    hints = report.get("setup_hints", [])
    if hints:
        lines.extend(f"- {hint}" for hint in hints[:10])
    else:
        lines.append("- No setup hints right now.")
    return "\n".join(lines)


def format_dashboard_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True)


def _runtime_section(runtime: RuntimeConfig, error: str) -> dict[str, Any]:
    return {
        "model": runtime.lmstudio_model,
        "model_set": bool(runtime.lmstudio_model),
        "base_url": runtime.lmstudio_base_url,
        "temperature": runtime.temperature,
        "top_p": runtime.top_p,
        "max_tokens": runtime.max_tokens,
        "tool_mode": runtime.tool_mode,
        "debug": runtime.debug,
        "audit_log_path": runtime.audit_log_path,
        "capabilities_path": runtime.capabilities_path,
        "config_error": error or None,
    }


def _lmstudio_section(checks: Iterable[DoctorCheck]) -> dict[str, str]:
    by_name = {check.name: check for check in checks}
    server = by_name.get("lmstudio_server")
    model = by_name.get("lmstudio_model")
    selected = by_name.get("selected_model_available")
    return {
        "server_status": server.status if server else "unknown",
        "server_detail": server.detail if server else "not checked",
        "model_status": model.status if model else "unknown",
        "model_detail": model.detail if model else "not checked",
        "selected_model_status": selected.status if selected else "unknown",
        "selected_model_detail": selected.detail if selected else "not checked",
    }


def _tools_section(*, project_root: Path, capabilities: dict[str, Any]) -> dict[str, Any]:
    registry = default_registry(project_root=project_root)
    tool_names = sorted(schema["function"]["name"] for schema in registry.schemas())
    entries = capabilities.get("tools", {})
    enabled = sorted(
        name
        for name in tool_names
        if isinstance(entries.get(name), dict) and bool(entries[name].get("default_enabled"))
    )
    return {
        "registered_count": len(tool_names),
        "registered_tools": tool_names,
        "enabled_count": len(enabled),
        "enabled_tools": enabled,
    }


def _connector_summary(status: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": status.get("name"),
        "configured": status.get("configured"),
        "enabled": status.get("enabled"),
        "default_provider": status.get("default_provider"),
        "risk_level": status.get("risk_level"),
        "approval_required": status.get("approval_required"),
        "last_successful_call": status.get("last_successful_call"),
        "last_error": status.get("last_error"),
        "rate_limit_state": status.get("rate_limit_state"),
        "cache_state": status.get("cache_state"),
        "setup_hint": status.get("setup_hint") or status.get("docs_setup_hint"),
        "capabilities": status.get("capabilities", []),
    }


def _approvals_section(requests: list[ApprovalRequest]) -> dict[str, Any]:
    pending = [request for request in requests if request.status in {ApprovalStatus.PENDING, ApprovalStatus.DISPLAYED}]
    return {
        "total": len(requests),
        "pending_count": len(pending),
        "pending": [
            {
                "request_id": request.request_id,
                "timestamp": request.timestamp,
                "capability": request.capability,
                "tool_name": request.tool_name,
                "risk_level": request.risk_level.value,
                "status": request.status.value,
                "summary": request.summary,
                "expires_at": request.expires_at,
            }
            for request in pending
        ],
    }


def _safe_audit_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "timestamp": event.get("timestamp"),
        "request_id": event.get("request_id"),
        "route": event.get("route"),
        "tool_name": event.get("tool_name"),
        "capability": event.get("capability"),
        "risk_level": event.get("risk_level"),
        "trust_level": event.get("trust_level"),
        "policy_decision": event.get("policy_decision"),
        "approval_result": event.get("approval_result"),
        "result_summary": event.get("result_summary"),
        "files_read_count": len(event.get("files_read", []) or []),
        "files_written_count": len(event.get("files_written", []) or []),
        "commands_run_count": len(event.get("commands_run", []) or []),
        "network_domains_count": len(event.get("network_domains", []) or []),
        "dry_run": bool(event.get("dry_run", False)),
    }


def _memory_summary(memory_path: str | Path) -> dict[str, Any]:
    path = Path(memory_path)
    if not path.exists():
        return {"path": str(path), "configured": False, "total_records": 0, "by_category": {}, "by_scope": {}}
    try:
        with sqlite3.connect(path) as conn:
            rows = conn.execute("SELECT category, scope FROM memories").fetchall()
    except sqlite3.Error as exc:
        return {"path": str(path), "configured": True, "error": str(exc), "total_records": 0, "by_category": {}, "by_scope": {}}
    categories = Counter(str(row[0]) for row in rows)
    scopes = Counter(str(row[1]) for row in rows)
    return {
        "path": str(path),
        "configured": True,
        "total_records": len(rows),
        "by_category": dict(sorted(categories.items())),
        "by_scope": dict(sorted(scopes.items())),
        "content_returned": False,
    }


def _risk_settings(capabilities: dict[str, Any]) -> dict[str, Any]:
    tools = capabilities.get("tools", {})
    by_risk: Counter[str] = Counter()
    enabled_by_risk: Counter[str] = Counter()
    personal_enabled: list[str] = []
    critical_enabled: list[str] = []
    approval_required: list[str] = []
    for name, entry in tools.items():
        if not isinstance(entry, dict):
            continue
        risk = str(entry.get("risk_level", "UNKNOWN"))
        by_risk[risk] += 1
        if entry.get("default_enabled"):
            enabled_by_risk[risk] += 1
        if entry.get("connector_name") in PERSONAL_CONNECTORS and entry.get("default_enabled"):
            personal_enabled.append(str(name))
        if risk == "CRITICAL" and entry.get("default_enabled"):
            critical_enabled.append(str(name))
        if entry.get("approval_required"):
            approval_required.append(str(name))
    return {
        "by_risk": dict(sorted(by_risk.items())),
        "enabled_by_risk": dict(sorted(enabled_by_risk.items())),
        "approval_required_count": len(approval_required),
        "personal_defaults_disabled": not personal_enabled,
        "personal_enabled": personal_enabled,
        "critical_defaults_disabled": not critical_enabled,
        "critical_enabled": critical_enabled,
    }


def _last_test_run(path: Path) -> dict[str, str]:
    if not path.exists():
        return {"summary": "No project state file found.", "source": str(path)}
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.strip() == "## Last Test Result":
            for value in lines[index + 1 : index + 6]:
                if value.strip():
                    return {"summary": value.strip(), "source": str(path)}
    return {"summary": "Last test result not recorded.", "source": str(path)}


def _setup_hints(checks: Iterable[DoctorCheck], connectors: Iterable[dict[str, Any]]) -> list[str]:
    hints: list[str] = []
    for check in checks:
        if check.status in {"fail", "warn"}:
            hints.append(f"{check.name}: {check.detail}")
    for connector in connectors:
        if not connector.get("configured"):
            hint = connector.get("setup_hint") or connector.get("docs_setup_hint")
            if hint:
                hints.append(f"{connector.get('name')}: {hint}")
    return hints
