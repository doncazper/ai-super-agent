from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

from agent.platforms.detection import clear_detection_cache
from agent.platforms.doctor import (
    build_platform_doctor,
    build_platform_matrix,
    explain_platform_capability,
    list_platform_capabilities,
)
from agent.platforms.models import PlatformKind
from agent.safety.validation import validate_startup_policy
from agent.ui.cli_commands import dispatch_cli
from agent.ui.command_registry import get_command, validate_command_registry_docs


ROOT = Path(__file__).resolve().parents[2]
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
    "msgraph",
)


def _run_cli(argv: list[str], capsys, monkeypatch, tmp_path: Path) -> tuple[int, dict]:
    clear_detection_cache()
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))
    code = dispatch_cli(argv, project_root=ROOT)
    captured = capsys.readouterr()
    assert captured.err == ""
    return int(code), json.loads(captured.out)


def test_platform_doctor_works_with_mocked_macos(monkeypatch) -> None:
    clear_detection_cache()
    monkeypatch.setattr(sys, "platform", "darwin")

    payload = build_platform_doctor()

    assert payload["detected_platform"]["platform"] == PlatformKind.MACOS.value
    assert payload["runtime_mode"] in {"cli", "test"}
    assert payload["bridge_registry"]["status"] == "metadata_only"
    assert payload["personal_data_accessed"] is False
    assert payload["permissions_requested"] is False
    assert payload["platform_actions_executed"] is False
    assert payload["native_modules_imported"] == []


def test_platform_doctor_command_works_with_mocked_windows(monkeypatch, capsys, tmp_path: Path) -> None:
    monkeypatch.setattr(sys, "platform", "win32")

    code, payload = _run_cli(["platform", "doctor"], capsys, monkeypatch, tmp_path)

    assert code == 0
    assert payload["detected_platform"]["platform"] == PlatformKind.WINDOWS.value
    assert payload["config_status"]["platform_bridges_enabled"] is False
    assert payload["network_calls"] is False
    assert payload["app_bridge_server_started"] is False


def test_platform_status_handles_unknown_platform(monkeypatch, capsys, tmp_path: Path) -> None:
    monkeypatch.setattr(sys, "platform", "plan9")

    code, payload = _run_cli(["platform", "status"], capsys, monkeypatch, tmp_path)

    assert code == 0
    assert payload["platform"] == PlatformKind.UNKNOWN.value
    assert payload["platform_status"] == "unknown"
    assert "metadata-only" in payload["summary"]


def test_platform_capabilities_lists_registry_entries(capsys, monkeypatch, tmp_path: Path) -> None:
    code, payload = _run_cli(["platform", "capabilities"], capsys, monkeypatch, tmp_path)

    assert code == 0
    assert payload["capability_count"] >= 27
    capability_ids = {row["capability_id"] for row in payload["capabilities"]}
    assert "macos.calendar.read" in capability_ids
    assert "windows.platform_doctor" in capability_ids
    assert all(row["default_enabled"] is False for row in payload["capabilities"])


def test_platform_matrix_includes_macos_ios_windows_and_web() -> None:
    payload = build_platform_matrix()

    rows = {row["platform"]: row for row in payload["rows"]}
    assert set(rows) == {"macos", "ios_companion", "windows", "web"}
    assert "macos.calendar.read" in rows["macos"]["capabilities"]
    assert "ios.message_compose_handoff" in rows["ios_companion"]["capabilities"]
    assert "windows.platform_doctor" in rows["windows"]["capabilities"]
    assert "app_bridge.status" in rows["web"]["capabilities"]
    assert "app_bridge.connector_status" in rows["web"]["capabilities"]
    assert payload["platform_actions_executed"] is False


def test_platform_explain_handles_known_capability(capsys, monkeypatch, tmp_path: Path) -> None:
    code, payload = _run_cli(["platform", "explain", "macos.calendar.read"], capsys, monkeypatch, tmp_path)

    assert code == 0
    assert payload["capability_id"] == "macos.calendar.read"
    assert payload["risk_level"] == "HIGH"
    assert payload["trust_level"] == "LOCAL_PRIVATE_DATA"
    assert payload["default_enabled"] is False
    assert payload["executable"] is False
    assert payload["toolbroker_mapping_required_before_execution"] is True


def test_platform_explain_handles_unknown_capability() -> None:
    payload = explain_platform_capability("macos.secret_backdoor")

    assert payload["status"] == "not_found"
    assert payload["capability_id"] == "macos.secret_backdoor"
    assert payload["risk_level"] == "FORBIDDEN"
    assert payload["executable"] is False


def test_platform_inspection_imports_no_native_or_heavy_modules() -> None:
    before = set(sys.modules)
    importlib.import_module("agent.tools.platform")
    build_platform_doctor(platform_name="darwin")
    list_platform_capabilities()
    imported = set(sys.modules) - before

    assert not any(
        module == prefix or module.startswith(f"{prefix}.")
        for module in imported
        for prefix in NATIVE_MODULE_PREFIXES
    )


def test_platform_commands_validate_policy_and_registry_docs() -> None:
    validate_startup_policy(ROOT / "config/capabilities.yaml")
    report = validate_command_registry_docs(ROOT)

    assert report["status"] == "ok"
    assert report["command_count"] >= 387
    for command_id in ("CMD-PLATFORM-001", "CMD-PLATFORM-002", "CMD-PLATFORM-003", "CMD-PLATFORM-004", "CMD-PLATFORM-005"):
        record = get_command(command_id)
        assert record is not None
        assert record.status == "active"
        assert record.risk_level == "SAFE"
