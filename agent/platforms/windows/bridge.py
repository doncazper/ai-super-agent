from __future__ import annotations

from agent.platforms.models import PlatformKind
from agent.platforms.null_bridge import NullPlatformBridge
from agent.platforms.registry import PlatformCapabilityRegistry
from agent.platforms.windows.docs import SETUP_HINT


class WindowsPlatformBridge(NullPlatformBridge):
    """Fail-closed Windows bridge stub."""

    def __init__(self, *, capability_registry: PlatformCapabilityRegistry | None = None) -> None:
        super().__init__(
            PlatformKind.WINDOWS,
            bridge_id="windows_bridge",
            capability_registry=capability_registry,
            setup_hint=SETUP_HINT,
        )
