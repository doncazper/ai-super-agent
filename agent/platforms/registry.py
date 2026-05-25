from __future__ import annotations

from collections.abc import Iterable

from agent.platforms.capabilities import STATIC_PLATFORM_CAPABILITIES
from agent.platforms.errors import PlatformCapabilityNotFoundError
from agent.platforms.models import (
    PlatformCapability,
    PlatformCapabilityStatus,
    PlatformKind,
    unsupported_capability,
)


class PlatformCapabilityRegistry:
    """Static platform capability registry.

    Registry lookups are metadata-only. They do not import bridge modules,
    inspect personal data, or execute platform actions.
    """

    def __init__(self, capabilities: Iterable[PlatformCapability] = STATIC_PLATFORM_CAPABILITIES) -> None:
        self._capabilities = tuple(capabilities)
        self._by_id = {capability.capability_id: capability for capability in self._capabilities}

    def all(self) -> tuple[PlatformCapability, ...]:
        return self._capabilities

    def get(self, capability_id: str) -> PlatformCapability:
        return self._by_id.get(capability_id, unsupported_capability(capability_id))

    def require(self, capability_id: str) -> PlatformCapability:
        capability = self._by_id.get(capability_id)
        if capability is None:
            raise PlatformCapabilityNotFoundError(f"unknown platform capability: {capability_id}")
        return capability

    def by_platform(self, platform: PlatformKind | str) -> tuple[PlatformCapability, ...]:
        platform_kind = parse_platform_kind(platform)
        if platform_kind is PlatformKind.UNKNOWN:
            return (
                PlatformCapability(
                    capability_id="unknown.platform.unsupported",
                    platform=PlatformKind.UNKNOWN,
                    name="Unknown platform",
                    description="The requested platform is unknown; no capabilities are executable.",
                    status=PlatformCapabilityStatus.UNSUPPORTED,
                    risk_level=unsupported_capability("unknown.platform.unsupported").risk_level,
                    trust_level=unsupported_capability("unknown.platform.unsupported").trust_level,
                    default_enabled=False,
                    approval_required=False,
                    provider="none",
                    setup_hint="Unknown platform. Use a supported platform id such as macos, ios_companion, windows, linux, or web.",
                    docs_path="docs/platforms/CAPABILITY_MATRIX.md",
                    command_examples=(),
                    lazy_load_module=None,
                    performance_notes="Unsupported platform lookup does not load bridge modules.",
                ),
            )
        return tuple(capability for capability in self._capabilities if capability.platform is platform_kind)

    def ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_id))


def parse_platform_kind(platform: PlatformKind | str) -> PlatformKind:
    if isinstance(platform, PlatformKind):
        return platform
    try:
        return PlatformKind(str(platform))
    except ValueError:
        return PlatformKind.UNKNOWN


def default_registry() -> PlatformCapabilityRegistry:
    return PlatformCapabilityRegistry()
