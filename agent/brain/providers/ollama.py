from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import httpx

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
from agent.config.runtime import RuntimeConfigError, validate_base_url


@dataclass(frozen=True)
class OllamaConfig:
    enabled: bool = False
    base_url: str = "http://localhost:11434"
    model: str = ""
    openai_compat_base_url: str = "http://localhost:11434/v1"
    timeout_seconds: float = 60.0
    supports_tool_calls: bool = False
    supports_streaming: bool = False

    def normalized_base_url(self) -> str:
        return validate_base_url(self.base_url)

    def normalized_openai_compat_base_url(self) -> str:
        return validate_base_url(self.openai_compat_base_url)


class OllamaBrainProvider(BrainProvider):
    """OpenAI-compatible adapter for a user-managed local Ollama daemon."""

    def __init__(self, config: OllamaConfig | None = None) -> None:
        self.config = config or OllamaConfig()

    def provider_id(self) -> str:
        return "ollama"

    def provider_name(self) -> str:
        return "Ollama"

    def is_configured(self) -> bool:
        return bool(self.config.enabled and self.config.base_url and self.config.openai_compat_base_url and self.config.model)

    def is_available(self) -> bool:
        return self.is_configured()

    def health_check(self) -> BrainProviderHealth:
        setup = self._setup_error()
        if setup is not None:
            return BrainProviderHealth(
                provider_id=self.provider_id(),
                status="disabled" if not self.config.enabled else "requires_setup",
                configured=False,
                available=False,
                error=setup,
                setup_hint=setup.setup_hint,
            )
        try:
            with httpx.Client(timeout=min(self.config.timeout_seconds, 10.0)) as client:
                response = client.get(f"{self.config.normalized_base_url()}/api/tags")
                response.raise_for_status()
                data = response.json()
        except httpx.ConnectError:
            return self._health_error(
                "daemon_unavailable",
                f"Ollama daemon not reachable at {self.config.base_url}.",
            )
        except httpx.TimeoutException:
            return self._health_error("timeout", f"Ollama health check timed out at {self.config.base_url}.")
        except httpx.HTTPStatusError as exc:
            return self._health_error("http_error", f"Ollama returned HTTP {exc.response.status_code}.")
        except ValueError:
            return self._health_error("malformed_response", "Ollama returned malformed JSON from /api/tags.")
        models = data.get("models", []) if isinstance(data, Mapping) else []
        return BrainProviderHealth(
            provider_id=self.provider_id(),
            status="ok",
            configured=True,
            available=True,
            model_count=len(models) if isinstance(models, list) else 0,
            setup_hint="",
        )

    def list_models(self) -> tuple[BrainModelInfo, ...]:
        if not self.config.model:
            return ()
        return (
            BrainModelInfo(
                model_id=self.config.model,
                provider_id=self.provider_id(),
                display_name=self.config.model,
                supports_tool_calls=self.config.supports_tool_calls,
                supports_streaming=self.config.supports_streaming,
                supports_reasoning_content=False,
                supports_json_schema=False,
                metadata={
                    "base_url": self.config.base_url,
                    "openai_compat_base_url": self.config.openai_compat_base_url,
                    "source": "OLLAMA_MODEL",
                },
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
        setup = self._setup_error()
        if setup is not None:
            return self._error_response(setup)
        if tools and not self.config.supports_tool_calls:
            return self._error_response(
                BrainProviderError(
                    "Ollama tool-call support is disabled. Set OLLAMA_SUPPORTS_TOOL_CALLS=true only after verifying your daemon/model supports OpenAI-compatible tool calls.",
                    provider_id=self.provider_id(),
                    error_code="tool_calls_unsupported",
                    setup_hint="Use no-tools mode or enable tool-call support only after verification.",
                )
            )
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": [_message_to_openai(message) for message in messages],
            "temperature": settings.temperature if settings else 0.7,
            "top_p": settings.top_p if settings else 0.95,
            "max_tokens": settings.max_tokens if settings else 2048,
        }
        if settings and settings.stop:
            payload["stop"] = list(settings.stop)
        if tools:
            payload["tools"] = list(tools)
            payload["tool_choice"] = tool_choice or "auto"
        try:
            with httpx.Client(timeout=self.config.timeout_seconds) as client:
                response = client.post(f"{self.config.normalized_openai_compat_base_url()}/chat/completions", json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.ConnectError:
            return self._error_response(
                BrainProviderError(
                    f"Ollama daemon not reachable at {self.config.openai_compat_base_url}. Start Ollama yourself and retry.",
                    provider_id=self.provider_id(),
                    error_code="daemon_unavailable",
                    setup_hint="Start the Ollama daemon yourself; the agent never starts it automatically or pulls models.",
                )
            )
        except httpx.TimeoutException:
            return self._error_response(
                BrainProviderError(
                    f"Ollama request timed out at {self.config.openai_compat_base_url}.",
                    provider_id=self.provider_id(),
                    error_code="timeout",
                    setup_hint="Confirm the daemon is running and the model is already pulled by the user.",
                )
            )
        except httpx.HTTPStatusError as exc:
            return self._error_response(
                BrainProviderError(
                    f"Ollama returned HTTP {exc.response.status_code}. Response: {exc.response.text[:500]}",
                    provider_id=self.provider_id(),
                    error_code="http_error",
                    setup_hint="Confirm OLLAMA_MODEL is available locally; the agent does not pull models.",
                )
            )
        except (RuntimeConfigError, ValueError) as exc:
            return self._error_response(
                BrainProviderError(
                    str(exc) if isinstance(exc, RuntimeConfigError) else "Ollama returned a malformed response.",
                    provider_id=self.provider_id(),
                    error_code="malformed_response",
                    setup_hint="Check OLLAMA_OPENAI_COMPAT_BASE_URL and OpenAI compatibility.",
                )
            )
        return self._normalize_response(data)

    def supports_tool_calls(self) -> bool:
        return self.config.supports_tool_calls

    def supports_streaming(self) -> bool:
        return self.config.supports_streaming

    def supports_reasoning_content(self) -> bool:
        return False

    def supports_json_schema(self) -> bool:
        return False

    def _setup_error(self) -> BrainProviderError | None:
        if not self.config.enabled:
            return BrainProviderError(
                "Ollama provider is disabled.",
                provider_id=self.provider_id(),
                error_code="provider_disabled",
                setup_hint="Set OLLAMA_ENABLED=true after starting a user-managed local Ollama daemon.",
            )
        if not self.config.model:
            return BrainProviderError(
                "OLLAMA_MODEL is not set.",
                provider_id=self.provider_id(),
                error_code="provider_not_configured",
                setup_hint="Set OLLAMA_MODEL to a model already available in your local Ollama daemon.",
            )
        try:
            self.config.normalized_base_url()
            self.config.normalized_openai_compat_base_url()
        except RuntimeConfigError as exc:
            return BrainProviderError(
                str(exc),
                provider_id=self.provider_id(),
                error_code="invalid_base_url",
                setup_hint="Set OLLAMA_BASE_URL and OLLAMA_OPENAI_COMPAT_BASE_URL to local http(s) URLs.",
            )
        return None

    def _normalize_response(self, raw: Mapping[str, Any]) -> BrainChatResponse:
        choices = raw.get("choices")
        if not isinstance(choices, list) or not choices:
            return self._error_response(
                BrainProviderError(
                    "Ollama returned a malformed response: missing choices.",
                    provider_id=self.provider_id(),
                    error_code="malformed_response",
                    setup_hint="Confirm the daemon exposes OpenAI-compatible chat completions.",
                )
            )
        choice = choices[0] if isinstance(choices[0], Mapping) else {}
        raw_message = choice.get("message")
        if not isinstance(raw_message, Mapping):
            return self._error_response(
                BrainProviderError(
                    "Ollama returned a malformed response: missing message.",
                    provider_id=self.provider_id(),
                    error_code="malformed_response",
                )
            )
        tool_calls = tuple(_normalize_tool_call(tool_call) for tool_call in raw_message.get("tool_calls") or [])
        return BrainChatResponse(
            provider_id=self.provider_id(),
            model=str(raw.get("model") or self.config.model),
            message=BrainMessage(role=str(raw_message.get("role") or "assistant"), content=str(raw_message.get("content") or "")),
            tool_calls=tool_calls,
            finish_reason=str(choice.get("finish_reason") or ("tool_calls" if tool_calls else "stop")),
            usage=raw.get("usage") if isinstance(raw.get("usage"), Mapping) else {},
            raw_response=dict(raw),
        )

    def _error_response(self, error: BrainProviderError) -> BrainChatResponse:
        return BrainChatResponse(
            provider_id=self.provider_id(),
            model=self.config.model,
            message=BrainMessage(role="assistant", content=""),
            finish_reason="error",
            error=error,
        )

    def _health_error(self, error_code: str, message: str) -> BrainProviderHealth:
        error = BrainProviderError(
            message,
            provider_id=self.provider_id(),
            error_code=error_code,
            setup_hint="Check the user-managed Ollama daemon; the agent does not start it or pull models.",
        )
        return BrainProviderHealth(
            provider_id=self.provider_id(),
            status="unavailable",
            configured=True,
            available=False,
            error=error,
            setup_hint=error.setup_hint,
        )


def _message_to_openai(message: BrainMessage | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(message, BrainMessage):
        return message.to_dict()
    return dict(message)


def _normalize_tool_call(tool_call: Any) -> BrainToolCall:
    if not isinstance(tool_call, Mapping):
        return BrainToolCall(tool_call_id="", name="", arguments={})
    function = tool_call.get("function") if isinstance(tool_call.get("function"), Mapping) else {}
    raw_arguments = function.get("arguments", "{}")
    if isinstance(raw_arguments, str):
        try:
            loaded = json.loads(raw_arguments or "{}")
            arguments = loaded if isinstance(loaded, Mapping) else {"value": loaded}
            raw_text = None
        except ValueError:
            arguments = {}
            raw_text = raw_arguments
    elif isinstance(raw_arguments, Mapping):
        arguments = raw_arguments
        raw_text = None
    else:
        arguments = {"value": raw_arguments}
        raw_text = None
    return BrainToolCall(
        tool_call_id=str(tool_call.get("id") or ""),
        name=str(function.get("name") or ""),
        arguments=arguments,
        raw_arguments=raw_text,
    )
