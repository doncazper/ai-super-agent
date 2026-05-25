import importlib
import sys

from agent.platforms.detection import detect_platform
from agent.platforms.models import PlatformCapabilityStatus, PlatformKind
from agent.platforms.registry import PlatformCapabilityRegistry, default_registry
from agent.safety.policy import RiskLevel
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


def test_registry_loads_on_any_os() -> None:
    registry = default_registry()

    assert isinstance(registry, PlatformCapabilityRegistry)
    assert len(registry.all()) >= 27
    assert "macos.calendar.read" in registry.ids()
    assert "windows.platform_doctor" in registry.ids()
    assert "app_bridge.status" in registry.ids()


def test_unknown_platform_returns_structured_unsupported_record() -> None:
    capabilities = default_registry().by_platform("beos")

    assert len(capabilities) == 1
    record = capabilities[0]
    assert record.platform is PlatformKind.UNKNOWN
    assert record.status is PlatformCapabilityStatus.UNSUPPORTED
    assert record.default_enabled is False
    assert "Unknown platform" in record.setup_hint


def test_unknown_capability_returns_structured_not_found_record() -> None:
    capability = default_registry().get("macos.secret_backdoor")

    assert capability.capability_id == "macos.secret_backdoor"
    assert capability.platform is PlatformKind.UNKNOWN
    assert capability.status is PlatformCapabilityStatus.UNSUPPORTED
    assert capability.risk_level is RiskLevel.FORBIDDEN
    assert capability.default_enabled is False
    assert "Unknown platform capability" in capability.name


def test_lookup_by_platform_and_capability_id() -> None:
    registry = default_registry()

    macos = registry.by_platform(PlatformKind.MACOS)
    assert {cap.capability_id for cap in macos} >= {
        "macos.calendar.read",
        "macos.calendar.write",
        "macos.contacts.search",
        "macos.contacts.update",
    }

    capability = registry.get("ios.message_compose_handoff")
    assert capability.platform is PlatformKind.IOS_COMPANION
    assert capability.risk_level is RiskLevel.CRITICAL
    assert capability.approval_required == "per_action"


def test_every_capability_has_required_fields() -> None:
    for capability in default_registry().all():
        payload = capability.to_dict()
        assert payload["capability_id"]
        assert payload["platform"] in {kind.value for kind in PlatformKind}
        assert payload["name"]
        assert payload["description"]
        assert payload["status"] in {status.value for status in PlatformCapabilityStatus}
        assert payload["risk_level"] in {risk.value for risk in RiskLevel}
        assert payload["trust_level"] in {trust.value for trust in TrustLevel}
        assert payload["default_enabled"] is False
        assert "approval_required" in payload
        assert payload["provider"]
        assert payload["setup_hint"]
        assert payload["docs_path"]
        assert "performance_notes" in payload


def test_planned_personal_data_capabilities_default_disabled() -> None:
    personal_capabilities = [
        capability
        for capability in default_registry().all()
        if capability.trust_level
        in {
            TrustLevel.LOCAL_PRIVATE_DATA,
            TrustLevel.UNTRUSTED_EMAIL,
            TrustLevel.UNTRUSTED_MESSAGE,
        }
    ]

    assert personal_capabilities
    assert all(capability.default_enabled is False for capability in personal_capabilities)


def test_critical_capabilities_require_per_action_approval() -> None:
    critical_capabilities = [
        capability for capability in default_registry().all() if capability.risk_level is RiskLevel.CRITICAL
    ]

    assert critical_capabilities
    assert all(capability.approval_required == "per_action" for capability in critical_capabilities)


def test_registry_import_does_not_import_native_platform_modules() -> None:
    before = set(sys.modules)
    importlib.import_module("agent.platforms.registry")
    importlib.import_module("agent.platforms.capabilities")
    after = set(sys.modules)
    imported = after - before

    assert not any(
        module == prefix or module.startswith(f"{prefix}.")
        for module in imported
        for prefix in NATIVE_MODULE_PREFIXES
    )


def test_detection_is_safe_and_mockable_without_personal_data() -> None:
    macos = detect_platform("darwin")
    windows = detect_platform("win32")
    linux = detect_platform("linux")
    unknown = detect_platform("weird-os")

    assert macos.platform is PlatformKind.MACOS
    assert windows.platform is PlatformKind.WINDOWS
    assert linux.platform is PlatformKind.LINUX
    assert unknown.platform is PlatformKind.UNKNOWN
    assert macos.personal_data_accessed is False
    assert windows.native_modules_imported == ()
