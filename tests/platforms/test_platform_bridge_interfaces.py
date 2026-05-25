from __future__ import annotations

import importlib
import sys
from typing import Any, Mapping

from agent.platforms.action_payloads import PlatformActionPayload, PlatformActionResult, PlatformHealthStatus
from agent.platforms.base import PlatformBridge
from agent.platforms.bridge_registry import PlatformBridgeRegistry
from agent.platforms.models import PlatformCapability, PlatformCapabilityStatus, PlatformKind, PlatformStatus
from agent.platforms.null_bridge import NullPlatformBridge
from agent.platforms.registry import default_registry
from agent.safety.trust import TrustLevel


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


class FakeBridge(PlatformBridge):
    def __init__(self) -> None:
        self.prepared = 0
        self.executed = 0

    def platform_kind(self) -> PlatformKind:
        return PlatformKind.WEB

    def bridge_id(self) -> str:
        return "fake_web_bridge"

    def is_available(self) -> bool:
        return True

    def health_check(self) -> PlatformHealthStatus:
        return PlatformHealthStatus(
            platform=PlatformKind.WEB,
            bridge_id=self.bridge_id(),
            status=PlatformStatus.AVAILABLE,
            available=True,
            personal_data_accessed=False,
            native_modules_imported=(),
        )

    def list_capabilities(self) -> tuple[PlatformCapability, ...]:
        return ()

    def get_capability_status(self, capability_id: str) -> PlatformCapabilityStatus:
        return PlatformCapabilityStatus.UNSUPPORTED

    def prepare_action(self, capability_id: str, args: Mapping[str, Any] | None = None) -> PlatformActionPayload:
        self.prepared += 1
        return PlatformActionPayload(
            capability_id=capability_id,
            platform=PlatformKind.WEB,
            bridge_id=self.bridge_id(),
            args=dict(args or {}),
            audit_correlation_id="fake-preview",
        )

    def execute_action(
        self,
        capability_id: str,
        args: Mapping[str, Any] | None = None,
        *,
        broker_context: Mapping[str, Any] | None = None,
    ) -> PlatformActionResult:
        self.executed += 1
        return PlatformActionResult(
            capability_id=capability_id,
            platform=PlatformKind.WEB,
            bridge_id=self.bridge_id(),
            status=PlatformCapabilityStatus.BLOCKED,
            success=False,
            audit_correlation_id="fake-result",
            blocked_reason="test_bridge_never_executes",
        )


def test_null_platform_bridge_works_and_fails_closed() -> None:
    bridge = NullPlatformBridge(PlatformKind.MACOS)

    assert bridge.platform_kind() is PlatformKind.MACOS
    assert bridge.bridge_id() == "null_macos_bridge"
    assert bridge.is_available() is False

    health = bridge.health_check()
    assert health.status is PlatformStatus.REQUIRES_SETUP
    assert health.available is False
    assert health.personal_data_accessed is False
    assert health.native_modules_imported == ()

    preview = bridge.prepare_action("macos.calendar.read", {"days": 1})
    assert preview.requires_toolbroker is True
    assert preview.side_effects is False
    assert preview.audit_correlation_id
    assert preview.trust_level is TrustLevel.LOCAL_PRIVATE_DATA

    result = bridge.execute_action("macos.calendar.read", {"days": 1})
    assert result.success is False
    assert result.status is PlatformCapabilityStatus.BLOCKED
    assert result.blocked_reason == "direct_bridge_execution_forbidden"
    assert result.side_effects_performed is False
    assert result.audit_correlation_id


def test_bridge_registry_returns_null_bridge_for_unavailable_platform() -> None:
    registry = PlatformBridgeRegistry()

    unknown = registry.get_bridge("beos")
    windows = registry.get_bridge(PlatformKind.WINDOWS)

    assert isinstance(unknown, NullPlatformBridge)
    assert unknown.platform_kind() is PlatformKind.UNKNOWN
    assert isinstance(windows, NullPlatformBridge)
    assert windows.platform_kind() is PlatformKind.WINDOWS


def test_bridge_registry_lazy_loads_via_mocks() -> None:
    calls = {"count": 0}

    def load_fake() -> FakeBridge:
        calls["count"] += 1
        return FakeBridge()

    registry = PlatformBridgeRegistry(loaders={PlatformKind.WEB: load_fake})

    assert registry.list_registered_platforms() == (PlatformKind.WEB,)
    assert calls["count"] == 0

    bridge = registry.get_bridge(PlatformKind.WEB)
    same_bridge = registry.get_bridge(PlatformKind.WEB)

    assert isinstance(bridge, FakeBridge)
    assert same_bridge is bridge
    assert calls["count"] == 1


def test_prepare_action_produces_no_side_effects() -> None:
    bridge = NullPlatformBridge(PlatformKind.IOS_COMPANION)

    preview = bridge.prepare_action("ios.message_compose_handoff", {"body": "hello"})

    assert preview.side_effects is False
    assert preview.requires_toolbroker is True
    assert bridge.health_check().personal_data_accessed is False


def test_execute_action_direct_call_is_guarded() -> None:
    bridge = NullPlatformBridge(PlatformKind.WINDOWS)

    result = bridge.execute_action("windows.ui_automation", {"window": "Example"})

    assert result.status is PlatformCapabilityStatus.BLOCKED
    assert result.toolbroker_routed is False
    assert result.policy_evaluated is False
    assert result.approval_checked is False
    assert result.blocked_reason == "direct_bridge_execution_forbidden"


def test_brokered_null_bridge_still_requires_setup() -> None:
    bridge = NullPlatformBridge(PlatformKind.WINDOWS)

    result = bridge.execute_action(
        "windows.platform_doctor",
        {},
        broker_context={
            "toolbroker_approved": True,
            "policy_evaluated": True,
            "approval_checked": False,
            "audit_correlation_id": "audit-123",
        },
    )

    assert result.status is PlatformCapabilityStatus.REQUIRES_SETUP
    assert result.toolbroker_routed is True
    assert result.policy_evaluated is True
    assert result.side_effects_performed is False
    assert result.audit_correlation_id == "audit-123"


def test_capability_list_maps_to_registry_records() -> None:
    bridge = NullPlatformBridge(PlatformKind.MACOS)
    expected_ids = {capability.capability_id for capability in default_registry().by_platform(PlatformKind.MACOS)}

    assert {capability.capability_id for capability in bridge.list_capabilities()} == expected_ids
    assert bridge.get_capability_status("macos.calendar.write") is PlatformCapabilityStatus.PLANNED
    assert bridge.get_capability_status("windows.platform_doctor") is PlatformCapabilityStatus.UNSUPPORTED


def test_health_check_does_not_access_personal_data() -> None:
    bridge = NullPlatformBridge(PlatformKind.UNKNOWN)

    health = bridge.health_check()

    assert health.status is PlatformStatus.UNSUPPORTED
    assert health.personal_data_accessed is False
    assert health.native_modules_imported == ()
    assert "no_personal_data_access" in health.checks


def test_no_native_imports_required_for_bridge_interfaces() -> None:
    before = set(sys.modules)
    importlib.import_module("agent.platforms.base")
    importlib.import_module("agent.platforms.null_bridge")
    importlib.import_module("agent.platforms.bridge_registry")
    imported = set(sys.modules) - before

    assert not any(
        module == prefix or module.startswith(f"{prefix}.")
        for module in imported
        for prefix in NATIVE_MODULE_PREFIXES
    )


def test_toolbroker_mapping_requirement_documented() -> None:
    strategy = open("docs/platforms/PLATFORM_BRIDGE_STRATEGY.md", encoding="utf-8").read()
    guide = open("docs/platforms/FUTURE_BRIDGE_IMPLEMENTATION_GUIDE.md", encoding="utf-8").read()

    assert "ToolBroker" in PlatformBridge.__doc__
    assert "execute_action" in PlatformBridge.execute_action.__doc__
    assert "ToolBroker" in strategy
    assert "execute_action" in guide
