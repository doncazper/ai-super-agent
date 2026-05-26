from __future__ import annotations

from agent.sandbox.base import SandboxBackend
from agent.sandbox.models import SandboxBackendInfo, SandboxBackendType, SandboxRequest, SandboxResult
from agent.sandbox.policy import validate_sandbox_request


class MockSandboxBackend(SandboxBackend):
    def backend_info(self) -> SandboxBackendInfo:
        return SandboxBackendInfo(
            backend_id="mock",
            backend_type=SandboxBackendType.MOCK,
            status="available",
            default_enabled=True,
            network_default=False,
            personal_data_default=False,
            filesystem_scope="workspace_metadata_only",
            command_execution="disabled",
            setup_hint="Mock backend is available for policy previews and dry-runs only.",
            docs_path="docs/autonomy/SANDBOX_BACKEND_ABSTRACTION.md",
        )

    def dry_run(self, request: SandboxRequest) -> SandboxResult:
        allowed, reason = validate_sandbox_request(request)
        return SandboxResult(
            status="dry_run" if allowed else "blocked",
            backend_id="mock",
            dry_run=True,
            allowed=allowed,
            reason=reason,
            tools_executed=[],
            network_used=False,
            filesystem_accessed=[],
            personal_data_accessed=False,
            audit_required=request.audit_required,
            setup_hint="No sandbox process was started and no command was executed.",
        )


class PlannedSandboxBackend(SandboxBackend):
    def __init__(self, info: SandboxBackendInfo) -> None:
        self._info = info

    def backend_info(self) -> SandboxBackendInfo:
        return self._info

    def dry_run(self, request: SandboxRequest) -> SandboxResult:
        return SandboxResult(
            status="requires_setup" if self._info.status == "planned" else self._info.status,
            backend_id=self._info.backend_id,
            dry_run=True,
            allowed=False,
            reason=f"{self._info.backend_id} is {self._info.status} and cannot execute sandbox work in v1.",
            setup_hint=self._info.setup_hint,
        )
