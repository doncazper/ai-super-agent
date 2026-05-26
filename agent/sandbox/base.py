from __future__ import annotations

from abc import ABC, abstractmethod

from agent.sandbox.models import SandboxBackendInfo, SandboxRequest, SandboxResult


class SandboxBackend(ABC):
    @abstractmethod
    def backend_info(self) -> SandboxBackendInfo:
        raise NotImplementedError

    @abstractmethod
    def dry_run(self, request: SandboxRequest) -> SandboxResult:
        raise NotImplementedError

    def execute(self, request: SandboxRequest) -> SandboxResult:
        return SandboxResult(
            status="blocked",
            backend_id=request.sandbox_id,
            dry_run=False,
            allowed=False,
            reason="Sandbox execution is disabled in this scaffold; use dry-run only.",
            setup_hint="Future execution must be ToolBroker-routed, policy checked, audited, and release-gated.",
        )
