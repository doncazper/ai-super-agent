from __future__ import annotations

import json
from typing import Any

from agent.brain.providers.lmstudio import LMStudioBrainProvider, brain_response_to_openai
from agent.brain.status import brain_doctor, brain_providers, brain_status
from agent.core.lmstudio_client import LMStudioConfig, LMStudioError
from agent.ui import cli_commands


class FakeLMStudioClient:
    def __init__(self, raw_response: dict[str, Any] | None = None, error: LMStudioError | None = None) -> None:
        self.config = LMStudioConfig(model="qwopus", temperature=0.2, top_p=0.9, max_tokens=64)
        self.raw_response = raw_response or {
            "choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": "hello"}}],
            "model": "qwopus",
        }
        self.error = error
        self.calls: list[dict[str, Any]] = []

    def chat(self, messages: list[dict[str, Any]], *, tools=None) -> dict[str, Any]:
        self.calls.append({"messages": messages, "tools": tools})
        if self.error is not None:
            raise self.error
        return self.raw_response


def test_lmstudio_provider_request_format_matches_existing_payload() -> None:
    fake = FakeLMStudioClient()
    provider = LMStudioBrainProvider(client=fake)

    response = provider.chat([{"role": "user", "content": "hello"}])

    assert response.ok is True
    assert fake.calls == [{"messages": [{"role": "user", "content": "hello"}], "tools": None}]
    assert response.message.content == "hello"
    assert response.provider_id == "lmstudio"


def test_lmstudio_provider_tool_call_normalization_roundtrips_to_openai_shape() -> None:
    fake = FakeLMStudioClient(
        {
            "choices": [
                {
                    "finish_reason": "tool_calls",
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_time",
                                "type": "function",
                                "function": {"name": "time.get_current_time", "arguments": "{\"timezone\": \"UTC\"}"},
                            }
                        ],
                    },
                }
            ],
            "model": "qwopus",
        }
    )
    provider = LMStudioBrainProvider(client=fake)

    response = provider.chat(
        [{"role": "user", "content": "time?"}],
        tools=[{"type": "function", "function": {"name": "time.get_current_time", "parameters": {}}}],
    )
    openai_response = brain_response_to_openai(response)

    assert response.tool_calls[0].name == "time.get_current_time"
    assert response.tool_calls[0].arguments == {"timezone": "UTC"}
    assert json.loads(openai_response["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"]) == {
        "timezone": "UTC"
    }


def test_lmstudio_provider_preserves_malformed_tool_arguments_for_toolbroker() -> None:
    fake = FakeLMStudioClient(
        {
            "choices": [
                {
                    "finish_reason": "tool_calls",
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_bad",
                                "type": "function",
                                "function": {"name": "time.get_current_time", "arguments": "{not-json"},
                            }
                        ],
                    },
                }
            ]
        }
    )
    provider = LMStudioBrainProvider(client=fake)

    response = provider.chat([{"role": "user", "content": "time?"}], tools=[{"function": {"name": "time.get_current_time"}}])
    openai_response = brain_response_to_openai(response)

    assert response.tool_calls[0].raw_arguments == "{not-json"
    assert openai_response["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"] == "{not-json"


def test_missing_lmstudio_model_error_remains_clear() -> None:
    provider = LMStudioBrainProvider(config=LMStudioConfig(model=""))

    response = provider.chat([{"role": "user", "content": "hello"}])

    assert response.ok is False
    assert "LMSTUDIO_MODEL is not set" in str(response.error)
    assert response.error.setup_hint


def test_server_unavailable_error_is_normalized_without_losing_message() -> None:
    provider = LMStudioBrainProvider(client=FakeLMStudioClient(error=LMStudioError("LM Studio server not reachable at http://localhost:1234/v1.")))

    response = provider.chat([{"role": "user", "content": "hello"}])

    assert response.ok is False
    assert "server not reachable" in str(response.error)
    assert response.error.provider_id == "lmstudio"


def test_brain_registry_and_doctor_include_lmstudio_without_model_generation() -> None:
    providers = brain_providers({"BRAIN_DEFAULT_PROVIDER": "lmstudio"})
    status = brain_status({"BRAIN_DEFAULT_PROVIDER": "lmstudio"})
    doctor = brain_doctor({"BRAIN_DEFAULT_PROVIDER": "lmstudio"})

    assert providers["providers"][0]["provider_id"] == "lmstudio"
    assert providers["providers"][0]["status"] == "registered_lazy"
    assert status["default_provider"]["provider_id"] == "lmstudio"
    assert status["no_model_call_performed"] is True
    assert doctor["health"]["providers"][0]["provider_id"] == "lmstudio"
    assert doctor["safety"]["no_tool_execution"] is True


def test_brain_cli_status_and_doctor(capsys) -> None:
    assert cli_commands.dispatch_cli(["brain", "providers"]) == 0
    providers = json.loads(capsys.readouterr().out)
    assert providers["providers"][0]["provider_id"] == "lmstudio"

    assert cli_commands.dispatch_cli(["brain", "status"]) == 0
    status = json.loads(capsys.readouterr().out)
    assert status["default_provider"]["provider_id"] == "lmstudio"

    assert cli_commands.dispatch_cli(["brain", "doctor"]) == 0
    doctor = json.loads(capsys.readouterr().out)
    assert doctor["safety"]["no_model_generation"] is True
