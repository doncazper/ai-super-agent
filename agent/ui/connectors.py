from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

from agent.config.loader import load_capabilities_config
from agent.safety.policy import RiskLevel
from agent.tools.weather.provider import weather_provider_status


CONNECTOR_NAMES = ("weather", "web", "calendar", "contacts", "email", "messages")
RISK_ORDER = {
    "SAFE": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
    "FORBIDDEN": 5,
}
SECRET_KEY_MARKERS = ("password", "secret", "token", "api_key", "apikey", "access_key", "private_key")
NON_SECRET_STATUS_KEYS = {"api_key_configured", "requires_api_key"}


def list_connectors(config: Mapping[str, Any] | None = None, *, environ: Mapping[str, str] | None = None) -> list[dict[str, Any]]:
    return [connector_status(name, config=config, environ=environ) for name in CONNECTOR_NAMES]


def connectors_doctor(
    config: Mapping[str, Any] | None = None,
    *,
    audit_path: str | Path = "logs/audit.jsonl",
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    statuses = [
        connector_status(name, config=config, audit_path=audit_path, environ=environ)
        for name in CONNECTOR_NAMES
    ]
    return {
        "status": "ok" if all(status["status"] in {"ok", "not_configured"} for status in statuses) else "warn",
        "connectors": statuses,
    }


def connector_status(
    connector: str,
    config: Mapping[str, Any] | None = None,
    *,
    audit_path: str | Path = "logs/audit.jsonl",
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    if connector not in CONNECTOR_NAMES:
        raise ValueError(f"unknown connector: {connector}")
    env = environ or os.environ
    config_data = config or load_capabilities_config()
    capabilities = _connector_capabilities(connector, config_data)
    configured, provider, setup_hint, extra = _configuration(connector, env)
    enabled = _connector_enabled(capabilities, env)
    last_success, last_error = _audit_status(connector, audit_path)
    risk_level = _max_risk(capabilities)
    return {
        "name": connector,
        "configured": configured,
        "enabled": enabled,
        "default_provider": provider,
        "risk_level": risk_level,
        "approval_required": _approval_required(capabilities),
        "last_successful_call": last_success,
        "last_error": last_error,
        "rate_limit_state": _rate_limit_state(capabilities),
        "cache_state": "not_applicable",
        "docs_setup_hint": setup_hint,
        "status": "ok" if configured and enabled else "not_configured",
        **extra,
    }


def format_connectors_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True)


def _connector_capabilities(connector: str, config: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    tools = config.get("tools", {})
    if not isinstance(tools, Mapping):
        return {}
    prefixes = {
        "weather": ("weather.",),
        "web": ("web.",),
        "calendar": ("calendar.",),
        "contacts": ("contacts.",),
        "email": ("email.",),
        "messages": ("messages.",),
    }[connector]
    return {
        name: entry
        for name, entry in tools.items()
        if isinstance(name, str) and name.startswith(prefixes) and isinstance(entry, Mapping)
    }


def _configuration(connector: str, env: Mapping[str, str]) -> tuple[bool, str, str, dict[str, Any]]:
    if connector == "weather":
        status = weather_provider_status()
        return (
            bool(status["configured"]),
            str(status["provider"]),
            "Set WEATHER_PROVIDER=open-meteo for no-key weather lookups.",
            {"provider_status": _redact(status)},
        )
    if connector == "web":
        provider = _env(env, "WEB_SEARCH_PROVIDER") or ("brave" if _env(env, "BRAVE_SEARCH_API_KEY") else "disabled")
        configured = provider == "brave" and bool(_env(env, "BRAVE_SEARCH_API_KEY"))
        hint = "Set WEB_SEARCH_PROVIDER=brave and BRAVE_SEARCH_API_KEY, or leave disabled."
        if provider not in {"disabled", "brave"}:
            hint = "Configured web search provider is not supported by this build."
        return configured, provider, hint, {}
    if connector == "calendar":
        provider = _env(env, "CALENDAR_CONNECTOR") or "disabled"
        return provider != "disabled", provider, "Set CALENDAR_CONNECTOR=applescript only after approving read-only calendar setup.", {}
    if connector == "contacts":
        provider = _env(env, "CONTACTS_CONNECTOR") or "disabled"
        return provider != "disabled", provider, "Set CONTACTS_CONNECTOR=applescript only after approving read-only contacts setup.", {}
    if connector == "email":
        provider = _env(env, "EMAIL_CONNECTOR") or "disabled"
        configured = provider == "imap" and all(_env(env, key) for key in ("IMAP_HOST", "IMAP_USERNAME", "IMAP_PASSWORD"))
        hint = "Set EMAIL_CONNECTOR=imap with IMAP_HOST, IMAP_USERNAME, and IMAP_PASSWORD via environment or external secret setup."
        return configured, provider, hint, {}
    if connector == "messages":
        provider = _env(env, "MESSAGES_CONNECTOR") or "disabled"
        return False if provider == "disabled" else True, provider, "Messages live connector is intentionally unavailable until a safe permissioned path exists.", {}
    raise ValueError(f"unknown connector: {connector}")


def _connector_enabled(capabilities: Mapping[str, Mapping[str, Any]], env: Mapping[str, str]) -> bool:
    if not capabilities:
        return False
    enabled = any(bool(entry.get("default_enabled")) for entry in capabilities.values())
    requires_web = any(bool(entry.get("requires_web_access")) for entry in capabilities.values())
    if requires_web and _env(env, "WEB_ACCESS_ENABLED", "true").strip().casefold() in {"0", "false", "no", "off"}:
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
