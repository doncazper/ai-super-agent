from __future__ import annotations

import pytest

from agent.config.loader import load_capabilities_config
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


def test_capability_manifest_has_required_hardening_metadata() -> None:
    config = load_capabilities_config()

    validate_capabilities_config(config)

    for name, entry in config["tools"].items():
        assert name
        assert "risk_level" in entry
        assert "default_enabled" in entry
        assert "approval_required" in entry
        assert "stores_data" in entry
        assert "trust_level" in entry
        assert "audit_fields" in entry
        assert "tool_name" in entry["audit_fields"]
        assert "policy_decision" in entry["audit_fields"]
        if name.startswith("web."):
            assert "network_domains" in entry["audit_fields"]
        if entry.get("requires_web_access"):
            assert entry["rate_limit"]["requests_per_minute"] > 0


def test_validator_rejects_missing_trust_level_and_audit_fields() -> None:
    config = {
        "tools": {
            "time.get_current_time": {
                "risk_level": "SAFE",
                "default_enabled": True,
                "approval_required": False,
                "stores_data": False,
            }
        }
    }

    with pytest.raises(CapabilityConfigError, match="missing trust_level"):
        validate_capabilities_config(config)

    config["tools"]["time.get_current_time"]["trust_level"] = "MODEL_OUTPUT"
    with pytest.raises(CapabilityConfigError, match="audit_fields"):
        validate_capabilities_config(config)


def test_validator_rejects_web_capability_without_rate_limit() -> None:
    config = {
        "tools": {
            "web.fetch_url": {
                "risk_level": "MEDIUM",
                "default_enabled": True,
                "approval_required": False,
                "stores_data": False,
                "trust_level": "UNTRUSTED_WEB",
                "audit_fields": ["tool_name", "policy_decision", "network_domains"],
                "requires_web_access": True,
            }
        }
    }

    with pytest.raises(CapabilityConfigError, match="rate limits"):
        validate_capabilities_config(config)
