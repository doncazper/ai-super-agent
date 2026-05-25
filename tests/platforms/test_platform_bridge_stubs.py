from __future__ import annotations

import importlib
import sys

from agent.platforms.bridge_registry import default_bridge_registry
from agent.platforms.doctor import build_platform_doctor
from agent.platforms.models import PlatformCapabilityStatus, PlatformKind, PlatformStatus


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

BRIDGE_MODULES = {
    PlatformKind.MACOS: "agent.platforms.macos.bridge",
    PlatformKind.IOS_COMPANION: "agent.platforms.ios_companion.bridge",
    PlatformKind.WINDOWS: "agent.platforms.windows.bridge",
    PlatformKind.WEB: "agent.platforms.web_bridge.bridge",
}

EXPECTED_CAPABILITY_IDS = {
    PlatformKind.MACOS: {
        "macos.calendar.read",
        "macos.calendar.write",
        "macos.contacts.search",
        "macos.contacts.update",
        "macos.file_picker",
        "macos.security_scoped_bookmark",
        "macos.messages.probe",
        "macos.notifications",
    },
    PlatformKind.IOS_COMPANION: {
        "ios.message_compose_handoff",
        "ios.mobile_approval",
        "ios.notification",
        "ios.quick_action",
        "ios.pairing",
    },
    PlatformKind.WINDOWS: {
        "windows.platform_doctor",
        "windows.file_picker",
        "windows.notifications",
        "windows.ui_automation",
        "microsoft_graph.mail",
        "microsoft_graph.calendar",
        "microsoft_graph.contacts",
        "windows.outlook_bridge",
        "windows.teams_bridge",
    },
    PlatformKind.WEB: {
        "app_bridge.status",
        "app_bridge.pending_actions",
        "app_bridge.submit_approval",
        "app_bridge.audit_summary",
        "app_bridge.connector_status",
    },
}


def _unload_stub_bridge_modules() -> None:
    for module_name in BRIDGE_MODULES.values():
        sys.modules.pop(module_name, None)


def _assert_no_native_imports(imported: set[str]) -> None:
    assert not any(
        module == prefix or module.startswith(f"{prefix}.")
        for module in imported
        for prefix in NATIVE_MODULE_PREFIXES
    )


def test_default_registry_registers_stub_loaders_without_loading_modules() -> None:
    _unload_stub_bridge_modules()

    registry = default_bridge_registry()

    assert set(registry.list_registered_platforms()) == set(BRIDGE_MODULES)
    assert registry.list_loaded_bridges() == ()
    assert not any(module_name in sys.modules for module_name in BRIDGE_MODULES.values())


def test_each_stub_loads_lazily_and_declares_capabilities() -> None:
    for platform, module_name in BRIDGE_MODULES.items():
        _unload_stub_bridge_modules()
        registry = default_bridge_registry()

        assert module_name not in sys.modules
        bridge = registry.get_bridge(platform)

        assert module_name in sys.modules
        assert bridge.platform_kind() is platform
        assert bridge.is_available() is False
        assert {capability.capability_id for capability in bridge.list_capabilities()} == EXPECTED_CAPABILITY_IDS[platform]


def test_stub_actions_return_setup_or_blocked_without_side_effects() -> None:
    registry = default_bridge_registry()

    for platform, capability_ids in EXPECTED_CAPABILITY_IDS.items():
        bridge = registry.get_bridge(platform)
        capability_id = sorted(capability_ids)[0]

        health = bridge.health_check()
        assert health.status is PlatformStatus.REQUIRES_SETUP
        assert health.personal_data_accessed is False
        assert health.native_modules_imported == ()

        preview = bridge.prepare_action(capability_id, {"sample": True})
        assert preview.requires_toolbroker is True
        assert preview.side_effects is False
        assert preview.metadata["bridge_available"] is False

        direct = bridge.execute_action(capability_id, {"sample": True})
        assert direct.status is PlatformCapabilityStatus.BLOCKED
        assert direct.blocked_reason == "direct_bridge_execution_forbidden"
        assert direct.side_effects_performed is False

        brokered = bridge.execute_action(
            capability_id,
            {"sample": True},
            broker_context={
                "toolbroker_approved": True,
                "policy_evaluated": True,
                "approval_checked": True,
                "audit_correlation_id": "audit-stub",
            },
        )
        assert brokered.status is PlatformCapabilityStatus.REQUIRES_SETUP
        assert brokered.toolbroker_routed is True
        assert brokered.policy_evaluated is True
        assert brokered.approval_checked is True
        assert brokered.side_effects_performed is False
        assert brokered.audit_correlation_id == "audit-stub"


def test_stub_imports_do_not_import_native_modules_or_access_personal_data() -> None:
    _unload_stub_bridge_modules()
    before = set(sys.modules)
    registry = default_bridge_registry()
    for platform in BRIDGE_MODULES:
        bridge = registry.get_bridge(platform)
        assert bridge.health_check().personal_data_accessed is False
    imported = set(sys.modules) - before

    _assert_no_native_imports(imported)


def test_bridge_registry_can_list_stubs_and_platform_doctor_displays_them() -> None:
    _unload_stub_bridge_modules()

    registry = default_bridge_registry()
    payload = build_platform_doctor(bridge_registry=registry)

    assert payload["bridge_registry"]["registered_loader_count"] == 4
    assert set(payload["bridge_registry"]["registered_platforms"]) == {
        "ios_companion",
        "macos",
        "web",
        "windows",
    }
    assert payload["bridge_registry"]["loaded_bridge_count"] == 0
    assert all(record["stub_registered"] is True for record in payload["unavailable_bridges"])
    assert any(record["lazy_load_module"] == "agent.platforms.macos.bridge" for record in payload["unavailable_bridges"])
    assert payload["platform_actions_executed"] is False
    assert payload["personal_data_accessed"] is False


def test_import_time_overhead_remains_low_for_bridge_registry_module() -> None:
    _unload_stub_bridge_modules()

    importlib.import_module("agent.platforms.bridge_registry")

    assert not any(module_name in sys.modules for module_name in BRIDGE_MODULES.values())
