from __future__ import annotations

from agent.platforms.models import PlatformKind
from agent.platforms.null_bridge import NullPlatformBridge
from agent.platforms.registry import PlatformCapabilityRegistry
from agent.platforms.web_bridge.docs import SETUP_HINT


class WebBridgePlatformBridge(NullPlatformBridge):
    """Fail-closed generic app/web bridge stub."""

    def __init__(self, *, capability_registry: PlatformCapabilityRegistry | None = None) -> None:
        super().__init__(
            PlatformKind.WEB,
            bridge_id="web_app_bridge",
            capability_registry=capability_registry,
            setup_hint=SETUP_HINT,
        )
