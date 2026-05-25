from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from agent.platforms.errors import PlatformUnsupportedError
from agent.safety.policy import RiskLevel
from agent.safety.trust import TrustLevel


class PlatformKind(StrEnum):
    MACOS = "macos"
    IOS_COMPANION = "ios_companion"
    WINDOWS = "windows"
    LINUX = "linux"
    WEB = "web"
    UNKNOWN = "unknown"


class PlatformStatus(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DISABLED = "disabled"
    BLOCKED = "blocked"
    UNSUPPORTED = "unsupported"
    REQUIRES_SETUP = "requires_setup"
    UNKNOWN = "unknown"


class PlatformCapabilityStatus(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    PLANNED = "planned"
    STUBBED = "stubbed"
    DISABLED = "disabled"
    BLOCKED = "blocked"
    UNSUPPORTED = "unsupported"
    REQUIRES_SETUP = "requires_setup"
    REQUIRES_APPROVAL = "requires_approval"


@dataclass(frozen=True)
class PlatformCapability:
    capability_id: str
    platform: PlatformKind
    name: str
    description: str
    status: PlatformCapabilityStatus
    risk_level: RiskLevel
    trust_level: TrustLevel
    default_enabled: bool
    approval_required: bool | str
    provider: str
    setup_hint: str
    docs_path: str
    command_examples: tuple[str, ...] = field(default_factory=tuple)
    lazy_load_module: str | None = None
    performance_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "platform": self.platform.value,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "risk_level": self.risk_level.value,
            "trust_level": self.trust_level.value,
            "default_enabled": self.default_enabled,
            "approval_required": self.approval_required,
            "provider": self.provider,
            "setup_hint": self.setup_hint,
            "docs_path": self.docs_path,
            "command_examples": list(self.command_examples),
            "lazy_load_module": self.lazy_load_module,
            "performance_notes": self.performance_notes,
        }


@dataclass(frozen=True)
class PlatformBridgeInfo:
    bridge_id: str
    platform: PlatformKind
    status: PlatformStatus
    default_enabled: bool
    capabilities: tuple[str, ...]
    setup_hint: str
    docs_path: str
    lazy_load_module: str | None = None
    performance_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "bridge_id": self.bridge_id,
            "platform": self.platform.value,
            "status": self.status.value,
            "default_enabled": self.default_enabled,
            "capabilities": list(self.capabilities),
            "setup_hint": self.setup_hint,
            "docs_path": self.docs_path,
            "lazy_load_module": self.lazy_load_module,
            "performance_notes": self.performance_notes,
        }


@dataclass(frozen=True)
class PlatformDetectionResult:
    platform: PlatformKind
    status: PlatformStatus
    runtime_mode: str = "cli"
    detected_by: str = "python_platform"
    setup_hint: str = ""
    warnings: tuple[str, ...] = field(default_factory=tuple)
    personal_data_accessed: bool = False
    native_modules_imported: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "platform": self.platform.value,
            "status": self.status.value,
            "runtime_mode": self.runtime_mode,
            "detected_by": self.detected_by,
            "setup_hint": self.setup_hint,
            "warnings": list(self.warnings),
            "personal_data_accessed": self.personal_data_accessed,
            "native_modules_imported": list(self.native_modules_imported),
        }


def unsupported_capability(capability_id: str) -> PlatformCapability:
    return PlatformCapability(
        capability_id=capability_id,
        platform=PlatformKind.UNKNOWN,
        name=f"Unknown platform capability: {capability_id}",
        description="This capability is not registered and is not executable.",
        status=PlatformCapabilityStatus.UNSUPPORTED,
        risk_level=RiskLevel.FORBIDDEN,
        trust_level=TrustLevel.MODEL_OUTPUT,
        default_enabled=False,
        approval_required=False,
        provider="none",
        setup_hint="Unknown platform capability. Add a registry entry, manifest declaration, ToolBroker mapping, policy tests, and audit coverage before execution.",
        docs_path="docs/platforms/CAPABILITY_MATRIX.md",
        command_examples=(),
        lazy_load_module=None,
        performance_notes="Unsupported records do not load bridge modules.",
    )
