from __future__ import annotations

import json
from typing import Any

import httpx

from agent.brain.config import BrainRuntimeConfig
from agent.brain.providers.ollama import OllamaBrainProvider, OllamaConfig
from agent.brain.registry import default_registry
from agent.ui import cli_commands


class FakeOllamaHTTPClient:
    def __init__(self, *, timeout: float) -> None:
        self.timeout = timeout

    def __enter__(self) -> "FakeOllamaHTTPClient":
        return self

    def __exit__(self, *args) -> None:
        return None

    def get(self, url: str):
        return httpx.Response(
            200,
            json={"models": [{"name": "llama3.2:latest"}]},
            request=httpx.Request("GET", url),
        )

    def post(self, url: str, *, json: dict[str, Any]):
        self.payload = json
        return httpx.Response(
            200,
            json={
                "model": json["model"],
                "choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": "ollama reply"}}],
            },
            request=httpx.Request("POST", url),
        )


def enabled_config(**overrides: Any) -> OllamaConfig:
    values = {
        "enabled": True,
        "base_url": "http://localhost:11434",
        "model": "llama3.2:latest",
        "openai_compat_base_url": "http://localhost:11434/v1",
        "timeout_seconds": 3,
        "supports_tool_calls": False,
        "supports_streaming": False,
    }
    values.update(overrides)
    return OllamaConfig(**values)


def test_missing_model_returns_setup_hint() -> None:
    provider = OllamaBrainProvider(OllamaConfig(enabled=True))

    health = provider.health_check()
    response = provider.chat([{"role": "user", "content": "hello"}])

    assert health.status == "requires_setup"
    assert response.ok is False
    assert response.error.error_code == "provider_not_configured"
    assert "OLLAMA_MODEL" in str(response.error)
    assert response.error.setup_hint


def test_health_mock_success(monkeypatch) -> None:
    monkeypatch.setattr(httpx, "Client", FakeOllamaHTTPClient)
    provider = OllamaBrainProvider(enabled_config())

    health = provider.health_check()

    assert health.status == "ok"
    assert health.model_count == 1


def test_daemon_unavailable_handled(monkeypatch) -> None:
    class FailingHTTPClient(FakeOllamaHTTPClient):
        def get(self, url: str):
            raise httpx.ConnectError("down", request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx, "Client", FailingHTTPClient)
    provider = OllamaBrainProvider(enabled_config())

    health = provider.health_check()

    assert health.available is False
    assert health.error.error_code == "daemon_unavailable"


def test_no_tool_chat_mock_works(monkeypatch) -> None:
    monkeypatch.setattr(httpx, "Client", FakeOllamaHTTPClient)
    provider = OllamaBrainProvider(enabled_config())

    response = provider.chat([{"role": "user", "content": "hello"}])

    assert response.ok is True
    assert response.message.content == "ollama reply"
    assert response.provider_id == "ollama"


def test_malformed_response_handled(monkeypatch) -> None:
    class MalformedHTTPClient(FakeOllamaHTTPClient):
        def post(self, url: str, *, json: dict[str, Any]):
            return httpx.Response(200, json={"not_choices": []}, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "Client", MalformedHTTPClient)
    provider = OllamaBrainProvider(enabled_config())

    response = provider.chat([{"role": "user", "content": "hello"}])

    assert response.ok is False
    assert response.error.error_code == "malformed_response"


def test_tool_call_unsupported_path_fails_closed() -> None:
    provider = OllamaBrainProvider(enabled_config(supports_tool_calls=False))

    response = provider.chat(
        [{"role": "user", "content": "time?"}],
        tools=[{"type": "function", "function": {"name": "time.get_current_time", "parameters": {}}}],
    )

    assert response.ok is False
    assert response.error.error_code == "tool_calls_unsupported"


def test_provider_registry_lists_ollama_disabled_by_default() -> None:
    registry = default_registry(BrainRuntimeConfig.from_env({}))
    statuses = {status.provider_id: status for status in registry.list_provider_status()}

    assert "ollama" in statuses
    assert statuses["ollama"].status == "disabled"


def test_brain_health_and_doctor_provider_cli(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "agent.brain.status.build_brain_registry",
        lambda env=None: default_registry(
            BrainRuntimeConfig.from_env(
                {
                    "OLLAMA_ENABLED": "true",
                    "OLLAMA_MODEL": "llama3.2:latest",
                    "OLLAMA_BASE_URL": "http://localhost:11434",
                    "OLLAMA_OPENAI_COMPAT_BASE_URL": "http://localhost:11434/v1",
                }
            )
        ),
    )
    monkeypatch.setattr(httpx, "Client", FakeOllamaHTTPClient)

    assert cli_commands.dispatch_cli(["brain", "doctor", "--provider", "ollama"]) == 0
    doctor = json.loads(capsys.readouterr().out)
    assert doctor["health"]["providers"][0]["provider_id"] == "ollama"

    assert cli_commands.dispatch_cli(["brain", "health", "--provider", "ollama"]) == 0
    health = json.loads(capsys.readouterr().out)
    assert health["provider"]["status"] == "ok"
