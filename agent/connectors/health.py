from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from agent.config.loader import load_capabilities_config
from agent.connectors.registry import ConnectorRegistry, default_connector_registry


def connector_health(
    name: str,
    config: Mapping[str, Any] | None = None,
    *,
    audit_path: str | Path = "logs/audit.jsonl",
    registry: ConnectorRegistry | None = None,
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    active_registry = registry or default_connector_registry()
    return active_registry.status(
        name,
        config or load_capabilities_config(),
        audit_path=audit_path,
        environ=environ,
        include_health=True,
    )


def connectors_health_report(
    config: Mapping[str, Any] | None = None,
    *,
    audit_path: str | Path = "logs/audit.jsonl",
    registry: ConnectorRegistry | None = None,
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    active_registry = registry or default_connector_registry()
    statuses = active_registry.list_statuses(
        config or load_capabilities_config(),
        audit_path=audit_path,
        environ=environ,
        include_health=True,
    )
    return {
        "status": "ok" if all(status["status"] in {"ok", "not_configured"} for status in statuses) else "warn",
        "connectors": statuses,
    }
