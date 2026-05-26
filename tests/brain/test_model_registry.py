from __future__ import annotations

import importlib
import sys

import pytest

from agent.brain.config import BrainRuntimeConfig
from agent.brain.errors import BrainProviderNotFoundError, normalize_provider_error
from agent.brain.mock_provider import MockBrainProvider
from agent.brain.registry import BrainProviderRegistration, BrainProviderRegistry, default_registry, make_mock_registration


def test_registry_loads_registered_providers_lazily() -> None:
    created = {"count": 0}

    def factory() -> MockBrainProvider:
        created["count"] += 1
        return MockBrainProvider()

    registry = BrainProviderRegistry(
        [BrainProviderRegistration(provider_id="mock", provider_name="Mock", factory=factory, setup_hint="test only")],
        config=BrainRuntimeConfig(default_provider="mock", provider_order=("mock",)),
    )

    providers = registry.list_providers()
    assert providers[0].provider_id == "mock"
    assert created["count"] == 0
    assert registry.provider_status("mock").status == "registered_lazy"
    assert created["count"] == 0

    assert registry.default_provider().provider_id() == "mock"
    assert created["count"] == 1
    assert registry.provider_status("mock").available is True


def test_unknown_provider_is_structured_and_require_provider_raises() -> None:
    registry = BrainProviderRegistry(config=BrainRuntimeConfig())

    status = registry.provider_status("missing-provider")
    assert status.registered is False
    assert status.status == "unknown"
    assert status.setup_hint
    assert registry.get_provider("missing-provider") is None
    with pytest.raises(BrainProviderNotFoundError):
        registry.require_provider("missing-provider")


def test_default_provider_is_configurable() -> None:
    registry = BrainProviderRegistry(
        [make_mock_registration()],
        config=BrainRuntimeConfig(default_provider="mock", provider_order=("mock",), mock_provider_enabled=True),
    )

    assert registry.default_provider().provider_id() == "mock"


def test_config_defaults_preserve_lmstudio_and_disable_fallback() -> None:
    config = BrainRuntimeConfig.from_env({})

    assert config.default_provider == "lmstudio"
    assert config.provider_order[:3] == ("lmstudio", "llama_cpp_server", "ollama")
    assert config.fallback_enabled is False
    assert config.mock_provider_enabled is False
    assert config.provider_health_timeout_seconds == 5.0


def test_default_registry_only_enables_mock_when_configured_for_tests() -> None:
    registry = default_registry(BrainRuntimeConfig.from_env({}))
    assert [provider.provider_id for provider in registry.list_providers()] == [
        "lmstudio",
        "llama_cpp_server",
        "ollama",
        "llama_cpp_inprocess",
        "mlx",
    ]
    assert registry.provider_status("lmstudio").status == "registered_lazy"
    assert registry.provider_status("llama_cpp_server").status == "disabled"
    assert registry.provider_status("ollama").status == "disabled"
    assert registry.provider_status("llama_cpp_inprocess").status == "disabled"

    registry = default_registry(
        BrainRuntimeConfig.from_env({"BRAIN_DEFAULT_PROVIDER": "mock", "BRAIN_MOCK_PROVIDER_ENABLED": "true"})
    )

    assert [provider.provider_id for provider in registry.list_providers()] == [
        "lmstudio",
        "llama_cpp_server",
        "ollama",
        "llama_cpp_inprocess",
        "mlx",
        "mock",
    ]
    assert registry.default_provider().provider_id() == "mock"


def test_health_summary_uses_mock_provider_only_when_explicit() -> None:
    registry = BrainProviderRegistry(
        [make_mock_registration(MockBrainProvider(response_text="ok"))],
        config=BrainRuntimeConfig(default_provider="mock", provider_order=("mock",), mock_provider_enabled=True),
    )

    summary = registry.health_summary()

    assert summary["default_provider_id"] == "mock"
    assert summary["default_provider_registered"] is True
    assert summary["providers"][0]["provider_id"] == "mock"
    assert summary["providers"][0]["status"] == "ok"


def test_provider_error_normalization() -> None:
    normalized = normalize_provider_error(ValueError("bad provider response"), provider_id="mock")

    assert normalized.provider_id == "mock"
    assert normalized.error_code == "ValueError"
    assert normalized.to_dict()["message"] == "bad provider response"


def test_registry_import_does_not_import_heavy_runtime_modules() -> None:
    for module_name in ("agent.core.lmstudio_client", "ollama", "llama_cpp", "mlx"):
        sys.modules.pop(module_name, None)

    importlib.reload(importlib.import_module("agent.brain.registry"))

    assert "agent.core.lmstudio_client" not in sys.modules
    assert "ollama" not in sys.modules
    assert "llama_cpp" not in sys.modules
    assert "mlx" not in sys.modules
