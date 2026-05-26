from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from agent.brain.errors import BrainProviderError


@dataclass(frozen=True)
class BrainMessage:
    role: str
    content: str
    name: str | None = None

    def to_dict(self) -> dict[str, str]:
        payload = {"role": self.role, "content": self.content}
        if self.name:
            payload["name"] = self.name
        return payload


@dataclass(frozen=True)
class BrainToolSpec:
    name: str
    description: str
    parameters: Mapping[str, Any] = field(default_factory=dict)

    def to_openai_tool(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": dict(self.parameters),
            },
        }


@dataclass(frozen=True)
class BrainToolCall:
    tool_call_id: str
    name: str
    arguments: Mapping[str, Any] = field(default_factory=dict)
    raw_arguments: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {"id": self.tool_call_id, "name": self.name, "arguments": dict(self.arguments)}
        if self.raw_arguments is not None:
            payload["raw_arguments"] = self.raw_arguments
        return payload


@dataclass(frozen=True)
class BrainGenerationSettings:
    temperature: float = 0.7
    top_p: float = 0.95
    max_tokens: int = 2048
    stop: tuple[str, ...] = ()
    stream: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
            "stop": list(self.stop),
            "stream": self.stream,
        }


@dataclass(frozen=True)
class BrainChatRequest:
    messages: Sequence[BrainMessage | Mapping[str, Any]]
    tools: Sequence[BrainToolSpec | Mapping[str, Any]] = ()
    tool_choice: str | Mapping[str, Any] | None = None
    settings: BrainGenerationSettings | None = None


@dataclass(frozen=True)
class BrainChatResponse:
    provider_id: str
    model: str
    message: BrainMessage
    tool_calls: tuple[BrainToolCall, ...] = ()
    raw_response: Mapping[str, Any] = field(default_factory=dict)
    finish_reason: str = "stop"
    usage: Mapping[str, Any] = field(default_factory=dict)
    error: BrainProviderError | None = None

    @property
    def ok(self) -> bool:
        return self.error is None

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "model": self.model,
            "message": self.message.to_dict(),
            "tool_calls": [tool_call.to_dict() for tool_call in self.tool_calls],
            "finish_reason": self.finish_reason,
            "usage": dict(self.usage),
            "raw_response": dict(self.raw_response),
            "error": self.error.to_dict() if self.error else None,
        }


@dataclass(frozen=True)
class BrainProviderHealth:
    provider_id: str
    status: str
    configured: bool
    available: bool
    latency_ms: float | None = None
    model_count: int = 0
    error: BrainProviderError | None = None
    setup_hint: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "status": self.status,
            "configured": self.configured,
            "available": self.available,
            "latency_ms": self.latency_ms,
            "model_count": self.model_count,
            "error": self.error.to_dict() if self.error else None,
            "setup_hint": self.setup_hint,
        }


@dataclass(frozen=True)
class BrainProviderStatus:
    provider_id: str
    provider_name: str
    registered: bool
    configured: bool | None = None
    available: bool | None = None
    lazy: bool = True
    setup_hint: str = ""
    status: str = "registered"

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "provider_name": self.provider_name,
            "registered": self.registered,
            "configured": self.configured,
            "available": self.available,
            "lazy": self.lazy,
            "setup_hint": self.setup_hint,
            "status": self.status,
        }


@dataclass(frozen=True)
class BrainModelInfo:
    model_id: str
    provider_id: str
    display_name: str = ""
    context_window: int | None = None
    supports_tool_calls: bool = False
    supports_streaming: bool = False
    supports_reasoning_content: bool = False
    supports_json_schema: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "provider_id": self.provider_id,
            "display_name": self.display_name or self.model_id,
            "context_window": self.context_window,
            "supports_tool_calls": self.supports_tool_calls,
            "supports_streaming": self.supports_streaming,
            "supports_reasoning_content": self.supports_reasoning_content,
            "supports_json_schema": self.supports_json_schema,
            "metadata": dict(self.metadata),
        }
