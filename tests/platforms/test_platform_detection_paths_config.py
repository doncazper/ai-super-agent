from __future__ import annotations

import importlib
import sys
from pathlib import Path

from agent.platforms.config import PlatformBridgeMode, PlatformRuntimeMode, load_platform_config
from agent.platforms.detection import clear_detection_cache, detect_platform, detect_runtime_mode
from agent.platforms.models import PlatformKind, PlatformStatus
from agent.platforms.paths import get_platform_paths


NATIVE_MODULE_PREFIXES = (
    "AppKit",
    "CalendarStore",
    "Contacts",
    "EventKit",
    "Foundation",
    "ScriptingBridge",
    "objc",
    "pywinauto",
    "win32com",
    "win32gui",
    "uiautomation",
)


def test_macos_windows_linux_detection_mocked() -> None:
    assert detect_platform("darwin").platform is PlatformKind.MACOS
    assert detect_platform("win32").platform is PlatformKind.WINDOWS
    assert detect_platform("linux").platform is PlatformKind.LINUX


def test_unknown_platform_is_structured_and_does_not_crash() -> None:
    result = detect_platform("plan9")

    assert result.platform is PlatformKind.UNKNOWN
    assert result.status is PlatformStatus.UNKNOWN
    assert result.personal_data_accessed is False
    assert result.native_modules_imported == ()
    assert "unsupported" in result.setup_hint


def test_runtime_mode_defaults_to_cli_and_test_can_be_forced() -> None:
    assert detect_runtime_mode({}) == PlatformRuntimeMode.CLI.value
    assert detect_runtime_mode({"PLATFORM_RUNTIME_MODE": "test"}) == PlatformRuntimeMode.TEST.value
    assert detect_runtime_mode({"AI_AGENT_TEST_MODE": "true"}) == PlatformRuntimeMode.TEST.value


def test_detection_cache_can_be_bypassed_for_explicit_platforms(monkeypatch) -> None:
    clear_detection_cache()
    monkeypatch.setattr(sys, "platform", "darwin")
    first = detect_platform(cache_seconds=300, now=1)

    monkeypatch.setattr(sys, "platform", "win32")
    cached = detect_platform(cache_seconds=300, now=2)
    explicit = detect_platform("win32", cache_seconds=300, now=2)

    assert first.platform is PlatformKind.MACOS
    assert cached.platform is PlatformKind.MACOS
    assert explicit.platform is PlatformKind.WINDOWS


def test_detection_cache_expires(monkeypatch) -> None:
    clear_detection_cache()
    monkeypatch.setattr(sys, "platform", "darwin")
    first = detect_platform(cache_seconds=10, now=1)

    monkeypatch.setattr(sys, "platform", "linux")
    expired = detect_platform(cache_seconds=10, now=20)

    assert first.platform is PlatformKind.MACOS
    assert expired.platform is PlatformKind.LINUX


def test_safe_paths_are_project_local_without_scanning_personal_data(tmp_path: Path, monkeypatch) -> None:
    def fail_home() -> Path:
        raise AssertionError("Path.home must not be used by platform path helpers")

    monkeypatch.setattr(Path, "home", fail_home)

    paths = get_platform_paths(project_root=tmp_path, platform=PlatformKind.MACOS, runtime_mode="test")

    assert paths.platform is PlatformKind.MACOS
    assert paths.runtime_mode == "test"
    assert paths.config_dir == tmp_path / "config"
    assert paths.workspace_dir == tmp_path / "workspace"
    assert paths.reports_dir == tmp_path / "reports"
    assert str(paths.platform_state_dir).startswith(str(tmp_path))
    assert paths.personal_data_scanned is False
    assert paths.directories_created is False
    assert not paths.platform_state_dir.exists()


def test_windows_paths_are_metadata_only_and_do_not_over_apply_policy(tmp_path: Path) -> None:
    paths = get_platform_paths(project_root=tmp_path, platform="windows")

    assert paths.platform is PlatformKind.WINDOWS
    assert paths.platform_state_dir == tmp_path / "workspace" / "platform_state" / "windows"
    assert paths.warnings
    assert "existing filesystem policy" in paths.warnings[0].lower()


def test_config_defaults_are_safe() -> None:
    config = load_platform_config({})

    assert config.platform_bridges_enabled is False
    assert config.platform_bridge_mode is PlatformBridgeMode.AUTO
    assert config.platform_detection_cache_seconds == 300
    assert config.platform_lazy_load_bridges is True
    assert config.macos_bridge_enabled is False
    assert config.ios_companion_bridge_enabled is False
    assert config.windows_bridge_enabled is False
    assert config.web_app_bridge_enabled is False


def test_invalid_config_values_fall_back_to_safe_defaults() -> None:
    config = load_platform_config(
        {
            "PLATFORM_BRIDGES_ENABLED": "definitely",
            "PLATFORM_BRIDGE_MODE": "superuser",
            "PLATFORM_DETECTION_CACHE_SECONDS": "-5",
            "PLATFORM_LAZY_LOAD_BRIDGES": "maybe",
        }
    )

    assert config.platform_bridges_enabled is False
    assert config.platform_bridge_mode is PlatformBridgeMode.AUTO
    assert config.platform_detection_cache_seconds == 300
    assert config.platform_lazy_load_bridges is True
    assert len(config.warnings) == 4


def test_secret_env_vars_are_not_exposed_in_platform_config_metadata() -> None:
    config = load_platform_config(
        {
            "PLATFORM_BRIDGES_ENABLED": "false",
            "BRAVE_SEARCH_API_KEY": "sk-secret",
            "REDDIT_CLIENT_SECRET": "reddit-secret",
        }
    )
    payload = config.to_dict()

    assert "BRAVE_SEARCH_API_KEY" not in payload
    assert "REDDIT_CLIENT_SECRET" not in payload
    assert "sk-secret" not in str(payload)
    assert "reddit-secret" not in str(payload)


def test_startup_import_does_not_import_native_bridge_modules() -> None:
    before = set(sys.modules)
    importlib.import_module("agent.platforms.config")
    importlib.import_module("agent.platforms.detection")
    importlib.import_module("agent.platforms.paths")
    imported = set(sys.modules) - before

    assert not any(
        module == prefix or module.startswith(f"{prefix}.")
        for module in imported
        for prefix in NATIVE_MODULE_PREFIXES
    )
