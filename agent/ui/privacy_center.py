from __future__ import annotations

import json
import sqlite3
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

from agent.config.loader import load_capabilities_config
from agent.config.runtime import RuntimeConfig
from agent.connectors.registry import default_connector_registry
from agent.core.tool_broker import ToolBroker
from agent.safety.actions import ActionCenterStore, ActionRecord
from agent.safety.approvals import ApprovalRequest, ApprovalStatus, ApprovalStore
from agent.safety.audit import AuditEvent, AuditLogger, new_request_id
from agent.safety.policy import PolicyDecision, RiskLevel
from agent.safety.redaction import SecretRedactor
from agent.safety.trust import TrustLevel
from agent.ui.permissions_dashboard import PermissionStore


PERSONAL_CONNECTORS = {"calendar", "contacts", "email", "messages", "tasks"}
PERSONAL_BROWSER_CAPABILITIES = {"browser.selected_tab", "browser.read_selected_tab"}
PERSONAL_MEMORY_CAPABILITIES = {"memory.store_personal"}
CONFIRM_DELETE_MEMORY = "DELETE-MEMORY"


def privacy_status(
    *,
    project_root: str | Path = ".",
    runtime: RuntimeConfig | None = None,
    audit_logger: AuditLogger | None = None,
) -> dict[str, Any]:
    active_runtime = runtime or RuntimeConfig.from_env()
    report = {
        "status": "ok",
        "read_only": True,
        "personal_connector_reads_performed": False,
        "connectors": _connector_overview(active_runtime),
        "memory": _memory_counts(_memory_path(project_root)),
        "captures": _capture_counts(project_root),
        "audit": _audit_metadata(active_runtime.audit_log_path),
        "pending_personal_actions": _pending_personal_actions_count(),
        "approvals": _approval_counts(),
        "notes": _privacy_notes(),
    }
    _audit_privacy(
        audit_logger or AuditLogger(active_runtime.audit_log_path),
        "privacy.status",
        "privacy status generated",
        files_read=[],
    )
    return _redact(report)


def privacy_inventory(
    *,
    project_root: str | Path = ".",
    runtime: RuntimeConfig | None = None,
    audit_logger: AuditLogger | None = None,
) -> dict[str, Any]:
    active_runtime = runtime or RuntimeConfig.from_env()
    capabilities = load_capabilities_config(active_runtime.capabilities_path)
    report = {
        "status": "ok",
        "generated_at": _now(),
        "metadata_only": True,
        "personal_connector_reads_performed": False,
        "enabled_connectors": [item for item in _connector_statuses(active_runtime) if item.get("enabled")],
        "disabled_connectors": [item for item in _connector_statuses(active_runtime) if not item.get("enabled")],
        "personal_data_capabilities": _personal_capabilities(capabilities),
        "memory": _memory_counts(_memory_path(project_root)),
        "captures": _capture_counts(project_root),
        "audit": _audit_metadata(active_runtime.audit_log_path),
        "caches": _cache_inventory(project_root),
        "pending_actions_with_personal_data": _pending_personal_actions(),
        "approvals": _approval_counts(),
        "permissions": _permissions_summary(),
        "data_deletion_options": _deletion_options(),
        "not_included": _not_included(),
    }
    _audit_privacy(
        audit_logger or AuditLogger(active_runtime.audit_log_path),
        "privacy.inventory",
        "privacy inventory generated",
        files_read=[],
    )
    return _redact(report)


def privacy_export(
    *,
    project_root: str | Path = ".",
    runtime: RuntimeConfig | None = None,
    audit_logger: AuditLogger | None = None,
) -> dict[str, Any]:
    active_runtime = runtime or RuntimeConfig.from_env()
    report = {
        "status": "ok",
        "exported_at": _now(),
        "redacted": True,
        "content_policy": "Secrets are redacted. Memory content is exported as redacted previews only by default.",
        "inventory": privacy_inventory(project_root=project_root, runtime=active_runtime, audit_logger=audit_logger),
        "memory_records": _memory_export_preview(_memory_path(project_root)),
        "capture_records": _capture_export_preview(project_root),
        "actions": [record.to_export_dict() for record in ActionCenterStore().list()],
        "approvals": [_approval_export(request) for request in ApprovalStore().list()],
        "audit_summary": privacy_audit_summary(runtime=active_runtime, audit_logger=audit_logger),
        "not_included": _not_included(),
    }
    _audit_privacy(
        audit_logger or AuditLogger(active_runtime.audit_log_path),
        "privacy.export",
        "privacy export generated with redaction",
        files_read=[],
        risk_level=RiskLevel.LOW,
    )
    return _redact(report)


def privacy_delete_memory(
    broker: ToolBroker,
    *,
    scope: str = "default",
    confirm: str = "",
    audit_logger: AuditLogger | None = None,
) -> dict[str, Any]:
    logger = audit_logger or broker.audit_logger
    if confirm != CONFIRM_DELETE_MEMORY:
        _audit_privacy(
            logger,
            "privacy.delete_memory",
            "memory deletion denied: confirmation missing",
            policy_decision=PolicyDecision.DENY,
            risk_level=RiskLevel.MEDIUM,
            sanitized_args={"scope": scope, "confirmed": False},
        )
        return {
            "status": "error",
            "deleted": False,
            "error": f"confirmation required; rerun with --confirm {CONFIRM_DELETE_MEMORY}",
            "scope": scope,
        }
    _audit_privacy(
        logger,
        "privacy.delete_memory",
        "memory deletion requested",
        risk_level=RiskLevel.MEDIUM,
        sanitized_args={"scope": scope, "confirmed": True},
    )
    result = broker.execute(
        {
            "id": "privacy_delete_memory",
            "type": "function",
            "function": {"name": "memory.clear", "arguments": json.dumps({"scope": scope})},
        }
    )
    try:
        payload = json.loads(result.content)
    except json.JSONDecodeError:
        payload = {"error": "invalid memory.clear response"}
    return {
        "status": "ok" if result.allowed else "error",
        "deleted": bool(result.allowed),
        "scope": scope,
        "memory_result": payload,
        "toolbroker_path": "memory.clear",
        "allowed": result.allowed,
        "deletion_limits": payload.get("deletion_limits") if isinstance(payload, dict) else None,
    }


def privacy_audit_summary(
    *,
    runtime: RuntimeConfig | None = None,
    audit_logger: AuditLogger | None = None,
    limit: int = 5000,
) -> dict[str, Any]:
    active_runtime = runtime or RuntimeConfig.from_env()
    path = Path(active_runtime.audit_log_path)
    summary = _audit_summary(path, limit=limit)
    _audit_privacy(
        audit_logger or AuditLogger(active_runtime.audit_log_path),
        "privacy.audit_summary",
        "privacy audit summary generated",
        risk_level=RiskLevel.SAFE,
    )
    return summary


def privacy_permissions(
    *,
    runtime: RuntimeConfig | None = None,
    audit_logger: AuditLogger | None = None,
) -> dict[str, Any]:
    active_runtime = runtime or RuntimeConfig.from_env()
    capabilities = load_capabilities_config(active_runtime.capabilities_path)
    report = {
        "status": "ok",
        "permission_grants": PermissionStore().show(),
        "personal_data_capabilities": _personal_capabilities(capabilities),
        "high_risk_capabilities": _capabilities_by_risk(capabilities, RiskLevel.HIGH.value),
        "critical_capabilities": _capabilities_by_risk(capabilities, RiskLevel.CRITICAL.value),
        "critical_approval_rule": "per_action; approval reuse is not allowed",
        "personal_connector_reads_performed": False,
    }
    _audit_privacy(
        audit_logger or AuditLogger(active_runtime.audit_log_path),
        "privacy.permissions",
        "privacy permissions summary generated",
    )
    return _redact(report)


def format_privacy_json(report: dict[str, Any]) -> str:
    return json.dumps(_redact(report), indent=2, sort_keys=True)


def _connector_statuses(runtime: RuntimeConfig) -> list[dict[str, Any]]:
    return default_connector_registry().list_statuses(
        load_capabilities_config(runtime.capabilities_path),
        audit_path=runtime.audit_log_path,
        include_health=False,
    )


def _connector_overview(runtime: RuntimeConfig) -> dict[str, Any]:
    statuses = _connector_statuses(runtime)
    personal_capabilities = _personal_capabilities(load_capabilities_config(runtime.capabilities_path))
    personal_read_capabilities = [
        item
        for item in personal_capabilities
        if item.get("connector_name") in PERSONAL_CONNECTORS or item.get("capability") in PERSONAL_BROWSER_CAPABILITIES
    ]
    approval_sensitive_capabilities = [
        item
        for item in personal_capabilities
        if (
            item.get("connector_name") in PERSONAL_CONNECTORS
            or item.get("capability") in PERSONAL_BROWSER_CAPABILITIES
            or item.get("capability") in PERSONAL_MEMORY_CAPABILITIES
            or item.get("risk_level") in {RiskLevel.HIGH.value, RiskLevel.CRITICAL.value}
            or item.get("default_enabled") is False
        )
    ]
    return {
        "enabled": sorted(str(item.get("name")) for item in statuses if item.get("enabled")),
        "disabled": sorted(str(item.get("name")) for item in statuses if not item.get("enabled")),
        "personal_connector_reads_disabled_by_default": not any(
            item.get("default_enabled") for item in personal_read_capabilities
        ),
        "personal_data_capabilities_requiring_approval": all(
            item.get("approval_required") is True or item.get("approval_required") == "per_action"
            for item in approval_sensitive_capabilities
        ),
    }


def _personal_capabilities(capabilities: Mapping[str, Any]) -> list[dict[str, Any]]:
    tools = capabilities.get("tools", {})
    rows: list[dict[str, Any]] = []
    for name, entry in sorted(tools.items()):
        if not isinstance(entry, Mapping):
            continue
        connector = str(entry.get("connector_name", ""))
        trust = str(entry.get("trust_level", ""))
        risk = str(entry.get("risk_level", ""))
        is_personal = _is_personal_data_capability(str(name), connector, trust, entry)
        if not is_personal:
            continue
        rows.append(
            {
                "capability": str(name),
                "tool_name": entry.get("tool_name"),
                "connector_name": connector,
                "risk_level": risk,
                "trust_level": trust,
                "default_enabled": bool(entry.get("default_enabled")),
                "approval_required": entry.get("approval_required"),
                "approval_reuse_allowed": entry.get("approval_reuse_allowed"),
                "memory_behavior": entry.get("memory_behavior"),
                "docs_reference": entry.get("docs_reference"),
            }
        )
    return rows


def _is_personal_data_capability(capability: str, connector: str, trust: str, entry: Mapping[str, Any] | None = None) -> bool:
    if capability.startswith("lead.") and not _is_personal_lead_capability(capability, entry or {}):
        return False
    if connector in {"messaging_handoff", "messaging_inbound"}:
        return False
    if capability in PERSONAL_BROWSER_CAPABILITIES or capability in PERSONAL_MEMORY_CAPABILITIES:
        return True
    if connector in PERSONAL_CONNECTORS:
        return True
    return trust in {TrustLevel.UNTRUSTED_EMAIL.value, TrustLevel.UNTRUSTED_MESSAGE.value}


def _is_personal_lead_capability(capability: str, entry: Mapping[str, Any]) -> bool:
    if capability in {"lead.inbox.read_selected", "lead.send_approved"}:
        return True
    return bool(entry.get("personal_data_provider", False))


def _capabilities_by_risk(capabilities: Mapping[str, Any], risk_level: str) -> list[dict[str, Any]]:
    return [
        {
            "capability": str(name),
            "connector_name": entry.get("connector_name"),
            "default_enabled": bool(entry.get("default_enabled")),
            "approval_required": entry.get("approval_required"),
            "approval_reuse_allowed": entry.get("approval_reuse_allowed"),
        }
        for name, entry in sorted(capabilities.get("tools", {}).items())
        if isinstance(entry, Mapping) and str(entry.get("risk_level")) == risk_level
    ]


def _memory_path(project_root: str | Path) -> Path:
    return Path(project_root) / "data" / "memory.sqlite3"


def _memory_counts(path: str | Path) -> dict[str, Any]:
    memory_path = Path(path)
    if not memory_path.exists():
        return {"path": str(memory_path), "exists": False, "total_records": 0, "by_category": {}, "by_scope": {}, "contents_returned": False}
    try:
        with sqlite3.connect(memory_path) as conn:
            rows = conn.execute("SELECT category, scope, source_trust FROM memories").fetchall()
    except sqlite3.Error as exc:
        return {"path": str(memory_path), "exists": True, "error": str(exc), "total_records": 0, "by_category": {}, "by_scope": {}, "contents_returned": False}
    return {
        "path": str(memory_path),
        "exists": True,
        "size_bytes": _file_size(memory_path),
        "total_records": len(rows),
        "by_category": dict(sorted(Counter(str(row[0]) for row in rows).items())),
        "by_scope": dict(sorted(Counter(str(row[1]) for row in rows).items())),
        "by_source_trust": dict(sorted(Counter(str(row[2]) for row in rows).items())),
        "contents_returned": False,
    }


def _memory_export_preview(path: str | Path) -> dict[str, Any]:
    memory_path = Path(path)
    if not memory_path.exists():
        return {"path": str(memory_path), "records": [], "content_mode": "none"}
    records = []
    try:
        with sqlite3.connect(memory_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT id, category, scope, content, source_trust, metadata_json, created_at FROM memories ORDER BY created_at DESC"
            ).fetchall()
    except sqlite3.Error as exc:
        return {"path": str(memory_path), "records": [], "error": str(exc), "content_mode": "redacted_preview"}
    redactor = SecretRedactor()
    for row in rows:
        content = redactor.redact_text(str(row["content"]))
        records.append(
            {
                "id": row["id"],
                "category": row["category"],
                "scope": row["scope"],
                "source_trust": row["source_trust"],
                "created_at": row["created_at"],
                "content_preview": _preview(content),
                "metadata": redactor.redact(_json_object(row["metadata_json"])),
            }
        )
    return {"path": str(memory_path), "records": records, "content_mode": "redacted_preview"}


def _capture_counts(project_root: str | Path) -> dict[str, Any]:
    capture_dir = Path(project_root) / "workspace" / "captures"
    if not capture_dir.exists():
        return {"path": str(capture_dir), "exists": False, "total_captures": 0, "by_source_type": {}, "by_source_trust": {}}
    by_source_type: Counter[str] = Counter()
    by_source_trust: Counter[str] = Counter()
    unreadable = 0
    for path in capture_dir.glob("*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            unreadable += 1
            continue
        if isinstance(payload, Mapping):
            by_source_type[str(payload.get("source_type", "unknown"))] += 1
            by_source_trust[str(payload.get("source_trust", "unknown"))] += 1
    total = sum(by_source_type.values()) + unreadable
    return {
        "path": str(capture_dir),
        "exists": True,
        "total_captures": total,
        "by_source_type": dict(sorted(by_source_type.items())),
        "by_source_trust": dict(sorted(by_source_trust.items())),
        "unreadable_files": unreadable,
        "contents_returned": False,
    }


def _capture_export_preview(project_root: str | Path) -> dict[str, Any]:
    capture_dir = Path(project_root) / "workspace" / "captures"
    if not capture_dir.exists():
        return {"path": str(capture_dir), "records": [], "content_mode": "none"}
    redactor = SecretRedactor()
    records = []
    for path in sorted(capture_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(payload, Mapping):
            continue
        content = redactor.redact_text(str(payload.get("content", "")))
        records.append(
            {
                "id": payload.get("id"),
                "created_at": payload.get("created_at"),
                "title": redactor.redact(payload.get("title")),
                "source_type": payload.get("source_type"),
                "source_ref": redactor.redact(payload.get("source_ref")),
                "source_trust": payload.get("source_trust"),
                "stored_in_memory": bool(payload.get("stored_in_memory")),
                "content_preview": _preview(content),
            }
        )
    return {"path": str(capture_dir), "records": records, "content_mode": "redacted_preview"}


def _audit_metadata(path: str | Path) -> dict[str, Any]:
    audit_path = Path(path)
    return {
        "path": str(audit_path),
        "exists": audit_path.exists(),
        "size_bytes": _file_size(audit_path),
        "line_count": _line_count(audit_path),
    }


def _audit_summary(path: Path, *, limit: int) -> dict[str, Any]:
    counters = {
        "by_policy_decision": Counter(),
        "by_approval_result": Counter(),
        "by_risk_level": Counter(),
        "by_tool_group": Counter(),
    }
    first_timestamp = None
    last_timestamp = None
    total = 0
    if path.exists():
        try:
            lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()][-limit:]
        except OSError:
            lines = []
        for line in lines:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            total += 1
            first_timestamp = first_timestamp or event.get("timestamp")
            last_timestamp = event.get("timestamp") or last_timestamp
            counters["by_policy_decision"][str(event.get("policy_decision", "unknown"))] += 1
            counters["by_approval_result"][str(event.get("approval_result", "unknown"))] += 1
            counters["by_risk_level"][str(event.get("risk_level", "unknown"))] += 1
            tool_name = str(event.get("tool_name", "unknown"))
            counters["by_tool_group"][tool_name.split(".", 1)[0]] += 1
    return {
        "status": "ok",
        "path": str(path),
        "size_bytes": _file_size(path),
        "events_considered": total,
        "first_timestamp": first_timestamp,
        "last_timestamp": last_timestamp,
        "by_policy_decision": dict(sorted(counters["by_policy_decision"].items())),
        "by_approval_result": dict(sorted(counters["by_approval_result"].items())),
        "by_risk_level": dict(sorted(counters["by_risk_level"].items())),
        "by_tool_group": dict(sorted(counters["by_tool_group"].items())),
        "raw_args_returned": False,
    }


def _cache_inventory(project_root: str | Path) -> dict[str, Any]:
    weather_path = Path(project_root) / "data" / "weather_cache.json"
    return {
        "weather": _json_cache_state(weather_path),
        "web": {"configured": False, "entries": 0, "note": "No durable web cache is configured in v1."},
    }


def _json_cache_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "exists": False, "entries": 0}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"path": str(path), "exists": True, "entries": 0, "state": "unreadable", "size_bytes": _file_size(path)}
    entries = len(payload) if isinstance(payload, Mapping) else 0
    return {"path": str(path), "exists": True, "entries": entries, "size_bytes": _file_size(path), "contents_returned": False}


def _pending_personal_actions_count() -> int:
    return len(_pending_personal_actions())


def _pending_personal_actions() -> list[dict[str, Any]]:
    rows = []
    for record in ActionCenterStore().list():
        if record.status.value not in {"pending", "approved"}:
            continue
        if _action_has_personal_data(record):
            rows.append(
                {
                    "action_id": record.action_id,
                    "status": record.status.value,
                    "action_type": record.action_type,
                    "risk_level": record.risk_level.value,
                    "trust_level": record.trust_level.value,
                    "source_workflow": record.source_workflow,
                    "preview_summary": _preview(str(record.preview.get("summary", ""))),
                    "exact_preview_available_locally": True,
                }
            )
    return rows


def _action_has_personal_data(record: ActionRecord) -> bool:
    return (
        record.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}
        or record.trust_level
        in {
            TrustLevel.LOCAL_PRIVATE_DATA,
            TrustLevel.UNTRUSTED_EMAIL,
            TrustLevel.UNTRUSTED_MESSAGE,
        }
    )


def _approval_counts() -> dict[str, Any]:
    requests = ApprovalStore().list()
    by_status = Counter(request.status.value for request in requests)
    by_risk = Counter(request.risk_level.value for request in requests)
    return {
        "total": len(requests),
        "by_status": dict(sorted(by_status.items())),
        "by_risk_level": dict(sorted(by_risk.items())),
        "granted": by_status.get(ApprovalStatus.APPROVED.value, 0),
        "denied": by_status.get(ApprovalStatus.DENIED.value, 0),
    }


def _approval_export(request: ApprovalRequest) -> dict[str, Any]:
    redactor = SecretRedactor()
    return redactor.redact(
        {
            "request_id": request.request_id,
            "timestamp": request.timestamp,
            "capability": request.capability,
            "tool_name": request.tool_name,
            "risk_level": request.risk_level.value,
            "trust_level": request.trust_level.value,
            "summary": request.summary,
            "per_action": request.per_action,
            "status": request.status.value,
            "expires_at": request.expires_at,
            "args_preview": request.args_preview,
        }
    )


def _permissions_summary() -> dict[str, Any]:
    grants = PermissionStore().show()
    return {"grants": grants, "grant_count": len(grants)}


def _deletion_options() -> list[dict[str, str]]:
    return [
        {"command": "python smart_agent.py privacy delete-memory --confirm DELETE-MEMORY", "description": "Clear local memory scope through brokered memory.clear."},
        {"command": "python smart_agent.py memory delete <id>", "description": "Delete a single memory record through brokered memory.delete."},
        {"command": "python smart_agent.py weather cache clear", "description": "Clear operational weather cache."},
        {"command": "python smart_agent.py actions clear-denied", "description": "Clear denied Action Center records only."},
    ]


def _not_included() -> list[str]:
    return [
        "No personal connector data is read to build this report.",
        "Calendar, contacts, email, messages, and task contents are not inventoried unless already present in local agent stores.",
        "Secrets and private app databases are not read.",
        "Audit logs are summarized; raw sanitized arguments are not returned by audit-summary.",
        "Filesystem backups and external app/provider records are not deleted by privacy delete-memory.",
    ]


def _privacy_notes() -> list[str]:
    return [
        "Privacy Center uses metadata/status only for connector inventory.",
        "Use privacy export for a redacted local export preview.",
        "Delete operations require explicit confirmation and keep audit history intact.",
    ]


def _file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def _line_count(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    except OSError:
        return 0


def _json_object(raw: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _preview(text: str, *, max_chars: int = 160) -> str:
    collapsed = " ".join(text.split())
    if len(collapsed) <= max_chars:
        return collapsed
    return collapsed[: max_chars - 3].rstrip() + "..."


def _redact(value: Any) -> Any:
    return SecretRedactor().redact(value)


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _audit_privacy(
    audit_logger: AuditLogger,
    capability: str,
    summary: str,
    *,
    files_read: list[str] | None = None,
    policy_decision: PolicyDecision = PolicyDecision.ALLOW,
    risk_level: RiskLevel = RiskLevel.SAFE,
    sanitized_args: dict[str, Any] | None = None,
) -> None:
    audit_logger.log(
        AuditEvent(
            session_id="privacy-center",
            request_id=new_request_id(),
            route="privacy_center",
            model="local-cli",
            tool_name=capability,
            capability=capability,
            risk_level=risk_level.value,
            trust_level=TrustLevel.LOCAL_PRIVATE_DATA.value,
            policy_decision=policy_decision.value,
            approval_result="not_required",
            sanitized_args=sanitized_args or {},
            result_summary=summary,
            files_read=files_read or [],
        )
    )
