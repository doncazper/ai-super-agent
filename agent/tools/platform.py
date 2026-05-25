from __future__ import annotations

from typing import Any, Callable

from agent.platforms.doctor import (
    build_platform_doctor,
    build_platform_matrix,
    build_platform_status,
    explain_platform_capability,
    list_platform_capabilities,
)


def _schema(
    name: str,
    description: str,
    properties: dict[str, Any] | None = None,
    required: list[str] | None = None,
) -> dict[str, Any]:
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


PLATFORM_SCHEMAS: dict[str, dict[str, Any]] = {
    "platform.doctor": _schema(
        "platform.doctor",
        "Run read-only platform diagnostics without native imports, permission prompts, personal-data reads, or bridge actions.",
    ),
    "platform.status": _schema(
        "platform.status",
        "Show short read-only platform and bridge status metadata.",
    ),
    "platform.capabilities": _schema(
        "platform.capabilities",
        "List platform capability metadata without executing platform actions.",
    ),
    "platform.matrix": _schema(
        "platform.matrix",
        "Show a read-only platform capability matrix for macOS, iOS companion, Windows, and app/web bridge planning.",
    ),
    "platform.explain": _schema(
        "platform.explain",
        "Explain one platform capability record, including risk, trust, approval, defaults, docs, and setup hint.",
        {"capability_id": {"type": "string"}},
        ["capability_id"],
    ),
}


def _with_audit(payload: dict[str, Any], summary: str) -> dict[str, Any]:
    payload["_audit"] = {
        "files_read": [],
        "files_written": [],
        "commands_run": [],
        "network_domains": [],
        "result_summary": summary,
    }
    return payload


def make_platform_tools() -> dict[str, Callable[..., dict[str, Any]]]:
    def doctor() -> dict[str, Any]:
        payload = build_platform_doctor()
        return _with_audit(payload, "Ran platform doctor metadata checks without platform actions.")

    def status() -> dict[str, Any]:
        payload = build_platform_status()
        return _with_audit(payload, "Read platform status metadata without platform actions.")

    def capabilities() -> dict[str, Any]:
        payload = list_platform_capabilities()
        return _with_audit(payload, f"Listed {payload['capability_count']} platform capability records.")

    def matrix() -> dict[str, Any]:
        payload = build_platform_matrix()
        return _with_audit(payload, "Built platform capability matrix from static metadata.")

    def explain(capability_id: str) -> dict[str, Any]:
        payload = explain_platform_capability(capability_id)
        return _with_audit(payload, f"Explained platform capability {capability_id!r}.")

    return {
        "platform.doctor": doctor,
        "platform.status": status,
        "platform.capabilities": capabilities,
        "platform.matrix": matrix,
        "platform.explain": explain,
    }
