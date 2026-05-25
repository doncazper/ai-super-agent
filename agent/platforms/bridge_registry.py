from __future__ import annotations

from collections.abc import Callable

from agent.platforms.base import PlatformBridge
from agent.platforms.models import PlatformKind
from agent.platforms.null_bridge import DEFAULT_SETUP_HINT, NullPlatformBridge
from agent.platforms.registry import PlatformCapabilityRegistry, default_registry, parse_platform_kind


BridgeLoader = Callable[[], PlatformBridge]


def _load_macos_bridge() -> PlatformBridge:
    from agent.platforms.macos.bridge import MacOSPlatformBridge

    return MacOSPlatformBridge()


def _load_ios_companion_bridge() -> PlatformBridge:
    from agent.platforms.ios_companion.bridge import IOSCompanionPlatformBridge

    return IOSCompanionPlatformBridge()


def _load_windows_bridge() -> PlatformBridge:
    from agent.platforms.windows.bridge import WindowsPlatformBridge

    return WindowsPlatformBridge()


def _load_web_bridge() -> PlatformBridge:
    from agent.platforms.web_bridge.bridge import WebBridgePlatformBridge

    return WebBridgePlatformBridge()


class PlatformBridgeRegistry:
    """Lazy registry for optional platform bridge implementations.

    Loaders are called only when a specific bridge is requested. Registering a
    loader must not import native platform modules at core startup.
    """

    def __init__(
        self,
        *,
        capability_registry: PlatformCapabilityRegistry | None = None,
        loaders: dict[PlatformKind | str, BridgeLoader] | None = None,
    ) -> None:
        self._capability_registry = capability_registry or default_registry()
        self._loaders: dict[PlatformKind, BridgeLoader] = {}
        self._loaded: dict[PlatformKind, PlatformBridge] = {}
        for platform, loader in (loaders or {}).items():
            self.register_loader(platform, loader)

    def register_loader(self, platform: PlatformKind | str, loader: BridgeLoader) -> None:
        self._loaders[parse_platform_kind(platform)] = loader

    def get_bridge(self, platform: PlatformKind | str) -> PlatformBridge:
        platform_kind = parse_platform_kind(platform)
        if platform_kind in self._loaded:
            return self._loaded[platform_kind]

        loader = self._loaders.get(platform_kind)
        if loader is None or platform_kind is PlatformKind.UNKNOWN:
            bridge = self._null_bridge(platform_kind)
            self._loaded[platform_kind] = bridge
            return bridge

        try:
            bridge = loader()
        except Exception as exc:  # pragma: no cover - defensive fail-closed path
            bridge = self._null_bridge(
                platform_kind,
                setup_hint=f"Bridge loader failed with {type(exc).__name__}; platform actions remain unavailable.",
            )
        self._loaded[platform_kind] = bridge
        return bridge

    def list_registered_platforms(self) -> tuple[PlatformKind, ...]:
        return tuple(sorted(self._loaders, key=lambda item: item.value))

    def list_loaded_bridges(self) -> tuple[PlatformBridge, ...]:
        return tuple(self._loaded[platform] for platform in sorted(self._loaded, key=lambda item: item.value))

    def _null_bridge(self, platform: PlatformKind, *, setup_hint: str | None = None) -> NullPlatformBridge:
        return NullPlatformBridge(
            platform,
            capability_registry=self._capability_registry,
            setup_hint=setup_hint or DEFAULT_SETUP_HINT,
        )


def default_bridge_registry() -> PlatformBridgeRegistry:
    return PlatformBridgeRegistry(
        loaders={
            PlatformKind.MACOS: _load_macos_bridge,
            PlatformKind.IOS_COMPANION: _load_ios_companion_bridge,
            PlatformKind.WINDOWS: _load_windows_bridge,
            PlatformKind.WEB: _load_web_bridge,
        }
    )
