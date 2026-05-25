from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from agent.config.runtime import env_bool
from agent.connectors.base import ConnectorDefinition, ConnectorStatus
from agent.safety.policy import RiskLevel


RISK_ORDER = {
    "SAFE": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
    "FORBIDDEN": 5,
}
SECRET_KEY_MARKERS = ("password", "secret", "token", "api_key", "apikey", "access_key", "private_key")
NON_SECRET_STATUS_KEYS = {
    "api_key_configured",
    "requires_api_key",
    "credentials_configured",
    "token_configured",
    "optional_token_supported",
}


def build_connector_status(
    definition: ConnectorDefinition,
    config: Mapping[str, Any],
    *,
    audit_path: str | Path = "logs/audit.jsonl",
    environ: Mapping[str, str],
    include_health: bool = False,
) -> ConnectorStatus:
    capabilities = definition.capability_entries(config)
    configuration = definition.configuration_probe(environ)
    enabled = _connector_enabled(capabilities, environ)
    last_success, last_error = _audit_status(definition.name, audit_path)
    health = None
    if include_health and definition.health_probe is not None:
        if definition.personal_data and definition.health_accesses_personal_data:
            health = None
        else:
            health = definition.health_probe(environ)
    cache_state: str | dict[str, Any] = "not_applicable"
    if definition.cache_probe is not None:
        cache_state = definition.cache_probe(environ)
    return ConnectorStatus(
        name=definition.name,
        configured=configuration.configured,
        enabled=enabled,
        default_provider=configuration.provider_name,
        risk_level=_max_risk(capabilities),
        approval_required=_approval_required(capabilities),
        last_successful_call=last_success,
        last_error=last_error,
        rate_limit_state=_rate_limit_state(capabilities),
        cache_state=cache_state,
        docs_setup_hint=configuration.setup_hint or definition.setup_docs,
        status="ok" if configuration.configured and enabled else "not_configured",
        health=health,
        capabilities=_capability_statuses(capabilities),
        metadata=_redact(configuration.metadata),
    )


def format_status_json(value: Any) -> str:
    return json.dumps(_redact(value), indent=2, sort_keys=True)


def _connector_enabled(capabilities: Mapping[str, Mapping[str, Any]], env: Mapping[str, str]) -> bool:
    if not capabilities:
        return False
    enabled = any(bool(entry.get("default_enabled")) for entry in capabilities.values())
    requires_web = any(bool(entry.get("requires_web_access")) for entry in capabilities.values())
    web_disabled = _env(env, "WEB_ACCESS_ENABLED", "true").strip().casefold() in {"0", "false", "no", "off"}
    if requires_web and web_disabled:
        return False
    return enabled


def _max_risk(capabilities: Mapping[str, Mapping[str, Any]]) -> str:
    risks = [str(entry.get("risk_level", RiskLevel.FORBIDDEN.value)) for entry in capabilities.values()]
    if not risks:
        return RiskLevel.FORBIDDEN.value
    return max(risks, key=lambda risk: RISK_ORDER.get(risk, 99))


def _approval_required(capabilities: Mapping[str, Mapping[str, Any]]) -> bool | str:
    requirements = [entry.get("approval_required", False) for entry in capabilities.values()]
    if "per_action" in requirements:
        return "per_action"
    return any(requirement is True for requirement in requirements)


def _rate_limit_state(capabilities: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    limits = {
        name: entry["rate_limit"]
        for name, entry in capabilities.items()
        if isinstance(entry.get("rate_limit"), Mapping)
    }
    return {"configured": bool(limits), "limits": limits}


def _capability_statuses(capabilities: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "risk_level": str(entry.get("risk_level", RiskLevel.FORBIDDEN.value)),
            "trust_level": str(entry.get("trust_level", "")),
            "default_enabled": bool(entry.get("default_enabled")),
            "approval_required": entry.get("approval_required", False),
            "memory_behavior": entry.get("memory_behavior"),
            "docs_reference": entry.get("docs_reference"),
        }
        for name, entry in sorted(capabilities.items())
    ]


def _audit_status(connector: str, audit_path: str | Path) -> tuple[str | None, str | None]:
    path = Path(audit_path)
    if not path.exists():
        return None, None
    last_success: str | None = None
    last_error: str | None = None
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None, "audit log unreadable"
    for line in lines[-1000:]:
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        tool_name = str(event.get("tool_name", ""))
        if not tool_name.startswith(f"{connector}."):
            continue
        timestamp = str(event.get("timestamp", ""))
        summary = str(event.get("result_summary", ""))
        if event.get("policy_decision") == "ALLOW" and summary == "Tool executed successfully.":
            last_success = timestamp
        elif _is_error_summary(event, summary):
            last_error = f"{timestamp}: {summary}"
    return last_success, last_error


def _is_error_summary(event: Mapping[str, Any], summary: str) -> bool:
    if event.get("policy_decision") == "DENY":
        return True
    lowered = summary.casefold()
    return "failed" in lowered or "error" in lowered


def _env(env: Mapping[str, str], key: str, default: str = "") -> str:
    return env.get(key, default) or default


def _redact(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: (_redact_secret_value(key, item) if _is_secret_key(key) else _redact(item))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def _is_secret_key(key: object) -> bool:
    normalized = str(key).lower()
    if normalized in NON_SECRET_STATUS_KEYS:
        return False
    return any(marker in normalized for marker in SECRET_KEY_MARKERS)


def _redact_secret_value(key: object, value: Any) -> Any:
    if str(key).lower() in NON_SECRET_STATUS_KEYS:
        return _redact(value)
    if value in {None, "", False}:
        return value
    return "[REDACTED]"
