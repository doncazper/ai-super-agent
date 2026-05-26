from __future__ import annotations

import json
from typing import Any

import httpx

from agent.brain.config import BrainRuntimeConfig
from agent.brain.providers.llama_cpp_server import LlamaCppServerBrainProvider, LlamaCppServerConfig
from agent.brain.registry import default_registry
from agent.brain.status import brain_doctor, brain_health
from agent.ui import cli_commands


class FakeHTTPClient:
    def __init__(self, *, timeout: float) -> None:
        self.timeout = timeout

    def __enter__(self) -> "FakeHTTPClient":
        return self

    def __exit__(self, *args) -> None:
        return None

    def get(self, url: str):
        return httpx.Response(
            200,
            json={"data": [{"id": "local-model"}]},
            request=httpx.Request("GET", url),
        )

    def post(self, url: str, *, json: dict[str, Any]):
        self.payload = json
        return httpx.Response(
            200,
            json={
                "model": json["model"],
                "choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": "local reply"}}],
            },
            request=httpx.Request("POST", url),
        )


def enabled_config(**overrides: Any) -> LlamaCppServerConfig:
    values = {
        "enabled": True,
        "base_url": "http://localhost:8080/v1",
        "model": "local-model",
        "timeout_seconds": 3,
        "supports_tool_calls": False,
        "supports_streaming": False,
    }
    values.update(overrides)
    return LlamaCppServerConfig(**values)


def test_missing_config_returns_setup_hint() -> None:
    provider = LlamaCppServerBrainProvider(LlamaCppServerConfig())

    health = provider.health_check()
    response = provider.chat([{"role": "user", "content": "hello"}])

    assert health.status == "disabled"
    assert response.ok is False
    assert "disabled" in str(response.error)
    assert response.error.setup_hint


def test_server_health_mock_success(monkeypatch) -> None:
    monkeypatch.setattr(httpx, "Client", FakeHTTPClient)
    provider = LlamaCppServerBrainProvider(enabled_config())

    health = provider.health_check()

    assert health.status == "ok"
    assert health.model_count == 1


def test_server_unavailable_handled(monkeypatch) -> None:
    class FailingHTTPClient(FakeHTTPClient):
        def get(self, url: str):
            raise httpx.ConnectError("down", request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx, "Client", FailingHTTPClient)
    provider = LlamaCppServerBrainProvider(enabled_config())

    health = provider.health_check()

    assert health.available is False
    assert health.error.error_code == "server_unavailable"


def test_no_tool_chat_mock_works(monkeypatch) -> None:
    monkeypatch.setattr(httpx, "Client", FakeHTTPClient)
    provider = LlamaCppServerBrainProvider(enabled_config())

    response = provider.chat([{"role": "user", "content": "hello"}])

    assert response.ok is True
    assert response.message.content == "local reply"
    assert response.provider_id == "llama_cpp_server"


def test_malformed_response_handled(monkeypatch) -> None:
    class MalformedHTTPClient(FakeHTTPClient):
        def post(self, url: str, *, json: dict[str, Any]):
            return httpx.Response(200, json={"not_choices": []}, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "Client", MalformedHTTPClient)
    provider = LlamaCppServerBrainProvider(enabled_config())

    response = provider.chat([{"role": "user", "content": "hello"}])

    assert response.ok is False
    assert response.error.error_code == "malformed_response"


def test_tool_call_unsupported_path_fails_closed() -> None:
    provider = LlamaCppServerBrainProvider(enabled_config(supports_tool_calls=False))

    response = provider.chat(
        [{"role": "user", "content": "time?"}],
        tools=[{"type": "function", "function": {"name": "time.get_current_time", "parameters": {}}}],
    )

    assert response.ok is False
    assert response.error.error_code == "tool_calls_unsupported"


def test_provider_registry_lists_llama_cpp_server_disabled_by_default() -> None:
    registry = default_registry(BrainRuntimeConfig.from_env({}))
    statuses = {status.provider_id: status for status in registry.list_provider_status()}

    assert "llama_cpp_server" in statuses
    assert statuses["llama_cpp_server"].status == "disabled"


def test_brain_health_and_doctor_provider_cli(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "agent.brain.status.build_brain_registry",
        lambda env=None: default_registry(
            BrainRuntimeConfig.from_env(
                {
                    "LLAMA_CPP_SERVER_ENABLED": "true",
                    "LLAMA_CPP_SERVER_MODEL": "local-model",
                    "LLAMA_CPP_SERVER_BASE_URL": "http://localhost:8080/v1",
                }
            )
        ),
    )
    monkeypatch.setattr(httpx, "Client", FakeHTTPClient)

    assert cli_commands.dispatch_cli(["brain", "doctor", "--provider", "llama_cpp_server"]) == 0
    doctor = json.loads(capsys.readouterr().out)
    assert doctor["health"]["providers"][0]["provider_id"] == "llama_cpp_server"

    assert cli_commands.dispatch_cli(["brain", "health", "--provider", "llama_cpp_server"]) == 0
    health = json.loads(capsys.readouterr().out)
    assert health["provider"]["status"] == "ok"


def test_brain_health_unknown_provider() -> None:
    payload = brain_health("missing", {})

    assert payload["status"] == "unknown_provider"
