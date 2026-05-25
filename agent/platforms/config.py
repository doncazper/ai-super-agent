from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
import os
from typing import Any


class PlatformBridgeMode(StrEnum):
    AUTO = "auto"
    OFF = "off"
    MACOS = "macos"
    IOS_COMPANION = "ios_companion"
    WINDOWS = "windows"
    WEB = "web"


class PlatformRuntimeMode(StrEnum):
    CLI = "cli"
    PACKAGED_APP = "packaged_app"
    MAC_APP_BRIDGE = "mac_app_bridge"
    IOS_COMPANION_BRIDGE = "ios_companion_bridge"
    WINDOWS_APP_BRIDGE = "windows_app_bridge"
    WEB_BRIDGE = "web_bridge"
    TEST = "test"


class AppBridgeTransport(StrEnum):
    STDIO = "stdio"
    UNIX_SOCKET = "unix_socket"
    LOCALHOST_HTTP = "localhost_http"


TRUE_VALUES = {"1", "true", "yes", "y", "on", "enabled"}
FALSE_VALUES = {"0", "false", "no", "n", "off", "disabled", ""}
LOCALHOST_VALUES = {"127.0.0.1", "localhost", "::1"}


@dataclass(frozen=True)
class PlatformConfig:
    platform_bridges_enabled: bool = False
    platform_bridge_mode: PlatformBridgeMode = PlatformBridgeMode.AUTO
    platform_detection_cache_seconds: int = 300
    platform_lazy_load_bridges: bool = True
    macos_bridge_enabled: bool = False
    ios_companion_bridge_enabled: bool = False
    windows_bridge_enabled: bool = False
    web_app_bridge_enabled: bool = False
    app_bridge_enabled: bool = False
    app_bridge_host: str = "127.0.0.1"
    app_bridge_port: str = ""
    app_bridge_transport: AppBridgeTransport = AppBridgeTransport.STDIO
    app_bridge_require_pairing: bool = True
    app_bridge_allow_remote: bool = False
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Return config metadata only; never include raw environment values."""

        return {
            "platform_bridges_enabled": self.platform_bridges_enabled,
            "platform_bridge_mode": self.platform_bridge_mode.value,
            "platform_detection_cache_seconds": self.platform_detection_cache_seconds,
            "platform_lazy_load_bridges": self.platform_lazy_load_bridges,
            "macos_bridge_enabled": self.macos_bridge_enabled,
            "ios_companion_bridge_enabled": self.ios_companion_bridge_enabled,
            "windows_bridge_enabled": self.windows_bridge_enabled,
            "web_app_bridge_enabled": self.web_app_bridge_enabled,
            "app_bridge_enabled": self.app_bridge_enabled,
            "app_bridge_host": self.app_bridge_host,
            "app_bridge_port": self.app_bridge_port,
            "app_bridge_transport": self.app_bridge_transport.value,
            "app_bridge_require_pairing": self.app_bridge_require_pairing,
            "app_bridge_allow_remote": self.app_bridge_allow_remote,
            "warnings": list(self.warnings),
        }


def load_platform_config(env: Mapping[str, str] | None = None) -> PlatformConfig:
    """Load platform bridge config from environment metadata.

    The loader reads only explicit platform-related variables. It does not
    inspect secrets, read config files, import bridge modules, or touch the
    filesystem.
    """

    source = os.environ if env is None else env
    warnings: list[str] = []

    bridge_mode = _parse_bridge_mode(source.get("PLATFORM_BRIDGE_MODE", "auto"), warnings)
    cache_seconds = _parse_int(
        source.get("PLATFORM_DETECTION_CACHE_SECONDS", "300"),
        default=300,
        name="PLATFORM_DETECTION_CACHE_SECONDS",
        warnings=warnings,
    )

    return PlatformConfig(
        platform_bridges_enabled=_parse_bool(
            source.get("PLATFORM_BRIDGES_ENABLED", "false"),
            default=False,
            name="PLATFORM_BRIDGES_ENABLED",
            warnings=warnings,
        ),
        platform_bridge_mode=bridge_mode,
        platform_detection_cache_seconds=cache_seconds,
        platform_lazy_load_bridges=_parse_bool(
            source.get("PLATFORM_LAZY_LOAD_BRIDGES", "true"),
            default=True,
            name="PLATFORM_LAZY_LOAD_BRIDGES",
            warnings=warnings,
        ),
        macos_bridge_enabled=_parse_bool(
            source.get("MACOS_BRIDGE_ENABLED", "false"),
            default=False,
            name="MACOS_BRIDGE_ENABLED",
            warnings=warnings,
        ),
        ios_companion_bridge_enabled=_parse_bool(
            source.get("IOS_COMPANION_BRIDGE_ENABLED", "false"),
            default=False,
            name="IOS_COMPANION_BRIDGE_ENABLED",
            warnings=warnings,
        ),
        windows_bridge_enabled=_parse_bool(
            source.get("WINDOWS_BRIDGE_ENABLED", "false"),
            default=False,
            name="WINDOWS_BRIDGE_ENABLED",
            warnings=warnings,
        ),
        web_app_bridge_enabled=_parse_bool(
            source.get("WEB_APP_BRIDGE_ENABLED", "false"),
            default=False,
            name="WEB_APP_BRIDGE_ENABLED",
            warnings=warnings,
        ),
        app_bridge_enabled=_parse_bool(
            source.get("APP_BRIDGE_ENABLED", "false"),
            default=False,
            name="APP_BRIDGE_ENABLED",
            warnings=warnings,
        ),
        app_bridge_host=_parse_app_bridge_host(source.get("APP_BRIDGE_HOST", "127.0.0.1"), warnings),
        app_bridge_port=source.get("APP_BRIDGE_PORT", "").strip(),
        app_bridge_transport=_parse_app_bridge_transport(source.get("APP_BRIDGE_TRANSPORT", "stdio"), warnings),
        app_bridge_require_pairing=_parse_bool(
            source.get("APP_BRIDGE_REQUIRE_PAIRING", "true"),
            default=True,
            name="APP_BRIDGE_REQUIRE_PAIRING",
            warnings=warnings,
        ),
        app_bridge_allow_remote=_parse_app_bridge_allow_remote(source.get("APP_BRIDGE_ALLOW_REMOTE", "false"), warnings),
        warnings=tuple(warnings),
    )


def _parse_bool(value: str, *, default: bool, name: str, warnings: list[str]) -> bool:
    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    warnings.append(f"{name} has an invalid boolean value; using safe default {str(default).lower()}.")
    return default


def _parse_int(value: str, *, default: int, name: str, warnings: list[str]) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        warnings.append(f"{name} has an invalid integer value; using safe default {default}.")
        return default
    if parsed < 0:
        warnings.append(f"{name} cannot be negative; using safe default {default}.")
        return default
    return parsed


def _parse_bridge_mode(value: str, warnings: list[str]) -> PlatformBridgeMode:
    normalized = value.strip().lower()
    try:
        return PlatformBridgeMode(normalized)
    except ValueError:
        warnings.append("PLATFORM_BRIDGE_MODE is invalid; using safe default auto.")
        return PlatformBridgeMode.AUTO


def _parse_app_bridge_transport(value: str, warnings: list[str]) -> AppBridgeTransport:
    normalized = value.strip().lower()
    try:
        return AppBridgeTransport(normalized)
    except ValueError:
        warnings.append("APP_BRIDGE_TRANSPORT is invalid; using safe default stdio.")
        return AppBridgeTransport.STDIO


def _parse_app_bridge_host(value: str, warnings: list[str]) -> str:
    normalized = value.strip() or "127.0.0.1"
    if normalized in LOCALHOST_VALUES:
        return normalized
    warnings.append("APP_BRIDGE_HOST must be localhost/IPC only in v1; using safe default 127.0.0.1.")
    return "127.0.0.1"


def _parse_app_bridge_allow_remote(value: str, warnings: list[str]) -> bool:
    requested = _parse_bool(value, default=False, name="APP_BRIDGE_ALLOW_REMOTE", warnings=warnings)
    if requested:
        warnings.append("APP_BRIDGE_ALLOW_REMOTE=true is unsupported in v1; using safe default false.")
    return False
