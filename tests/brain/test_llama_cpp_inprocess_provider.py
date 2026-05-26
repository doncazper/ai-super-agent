from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from agent.brain.config import BrainRuntimeConfig
from agent.brain.providers.llama_cpp_inprocess import LlamaCppInProcessBrainProvider, LlamaCppInProcessConfig
from agent.brain.registry import default_registry
from agent.ui import cli_commands


class FakeBackend:
    def __init__(self) -> None:
        self.calls = 0

    def create_chat_completion(self, *, messages: list[dict[str, Any]], **kwargs: Any):
        self.calls += 1
        return {
            "choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": "inprocess reply"}}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 2},
        }


def enabled_config(model_path: str = "/tmp/model.gguf", **overrides: Any) -> LlamaCppInProcessConfig:
    values = {
        "enabled": True,
        "model_path": model_path,
        "n_ctx": 8192,
        "n_gpu_layers": -1,
        "threads": "auto",
        "supports_tool_calls": False,
        "load_on_startup": False,
        "max_loaded_models": 1,
    }
    values.update(overrides)
    return LlamaCppInProcessConfig(**values)


def test_dependency_missing_returns_setup_hint() -> None:
    provider = LlamaCppInProcessBrainProvider(enabled_config(), dependency_detector=lambda: False)

    health = provider.health_check()
    response = provider.chat([{"role": "user", "content": "hello"}])

    assert health.status == "requires_setup"
    assert response.ok is False
    assert response.error.error_code == "dependency_missing"
    assert "never installs packages" in response.error.setup_hint


def test_model_path_missing_returns_setup_hint() -> None:
    provider = LlamaCppInProcessBrainProvider(enabled_config(model_path=""), dependency_detector=lambda: True)

    health = provider.health_check()
    response = provider.chat([{"role": "user", "content": "hello"}])

    assert health.status == "requires_setup"
    assert response.ok is False
    assert response.error.error_code == "provider_not_configured"


def test_lazy_import_behavior() -> None:
    sys.modules.pop("llama_cpp", None)

    provider = LlamaCppInProcessBrainProvider(
        enabled_config(),
        dependency_detector=lambda: False,
    )

    assert provider.provider_id() == "llama_cpp_inprocess"
    assert "llama_cpp" not in sys.modules


def test_no_model_load_on_provider_status() -> None:
    loaded = {"count": 0}

    def factory(config: LlamaCppInProcessConfig) -> FakeBackend:
        loaded["count"] += 1
        return FakeBackend()

    provider = LlamaCppInProcessBrainProvider(
        enabled_config(),
        dependency_detector=lambda: True,
        backend_factory=factory,
    )

    health = provider.health_check()

    assert health.status == "configured"
    assert loaded["count"] == 0


def test_mock_chat_works_via_fake_backend(tmp_path: Path) -> None:
    model_path = tmp_path / "model.gguf"
    model_path.write_text("fake", encoding="utf-8")
    backend = FakeBackend()
    provider = LlamaCppInProcessBrainProvider(
        enabled_config(str(model_path)),
        dependency_detector=lambda: True,
        backend_factory=lambda config: backend,
    )

    response = provider.chat([{"role": "user", "content": "hello"}])

    assert response.ok is True
    assert response.message.content == "inprocess reply"
    assert response.provider_id == "llama_cpp_inprocess"
    assert backend.calls == 1


def test_provider_error_normalized(tmp_path: Path) -> None:
    model_path = tmp_path / "model.gguf"
    model_path.write_text("fake", encoding="utf-8")

    def factory(config: LlamaCppInProcessConfig) -> FakeBackend:
        raise RuntimeError("backend failed")

    provider = LlamaCppInProcessBrainProvider(
        enabled_config(str(model_path)),
        dependency_detector=lambda: True,
        backend_factory=factory,
    )

    response = provider.chat([{"role": "user", "content": "hello"}])

    assert response.ok is False
    assert response.error.error_code == "RuntimeError"
    assert "backend failed" in str(response.error)


def test_provider_registry_lists_inprocess_disabled_by_default() -> None:
    registry = default_registry(BrainRuntimeConfig.from_env({}))
    statuses = {status.provider_id: status for status in registry.list_provider_status()}

    assert "llama_cpp_inprocess" in statuses
    assert statuses["llama_cpp_inprocess"].status == "disabled"


def test_brain_health_and_doctor_provider_cli(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "agent.brain.status.build_brain_registry",
        lambda env=None: default_registry(
            BrainRuntimeConfig.from_env(
                {
                    "LLAMA_CPP_INPROCESS_ENABLED": "true",
                    "LLAMA_CPP_INPROCESS_MODEL_PATH": "/tmp/model.gguf",
                }
            )
        ),
    )
    monkeypatch.setattr("agent.brain.providers.llama_cpp_inprocess._dependency_available", lambda: True)

    assert cli_commands.dispatch_cli(["brain", "doctor", "--provider", "llama_cpp_inprocess"]) == 0
    doctor = json.loads(capsys.readouterr().out)
    assert doctor["health"]["providers"][0]["provider_id"] == "llama_cpp_inprocess"
    assert doctor["health"]["providers"][0]["status"] == "configured"

    assert cli_commands.dispatch_cli(["brain", "health", "--provider", "llama_cpp_inprocess"]) == 0
    health = json.loads(capsys.readouterr().out)
    assert health["provider"]["status"] == "configured"


def test_tool_call_unsupported_path_fails_closed(tmp_path: Path) -> None:
    model_path = tmp_path / "model.gguf"
    model_path.write_text("fake", encoding="utf-8")
    provider = LlamaCppInProcessBrainProvider(
        enabled_config(str(model_path), supports_tool_calls=False),
        dependency_detector=lambda: True,
        backend_factory=lambda config: FakeBackend(),
    )

    response = provider.chat(
        [{"role": "user", "content": "time?"}],
        tools=[{"type": "function", "function": {"name": "time.get_current_time", "parameters": {}}}],
    )

    assert response.ok is False
    assert response.error.error_code == "tool_calls_unsupported"
