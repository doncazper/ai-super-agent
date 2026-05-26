from __future__ import annotations

from pathlib import Path

from agent.sandbox.models import SandboxRequest


RISK_ORDER = {"SAFE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4, "FORBIDDEN": 5}


def sandbox_policy_summary() -> dict[str, object]:
    return {
        "status": "ok",
        "default_backend": "mock",
        "execution_enabled": False,
        "network_default": False,
        "personal_data_default": False,
        "arbitrary_command_execution": False,
        "filesystem_scope": "workspace_roots_only",
        "toolbroker_required": True,
        "policyengine_required": True,
        "audit_required": True,
        "planned_backends": ["docker_rootless", "macos_sandbox", "firecracker_vm", "browser_sandbox"],
        "deferred_backends": ["cloud_sandbox"],
        "forbidden_without_approval": [
            "arbitrary script execution",
            "networked sandbox execution",
            "browser automation",
            "broad filesystem mounts",
            "personal-data access",
            "background persistence",
        ],
    }


def validate_sandbox_request(request: SandboxRequest) -> tuple[bool, str]:
    if request.personal_data_allowed:
        return False, "personal data is disabled for sandbox requests by default"
    if request.network_allowed:
        return False, "network is disabled for sandbox requests by default"
    if RISK_ORDER.get(request.risk_level.upper(), 5) >= RISK_ORDER["HIGH"]:
        return False, "HIGH and CRITICAL sandbox requests require a future approval-gated execution design"
    if request.command:
        return False, "arbitrary command execution is disabled in sandbox dry-runs"
    for root in request.filesystem_roots:
        if not _is_workspace_root(root):
            return False, f"filesystem root is outside the approved workspace scope: {root}"
    return True, "request satisfies mock-only sandbox policy"


def _is_workspace_root(root: str) -> bool:
    raw = Path(root)
    if raw.is_absolute():
        return False
    return ".." not in raw.parts and (not raw.parts or raw.parts[0] in {"workspace", "."})
