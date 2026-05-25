from __future__ import annotations

from agent.platforms.macos.docs import SETUP_HINT
from agent.platforms.models import PlatformKind
from agent.platforms.null_bridge import NullPlatformBridge
from agent.platforms.registry import PlatformCapabilityRegistry


class MacOSPlatformBridge(NullPlatformBridge):
    """Fail-closed macOS bridge stub.

    The stub declares macOS capability metadata through the shared registry but
    performs no native imports, personal-data reads, permission requests, or
    platform actions.
    """

    def __init__(self, *, capability_registry: PlatformCapabilityRegistry | None = None) -> None:
        super().__init__(
            PlatformKind.MACOS,
            bridge_id="macos_bridge",
            capability_registry=capability_registry,
            setup_hint=SETUP_HINT,
        )
