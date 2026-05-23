from __future__ import annotations

from typing import Any

from agent.safety.policy import RiskLevel
from agent.safety.trust import TrustLevel


class CapabilityConfigError(ValueError):
    pass


REQUIRED_CAPABILITY_FIELDS = {
    "capability_name",
    "tool_name",
    "connector_name",
    "risk_level",
    "trust_level",
    "default_enabled",
    "approval_required",
    "approval_reuse_allowed",
    "rate_limit",
    "memory_behavior",
    "audit_fields",
    "setup_hint",
    "docs_reference",
}

PERSONAL_CONNECTORS = {"calendar", "contacts", "email", "messages", "browser", "tasks"}
VALID_MEMORY_BEHAVIORS = {
    "no_store",
    "cache_only",
    "stores_project_data",
    "stores_personal_with_approval",
    "workspace_write",
    "draft_only_no_send",
    "forbidden",
}
FORBIDDEN_FLAG_MARKERS = {"bypass", "skip_policy", "skip_audit", "disable_audit", "ignore_policy"}


def validate_capabilities_config(config: dict[str, Any]) -> None:
    tools = config.get("tools")
    if not isinstance(tools, dict):
        raise CapabilityConfigError("capabilities config must contain a tools object")

    for name, entry in tools.items():
        if not isinstance(name, str) or not name:
            raise CapabilityConfigError("capability names must be non-empty strings")
        if not isinstance(entry, dict):
            raise CapabilityConfigError(f"{name}: entry must be an object")
        _reject_bypass_flags(name, entry)
        for field_name in ("risk_level", "trust_level", "approval_required", "audit_fields"):
            if field_name not in entry:
                raise CapabilityConfigError(f"{name}: missing {field_name}")
        missing_fields = sorted(REQUIRED_CAPABILITY_FIELDS - set(entry))
        if missing_fields:
            raise CapabilityConfigError(f"{name}: missing required fields: {', '.join(missing_fields)}")
        if entry.get("capability_name") != name:
            raise CapabilityConfigError(f"{name}: capability_name must match capability key")
        if entry.get("tool_name") != name:
            raise CapabilityConfigError(f"{name}: tool_name must match capability key")
        connector_name = entry.get("connector_name")
        if connector_name is not None and not isinstance(connector_name, str):
            raise CapabilityConfigError(f"{name}: connector_name must be a string or null")
        try:
            risk = RiskLevel(str(entry["risk_level"]))
        except KeyError as exc:
            raise CapabilityConfigError(f"{name}: missing risk_level") from exc
        except ValueError as exc:
            raise CapabilityConfigError(f"{name}: invalid risk_level") from exc

        default_enabled = bool(entry.get("default_enabled", False))
        approval_required = entry.get("approval_required", False)
        if not isinstance(entry.get("default_enabled"), bool):
            raise CapabilityConfigError(f"{name}: default_enabled must be boolean")
        if approval_required not in {False, True, "per_action"}:
            raise CapabilityConfigError(f"{name}: approval_required must be false, true, or per_action")
        if not isinstance(entry.get("approval_reuse_allowed"), bool):
            raise CapabilityConfigError(f"{name}: approval_reuse_allowed must be boolean")
        if "stores_data" not in entry:
            raise CapabilityConfigError(f"{name}: missing stores_data")
        if not isinstance(entry.get("stores_data"), bool):
            raise CapabilityConfigError(f"{name}: stores_data must be boolean")
        if "trust_level" not in entry:
            raise CapabilityConfigError(f"{name}: missing trust_level")
        try:
            TrustLevel(str(entry["trust_level"]))
        except ValueError as exc:
            raise CapabilityConfigError(f"{name}: invalid trust_level") from exc
        memory_behavior = entry.get("memory_behavior")
        if memory_behavior not in VALID_MEMORY_BEHAVIORS:
            raise CapabilityConfigError(f"{name}: invalid memory_behavior")
        audit_fields = entry.get("audit_fields")
        if not isinstance(audit_fields, list) or not all(isinstance(item, str) for item in audit_fields):
            raise CapabilityConfigError(f"{name}: audit_fields must be a list of strings")
        if "tool_name" not in audit_fields or "policy_decision" not in audit_fields:
            raise CapabilityConfigError(f"{name}: audit_fields must include tool_name and policy_decision")
        rate_limit = entry.get("rate_limit")
        if rate_limit is not None:
            if not isinstance(rate_limit, dict) or not isinstance(rate_limit.get("requests_per_minute"), int):
                raise CapabilityConfigError(f"{name}: rate_limit must be null or contain integer requests_per_minute")
            if rate_limit["requests_per_minute"] <= 0:
                raise CapabilityConfigError(f"{name}: requests_per_minute must be positive")
        if not isinstance(entry.get("setup_hint"), str) or not entry["setup_hint"].strip():
            raise CapabilityConfigError(f"{name}: setup_hint must be a non-empty string")
        if not isinstance(entry.get("docs_reference"), str) or not entry["docs_reference"].strip():
            raise CapabilityConfigError(f"{name}: docs_reference must be a non-empty string")
        if bool(entry.get("requires_web_access")):
            if rate_limit is None:
                raise CapabilityConfigError(f"{name}: network capabilities require requests_per_minute rate limits")
        if risk is RiskLevel.FORBIDDEN and default_enabled:
            raise CapabilityConfigError(f"{name}: forbidden capabilities cannot be enabled")
        if risk is RiskLevel.CRITICAL:
            if approval_required != "per_action":
                raise CapabilityConfigError(f"{name}: critical capabilities require per_action approval")
            if entry.get("approval_reuse_allowed", False):
                raise CapabilityConfigError(f"{name}: critical capabilities cannot reuse approvals")
        if risk is RiskLevel.HIGH and approval_required is not True:
            raise CapabilityConfigError(f"{name}: high-risk capabilities require approval")
        if connector_name in PERSONAL_CONNECTORS and default_enabled:
            raise CapabilityConfigError(f"{name}: personal-data capabilities must be disabled by default")


def _reject_bypass_flags(name: str, value: Any, path: str = "") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower()
            if any(marker in normalized for marker in FORBIDDEN_FLAG_MARKERS):
                suffix = f".{key}" if path else str(key)
                raise CapabilityConfigError(f"{name}: bypass flags are not allowed: {suffix}")
            _reject_bypass_flags(name, item, f"{path}.{key}" if path else str(key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_bypass_flags(name, item, f"{path}[{index}]")
