from __future__ import annotations

from typing import Any, Mapping

from agent.platforms.action_payloads import PlatformActionPayload, PlatformActionResult, PlatformHealthStatus
from agent.platforms.base import PlatformBridge
from agent.platforms.models import PlatformCapability, PlatformCapabilityStatus, PlatformKind, PlatformStatus
from agent.platforms.registry import PlatformCapabilityRegistry, default_registry, parse_platform_kind


DEFAULT_SETUP_HINT = (
    "No platform bridge is available. Keep using CLI-only mode, or add a future "
    "bridge implementation with capability manifest entries, ToolBroker mapping, "
    "PolicyEngine tests, approval gates, and audit coverage."
)


class NullPlatformBridge(PlatformBridge):
    """Fail-closed bridge used when platform support is unavailable.

    The null bridge imports no platform modules, performs no side effects,
    reads no personal data, and never executes platform actions.
    """

    def __init__(
        self,
        platform: PlatformKind | str = PlatformKind.UNKNOWN,
        *,
        bridge_id: str | None = None,
        capability_registry: PlatformCapabilityRegistry | None = None,
        setup_hint: str = DEFAULT_SETUP_HINT,
    ) -> None:
        self._platform = parse_platform_kind(platform)
        self._bridge_id = bridge_id or f"null_{self._platform.value}_bridge"
        self._capability_registry = capability_registry or default_registry()
        self._setup_hint = setup_hint

    def platform_kind(self) -> PlatformKind:
        return self._platform

    def bridge_id(self) -> str:
        return self._bridge_id

    def is_available(self) -> bool:
        return False

    def health_check(self) -> PlatformHealthStatus:
        return PlatformHealthStatus(
            platform=self._platform,
            bridge_id=self._bridge_id,
            status=PlatformStatus.REQUIRES_SETUP if self._platform is not PlatformKind.UNKNOWN else PlatformStatus.UNSUPPORTED,
            available=False,
            checks=("metadata_only", "no_personal_data_access", "no_native_imports", "no_side_effects"),
            warnings=("platform actions unavailable",),
            setup_hint=self._setup_hint,
            personal_data_accessed=False,
            native_modules_imported=(),
            capabilities_count=len(self.list_capabilities()),
        )

    def list_capabilities(self) -> tuple[PlatformCapability, ...]:
        return self._capability_registry.by_platform(self._platform)

    def get_capability_status(self, capability_id: str) -> PlatformCapabilityStatus:
        capability = self._capability_registry.get(capability_id)
        if capability.platform is PlatformKind.UNKNOWN:
            return PlatformCapabilityStatus.UNSUPPORTED
        if self._platform is not PlatformKind.UNKNOWN and capability.platform is not self._platform:
            return PlatformCapabilityStatus.UNSUPPORTED
        return capability.status

    def prepare_action(self, capability_id: str, args: Mapping[str, Any] | None = None) -> PlatformActionPayload:
        capability = self._capability_registry.get(capability_id)
        setup_hint = capability.setup_hint if capability.platform is not PlatformKind.UNKNOWN else self._setup_hint
        return PlatformActionPayload(
            capability_id=capability_id,
            platform=self._platform,
            bridge_id=self._bridge_id,
            args=dict(args or {}),
            preview=f"{capability_id} is unavailable through {self._bridge_id}; no side effects were performed.",
            risk_level=capability.risk_level,
            trust_level=capability.trust_level,
            approval_required=capability.approval_required,
            provider=capability.provider,
            setup_hint=setup_hint,
            requires_toolbroker=True,
            side_effects=False,
            audit_correlation_id=self._audit_correlation_id(capability_id),
            metadata={
                "capability_status": self.get_capability_status(capability_id).value,
                "bridge_available": False,
            },
        )

    def execute_action(
        self,
        capability_id: str,
        args: Mapping[str, Any] | None = None,
        *,
        broker_context: Mapping[str, Any] | None = None,
    ) -> PlatformActionResult:
        capability = self._capability_registry.get(capability_id)
        routed = bool(broker_context and broker_context.get("toolbroker_approved"))
        if not routed:
            return PlatformActionResult(
                capability_id=capability_id,
                platform=self._platform,
                bridge_id=self._bridge_id,
                status=PlatformCapabilityStatus.BLOCKED,
                success=False,
                audit_correlation_id=self._audit_correlation_id(capability_id),
                error="Direct platform bridge execution is forbidden.",
                blocked_reason="direct_bridge_execution_forbidden",
                setup_hint=(
                    "Route future platform actions through a ToolBroker-approved tool with "
                    "PolicyEngine, PermissionManager, ApprovalManager when required, and AuditLogger evidence."
                ),
                toolbroker_routed=False,
                policy_evaluated=False,
                approval_checked=False,
                side_effects_performed=False,
                trust_level=capability.trust_level,
                metadata={"args_seen": bool(args), "bridge_available": False},
            )
        return PlatformActionResult(
            capability_id=capability_id,
            platform=self._platform,
            bridge_id=self._bridge_id,
            status=PlatformCapabilityStatus.REQUIRES_SETUP,
            success=False,
            audit_correlation_id=str(broker_context.get("audit_correlation_id") or self._audit_correlation_id(capability_id)),
            error="Platform bridge is unavailable.",
            blocked_reason="platform_bridge_unavailable",
            setup_hint=capability.setup_hint if capability.platform is not PlatformKind.UNKNOWN else self._setup_hint,
            toolbroker_routed=True,
            policy_evaluated=bool(broker_context.get("policy_evaluated")),
            approval_checked=bool(broker_context.get("approval_checked")),
            side_effects_performed=False,
            trust_level=capability.trust_level,
            metadata={"bridge_available": False},
        )

    def _audit_correlation_id(self, capability_id: str) -> str:
        safe_capability_id = capability_id.replace(" ", "_") or "unknown"
        return f"{self._bridge_id}:{safe_capability_id}:null"
