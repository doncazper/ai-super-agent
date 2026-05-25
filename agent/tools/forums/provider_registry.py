from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from agent.forums.provider_status import (
    provider_capabilities_report,
    provider_doctor_report,
    provider_status_report,
    providers_report,
)
from agent.forums.registry import default_forum_provider_registry


def _schema(name: str, description: str, properties: dict[str, Any] | None = None, required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties or {},
                "required": required or [],
                "additionalProperties": False,
            },
        },
    }


_PROVIDER_PROPERTIES = {"provider": {"type": "string"}}

FORUM_PROVIDER_SCHEMAS = {
    "forums.providers": _schema(
        "forums.providers",
        "List forum provider registry metadata without network, login, or personal-data reads.",
    ),
    "forums.status": _schema(
        "forums.status",
        "Show one forum provider status without provider API calls, login reads, or personal-data access.",
        _PROVIDER_PROPERTIES,
        ["provider"],
    ),
    "forums.doctor": _schema(
        "forums.doctor",
        "Run forum provider registry diagnostics without fetching forum content or touching logged-in accounts.",
    ),
    "forums.capabilities": _schema(
        "forums.capabilities",
        "Show read/write capability metadata for a forum provider without executing provider actions.",
        _PROVIDER_PROPERTIES,
        ["provider"],
    ),
}


def _with_audit(payload: dict[str, Any], summary: str) -> dict[str, Any]:
    payload["_audit"] = {"network_domains": [], "result_summary": summary}
    return payload


def make_forum_provider_tools(project_root: str | Path = ".") -> dict[str, Callable[..., dict[str, Any]]]:
    _ = Path(project_root)
    registry = default_forum_provider_registry()

    def providers() -> dict[str, Any]:
        payload = providers_report(registry)
        return _with_audit(payload, f"Listed {payload['provider_count']} forum providers without network calls.")

    def status(provider: str) -> dict[str, Any]:
        payload = provider_status_report(provider, registry)
        return _with_audit(payload, f"Checked forum provider status for {payload['provider_id']} without network calls.")

    def doctor() -> dict[str, Any]:
        payload = provider_doctor_report(registry)
        return _with_audit(payload, f"Forum provider doctor checked {payload['provider_count']} providers without network calls.")

    def capabilities(provider: str) -> dict[str, Any]:
        payload = provider_capabilities_report(provider, registry)
        return _with_audit(payload, f"Listed forum provider capabilities for {payload['provider_id']} without execution.")

    return {
        "forums.providers": providers,
        "forums.status": status,
        "forums.doctor": doctor,
        "forums.capabilities": capabilities,
    }
