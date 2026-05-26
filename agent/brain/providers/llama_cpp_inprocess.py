from __future__ import annotations

import importlib
import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence

from agent.brain.base import BrainProvider
from agent.brain.errors import BrainProviderError
from agent.brain.models import (
    BrainChatResponse,
    BrainGenerationSettings,
    BrainMessage,
    BrainModelInfo,
    BrainProviderHealth,
)


class LlamaCppBackend(Protocol):
    def create_chat_completion(self, *, messages: list[dict[str, Any]], **kwargs: Any) -> Mapping[str, Any]:
        ...


BackendFactory = Callable[["LlamaCppInProcessConfig"], LlamaCppBackend]
DependencyDetector = Callable[[], bool]


@dataclass(frozen=True)
class LlamaCppInProcessConfig:
    enabled: bool = False
    model_path: str = ""
    n_ctx: int = 8192
    n_gpu_layers: int = -1
    threads: str = "auto"
    supports_tool_calls: bool = False
    load_on_startup: bool = False
    max_loaded_models: int = 1


class LlamaCppInProcessBrainProvider(BrainProvider):
    """Optional in-process llama-cpp-python provider scaffold.

    This provider does not import llama_cpp at module import or registry listing
    time. It loads a backend only when chat is explicitly requested.
    """

    def __init__(
        self,
        config: LlamaCppInProcessConfig | None = None,
        *,
        dependency_detector: DependencyDetector | None = None,
        backend_factory: BackendFactory | None = None,
    ) -> None:
        self.config = config or LlamaCppInProcessConfig()
        self._dependency_detector = dependency_detector or _dependency_available
        self._backend_factory = backend_factory
        self._backend: LlamaCppBackend | None = None

    def provider_id(self) -> str:
        return "llama_cpp_inprocess"

    def provider_name(self) -> str:
        return "llama-cpp-python in-process"

    def is_configured(self) -> bool:
        return bool(self.config.enabled and self.config.model_path and self._dependency_detector())

    def is_available(self) -> bool:
        return self.is_configured()

    def health_check(self) -> BrainProviderHealth:
        setup = self._setup_error(check_model_file=False)
        if setup is not None:
            return BrainProviderHealth(
                provider_id=self.provider_id(),
                status="disabled" if not self.config.enabled else "requires_setup",
                configured=False,
                available=False,
                error=setup,
                setup_hint=setup.setup_hint,
            )
        return BrainProviderHealth(
            provider_id=self.provider_id(),
            status="configured",
            configured=True,
            available=True,
            model_count=1,
            setup_hint="Model is configured; it will load lazily only when chat is explicitly requested.",
        )

    def list_models(self) -> tuple[BrainModelInfo, ...]:
        if not self.config.model_path:
            return ()
        return (
            BrainModelInfo(
                model_id=self.config.model_path,
                provider_id=self.provider_id(),
                display_name=Path(self.config.model_path).name,
                supports_tool_calls=self.config.supports_tool_calls,
                supports_streaming=False,
                supports_reasoning_content=False,
                supports_json_schema=False,
                metadata={
                    "source": "LLAMA_CPP_INPROCESS_MODEL_PATH",
                    "n_ctx": self.config.n_ctx,
                    "n_gpu_layers": self.config.n_gpu_layers,
                    "threads": self.config.threads,
                    "load_on_startup": self.config.load_on_startup,
                    "max_loaded_models": self.config.max_loaded_models,
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
        setup = self._setup_error(check_model_file=True)
        if setup is not None:
            return self._error_response(setup)
        if tools and not self.config.supports_tool_calls:
            return self._error_response(
                BrainProviderError(
                    "llama-cpp-python tool-call support is disabled. Set LLAMA_CPP_INPROCESS_SUPPORTS_TOOL_CALLS=true only after verifying the model/runtime supports it.",
                    provider_id=self.provider_id(),
                    error_code="tool_calls_unsupported",
                    setup_hint="Use no-tools mode or enable tool-call support only after verification.",
                )
            )
        try:
            backend = self._load_backend()
            raw = backend.create_chat_completion(
                messages=[_message_to_openai(message) for message in messages],
                temperature=settings.temperature if settings else 0.7,
                top_p=settings.top_p if settings else 0.95,
                max_tokens=settings.max_tokens if settings else 2048,
                stop=list(settings.stop) if settings and settings.stop else None,
            )
        except Exception as exc:
            return self._error_response(
                BrainProviderError(
                    f"llama-cpp-python provider failed: {exc}",
                    provider_id=self.provider_id(),
                    error_code=exc.__class__.__name__,
                    setup_hint="Confirm the optional dependency, model path, and local build are valid.",
                )
            )
        return self._normalize_response(raw)

    def supports_tool_calls(self) -> bool:
        return self.config.supports_tool_calls

    def supports_streaming(self) -> bool:
        return False

    def supports_reasoning_content(self) -> bool:
        return False

    def supports_json_schema(self) -> bool:
        return False

    def _load_backend(self) -> LlamaCppBackend:
        if self._backend is not None:
            return self._backend
        if self._backend_factory is not None:
            self._backend = self._backend_factory(self.config)
            return self._backend
        module = importlib.import_module("llama_cpp")
        llama_class = getattr(module, "Llama")
        kwargs: dict[str, Any] = {
            "model_path": self.config.model_path,
            "n_ctx": self.config.n_ctx,
            "n_gpu_layers": self.config.n_gpu_layers,
        }
        if self.config.threads != "auto":
            kwargs["n_threads"] = int(self.config.threads)
        self._backend = llama_class(**kwargs)
        return self._backend

    def _setup_error(self, *, check_model_file: bool) -> BrainProviderError | None:
        if not self.config.enabled:
            return BrainProviderError(
                "llama-cpp-python in-process provider is disabled.",
                provider_id=self.provider_id(),
                error_code="provider_disabled",
                setup_hint="Set LLAMA_CPP_INPROCESS_ENABLED=true only after installing the optional dependency and choosing a local GGUF model.",
            )
        if not self._dependency_detector():
            return BrainProviderError(
                "Optional dependency llama-cpp-python is not installed.",
                provider_id=self.provider_id(),
                error_code="dependency_missing",
                setup_hint="Install llama-cpp-python yourself if you want this provider; the agent never installs packages automatically.",
            )
        if not self.config.model_path:
            return BrainProviderError(
                "LLAMA_CPP_INPROCESS_MODEL_PATH is not set.",
                provider_id=self.provider_id(),
                error_code="provider_not_configured",
                setup_hint="Set LLAMA_CPP_INPROCESS_MODEL_PATH to a local GGUF model path that you manage.",
            )
        if check_model_file and not Path(self.config.model_path).exists():
            return BrainProviderError(
                "LLAMA_CPP_INPROCESS_MODEL_PATH does not exist.",
                provider_id=self.provider_id(),
                error_code="model_path_missing",
                setup_hint="Choose an existing local GGUF model path; the agent never downloads models.",
            )
        return None

    def _normalize_response(self, raw: Mapping[str, Any]) -> BrainChatResponse:
        choices = raw.get("choices")
        if not isinstance(choices, list) or not choices:
            return self._error_response(
                BrainProviderError(
                    "llama-cpp-python returned a malformed response: missing choices.",
                    provider_id=self.provider_id(),
                    error_code="malformed_response",
                )
            )
        choice = choices[0] if isinstance(choices[0], Mapping) else {}
        raw_message = choice.get("message")
        content = ""
        role = "assistant"
        if isinstance(raw_message, Mapping):
            role = str(raw_message.get("role") or role)
            content = str(raw_message.get("content") or "")
        elif "text" in choice:
            content = str(choice.get("text") or "")
        else:
            return self._error_response(
                BrainProviderError(
                    "llama-cpp-python returned a malformed response: missing message.",
                    provider_id=self.provider_id(),
                    error_code="malformed_response",
                )
            )
        return BrainChatResponse(
            provider_id=self.provider_id(),
            model=self.config.model_path,
            message=BrainMessage(role=role, content=content),
            finish_reason=str(choice.get("finish_reason") or "stop"),
            usage=raw.get("usage") if isinstance(raw.get("usage"), Mapping) else {},
            raw_response=dict(raw),
        )

    def _error_response(self, error: BrainProviderError) -> BrainChatResponse:
        return BrainChatResponse(
            provider_id=self.provider_id(),
            model=self.config.model_path,
            message=BrainMessage(role="assistant", content=""),
            finish_reason="error",
            error=error,
        )


def _dependency_available() -> bool:
    return importlib.util.find_spec("llama_cpp") is not None


def _message_to_openai(message: BrainMessage | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(message, BrainMessage):
        return message.to_dict()
    return dict(message)
