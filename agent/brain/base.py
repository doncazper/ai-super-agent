from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, Sequence

from agent.brain.models import BrainChatResponse, BrainGenerationSettings, BrainMessage, BrainModelInfo, BrainProviderHealth


class BrainProvider(ABC):
    """Provider-neutral model runtime contract.

    Implementations must not execute tools. Tool-call output is data for the
    existing orchestrator and ToolBroker path to handle.
    """

    @abstractmethod
    def provider_id(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def is_configured(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> BrainProviderHealth:
        raise NotImplementedError

    @abstractmethod
    def list_models(self) -> tuple[BrainModelInfo, ...]:
        raise NotImplementedError

    @abstractmethod
    def chat(
        self,
        messages: Sequence[BrainMessage | Mapping[str, Any]],
        *,
        tools: Sequence[Mapping[str, Any]] | None = None,
        tool_choice: str | Mapping[str, Any] | None = None,
        settings: BrainGenerationSettings | None = None,
    ) -> BrainChatResponse:
        raise NotImplementedError

    @abstractmethod
    def supports_tool_calls(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def supports_streaming(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def supports_reasoning_content(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def supports_json_schema(self) -> bool:
        raise NotImplementedError

    def estimate_tokens(self, messages: Sequence[BrainMessage | Mapping[str, Any]]) -> int | None:
        return None

    def close(self) -> None:
        return None

    def shutdown(self) -> None:
        self.close()

