from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping


class RiskLevel(StrEnum):
    SAFE = "SAFE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    FORBIDDEN = "FORBIDDEN"


class PolicyDecision(StrEnum):
    ALLOW = "ALLOW"
    ASK = "ASK"
    DENY = "DENY"


@dataclass(frozen=True)
class Capability:
    name: str
    risk_level: RiskLevel
    default_enabled: bool = True
    approval_required: bool | str = False
    stores_data: bool = False
    approval_reuse_allowed: bool = True
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class PolicyResult:
    decision: PolicyDecision
    capability: Capability | None
    reason: str


class PolicyEngine:
    """Small M0 policy engine with deny-by-default behavior."""

    def __init__(self, capabilities: Mapping[str, Capability] | None = None) -> None:
        self._capabilities = dict(capabilities or default_capabilities())

    @classmethod
    def from_config(cls, config: Mapping[str, object]) -> "PolicyEngine":
        tools = config.get("tools")
        if not isinstance(tools, Mapping):
            raise ValueError("capabilities config must contain a tools object")

        capabilities: dict[str, Capability] = {}
        for name, entry in tools.items():
            if not isinstance(name, str) or not isinstance(entry, Mapping):
                raise ValueError("invalid capability entry")
            capabilities[name] = Capability(
                name=name,
                risk_level=RiskLevel(str(entry["risk_level"])),
                default_enabled=bool(entry.get("default_enabled", False)),
                approval_required=entry.get("approval_required", False),
                stores_data=bool(entry.get("stores_data", False)),
                approval_reuse_allowed=bool(entry.get("approval_reuse_allowed", True)),
                metadata={key: value for key, value in entry.items() if key not in {
                    "risk_level",
                    "default_enabled",
                    "approval_required",
                    "stores_data",
                    "approval_reuse_allowed",
                }},
            )
        return cls(capabilities)

    def evaluate(self, capability_name: str) -> PolicyResult:
        capability = self._capabilities.get(capability_name)
        if capability is None:
            return PolicyResult(PolicyDecision.DENY, None, "unknown capability")
        if not capability.default_enabled:
            return PolicyResult(PolicyDecision.DENY, capability, "capability disabled")
        if capability.risk_level is RiskLevel.FORBIDDEN:
            return PolicyResult(PolicyDecision.DENY, capability, "forbidden capability")
        if capability.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
            return PolicyResult(PolicyDecision.ASK, capability, "approval required")
        if capability.approval_required:
            return PolicyResult(PolicyDecision.ASK, capability, "approval required")
        return PolicyResult(PolicyDecision.ALLOW, capability, "allowed")


def default_capabilities() -> dict[str, Capability]:
    return {
        "time.get_current_time": Capability(
            name="time.get_current_time",
            risk_level=RiskLevel.SAFE,
            default_enabled=True,
            approval_required=False,
            stores_data=False,
        )
    }
