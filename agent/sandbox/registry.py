from __future__ import annotations

from agent.sandbox.base import SandboxBackend
from agent.sandbox.errors import UnknownSandboxBackendError
from agent.sandbox.mock_backend import MockSandboxBackend, PlannedSandboxBackend
from agent.sandbox.models import SandboxBackendInfo, SandboxBackendType


class SandboxBackendRegistry:
    def __init__(self, backends: dict[str, SandboxBackend] | None = None) -> None:
        self._backends = backends or _default_backends()

    def list_backends(self) -> list[SandboxBackendInfo]:
        return [backend.backend_info() for backend in self._backends.values()]

    def get(self, backend_id: str) -> SandboxBackend:
        normalized = backend_id.strip().casefold()
        backend = self._backends.get(normalized)
        if backend is None:
            raise UnknownSandboxBackendError(f"unknown sandbox backend: {backend_id}")
        return backend


def default_sandbox_registry() -> SandboxBackendRegistry:
    return SandboxBackendRegistry()


def _default_backends() -> dict[str, SandboxBackend]:
    planned = {
        "local_workspace_safe": _planned(
            "local_workspace_safe",
            SandboxBackendType.LOCAL_WORKSPACE_SAFE,
            "stubbed",
            "Local workspace-safe execution remains dry-run only until command allowlists and brokered execution gates are approved.",
        ),
        "docker_rootless": _planned(
            "docker_rootless",
            SandboxBackendType.DOCKER_ROOTLESS,
            "planned",
            "Docker/rootless sandbox support is planned only; do not install Docker from this track.",
        ),
        "macos_sandbox": _planned(
            "macos_sandbox",
            SandboxBackendType.MACOS_SANDBOX,
            "planned",
            "macOS sandbox support is planned only and must not import native frameworks at startup.",
        ),
        "firecracker_vm": _planned(
            "firecracker_vm",
            SandboxBackendType.FIRECRACKER_VM,
            "planned",
            "Firecracker VM support is planned only and requires a future release gate.",
        ),
        "browser_sandbox": _planned(
            "browser_sandbox",
            SandboxBackendType.BROWSER_SANDBOX,
            "planned",
            "Browser automation/sandboxing is planned only and remains disabled.",
        ),
        "cloud_sandbox": _planned(
            "cloud_sandbox",
            SandboxBackendType.CLOUD_SANDBOX,
            "deferred",
            "Cloud sandbox execution is deferred and requires explicit future approval.",
        ),
    }
    return {"mock": MockSandboxBackend(), **planned}


def _planned(backend_id: str, backend_type: SandboxBackendType, status: str, setup_hint: str) -> PlannedSandboxBackend:
    return PlannedSandboxBackend(
        SandboxBackendInfo(
            backend_id=backend_id,
            backend_type=backend_type,
            status=status,
            default_enabled=False,
            network_default=False,
            personal_data_default=False,
            filesystem_scope="workspace_roots_only",
            command_execution="disabled",
            setup_hint=setup_hint,
            docs_path="docs/autonomy/SANDBOX_BACKEND_ABSTRACTION.md",
        )
    )
