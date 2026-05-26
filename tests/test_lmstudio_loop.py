from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from agent.core.lmstudio_client import LMStudioConfig, LMStudioClient, LMStudioError
from agent.core.orchestrator import MINIMAL_SYSTEM_PROMPT, Orchestrator, format_debug_payload
from agent.core.tool_broker import ToolBroker
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry
from agent.brain.providers.lmstudio import LMStudioBrainProvider


class FakeClient:
    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self.config = LMStudioConfig(model="q")
        self.responses = responses
        self.calls: list[dict[str, Any]] = []

    def chat(self, messages: list[dict[str, Any]], *, tools=None) -> dict[str, Any]:
        self.calls.append({"messages": list(messages), "tools": tools})
        return self.responses.pop(0)


def response(message: dict[str, Any]) -> dict[str, Any]:
    return {"choices": [{"message": message}]}


class FakeWeatherProvider:
    name = "fake-weather"

    def is_configured(self) -> bool:
        return True

    def current_weather(self, location: str, units: str, locale: str | None = None) -> dict[str, Any]:
        return {
            "location": location,
            "current": {"temperature": 72, "condition": "clear", "rain": 0},
        }

    def forecast(
        self,
        location: str,
        days: int,
        units: str,
        locale: str | None = None,
        include_hourly: bool = False,
    ) -> dict[str, Any]:
        return {"location": location, "forecast": []}

    def alerts(self, location: str, locale: str | None = None) -> dict[str, Any]:
        return {"location": location, "alerts": []}


def make_orchestrator(fake_client: FakeClient, tmp_path, *, weather_provider=None) -> Orchestrator:
    registry = default_registry(weather_provider=weather_provider)
    capabilities = None
    if weather_provider is not None:
        capabilities = {
            "time.get_current_time": Capability("time.get_current_time", RiskLevel.SAFE),
            "weather.current": Capability("weather.current", RiskLevel.LOW, metadata={"requires_web_access": True}),
            "weather.forecast": Capability("weather.forecast", RiskLevel.LOW, metadata={"requires_web_access": True}),
            "weather.alerts": Capability("weather.alerts", RiskLevel.LOW, metadata={"requires_web_access": True}),
            "web.search": Capability("web.search", RiskLevel.LOW, metadata={"requires_web_access": True}),
        }
    broker = ToolBroker(
        registry,
        PolicyEngine(capabilities),
        AuditLogger(tmp_path / "audit.jsonl"),
        session_id="test-session",
        model="test-model",
        route="test",
    )
    return Orchestrator(fake_client, registry, broker)


def test_lmstudio_payload_omits_tools_when_none() -> None:
    client = LMStudioClient(LMStudioConfig(model="q"))

    payload = client.build_payload([{"role": "user", "content": "hello"}], tools=None)

    assert "tools" not in payload
    assert payload["model"] == "q"
    assert payload["max_tokens"] >= 2048


def test_missing_lmstudio_model_has_user_friendly_error() -> None:
    with pytest.raises(LMStudioError, match="LMSTUDIO_MODEL is not set"):
        LMStudioClient(LMStudioConfig(model=""))


def test_malformed_lmstudio_response_has_user_friendly_error(monkeypatch) -> None:
    class FakeHTTPClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args) -> None:
            pass

        def post(self, *args, **kwargs):
            return httpx.Response(
                200,
                json={"not_choices": []},
                request=httpx.Request("POST", "http://localhost:1234/v1/chat/completions"),
            )

    monkeypatch.setattr(httpx, "Client", FakeHTTPClient)
    client = LMStudioClient(LMStudioConfig(model="q"))

    with pytest.raises(LMStudioError, match="missing choices"):
        client.chat([{"role": "user", "content": "hello"}])


def test_no_tool_mode_attaches_no_tools_and_preserves_user_message(tmp_path) -> None:
    fake = FakeClient([response({"content": "RCS and iMessage are different messaging systems."})])
    orchestrator = make_orchestrator(fake, tmp_path)

    result = orchestrator.run("Explain RCS vs iMessage", no_tools=True)

    assert result.content == "RCS and iMessage are different messaging systems."
    assert fake.calls[0]["tools"] is None
    assert fake.calls[0]["messages"][0]["content"] == MINIMAL_SYSTEM_PROMPT
    assert fake.calls[0]["messages"][1] == {
        "role": "user",
        "content": "Explain RCS vs iMessage",
    }


def test_no_tool_mode_still_attaches_no_tools_through_lmstudio_provider(tmp_path) -> None:
    fake = FakeClient([response({"role": "assistant", "content": "No tools attached."})])
    provider = LMStudioBrainProvider(client=fake)
    orchestrator = make_orchestrator(provider, tmp_path)

    result = orchestrator.run("Explain RCS vs iMessage", no_tools=True)

    assert result.content == "No tools attached."
    assert fake.calls[0]["tools"] is None


def test_no_tool_mode_attaches_no_tools_for_weather_request(tmp_path) -> None:
    fake = FakeClient([response({"content": "I need a location to check weather."})])
    orchestrator = make_orchestrator(fake, tmp_path)

    result = orchestrator.run("What's the weather in Phoenix?", no_tools=True)

    assert result.content == "I need a location to check weather."
    assert fake.calls[0]["tools"] is None
    assert fake.calls[0]["messages"][1] == {
        "role": "user",
        "content": "What's the weather in Phoenix?",
    }


def test_normal_chat_route_attaches_no_tools_by_default(tmp_path) -> None:
    fake = FakeClient([response({"content": "Hello."})])
    orchestrator = make_orchestrator(fake, tmp_path)

    result = orchestrator.run("Tell me a short story.")

    assert result.content == "Hello."
    assert fake.calls[0]["tools"] is None


def test_weather_route_attaches_weather_tools_without_rewriting_user_message(tmp_path) -> None:
    fake = FakeClient([response({"content": "I'll need to check the weather."})])
    orchestrator = make_orchestrator(fake, tmp_path)

    result = orchestrator.run("What's the weather in Phoenix?")

    tool_names = {tool["function"]["name"] for tool in fake.calls[0]["tools"]}
    assert result.content == "I'll need to check the weather."
    assert {"weather.current", "weather.forecast"}.issubset(tool_names)
    assert fake.calls[0]["messages"][1] == {
        "role": "user",
        "content": "What's the weather in Phoenix?",
    }


def test_weather_impact_route_attaches_weather_and_web_tools(tmp_path) -> None:
    fake = FakeClient([response({"content": "I'll check weather and source-grounded web context."})])
    orchestrator = make_orchestrator(fake, tmp_path, weather_provider=FakeWeatherProvider())

    result = orchestrator.run("Are flights delayed due to weather at LAX?")

    tool_names = {tool["function"]["name"] for tool in fake.calls[0]["tools"]}
    assert result.content == "I'll check weather and source-grounded web context."
    assert {"weather.current", "weather.forecast", "web.search"}.issubset(tool_names)
    assert fake.calls[0]["messages"][1] == {
        "role": "user",
        "content": "Are flights delayed due to weather at LAX?",
    }


def test_weather_tool_chat_path_lets_model_write_final_answer(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEB_ACCESS_ENABLED", "true")
    fake = FakeClient(
        [
            response(
                {
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_weather",
                            "type": "function",
                            "function": {
                                "name": "weather.current",
                                "arguments": json.dumps({"location": "Phoenix, AZ"}),
                            },
                        }
                    ],
                }
            ),
            response({"content": "It is clear and 72 degrees in Phoenix."}),
        ]
    )
    orchestrator = make_orchestrator(fake, tmp_path, weather_provider=FakeWeatherProvider())

    result = orchestrator.run("What's the weather in Phoenix?")

    assert result.content == "It is clear and 72 degrees in Phoenix."
    assert len(result.tool_results) == 1
    assert json.loads(result.tool_results[0]["content"])["provider"] == "fake-weather"
    assert result.messages[-1]["content"] == "It is clear and 72 degrees in Phoenix."


def test_tool_result_is_appended_with_matching_tool_call_id(tmp_path) -> None:
    fake = FakeClient(
        [
            response(
                {
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_time",
                            "type": "function",
                            "function": {
                                "name": "time.get_current_time",
                                "arguments": json.dumps({"timezone": "UTC"}),
                            },
                        }
                    ],
                }
            ),
            response({"content": "It is whatever the tool reported."}),
        ]
    )
    orchestrator = make_orchestrator(fake, tmp_path)

    result = orchestrator.run("What time is it?")

    assert result.content == "It is whatever the tool reported."
    assert len(fake.calls) == 2
    tool_messages = [message for message in fake.calls[1]["messages"] if message["role"] == "tool"]
    assert len(tool_messages) == 1
    assert tool_messages[0]["tool_call_id"] == "call_time"
    assert tool_messages[0]["name"] == "time.get_current_time"
    assert json.loads(tool_messages[0]["content"])["timezone"] == "UTC"
    assert any(event["event"] == "tool_broker" for event in result.debug_events)


def test_malformed_tool_arguments_are_returned_as_tool_error(tmp_path) -> None:
    fake = FakeClient(
        [
            response(
                {
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_bad_args",
                            "type": "function",
                            "function": {
                                "name": "time.get_current_time",
                                "arguments": "{not-json",
                            },
                        }
                    ],
                }
            ),
            response({"content": "I could not use the tool."}),
        ]
    )
    orchestrator = make_orchestrator(fake, tmp_path)

    result = orchestrator.run("What time is it?")

    assert result.content == "I could not use the tool."
    tool_messages = [message for message in fake.calls[1]["messages"] if message["role"] == "tool"]
    assert json.loads(tool_messages[0]["content"])["error"] == "invalid tool arguments"


def test_tool_loop_limit_has_diagnostic(tmp_path) -> None:
    repeated_tool_call = response(
        {
            "content": None,
            "tool_calls": [
                {
                    "id": "call_time",
                    "type": "function",
                    "function": {"name": "time.get_current_time", "arguments": "{}"},
                }
            ],
        }
    )
    fake = FakeClient([repeated_tool_call, repeated_tool_call, repeated_tool_call, repeated_tool_call])
    orchestrator = make_orchestrator(fake, tmp_path)
    orchestrator.max_tool_iterations = 1

    result = orchestrator.run("What time is it?")

    assert "Tool-call loop limit reached" in result.content
    assert any(event["event"] == "tool_loop_limit" for event in result.debug_events)


def test_reasoning_content_is_not_fed_back_or_displayed(tmp_path) -> None:
    fake = FakeClient(
        [
            response(
                {
                    "content": "Final only.",
                    "reasoning_content": "hidden chain of thought",
                }
            )
        ]
    )
    orchestrator = make_orchestrator(fake, tmp_path)

    result = orchestrator.run("Tell me something.")

    assert result.content == "Final only."
    assert "reasoning_content" not in result.messages[-1]


def test_debug_payload_redacts_secrets() -> None:
    debug = format_debug_payload({"headers": {"Authorization": "token supersecret"}})

    assert "supersecret" not in debug
    assert "[REDACTED]" in debug
