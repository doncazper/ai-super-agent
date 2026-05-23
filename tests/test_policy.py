from __future__ import annotations

import pytest

from agent.config.loader import load_capabilities_config
from agent.config.schema import CapabilityConfigError, validate_capabilities_config
from agent.safety.policy import Capability, PolicyDecision, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry


def manifest_entry(
    name: str,
    *,
    risk_level: str = "LOW",
    trust_level: str = "MODEL_OUTPUT",
    default_enabled: bool = True,
    approval_required: bool | str = False,
    approval_reuse_allowed: bool = True,
    connector_name: str | None = None,
    rate_limit: dict[str, int] | None = None,
    memory_behavior: str = "no_store",
    requires_web_access: bool = False,
) -> dict[str, object]:
    entry: dict[str, object] = {
        "capability_name": name,
        "tool_name": name,
        "connector_name": connector_name,
        "risk_level": risk_level,
        "trust_level": trust_level,
        "default_enabled": default_enabled,
        "approval_required": approval_required,
        "approval_reuse_allowed": approval_reuse_allowed,
        "stores_data": False,
        "rate_limit": rate_limit,
        "memory_behavior": memory_behavior,
        "audit_fields": ["tool_name", "policy_decision"],
        "setup_hint": "test setup hint",
        "docs_reference": "README.md",
    }
    if requires_web_access:
        entry["requires_web_access"] = True
    return entry


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
            "critical.test": manifest_entry(
                "critical.test",
                risk_level="CRITICAL",
                trust_level="MODEL_OUTPUT",
                default_enabled=True,
                approval_required="per_action",
                approval_reuse_allowed=True,
            )
        }
    }

    with pytest.raises(CapabilityConfigError):
        validate_capabilities_config(config)


def test_validator_rejects_high_without_approval() -> None:
    config = {
        "tools": {
            "email.read_selected_thread": manifest_entry(
                "email.read_selected_thread",
                risk_level="HIGH",
                trust_level="UNTRUSTED_EMAIL",
                default_enabled=False,
                approval_required=False,
                connector_name="email",
            )
        }
    }

    with pytest.raises(CapabilityConfigError):
        validate_capabilities_config(config)


def test_capability_manifest_has_required_hardening_metadata() -> None:
    config = load_capabilities_config()

    validate_capabilities_config(config)

    for name, entry in config["tools"].items():
        assert name
        assert entry["capability_name"] == name
        assert entry["tool_name"] == name
        assert "connector_name" in entry
        assert "risk_level" in entry
        assert "default_enabled" in entry
        assert "approval_required" in entry
        assert "approval_reuse_allowed" in entry
        assert "stores_data" in entry
        assert "trust_level" in entry
        assert "rate_limit" in entry
        assert "memory_behavior" in entry
        assert "audit_fields" in entry
        assert "setup_hint" in entry
        assert "docs_reference" in entry
        assert "tool_name" in entry["audit_fields"]
        assert "policy_decision" in entry["audit_fields"]
        if name.startswith(("web.", "weather.")):
            assert "network_domains" in entry["audit_fields"]
        if entry.get("requires_web_access"):
            assert entry["rate_limit"]["requests_per_minute"] > 0


def test_registered_tools_have_manifest_entries() -> None:
    config = load_capabilities_config()
    registry = default_registry()

    missing = sorted(set(registry._tools) - set(config["tools"]))

    assert missing == []


def test_personal_data_capabilities_disabled_by_default_in_manifest() -> None:
    config = load_capabilities_config()

    for name, entry in config["tools"].items():
        if entry.get("connector_name") in {"calendar", "contacts", "email", "messages", "browser"}:
            assert entry["default_enabled"] is False, name


def test_critical_capabilities_are_per_action_in_manifest() -> None:
    config = load_capabilities_config()

    for name, entry in config["tools"].items():
        if entry["risk_level"] == "CRITICAL":
            assert entry["approval_required"] == "per_action", name
            assert entry["approval_reuse_allowed"] is False, name


def test_validator_rejects_missing_trust_level_and_audit_fields() -> None:
    config = {
        "tools": {
            "time.get_current_time": manifest_entry("time.get_current_time", risk_level="SAFE")
        }
    }
    del config["tools"]["time.get_current_time"]["trust_level"]

    with pytest.raises(CapabilityConfigError, match="missing trust_level"):
        validate_capabilities_config(config)

    config["tools"]["time.get_current_time"]["trust_level"] = "MODEL_OUTPUT"
    del config["tools"]["time.get_current_time"]["audit_fields"]
    with pytest.raises(CapabilityConfigError, match="audit_fields"):
        validate_capabilities_config(config)


def test_validator_rejects_web_capability_without_rate_limit() -> None:
    config = {
        "tools": {
            "web.fetch_url": manifest_entry(
                "web.fetch_url",
                risk_level="MEDIUM",
                trust_level="UNTRUSTED_WEB",
                connector_name="web",
                requires_web_access=True,
            )
        }
    }

    with pytest.raises(CapabilityConfigError, match="rate limits"):
        validate_capabilities_config(config)


def test_validator_rejects_missing_risk_level() -> None:
    entry = manifest_entry("time.get_current_time", risk_level="SAFE")
    del entry["risk_level"]

    with pytest.raises(CapabilityConfigError, match="missing risk_level"):
        validate_capabilities_config({"tools": {"time.get_current_time": entry}})


def test_validator_rejects_missing_approval_rule() -> None:
    entry = manifest_entry("time.get_current_time", risk_level="SAFE")
    del entry["approval_required"]

    with pytest.raises(CapabilityConfigError, match="approval_required"):
        validate_capabilities_config({"tools": {"time.get_current_time": entry}})


def test_validator_rejects_personal_capability_enabled_by_default() -> None:
    config = {
        "tools": {
            "calendar.read_date_range": manifest_entry(
                "calendar.read_date_range",
                risk_level="HIGH",
                trust_level="LOCAL_PRIVATE_DATA",
                default_enabled=True,
                approval_required=True,
                connector_name="calendar",
            )
        }
    }

    with pytest.raises(CapabilityConfigError, match="personal-data capabilities must be disabled"):
        validate_capabilities_config(config)


def test_validator_rejects_bypass_flags() -> None:
    entry = manifest_entry("web.search", trust_level="UNTRUSTED_WEB", connector_name="web")
    entry["bypass_policy"] = True

    with pytest.raises(CapabilityConfigError, match="bypass flags"):
        validate_capabilities_config({"tools": {"web.search": entry}})
