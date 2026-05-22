from __future__ import annotations

from typing import Any

from agent.safety.policy import RiskLevel
from agent.safety.trust import TrustLevel


class CapabilityConfigError(ValueError):
    pass


def validate_capabilities_config(config: dict[str, Any]) -> None:
    tools = config.get("tools")
    if not isinstance(tools, dict):
        raise CapabilityConfigError("capabilities config must contain a tools object")

    for name, entry in tools.items():
        if not isinstance(name, str) or not name:
            raise CapabilityConfigError("capability names must be non-empty strings")
        if not isinstance(entry, dict):
            raise CapabilityConfigError(f"{name}: entry must be an object")
        try:
            risk = RiskLevel(str(entry["risk_level"]))
        except KeyError as exc:
            raise CapabilityConfigError(f"{name}: missing risk_level") from exc
        except ValueError as exc:
            raise CapabilityConfigError(f"{name}: invalid risk_level") from exc

        default_enabled = bool(entry.get("default_enabled", False))
        approval_required = entry.get("approval_required", False)
        if "default_enabled" not in entry:
            raise CapabilityConfigError(f"{name}: missing default_enabled")
        if "approval_required" not in entry:
            raise CapabilityConfigError(f"{name}: missing approval_required")
        if "stores_data" not in entry:
            raise CapabilityConfigError(f"{name}: missing stores_data")
        if "trust_level" not in entry:
            raise CapabilityConfigError(f"{name}: missing trust_level")
        try:
            TrustLevel(str(entry["trust_level"]))
        except ValueError as exc:
            raise CapabilityConfigError(f"{name}: invalid trust_level") from exc
        audit_fields = entry.get("audit_fields")
        if not isinstance(audit_fields, list) or not all(isinstance(item, str) for item in audit_fields):
            raise CapabilityConfigError(f"{name}: audit_fields must be a list of strings")
        if bool(entry.get("requires_web_access")):
            rate_limit = entry.get("rate_limit")
            if not isinstance(rate_limit, dict) or not isinstance(rate_limit.get("requests_per_minute"), int):
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
