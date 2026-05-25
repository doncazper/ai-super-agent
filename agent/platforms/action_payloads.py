from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from agent.platforms.models import PlatformCapabilityStatus, PlatformKind, PlatformStatus
from agent.safety.policy import RiskLevel
from agent.safety.trust import TrustLevel


def _enum_value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


@dataclass(frozen=True)
class PlatformActionPayload:
    """Side-effect-free preview metadata for a future platform action.

    Payloads are descriptive only. They are not permission to execute, and they
    must be routed through ToolBroker-approved tools before any real bridge can
    perform side effects.
    """

    capability_id: str
    platform: PlatformKind
    bridge_id: str
    args: Mapping[str, Any] = field(default_factory=dict)
    preview: str = ""
    risk_level: RiskLevel = RiskLevel.SAFE
    trust_level: TrustLevel = TrustLevel.MODEL_OUTPUT
    approval_required: bool | str = False
    provider: str = "none"
    setup_hint: str = ""
    requires_toolbroker: bool = True
    side_effects: bool = False
    audit_correlation_id: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "platform": self.platform.value,
            "bridge_id": self.bridge_id,
            "args": dict(self.args),
            "preview": self.preview,
            "risk_level": self.risk_level.value,
            "trust_level": self.trust_level.value,
            "approval_required": self.approval_required,
            "provider": self.provider,
            "setup_hint": self.setup_hint,
            "requires_toolbroker": self.requires_toolbroker,
            "side_effects": self.side_effects,
            "audit_correlation_id": self.audit_correlation_id,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class PlatformActionResult:
    """Result envelope for platform bridge action attempts.

    Future brokered tools must fill audit correlation fields before returning
    results. Direct bridge execution remains fail-closed.
    """

    capability_id: str
    platform: PlatformKind
    bridge_id: str
    status: PlatformCapabilityStatus
    success: bool
    audit_correlation_id: str
    result: Mapping[str, Any] = field(default_factory=dict)
    error: str = ""
    blocked_reason: str = ""
    setup_hint: str = ""
    toolbroker_routed: bool = False
    policy_evaluated: bool = False
    approval_checked: bool = False
    side_effects_performed: bool = False
    trust_level: TrustLevel = TrustLevel.MODEL_OUTPUT
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "platform": self.platform.value,
            "bridge_id": self.bridge_id,
            "status": self.status.value,
            "success": self.success,
            "audit_correlation_id": self.audit_correlation_id,
            "result": dict(self.result),
            "error": self.error,
            "blocked_reason": self.blocked_reason,
            "setup_hint": self.setup_hint,
            "toolbroker_routed": self.toolbroker_routed,
            "policy_evaluated": self.policy_evaluated,
            "approval_checked": self.approval_checked,
            "side_effects_performed": self.side_effects_performed,
            "trust_level": self.trust_level.value,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class PlatformPermissionStatus:
    platform: PlatformKind
    bridge_id: str
    status: PlatformCapabilityStatus
    capability_id: str = ""
    granted: bool = False
    setup_hint: str = ""
    personal_data_accessed: bool = False
    native_modules_imported: tuple[str, ...] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "platform": self.platform.value,
            "bridge_id": self.bridge_id,
            "status": self.status.value,
            "capability_id": self.capability_id,
            "granted": self.granted,
            "setup_hint": self.setup_hint,
            "personal_data_accessed": self.personal_data_accessed,
            "native_modules_imported": list(self.native_modules_imported),
            "metadata": {_enum_value(key): _enum_value(value) for key, value in self.metadata.items()},
        }


@dataclass(frozen=True)
class PlatformHealthStatus:
    platform: PlatformKind
    bridge_id: str
    status: PlatformStatus
    available: bool = False
    checks: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    setup_hint: str = ""
    personal_data_accessed: bool = False
    native_modules_imported: tuple[str, ...] = field(default_factory=tuple)
    capabilities_count: int = 0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "platform": self.platform.value,
            "bridge_id": self.bridge_id,
            "status": self.status.value,
            "available": self.available,
            "checks": list(self.checks),
            "warnings": list(self.warnings),
            "setup_hint": self.setup_hint,
            "personal_data_accessed": self.personal_data_accessed,
            "native_modules_imported": list(self.native_modules_imported),
            "capabilities_count": self.capabilities_count,
            "metadata": dict(self.metadata),
        }
