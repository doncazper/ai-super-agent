from __future__ import annotations

import pytest

from agent.config.schema import CapabilityConfigError, validate_capabilities_config
from agent.safety.policy import Capability, PolicyDecision, PolicyEngine, RiskLevel


def test_unknown_capability_denied() -> None:
    result = PolicyEngine().evaluate("nope.missing")

    assert result.decision is PolicyDecision.DENY
    assert result.reason == "unknown capability"


def test_safe_action_allowed() -> None:
    result = PolicyEngine().evaluate("time.get_current_time")

    assert result.decision is PolicyDecision.ALLOW


def test_high_action_asks_approval_when_enabled() -> None:
    engine = PolicyEngine(
        {
            "email.read_selected_thread": Capability(
                name="email.read_selected_thread",
                risk_level=RiskLevel.HIGH,
                default_enabled=True,
                approval_required=True,
            )
        }
    )

    result = engine.evaluate("email.read_selected_thread")

    assert result.decision is PolicyDecision.ASK


def test_critical_action_asks_per_action_when_enabled() -> None:
    engine = PolicyEngine(
        {
            "email.send": Capability(
                name="email.send",
                risk_level=RiskLevel.CRITICAL,
                default_enabled=True,
                approval_required="per_action",
                approval_reuse_allowed=False,
            )
        }
    )

    result = engine.evaluate("email.send")

    assert result.decision is PolicyDecision.ASK


def test_forbidden_action_denied() -> None:
    engine = PolicyEngine(
        {
            "secrets.read": Capability(
                name="secrets.read",
                risk_level=RiskLevel.FORBIDDEN,
                default_enabled=True,
            )
        }
    )

    result = engine.evaluate("secrets.read")

    assert result.decision is PolicyDecision.DENY


def test_validator_rejects_critical_approval_reuse() -> None:
    config = {
        "tools": {
            "email.send": {
                "risk_level": "CRITICAL",
                "default_enabled": True,
                "approval_required": "per_action",
                "approval_reuse_allowed": True,
            }
        }
    }

    with pytest.raises(CapabilityConfigError):
        validate_capabilities_config(config)


def test_validator_rejects_high_without_approval() -> None:
    config = {
        "tools": {
            "email.read_selected_thread": {
                "risk_level": "HIGH",
                "default_enabled": True,
                "approval_required": False,
            }
        }
    }

    with pytest.raises(CapabilityConfigError):
        validate_capabilities_config(config)
