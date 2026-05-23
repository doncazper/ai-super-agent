from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from agent.config.loader import load_capabilities_config
from agent.connectors.errors import UnknownConnectorError
from agent.connectors.health import connectors_health_report
from agent.connectors.registry import default_connector_registry
from agent.connectors.status import format_status_json


CONNECTOR_NAMES = tuple(default_connector_registry().names())


def list_connectors(config: Mapping[str, Any] | None = None, *, environ: Mapping[str, str] | None = None) -> list[dict[str, Any]]:
    registry = default_connector_registry()
    return registry.list_statuses(config or load_capabilities_config(), environ=environ)


def connectors_doctor(
    config: Mapping[str, Any] | None = None,
    *,
    audit_path: str | Path = "logs/audit.jsonl",
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    return connectors_health_report(config or load_capabilities_config(), audit_path=audit_path, environ=environ)


def connector_status(
    connector: str,
    config: Mapping[str, Any] | None = None,
    *,
    audit_path: str | Path = "logs/audit.jsonl",
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    registry = default_connector_registry()
    try:
        return registry.status(connector, config or load_capabilities_config(), audit_path=audit_path, environ=environ)
    except UnknownConnectorError as exc:
        raise ValueError(str(exc)) from exc


def format_connectors_json(value: Any) -> str:
    return format_status_json(value)
