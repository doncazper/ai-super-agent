from __future__ import annotations

from typing import Any, Callable

from agent.sandbox.errors import UnknownSandboxBackendError
from agent.sandbox.models import SandboxRequest
from agent.sandbox.policy import sandbox_policy_summary
from agent.sandbox.registry import SandboxBackendRegistry, default_sandbox_registry
from agent.tools.errors import ToolError


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


SANDBOX_SCHEMAS: dict[str, dict[str, Any]] = {
    "sandbox.backends": _schema(
        "sandbox.backends",
        "List sandbox backend metadata without installing runtimes, starting sandboxes, or executing commands.",
    ),
    "sandbox.policy": _schema(
        "sandbox.policy",
        "Show sandbox safety policy and disabled-by-default execution boundaries.",
    ),
    "sandbox.dry_run": _schema(
        "sandbox.dry_run",
        "Validate a sandbox request without executing commands, using network, or reading personal data.",
        {
            "backend_id": {"type": "string"},
            "task_type": {"type": "string"},
            "risk_level": {"type": "string"},
            "network_allowed": {"type": "boolean"},
            "filesystem_roots": {"type": "array", "items": {"type": "string"}},
            "time_limit_seconds": {"type": "integer"},
            "memory_limit_mb": {"type": "integer"},
            "command_allowlist": {"type": "array", "items": {"type": "string"}},
            "personal_data_allowed": {"type": "boolean"},
            "audit_required": {"type": "boolean"},
            "command": {"type": "string"},
        },
        [],
    ),
}


def make_sandbox_tools(registry: SandboxBackendRegistry | None = None) -> dict[str, Callable[..., dict[str, Any]]]:
    backend_registry = registry or default_sandbox_registry()

    def backends() -> dict[str, Any]:
        records = [backend.to_dict() for backend in backend_registry.list_backends()]
        return _with_audit(
            {
                "status": "ok",
                "default_backend": "mock",
                "backend_count": len(records),
                "backends": records,
                "execution_enabled": False,
                "network_default": False,
                "personal_data_default": False,
            },
            f"Listed {len(records)} sandbox backend metadata records without starting a sandbox.",
        )

    def policy() -> dict[str, Any]:
        return _with_audit(
            sandbox_policy_summary(),
            "Read sandbox policy metadata without starting a sandbox or executing commands.",
        )

    def dry_run(**kwargs: Any) -> dict[str, Any]:
        backend_id = str(kwargs.pop("backend_id", "mock") or "mock")
        try:
            backend = backend_registry.get(backend_id)
        except UnknownSandboxBackendError as exc:
            raise ToolError(str(exc)) from exc
        request = SandboxRequest(sandbox_id=backend_id, **_request_kwargs(kwargs))
        result = backend.dry_run(request).to_dict()
        return _with_audit(
            {
                **result,
                "toolbroker_required": True,
                "policyengine_required": True,
                "command_executed": False,
            },
            f"Sandbox dry-run evaluated for backend={backend_id}; allowed={result.get('allowed')}.",
        )

    return {
        "sandbox.backends": backends,
        "sandbox.policy": policy,
        "sandbox.dry_run": dry_run,
    }


def _request_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    allowed = set(SandboxRequest.__dataclass_fields__) - {"sandbox_id"}
    return {key: value for key, value in kwargs.items() if key in allowed and value is not None}


def _with_audit(payload: dict[str, Any], summary: str) -> dict[str, Any]:
    payload["_audit"] = {
        "files_read": [],
        "files_written": [],
        "commands_run": [],
        "network_domains": [],
        "result_summary": summary,
    }
    return payload
