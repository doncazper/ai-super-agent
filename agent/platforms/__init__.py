"""Portable platform metadata.

This package is intentionally data-driven. Importing it must not import native
OS frameworks, start services, read personal data, or execute platform actions.
"""

from agent.platforms.models import (
    PlatformBridgeInfo,
    PlatformCapability,
    PlatformCapabilityStatus,
    PlatformDetectionResult,
    PlatformKind,
    PlatformStatus,
)
from agent.platforms.action_payloads import (
    PlatformActionPayload,
    PlatformActionResult,
    PlatformHealthStatus,
    PlatformPermissionStatus,
)
from agent.platforms.base import PlatformBridge
from agent.platforms.bridge_registry import PlatformBridgeRegistry, default_bridge_registry
from agent.platforms.config import AppBridgeTransport, PlatformBridgeMode, PlatformConfig, PlatformRuntimeMode, load_platform_config
from agent.platforms.detection import clear_detection_cache, detect_platform, detect_runtime_mode
from agent.platforms.errors import PlatformCapabilityNotFoundError, PlatformUnsupportedError
from agent.platforms.null_bridge import NullPlatformBridge
from agent.platforms.paths import PlatformPaths, get_platform_paths
from agent.platforms.registry import PlatformCapabilityRegistry, default_registry

__all__ = [
    "NullPlatformBridge",
    "AppBridgeTransport",
    "PlatformActionPayload",
    "PlatformActionResult",
    "PlatformBridge",
    "PlatformCapabilityNotFoundError",
    "PlatformBridgeInfo",
    "PlatformBridgeMode",
    "PlatformBridgeRegistry",
    "PlatformCapability",
    "PlatformCapabilityRegistry",
    "PlatformCapabilityStatus",
    "PlatformConfig",
    "PlatformDetectionResult",
    "PlatformHealthStatus",
    "PlatformKind",
    "PlatformPaths",
    "PlatformPermissionStatus",
    "PlatformRuntimeMode",
    "PlatformStatus",
    "PlatformUnsupportedError",
    "clear_detection_cache",
    "default_bridge_registry",
    "default_registry",
    "detect_platform",
    "detect_runtime_mode",
    "get_platform_paths",
    "load_platform_config",
]
