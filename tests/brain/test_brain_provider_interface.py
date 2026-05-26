from __future__ import annotations

from agent.brain import BrainGenerationSettings, BrainMessage, BrainProviderError, BrainToolSpec
from agent.brain.mock_provider import MockBrainProvider
from agent.brain.models import BrainToolCall


def test_mock_provider_implements_brain_provider_contract() -> None:
    provider = MockBrainProvider(response_text="steady answer")

    assert provider.provider_id() == "mock"
    assert provider.provider_name()
    assert provider.is_configured() is True
    assert provider.is_available() is True
    assert provider.supports_tool_calls() is True
    assert provider.supports_streaming() is False
    assert provider.supports_reasoning_content() is False
    assert provider.supports_json_schema() is True
    assert provider.list_models()[0].provider_id == "mock"


def test_mock_provider_no_tool_chat_is_deterministic() -> None:
    provider = MockBrainProvider(response_text="deterministic reply")

    response = provider.chat(
        [BrainMessage(role="user", content="hello")],
        settings=BrainGenerationSettings(temperature=0.0, top_p=1.0, max_tokens=32),
    )

    assert response.ok is True
    assert response.message.content == "deterministic reply"
    assert response.tool_calls == ()
    assert response.finish_reason == "stop"
    assert response.raw_response["settings"]["temperature"] == 0.0


def test_mock_provider_tool_call_schema_is_provider_neutral() -> None:
    provider = MockBrainProvider(tool_call_arguments={"city": "Paris"})
    tool = BrainToolSpec(name="weather.lookup", description="Lookup weather", parameters={"type": "object"})

    response = provider.chat([BrainMessage(role="user", content="weather?")], tools=[tool.to_openai_tool()])

    assert response.message.content == ""
    assert response.finish_reason == "tool_calls"
    assert response.tool_calls == (BrainToolCall(tool_call_id="mock_tool_call_1", name="weather.lookup", arguments={"city": "Paris"}),)
    assert response.to_dict()["tool_calls"][0]["name"] == "weather.lookup"


def test_provider_error_response_is_normalized() -> None:
    provider = MockBrainProvider(configured=True, available=False)

    response = provider.chat([BrainMessage(role="user", content="hello")])

    assert response.ok is False
    assert isinstance(response.error, BrainProviderError)
    assert response.error.provider_id == "mock"
    assert response.error.error_code == "provider_unavailable"
    assert response.to_dict()["error"]["setup_hint"]


def test_mock_token_estimate_is_side_effect_free() -> None:
    provider = MockBrainProvider()

    assert provider.estimate_tokens([BrainMessage(role="user", content="one two three")]) == 3
