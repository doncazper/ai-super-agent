from __future__ import annotations

import platform
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

from agent.brain.base import BrainProvider
from agent.brain.errors import BrainProviderError
from agent.brain.models import (
    BrainChatResponse,
    BrainGenerationSettings,
    BrainMessage,
    BrainModelInfo,
    BrainProviderHealth,
)


AppleSiliconDetector = Callable[[], bool]


@dataclass(frozen=True)
class MLXProviderConfig:
    enabled: bool = False
    mode: str = "server"
    server_base_url: str = "http://localhost:8081/v1"
    model: str = ""
    supports_tool_calls: bool = False
    load_on_startup: bool = False


class MLXBrainProvider(BrainProvider):
    """Experimental MLX provider stub.

    The stub intentionally does not import MLX, call a server, or load a model.
    It exists so future MLX work can fit the provider registry without changing
    core runtime surfaces.
    """

    def __init__(
        self,
        config: MLXProviderConfig | None = None,
        *,
        apple_silicon_detector: AppleSiliconDetector | None = None,
    ) -> None:
        self.config = config or MLXProviderConfig()
        self._apple_silicon_detector = apple_silicon_detector or _is_apple_silicon

    def provider_id(self) -> str:
        return "mlx"

    def provider_name(self) -> str:
        return "MLX experimental stub"

    def is_configured(self) -> bool:
        return False

    def is_available(self) -> bool:
        return False

    def health_check(self) -> BrainProviderHealth:
        setup = self._setup_error()
        return BrainProviderHealth(
            provider_id=self.provider_id(),
            status="disabled" if not self.config.enabled else "requires_setup",
            configured=False,
            available=False,
            error=setup,
            setup_hint=setup.setup_hint,
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
                supports_streaming=False,
                supports_reasoning_content=False,
                supports_json_schema=False,
                metadata={
                    "mode": self.config.mode,
                    "server_base_url": self.config.server_base_url,
                    "load_on_startup": self.config.load_on_startup,
                    "apple_silicon_detected": self._apple_silicon_detector(),
                    "experimental_stub": True,
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
        return BrainChatResponse(
            provider_id=self.provider_id(),
            model=self.config.model,
            message=BrainMessage(role="assistant", content=""),
            finish_reason="error",
            error=self._setup_error(),
        )

    def supports_tool_calls(self) -> bool:
        return self.config.supports_tool_calls

    def supports_streaming(self) -> bool:
        return False

    def supports_reasoning_content(self) -> bool:
        return False

    def supports_json_schema(self) -> bool:
        return False

    def _setup_error(self) -> BrainProviderError:
        if not self.config.enabled:
            return BrainProviderError(
                "MLX provider is disabled.",
                provider_id=self.provider_id(),
                error_code="provider_disabled",
                setup_hint="MLX is experimental. Set MLX_PROVIDER_ENABLED=true only in a future approved implementation pass.",
            )
        if self.config.mode not in {"server", "inprocess"}:
            return BrainProviderError(
                "MLX_PROVIDER_MODE must be server or inprocess.",
                provider_id=self.provider_id(),
                error_code="invalid_mode",
                setup_hint="Use MLX_PROVIDER_MODE=server or MLX_PROVIDER_MODE=inprocess.",
            )
        if not self._apple_silicon_detector():
            return BrainProviderError(
                "MLX is intended for Apple Silicon and is not available on this runtime.",
                provider_id=self.provider_id(),
                error_code="unsupported_platform",
                setup_hint="Use LM Studio or another configured provider on non-Apple-Silicon systems.",
            )
        if not self.config.model:
            return BrainProviderError(
                "MLX_MODEL is not set.",
                provider_id=self.provider_id(),
                error_code="provider_not_configured",
                setup_hint="Future MLX support will require an explicit local model; the agent never downloads models.",
            )
        return BrainProviderError(
            "MLX provider is a strategy stub and cannot generate text yet.",
            provider_id=self.provider_id(),
            error_code="provider_stubbed",
            setup_hint="Wait for a future approved MLX implementation and release gate before using this provider.",
        )


def _is_apple_silicon() -> bool:
    return platform.system() == "Darwin" and platform.machine() in {"arm64", "aarch64"}
