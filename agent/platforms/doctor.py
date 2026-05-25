from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping
from typing import Any

from agent.platforms.bridge_registry import PlatformBridgeRegistry, default_bridge_registry
from agent.platforms.config import PlatformConfig, load_platform_config
from agent.platforms.detection import detect_platform
from agent.platforms.models import PlatformCapability, PlatformCapabilityStatus, PlatformKind, PlatformStatus
from agent.platforms.registry import PlatformCapabilityRegistry, default_registry


BRIDGE_DEFINITIONS: tuple[dict[str, str], ...] = (
    {
        "bridge_id": "macos_bridge",
        "platform": PlatformKind.MACOS.value,
        "enabled_field": "macos_bridge_enabled",
        "docs_path": "docs/platforms/PLATFORM_BRIDGE_STRATEGY.md",
        "setup_hint": "Future macOS bridge is disabled and not implemented. CLI-only mode remains available.",
    },
    {
        "bridge_id": "ios_companion_bridge",
        "platform": PlatformKind.IOS_COMPANION.value,
        "enabled_field": "ios_companion_bridge_enabled",
        "docs_path": "docs/platforms/PLATFORM_BRIDGE_STRATEGY.md",
        "setup_hint": "Future iOS companion bridge is disabled and not implemented.",
    },
    {
        "bridge_id": "windows_bridge",
        "platform": PlatformKind.WINDOWS.value,
        "enabled_field": "windows_bridge_enabled",
        "docs_path": "docs/platforms/PLATFORM_BRIDGE_STRATEGY.md",
        "setup_hint": "Future Windows bridge is disabled and not implemented.",
    },
    {
        "bridge_id": "web_app_bridge",
        "platform": PlatformKind.WEB.value,
        "enabled_field": "web_app_bridge_enabled",
        "docs_path": "docs/platforms/APP_BRIDGE_API.md",
        "setup_hint": "Future app/web bridge is disabled and not implemented.",
    },
)

FUTURE_WEB_BRIDGE_CAPABILITIES: tuple[str, ...] = (
    "app_bridge.status",
    "app_bridge.pending_actions",
    "app_bridge.submit_approval",
    "app_bridge.audit_summary",
    "app_bridge.connector_status",
)

READ_ONLY_SAFETY_FLAGS = {
    "read_only": True,
    "personal_data_accessed": False,
    "permissions_requested": False,
    "platform_actions_executed": False,
    "native_modules_imported": [],
    "network_calls": False,
    "subprocesses_started": False,
    "app_bridge_server_started": False,
    "secrets_redacted": True,
    "memory_written": False,
}


def build_platform_doctor(
    *,
    env: Mapping[str, str] | None = None,
    platform_name: str | None = None,
    capability_registry: PlatformCapabilityRegistry | None = None,
    bridge_registry: PlatformBridgeRegistry | None = None,
) -> dict[str, Any]:
    config = load_platform_config(env)
    detection = detect_platform(platform_name, env=env, cache_seconds=config.platform_detection_cache_seconds)
    capabilities = capability_registry or default_registry()
    bridges = bridge_registry or default_bridge_registry()
    bridge_summary = _bridge_summary(config, capabilities, bridges)
    capability_summary = _capability_summary(capabilities.all())

    warnings = list(config.warnings)
    warnings.extend(detection.warnings)
    if not config.platform_bridges_enabled:
        warnings.append("Platform bridges are disabled by default.")
    if detection.platform is PlatformKind.UNKNOWN:
        warnings.append("Detected platform is unknown; platform bridge support remains unsupported.")

    return {
        "status": "ok",
        "detected_platform": detection.to_dict(),
        "runtime_mode": detection.runtime_mode,
        "bridge_mode": config.platform_bridge_mode.value,
        "bridge_registry": bridge_summary,
        "available_bridges": bridge_summary["available_bridges"],
        "unavailable_bridges": bridge_summary["unavailable_bridges"],
        "planned_capabilities": capability_summary["planned_capabilities"],
        "disabled_capabilities": capability_summary["disabled_capabilities"],
        "capability_summary": capability_summary,
        "config_status": config.to_dict(),
        "performance": {
            "lazy_load_bridges": config.platform_lazy_load_bridges,
            "platform_specific_imports_at_startup": False,
            "status_checks_are_metadata_only": True,
            "detection_cache_seconds": config.platform_detection_cache_seconds,
        },
        "warnings": warnings,
        "next_setup_steps": _next_setup_steps(config),
        **READ_ONLY_SAFETY_FLAGS,
    }


def build_platform_status(
    *,
    env: Mapping[str, str] | None = None,
    platform_name: str | None = None,
    capability_registry: PlatformCapabilityRegistry | None = None,
) -> dict[str, Any]:
    config = load_platform_config(env)
    detection = detect_platform(platform_name, env=env, cache_seconds=config.platform_detection_cache_seconds)
    capabilities = capability_registry or default_registry()
    by_status = Counter(capability.status.value for capability in capabilities.all())
    return {
        "status": "ok",
        "platform": detection.platform.value,
        "platform_status": detection.status.value,
        "runtime_mode": detection.runtime_mode,
        "bridge_mode": config.platform_bridge_mode.value,
        "bridges_enabled": config.platform_bridges_enabled,
        "lazy_load_bridges": config.platform_lazy_load_bridges,
        "registered_capability_count": len(capabilities.all()),
        "capability_status_counts": dict(sorted(by_status.items())),
        "summary": "Platform bridges are metadata-only, disabled/lazy by default, and no platform actions executed.",
        **READ_ONLY_SAFETY_FLAGS,
    }


def list_platform_capabilities(
    *,
    capability_registry: PlatformCapabilityRegistry | None = None,
) -> dict[str, Any]:
    capabilities = capability_registry or default_registry()
    rows = [_capability_row(capability) for capability in capabilities.all()]
    return {
        "status": "ok",
        "capability_count": len(rows),
        "capabilities": rows,
        **READ_ONLY_SAFETY_FLAGS,
    }


def build_platform_matrix(
    *,
    capability_registry: PlatformCapabilityRegistry | None = None,
) -> dict[str, Any]:
    capabilities = capability_registry or default_registry()
    rows: list[dict[str, Any]] = []
    for platform in (PlatformKind.MACOS, PlatformKind.IOS_COMPANION, PlatformKind.WINDOWS, PlatformKind.WEB):
        platform_capabilities = list(capabilities.by_platform(platform))
        counts = Counter(capability.status.value for capability in platform_capabilities)
        row = {
            "platform": platform.value,
            "capability_count": len(platform_capabilities),
            "status_counts": dict(sorted(counts.items())),
            "capabilities": [capability.capability_id for capability in platform_capabilities],
            "default_enabled_count": sum(1 for capability in platform_capabilities if capability.default_enabled),
            "approval_required_count": sum(1 for capability in platform_capabilities if capability.approval_required),
            "setup_hint": _matrix_setup_hint(platform, platform_capabilities),
        }
        if platform is PlatformKind.WEB and not platform_capabilities:
            row["future_capabilities"] = list(FUTURE_WEB_BRIDGE_CAPABILITIES)
            row["status_counts"] = {"planned_contract": len(FUTURE_WEB_BRIDGE_CAPABILITIES)}
        rows.append(row)
    return {
        "status": "ok",
        "columns": [
            "platform",
            "capability_count",
            "status_counts",
            "default_enabled_count",
            "approval_required_count",
            "setup_hint",
        ],
        "rows": rows,
        "note": "Matrix is capability metadata only. Planned/stubbed records are not executable.",
        **READ_ONLY_SAFETY_FLAGS,
    }


def explain_platform_capability(
    capability_id: str,
    *,
    capability_registry: PlatformCapabilityRegistry | None = None,
) -> dict[str, Any]:
    capabilities = capability_registry or default_registry()
    capability = capabilities.get(capability_id)
    payload = capability.to_dict()
    payload.update(
        {
            "status": "ok" if capability.status is not PlatformCapabilityStatus.UNSUPPORTED else "not_found",
            "executable": False,
            "toolbroker_mapping_required_before_execution": True,
            "policy_engine_required_before_execution": True,
            "audit_required_before_execution": True,
            "approval_gate": capability.approval_required,
            **READ_ONLY_SAFETY_FLAGS,
        }
    )
    return payload


def _capability_row(capability: PlatformCapability) -> dict[str, Any]:
    return {
        "capability_id": capability.capability_id,
        "platform": capability.platform.value,
        "status": capability.status.value,
        "risk_level": capability.risk_level.value,
        "trust_level": capability.trust_level.value,
        "approval_required": capability.approval_required,
        "default_enabled": capability.default_enabled,
        "provider": capability.provider,
        "setup_hint": capability.setup_hint,
        "docs_path": capability.docs_path,
    }


def _capability_summary(capabilities: tuple[PlatformCapability, ...]) -> dict[str, Any]:
    by_status = Counter(capability.status.value for capability in capabilities)
    by_platform: dict[str, int] = defaultdict(int)
    for capability in capabilities:
        by_platform[capability.platform.value] += 1
    return {
        "capability_count": len(capabilities),
        "by_status": dict(sorted(by_status.items())),
        "by_platform": dict(sorted(by_platform.items())),
        "planned_capabilities": [
            capability.capability_id
            for capability in capabilities
            if capability.status is PlatformCapabilityStatus.PLANNED
        ],
        "disabled_capabilities": [
            capability.capability_id
            for capability in capabilities
            if not capability.default_enabled
        ],
        "requires_approval_capabilities": [
            capability.capability_id
            for capability in capabilities
            if capability.approval_required
        ],
    }


def _bridge_summary(
    config: PlatformConfig,
    capability_registry: PlatformCapabilityRegistry,
    bridge_registry: PlatformBridgeRegistry,
) -> dict[str, Any]:
    available: list[dict[str, Any]] = []
    unavailable: list[dict[str, Any]] = []
    registered_platforms = bridge_registry.list_registered_platforms()
    loaded_bridges = bridge_registry.list_loaded_bridges()
    loaded_bridge_ids = {bridge.bridge_id() for bridge in loaded_bridges}

    for definition in BRIDGE_DEFINITIONS:
        platform = PlatformKind(definition["platform"])
        bridge_enabled = bool(getattr(config, definition["enabled_field"]))
        enabled = config.platform_bridges_enabled and bridge_enabled
        status = PlatformStatus.REQUIRES_SETUP if enabled and platform in registered_platforms else PlatformStatus.DISABLED
        capabilities = capability_registry.by_platform(platform)
        record = {
            "bridge_id": definition["bridge_id"],
            "platform": platform.value,
            "status": status.value,
            "enabled": enabled,
            "default_enabled": False,
            "lazy_load_module": _lazy_load_module(platform),
            "stub_registered": platform in registered_platforms,
            "loaded": definition["bridge_id"] in loaded_bridge_ids,
            "capability_count": len(capabilities),
            "capabilities": [capability.capability_id for capability in capabilities],
            "setup_hint": definition["setup_hint"],
            "docs_path": definition["docs_path"],
        }
        if status is PlatformStatus.AVAILABLE:
            available.append(record)
        else:
            unavailable.append(record)

    return {
        "status": "metadata_only",
        "platform_bridges_enabled": config.platform_bridges_enabled,
        "lazy_load_bridges": config.platform_lazy_load_bridges,
        "registered_loader_count": len(registered_platforms),
        "registered_platforms": [platform.value for platform in registered_platforms],
        "loaded_bridge_count": len(loaded_bridges),
        "loaded_bridges": [bridge.bridge_id() for bridge in loaded_bridges],
        "available_bridges": available,
        "unavailable_bridges": unavailable,
    }


def _next_setup_steps(config: PlatformConfig) -> list[str]:
    steps = [
        "Keep using CLI-only mode; platform bridges are not required.",
        "Before future execution, add capability manifest entries and ToolBroker mappings.",
        "Add bridge stubs and tests before real platform implementations.",
    ]
    if not config.platform_bridges_enabled:
        steps.append("Leave PLATFORM_BRIDGES_ENABLED=false until a future bridge milestone explicitly enables a tested path.")
    return steps


def _matrix_setup_hint(platform: PlatformKind, capabilities: list[PlatformCapability]) -> str:
    if platform is PlatformKind.WEB and not capabilities:
        return "Future app/web bridge capability records are pending the App Bridge API contract milestone."
    if not capabilities:
        return "No platform capability records are registered."
    return "All listed records are metadata only; planned/stubbed capabilities are not executable."


def _lazy_load_module(platform: PlatformKind) -> str:
    modules = {
        PlatformKind.MACOS: "agent.platforms.macos.bridge",
        PlatformKind.IOS_COMPANION: "agent.platforms.ios_companion.bridge",
        PlatformKind.WINDOWS: "agent.platforms.windows.bridge",
        PlatformKind.WEB: "agent.platforms.web_bridge.bridge",
    }
    return modules.get(platform, "future")
