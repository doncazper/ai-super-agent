from __future__ import annotations

from typing import Any

from agent.safety.policy import RiskLevel


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
        if risk is RiskLevel.FORBIDDEN and default_enabled:
            raise CapabilityConfigError(f"{name}: forbidden capabilities cannot be enabled")
        if risk is RiskLevel.CRITICAL:
            if approval_required != "per_action":
                raise CapabilityConfigError(f"{name}: critical capabilities require per_action approval")
            if entry.get("approval_reuse_allowed", False):
                raise CapabilityConfigError(f"{name}: critical capabilities cannot reuse approvals")
        if risk is RiskLevel.HIGH and approval_required is not True:
            raise CapabilityConfigError(f"{name}: high-risk capabilities require approval")
