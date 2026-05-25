from __future__ import annotations

from agent.platforms.ios_companion.docs import SETUP_HINT
from agent.platforms.models import PlatformKind
from agent.platforms.null_bridge import NullPlatformBridge
from agent.platforms.registry import PlatformCapabilityRegistry


class IOSCompanionPlatformBridge(NullPlatformBridge):
    """Fail-closed iOS companion bridge stub."""

    def __init__(self, *, capability_registry: PlatformCapabilityRegistry | None = None) -> None:
        super().__init__(
            PlatformKind.IOS_COMPANION,
            bridge_id="ios_companion_bridge",
            capability_registry=capability_registry,
            setup_hint=SETUP_HINT,
        )
