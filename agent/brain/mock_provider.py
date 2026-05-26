from __future__ import annotations

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


class MockBrainProvider(BrainProvider):
    def __init__(
        self,
        *,
        configured: bool = True,
        available: bool = True,
        response_text: str = "mock response",
        model_id: str = "mock-model",
        tool_call_name: str | None = None,
        tool_call_arguments: Mapping[str, Any] | None = None,
    ) -> None:
        self.configured = configured
        self.available = available
        self.response_text = response_text
        self.model_id = model_id
        self.tool_call_name = tool_call_name
        self.tool_call_arguments = dict(tool_call_arguments or {})

    def provider_id(self) -> str:
        return "mock"

    def provider_name(self) -> str:
        return "Mock Brain Provider"

    def is_configured(self) -> bool:
        return self.configured

    def is_available(self) -> bool:
        return self.configured and self.available

    def health_check(self) -> BrainProviderHealth:
        if not self.configured:
            return BrainProviderHealth(
                provider_id=self.provider_id(),
                status="requires_setup",
                configured=False,
                available=False,
                setup_hint="Enable BRAIN_MOCK_PROVIDER_ENABLED=true in tests.",
            )
        return BrainProviderHealth(
            provider_id=self.provider_id(),
            status="ok" if self.available else "unavailable",
            configured=True,
            available=self.available,
            model_count=1 if self.available else 0,
            setup_hint="" if self.available else "Mock provider is configured but marked unavailable.",
        )

    def list_models(self) -> tuple[BrainModelInfo, ...]:
        if not self.is_available():
            return ()
        return (
            BrainModelInfo(
                model_id=self.model_id,
                provider_id=self.provider_id(),
                display_name="Mock Model",
                context_window=8192,
                supports_tool_calls=True,
                supports_streaming=False,
                supports_reasoning_content=False,
                supports_json_schema=True,
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
        if not self.is_available():
            error = BrainProviderError(
                "Mock brain provider is not available.",
                provider_id=self.provider_id(),
                error_code="provider_unavailable",
                setup_hint="Enable and mark the mock provider available in the test fixture.",
            )
            return BrainChatResponse(
                provider_id=self.provider_id(),
                model=self.model_id,
                message=BrainMessage(role="assistant", content=""),
                finish_reason="error",
                error=error,
            )
        tool_calls: tuple[BrainToolCall, ...] = ()
        if tools and tool_choice != "none":
            requested_name = self.tool_call_name or _first_tool_name(tools)
            if requested_name:
                tool_calls = (
                    BrainToolCall(
                        tool_call_id="mock_tool_call_1",
                        name=requested_name,
                        arguments=self.tool_call_arguments,
                    ),
                )
        finish_reason = "tool_calls" if tool_calls else "stop"
        return BrainChatResponse(
            provider_id=self.provider_id(),
            model=self.model_id,
            message=BrainMessage(role="assistant", content="" if tool_calls else self.response_text),
            tool_calls=tool_calls,
            finish_reason=finish_reason,
            raw_response={"mock": True, "settings": settings.to_dict() if settings else None},
        )

    def supports_tool_calls(self) -> bool:
        return True

    def supports_streaming(self) -> bool:
        return False

    def supports_reasoning_content(self) -> bool:
        return False

    def supports_json_schema(self) -> bool:
        return True

    def estimate_tokens(self, messages: Sequence[BrainMessage | Mapping[str, Any]]) -> int | None:
        total = 0
        for message in messages:
            content = message.content if isinstance(message, BrainMessage) else str(message.get("content", ""))
            total += max(1, len(content.split()))
        return total


def _first_tool_name(tools: Sequence[Mapping[str, Any]]) -> str | None:
    if not tools:
        return None
    first = tools[0]
    function = first.get("function")
    if isinstance(function, Mapping):
        return str(function.get("name") or "") or None
    return str(first.get("name") or "") or None

