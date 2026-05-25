from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping

from agent.platforms.action_payloads import PlatformActionPayload, PlatformActionResult, PlatformHealthStatus
from agent.platforms.models import PlatformCapability, PlatformCapabilityStatus, PlatformKind


class PlatformBridge(ABC):
    """Abstract platform bridge contract.

    Bridges describe and prepare platform actions, but workflows must not call
    execute_action directly. Any future executable bridge action is internal to
    ToolBroker-approved tools that have already passed PolicyEngine,
    PermissionManager, ApprovalManager when required, and AuditLogger
    correlation.
    """

    @abstractmethod
    def platform_kind(self) -> PlatformKind:
        """Return the platform this bridge represents."""

    @abstractmethod
    def bridge_id(self) -> str:
        """Return a stable bridge identifier."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return whether the bridge can perform brokered actions."""

    @abstractmethod
    def health_check(self) -> PlatformHealthStatus:
        """Return metadata-only health without personal-data reads."""

    @abstractmethod
    def list_capabilities(self) -> tuple[PlatformCapability, ...]:
        """Return declared capability metadata."""

    @abstractmethod
    def get_capability_status(self, capability_id: str) -> PlatformCapabilityStatus:
        """Return metadata status for a capability."""

    @abstractmethod
    def prepare_action(self, capability_id: str, args: Mapping[str, Any] | None = None) -> PlatformActionPayload:
        """Create a side-effect-free preview payload."""

    @abstractmethod
    def execute_action(
        self,
        capability_id: str,
        args: Mapping[str, Any] | None = None,
        *,
        broker_context: Mapping[str, Any] | None = None,
    ) -> PlatformActionResult:
        """Internal-only execute_action hook for brokered tools.

        Direct workflow calls must fail closed. Future concrete bridges should
        require broker context proving ToolBroker, PolicyEngine, approval when
        required, and audit correlation were already applied.
        """
