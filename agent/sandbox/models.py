from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class SandboxBackendType(str, Enum):
    MOCK = "mock"
    LOCAL_WORKSPACE_SAFE = "local_workspace_safe"
    DOCKER_ROOTLESS = "docker_rootless"
    MACOS_SANDBOX = "macos_sandbox"
    FIRECRACKER_VM = "firecracker_vm"
    BROWSER_SANDBOX = "browser_sandbox"
    CLOUD_SANDBOX = "cloud_sandbox"


@dataclass(frozen=True)
class SandboxBackendInfo:
    backend_id: str
    backend_type: SandboxBackendType
    status: str
    default_enabled: bool
    network_default: bool
    personal_data_default: bool
    filesystem_scope: str
    command_execution: str
    setup_hint: str
    docs_path: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["backend_type"] = self.backend_type.value
        return data


@dataclass(frozen=True)
class SandboxRequest:
    sandbox_id: str = "mock"
    task_type: str = "metadata_check"
    risk_level: str = "LOW"
    network_allowed: bool = False
    filesystem_roots: list[str] = field(default_factory=lambda: ["workspace"])
    time_limit_seconds: int = 30
    memory_limit_mb: int = 128
    command_allowlist: list[str] = field(default_factory=list)
    personal_data_allowed: bool = False
    audit_required: bool = True
    command: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SandboxResult:
    status: str
    backend_id: str
    dry_run: bool
    allowed: bool
    reason: str
    tools_executed: list[str] = field(default_factory=list)
    network_used: bool = False
    filesystem_accessed: list[str] = field(default_factory=list)
    personal_data_accessed: bool = False
    audit_required: bool = True
    setup_hint: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
