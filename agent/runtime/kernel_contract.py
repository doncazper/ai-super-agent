from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .models import now_iso
from .state import redact_runtime_value


KERNEL_OWNED_EXECUTION_TRUTH: tuple[str, ...] = (
    "canonical runtime state",
    "durable execution records",
    "active job state",
    "active prompt state",
    "active workflow state",
    "active action state",
    "approval-gated resume state",
    "checkpoint and recovery reports",
    "audit receipt references",
    "command and run summaries",
    "frontend and channel contracts",
)


@dataclass(frozen=True)
class RuntimeKernelContract:
    contract_id: str = "runtime_kernel_contract_v1"
    status: str = "metadata_only"
    kernel_owns: tuple[str, ...] = KERNEL_OWNED_EXECUTION_TRUTH
    frontend_entrypoints: tuple[str, ...] = ("cli", "future_local_app", "future_ios_companion", "future_windows_app", "future_web_dashboard")
    tool_execution_boundary: str = "ToolBroker only"
    policy_boundary: str = "PolicyEngine remains final authority"
    approval_boundary: str = "ApprovalManager required for HIGH/CRITICAL; gateway cannot self-approve"
    audit_boundary: str = "AuditLogger records future execution receipts"
    server_started: bool = False
    listeners_started: bool = False
    cli_replaced: bool = False
    generated_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["kernel_owns"] = list(self.kernel_owns)
        data["frontend_entrypoints"] = list(self.frontend_entrypoints)
        return redact_runtime_value(data)


def kernel_status() -> dict[str, Any]:
    return {
        "status": "ok",
        "kernel_contract": RuntimeKernelContract().to_dict(),
        "side_effects": "none; no tool execution, server, listener, or provider call",
    }


def frontend_contract() -> dict[str, Any]:
    return {
        "status": "ok",
        "frontends": [
            {"frontend": "cli", "status": "current_first_frontend", "can_execute_tools_directly": False, "can_self_approve": False},
            {"frontend": "local_app", "status": "future", "can_execute_tools_directly": False, "can_self_approve": False},
            {"frontend": "ios_companion", "status": "future", "can_execute_tools_directly": False, "can_self_approve": False},
            {"frontend": "windows_app", "status": "future", "can_execute_tools_directly": False, "can_self_approve": False},
            {"frontend": "web_dashboard", "status": "future", "can_execute_tools_directly": False, "can_self_approve": False},
        ],
        "request_flow": [
            "frontend submits request envelope",
            "gateway assigns request and correlation IDs",
            "gateway normalizes and redacts payload",
            "kernel-owned services inspect state and policy",
            "future execution paths must route through ToolBroker",
            "ApprovalManager handles HIGH/CRITICAL review",
            "AuditLogger receives execution receipts",
        ],
        "side_effects": "none; contract metadata only",
    }
