from __future__ import annotations

from collections.abc import Mapping
import os
import sys
import time

from agent.platforms.config import PlatformRuntimeMode, load_platform_config
from agent.platforms.models import PlatformDetectionResult, PlatformKind, PlatformStatus


_DETECTION_CACHE: tuple[float, float, PlatformDetectionResult] | None = None


def clear_detection_cache() -> None:
    global _DETECTION_CACHE
    _DETECTION_CACHE = None


def detect_runtime_mode(env: Mapping[str, str] | None = None) -> str:
    """Return safe runtime mode metadata from explicit environment flags only."""

    source = os.environ if env is None else env
    explicit = source.get("PLATFORM_RUNTIME_MODE") or source.get("AI_AGENT_RUNTIME_MODE")
    if explicit:
        normalized = explicit.strip().lower()
        if normalized in {mode.value for mode in PlatformRuntimeMode}:
            return normalized

    if source.get("PYTEST_CURRENT_TEST") or source.get("AI_AGENT_TEST_MODE", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }:
        return PlatformRuntimeMode.TEST.value
    if source.get("IOS_COMPANION_BRIDGE_ENABLED", "").strip().lower() in {"1", "true", "yes", "on"}:
        return PlatformRuntimeMode.IOS_COMPANION_BRIDGE.value
    if source.get("WINDOWS_BRIDGE_ENABLED", "").strip().lower() in {"1", "true", "yes", "on"}:
        return PlatformRuntimeMode.WINDOWS_APP_BRIDGE.value
    if source.get("MACOS_BRIDGE_ENABLED", "").strip().lower() in {"1", "true", "yes", "on"}:
        return PlatformRuntimeMode.MAC_APP_BRIDGE.value
    if source.get("WEB_APP_BRIDGE_ENABLED", "").strip().lower() in {"1", "true", "yes", "on"}:
        return PlatformRuntimeMode.WEB_BRIDGE.value
    if source.get("AI_AGENT_PACKAGED_APP", "").strip().lower() in {"1", "true", "yes", "on"}:
        return PlatformRuntimeMode.PACKAGED_APP.value
    return PlatformRuntimeMode.CLI.value


def detect_platform(
    platform_name: str | None = None,
    *,
    env: Mapping[str, str] | None = None,
    runtime_mode: str | None = None,
    cache_seconds: int | None = None,
    now: float | None = None,
) -> PlatformDetectionResult:
    """Return safe platform metadata without native imports or personal reads."""

    global _DETECTION_CACHE

    use_cache = platform_name is None and env is None and runtime_mode is None
    current_time = time.monotonic() if now is None else now
    if cache_seconds is None:
        cache_seconds = load_platform_config(env).platform_detection_cache_seconds

    if use_cache and cache_seconds > 0 and _DETECTION_CACHE is not None:
        cached_at, cached_for, cached = _DETECTION_CACHE
        if cached_for == cache_seconds and current_time - cached_at <= cache_seconds:
            return cached

    result = _detect_platform_uncached(platform_name, env=env, runtime_mode=runtime_mode)
    if use_cache and cache_seconds > 0:
        _DETECTION_CACHE = (current_time, float(cache_seconds), result)
    return result


def _detect_platform_uncached(
    platform_name: str | None,
    *,
    env: Mapping[str, str] | None,
    runtime_mode: str | None,
) -> PlatformDetectionResult:
    try:
        raw = _safe_lower(platform_name if platform_name is not None else sys.platform)
        if raw.startswith("darwin"):
            platform = PlatformKind.MACOS
            status = PlatformStatus.AVAILABLE
        elif raw.startswith(("win32", "cygwin", "msys", "windows", "win")):
            platform = PlatformKind.WINDOWS
            status = PlatformStatus.AVAILABLE
        elif raw.startswith("linux"):
            platform = PlatformKind.LINUX
            status = PlatformStatus.AVAILABLE
        else:
            platform = PlatformKind.UNKNOWN
            status = PlatformStatus.UNKNOWN

        detected_runtime = runtime_mode or detect_runtime_mode(env)
        setup_hint = (
            ""
            if platform is not PlatformKind.UNKNOWN
            else "Unknown platform; platform bridge capabilities remain unsupported."
        )
        return PlatformDetectionResult(
            platform=platform,
            status=status,
            runtime_mode=detected_runtime,
            detected_by="sys.platform",
            setup_hint=setup_hint,
            personal_data_accessed=False,
            native_modules_imported=(),
        )
    except Exception as exc:  # pragma: no cover - defensive fail-closed path
        return PlatformDetectionResult(
            platform=PlatformKind.UNKNOWN,
            status=PlatformStatus.UNKNOWN,
            runtime_mode=runtime_mode or PlatformRuntimeMode.CLI.value,
            detected_by="sys.platform",
            setup_hint="Platform detection failed; platform bridge capabilities remain unsupported.",
            warnings=(f"platform_detection_failed:{type(exc).__name__}",),
            personal_data_accessed=False,
            native_modules_imported=(),
        )


def _safe_lower(value: object) -> str:
    try:
        return str(value or "").lower()
    except Exception:
        return ""
