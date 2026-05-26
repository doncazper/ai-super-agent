from __future__ import annotations

import json
import sys

from agent.brain.config import BrainRuntimeConfig
from agent.brain.providers.mlx import MLXBrainProvider, MLXProviderConfig
from agent.brain.registry import default_registry
from agent.ui import cli_commands


def test_mlx_stub_lists_provider_disabled_by_default() -> None:
    registry = default_registry(BrainRuntimeConfig.from_env({}))
    status = registry.provider_status("mlx")

    assert status.registered is True
    assert status.status == "disabled"


def test_mlx_stub_disabled_setup_hint() -> None:
    provider = MLXBrainProvider(MLXProviderConfig())

    health = provider.health_check()
    response = provider.chat([{"role": "user", "content": "hello"}])

    assert health.status == "disabled"
    assert health.error.error_code == "provider_disabled"
    assert response.ok is False
    assert "experimental" in response.error.setup_hint


def test_mlx_stub_enabled_missing_model_setup_hint_on_apple_silicon() -> None:
    provider = MLXBrainProvider(
        MLXProviderConfig(enabled=True, mode="server", model=""),
        apple_silicon_detector=lambda: True,
    )

    health = provider.health_check()

    assert health.status == "requires_setup"
    assert health.error.error_code == "provider_not_configured"
    assert "never downloads models" in health.error.setup_hint


def test_mlx_stub_unsupported_platform() -> None:
    provider = MLXBrainProvider(
        MLXProviderConfig(enabled=True, mode="server", model="mlx-model"),
        apple_silicon_detector=lambda: False,
    )

    health = provider.health_check()

    assert health.status == "requires_setup"
    assert health.error.error_code == "unsupported_platform"


def test_mlx_stub_does_not_import_native_mlx_or_load_model() -> None:
    sys.modules.pop("mlx", None)
    provider = MLXBrainProvider(
        MLXProviderConfig(enabled=True, mode="inprocess", model="mlx-model", load_on_startup=True),
        apple_silicon_detector=lambda: True,
    )

    health = provider.health_check()

    assert health.error.error_code == "provider_stubbed"
    assert "mlx" not in sys.modules


def test_mlx_models_include_mocked_apple_silicon_metadata() -> None:
    provider = MLXBrainProvider(
        MLXProviderConfig(enabled=True, mode="server", model="mlx-model"),
        apple_silicon_detector=lambda: True,
    )

    models = provider.list_models()

    assert len(models) == 1
    assert models[0].provider_id == "mlx"
    assert models[0].metadata["apple_silicon_detected"] is True
    assert models[0].metadata["experimental_stub"] is True


def test_brain_health_and_doctor_provider_cli_for_mlx(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "agent.brain.status.build_brain_registry",
        lambda env=None: default_registry(BrainRuntimeConfig.from_env({"MLX_PROVIDER_ENABLED": "true"})),
    )

    assert cli_commands.dispatch_cli(["brain", "doctor", "--provider", "mlx"]) == 0
    doctor = json.loads(capsys.readouterr().out)
    assert doctor["health"]["providers"][0]["provider_id"] == "mlx"
    assert doctor["health"]["providers"][0]["status"] == "requires_setup"

    assert cli_commands.dispatch_cli(["brain", "health", "--provider", "mlx"]) == 0
    health = json.loads(capsys.readouterr().out)
    assert health["provider"]["provider_id"] == "mlx"
