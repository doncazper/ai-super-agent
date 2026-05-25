from __future__ import annotations

import pytest

from agent.runtime.errors import RuntimeUnavailableError
from agent.runtime.feature_flags import FeatureFlagRegistry
from agent.runtime.models import RuntimeFeatureStatus, RuntimeServiceInfo
from agent.runtime.service_registry import ServiceRegistry


def test_default_services_register_without_loading() -> None:
    loaded: list[str] = []
    registry = ServiceRegistry()
    registry.register(RuntimeServiceInfo("example", "Example"), loader=lambda: loaded.append("loaded"))

    assert registry.list_services()[0].service_id == "example"
    assert loaded == []


def test_disabled_service_cannot_load() -> None:
    registry = ServiceRegistry()
    registry.register(RuntimeServiceInfo("bridge", "Bridge", enabled_by_default=False), loader=lambda: object())

    with pytest.raises(RuntimeUnavailableError, match="disabled"):
        registry.load("bridge")


def test_default_feature_flags_keep_personal_disabled() -> None:
    registry = FeatureFlagRegistry()

    assert not registry.is_enabled("email.send")
    assert not registry.is_enabled("personal.read")
    assert registry.get("scheduler.background").status == RuntimeFeatureStatus.BLOCKED


def test_risky_feature_enable_requires_explicit_policy_path() -> None:
    registry = FeatureFlagRegistry()

    with pytest.raises(Exception, match="cannot enable risky"):
        registry.set_status("email.send", RuntimeFeatureStatus.ENABLED)

