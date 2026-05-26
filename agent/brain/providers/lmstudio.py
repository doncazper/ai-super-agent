from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

from agent.brain.base import BrainProvider
from agent.brain.errors import BrainProviderError
from agent.brain.models import (
    BrainChatResponse,
    BrainGenerationSettings,
    BrainMessage,
    BrainModelInfo,
    BrainProviderHealth,
    BrainToolCall,
)
from agent.core.lmstudio_client import LMStudioClient, LMStudioConfig, LMStudioError


class LMStudioBrainProvider(BrainProvider):
    """BrainProvider adapter around the existing LMStudioClient.

    This adapter preserves the current OpenAI-compatible payload construction
    and error wording by delegating model calls to LMStudioClient.
    """

    def __init__(self, config: LMStudioConfig | None = None, *, client: LMStudioClient | None = None) -> None:
        self.config = config or (client.config if client is not None else LMStudioConfig.from_env())
        self._client = client

    def provider_id(self) -> str:
        return "lmstudio"

    def provider_name(self) -> str:
        return "LM Studio"

    def is_configured(self) -> bool:
        return bool(self.config.model)

    def is_available(self) -> bool:
        return self.is_configured()

    def health_check(self) -> BrainProviderHealth:
        if not self.is_configured():
            error = BrainProviderError(
                "LMSTUDIO_MODEL is not set. Export LMSTUDIO_MODEL='<model id>'.",
                provider_id=self.provider_id(),
                error_code="provider_not_configured",
                setup_hint="Set LMSTUDIO_MODEL to a model loaded in LM Studio.",
            )
            return BrainProviderHealth(
                provider_id=self.provider_id(),
                status="requires_setup",
                configured=False,
                available=False,
                error=error,
                setup_hint=error.setup_hint,
            )
        return BrainProviderHealth(
            provider_id=self.provider_id(),
            status="configured",
            configured=True,
            available=True,
            model_count=1,
            setup_hint="Start LM Studio Developer Server if chat requests cannot connect.",
        )

    def list_models(self) -> tuple[BrainModelInfo, ...]:
        if not self.config.model:
            return ()
        return (
            BrainModelInfo(
                model_id=self.config.model,
                provider_id=self.provider_id(),
                display_name=self.config.model,
                supports_tool_calls=True,
                supports_streaming=False,
                supports_reasoning_content=True,
                supports_json_schema=False,
                metadata={"base_url": self.config.base_url, "source": "LMSTUDIO_MODEL"},
            ),
        )

    def chat(
        self,
        messages: Sequence[BrainMessage | Mapping[str, Any]],
        *,
        tools: Sequence[Mapping[str, Any]] | None = None,
        tool_choice: str | Mapping[str, Any] | None = None,
        settings: BrainGenerationSettings | None = None,
    ) -> BrainChatResponse:
        if not self.is_configured():
            return self._error_response(
                LMStudioError("LMSTUDIO_MODEL is not set. Export LMSTUDIO_MODEL='<model id>'."),
                error_code="provider_not_configured",
                setup_hint="Set LMSTUDIO_MODEL to a model loaded in LM Studio.",
            )

        payload_messages = [_message_to_openai(message) for message in messages]
        payload_tools = list(tools or [])
        client = self._get_client()
        if settings is not None:
            client = LMStudioClient(
                LMStudioConfig(
                    base_url=self.config.base_url,
                    model=self.config.model,
                    temperature=settings.temperature,
                    top_p=settings.top_p,
                    max_tokens=settings.max_tokens,
                    timeout_seconds=self.config.timeout_seconds,
                )
            )
        try:
            raw = client.chat(payload_messages, tools=payload_tools or None)
        except LMStudioError as exc:
            return self._error_response(exc)
        return self._normalize_response(raw)

    def supports_tool_calls(self) -> bool:
        return True

    def supports_streaming(self) -> bool:
        return False

    def supports_reasoning_content(self) -> bool:
        return True

    def supports_json_schema(self) -> bool:
        return False

    def estimate_tokens(self, messages: Sequence[BrainMessage | Mapping[str, Any]]) -> int | None:
        total = 0
        for message in messages:
            content = message.content if isinstance(message, BrainMessage) else str(message.get("content", ""))
            total += max(1, len(content.split()))
        return total

    def _get_client(self) -> LMStudioClient:
        if self._client is None:
            self._client = LMStudioClient(self.config)
        return self._client

    def _normalize_response(self, raw: Mapping[str, Any]) -> BrainChatResponse:
        choices = raw.get("choices")
        if not isinstance(choices, list) or not choices:
            return self._error_response(
                LMStudioError("LM Studio returned a malformed response: missing choices."),
                error_code="malformed_response",
            )
        choice = choices[0] if isinstance(choices[0], Mapping) else {}
        raw_message = choice.get("message")
        if not isinstance(raw_message, Mapping):
            return self._error_response(
                LMStudioError("LM Studio returned a malformed response: missing message."),
                error_code="malformed_response",
            )
        message = BrainMessage(
            role=str(raw_message.get("role") or "assistant"),
            content=str(raw_message.get("content") or ""),
        )
        tool_calls = tuple(_normalize_tool_call(tool_call) for tool_call in raw_message.get("tool_calls") or [])
        return BrainChatResponse(
            provider_id=self.provider_id(),
            model=str(raw.get("model") or self.config.model),
            message=message,
            tool_calls=tool_calls,
            finish_reason=str(choice.get("finish_reason") or ("tool_calls" if tool_calls else "stop")),
            usage=raw.get("usage") if isinstance(raw.get("usage"), Mapping) else {},
            raw_response=dict(raw),
        )

    def _error_response(
        self,
        exc: LMStudioError,
        *,
        error_code: str = "lmstudio_error",
        setup_hint: str = "Check LM Studio Developer Server, base URL, and selected model.",
    ) -> BrainChatResponse:
        error = BrainProviderError(
            str(exc),
            provider_id=self.provider_id(),
            error_code=error_code,
            setup_hint=setup_hint,
        )
        return BrainChatResponse(
            provider_id=self.provider_id(),
            model=self.config.model,
            message=BrainMessage(role="assistant", content=""),
            finish_reason="error",
            error=error,
        )


def brain_response_to_openai(response: BrainChatResponse) -> dict[str, Any]:
    message = response.message.to_dict()
    if response.tool_calls:
        message["tool_calls"] = [
            {
                "id": tool_call.tool_call_id,
                "type": "function",
                "function": {
                    "name": tool_call.name,
                    "arguments": tool_call.raw_arguments
                    if tool_call.raw_arguments is not None
                    else json.dumps(dict(tool_call.arguments)),
                },
            }
            for tool_call in response.tool_calls
        ]
    return {
        "choices": [{"finish_reason": response.finish_reason, "message": message}],
        "model": response.model,
        "usage": dict(response.usage),
    }


def _message_to_openai(message: BrainMessage | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(message, BrainMessage):
        return message.to_dict()
    return dict(message)


def _normalize_tool_call(tool_call: Any) -> BrainToolCall:
    if not isinstance(tool_call, Mapping):
        return BrainToolCall(tool_call_id="", name="", arguments={})
    function = tool_call.get("function") if isinstance(tool_call.get("function"), Mapping) else {}
    raw_arguments = function.get("arguments", "{}")
    parsed_arguments: Mapping[str, Any]
    raw_argument_text: str | None = None
    if isinstance(raw_arguments, str):
        try:
            loaded = json.loads(raw_arguments or "{}")
            parsed_arguments = loaded if isinstance(loaded, Mapping) else {"value": loaded}
        except ValueError:
            parsed_arguments = {}
            raw_argument_text = raw_arguments
    elif isinstance(raw_arguments, Mapping):
        parsed_arguments = raw_arguments
    else:
        parsed_arguments = {"value": raw_arguments}
    return BrainToolCall(
        tool_call_id=str(tool_call.get("id") or ""),
        name=str(function.get("name") or ""),
        arguments=parsed_arguments,
        raw_arguments=raw_argument_text,
    )
