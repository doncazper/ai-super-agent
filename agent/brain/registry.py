from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from agent.brain.base import BrainProvider
from agent.brain.config import BrainRuntimeConfig
from agent.brain.errors import BrainProviderNotFoundError, normalize_provider_error
from agent.brain.models import BrainProviderStatus
from agent.brain.mock_provider import MockBrainProvider


ProviderFactory = Callable[[], BrainProvider]


@dataclass(frozen=True)
class BrainProviderRegistration:
    provider_id: str
    provider_name: str
    factory: ProviderFactory
    lazy: bool = True
    setup_hint: str = ""
    default_status: str = "registered_lazy"

    def to_dict(self) -> dict[str, object]:
        return {
            "provider_id": self.provider_id,
            "provider_name": self.provider_name,
            "lazy": self.lazy,
            "setup_hint": self.setup_hint,
            "default_status": self.default_status,
        }


class BrainProviderRegistry:
    """Lazy model provider registry.

    Listing registrations does not instantiate providers or load models.
    """

    def __init__(
        self,
        registrations: Iterable[BrainProviderRegistration] = (),
        *,
        config: BrainRuntimeConfig | None = None,
    ) -> None:
        self.config = config or BrainRuntimeConfig()
        self._registrations: dict[str, BrainProviderRegistration] = {}
        self._instances: dict[str, BrainProvider] = {}
        for registration in registrations:
            self.register_provider(registration)

    def register_provider(self, registration: BrainProviderRegistration) -> None:
        provider_id = _normalize_provider_id(registration.provider_id)
        self._registrations[provider_id] = BrainProviderRegistration(
            provider_id=provider_id,
            provider_name=registration.provider_name,
            factory=registration.factory,
            lazy=registration.lazy,
            setup_hint=registration.setup_hint,
            default_status=registration.default_status,
        )

    def list_providers(self) -> tuple[BrainProviderRegistration, ...]:
        return tuple(self._registrations[provider_id] for provider_id in self.ordered_provider_ids())

    def list_provider_status(self) -> tuple[BrainProviderStatus, ...]:
        return tuple(self.provider_status(provider_id) for provider_id in self.ordered_provider_ids())

    def provider_status(self, provider_id: str) -> BrainProviderStatus:
        normalized = _normalize_provider_id(provider_id)
        registration = self._registrations.get(normalized)
        if registration is None:
            return BrainProviderStatus(
                provider_id=normalized,
                provider_name=normalized,
                registered=False,
                configured=False,
                available=False,
                lazy=True,
                setup_hint="Configure or register a supported brain provider.",
                status="unknown",
            )
        instance = self._instances.get(normalized)
        if instance is None:
            return BrainProviderStatus(
                provider_id=registration.provider_id,
                provider_name=registration.provider_name,
                registered=True,
                configured=None,
                available=None,
                lazy=registration.lazy,
                setup_hint=registration.setup_hint,
                status=registration.default_status,
            )
        return BrainProviderStatus(
            provider_id=registration.provider_id,
            provider_name=registration.provider_name,
            registered=True,
            configured=instance.is_configured(),
            available=instance.is_available(),
            lazy=registration.lazy,
            setup_hint=registration.setup_hint,
            status="available" if instance.is_available() else "requires_setup",
        )

    def ordered_provider_ids(self) -> tuple[str, ...]:
        configured_order = [_normalize_provider_id(provider_id) for provider_id in self.config.provider_order]
        known = set(self._registrations)
        ordered = [provider_id for provider_id in configured_order if provider_id in known]
        ordered.extend(sorted(known.difference(ordered)))
        return tuple(ordered)

    def get_provider(self, provider_id: str) -> BrainProvider | None:
        normalized = _normalize_provider_id(provider_id)
        registration = self._registrations.get(normalized)
        if registration is None:
            return None
        if normalized not in self._instances:
            self._instances[normalized] = registration.factory()
        return self._instances[normalized]

    def require_provider(self, provider_id: str) -> BrainProvider:
        provider = self.get_provider(provider_id)
        if provider is None:
            raise BrainProviderNotFoundError(_normalize_provider_id(provider_id), known_provider_ids=tuple(sorted(self._registrations)))
        return provider

    def default_provider(self) -> BrainProvider | None:
        return self.get_provider(self.config.default_provider)

    def configured_providers(self) -> tuple[BrainProvider, ...]:
        providers = []
        for provider_id in self.ordered_provider_ids():
            provider = self.get_provider(provider_id)
            if provider is not None and provider.is_configured():
                providers.append(provider)
        return tuple(providers)

    def health_summary(self, *, include_unconfigured: bool = True) -> dict[str, object]:
        providers = []
        for provider_id in self.ordered_provider_ids():
            provider = self.get_provider(provider_id)
            if provider is None:
                continue
            if not include_unconfigured and not provider.is_configured():
                continue
            try:
                health = provider.health_check()
            except Exception as exc:  # defensive normalization for provider boundary
                health = normalize_provider_error(exc, provider_id=provider_id)
                providers.append({"provider_id": provider_id, "status": "error", "error": health.to_dict()})
                continue
            providers.append(health.to_dict())
        default = self.default_provider()
        return {
            "default_provider_id": self.config.default_provider,
            "default_provider_registered": default is not None,
            "fallback_enabled": self.config.fallback_enabled,
            "providers": providers,
        }


def make_mock_registration(provider: MockBrainProvider | None = None) -> BrainProviderRegistration:
    instance = provider
    return BrainProviderRegistration(
        provider_id="mock",
        provider_name="Mock Brain Provider",
        factory=lambda: instance or MockBrainProvider(),
        lazy=True,
        setup_hint="Enable BRAIN_MOCK_PROVIDER_ENABLED=true in tests.",
    )


def make_lmstudio_registration() -> BrainProviderRegistration:
    def factory() -> BrainProvider:
        from agent.brain.providers.lmstudio import LMStudioBrainProvider

        return LMStudioBrainProvider()

    return BrainProviderRegistration(
        provider_id="lmstudio",
        provider_name="LM Studio",
        factory=factory,
        lazy=True,
        setup_hint="Set LMSTUDIO_MODEL and start the LM Studio Developer Server.",
    )


def make_llama_cpp_server_registration(config: BrainRuntimeConfig) -> BrainProviderRegistration:
    def factory() -> BrainProvider:
        from agent.brain.providers.llama_cpp_server import LlamaCppServerBrainProvider, LlamaCppServerConfig

        return LlamaCppServerBrainProvider(
            LlamaCppServerConfig(
                enabled=config.llama_cpp_server_enabled,
                base_url=config.llama_cpp_server_base_url,
                model=config.llama_cpp_server_model,
                timeout_seconds=config.llama_cpp_server_timeout_seconds,
                supports_tool_calls=config.llama_cpp_server_supports_tool_calls,
                supports_streaming=config.llama_cpp_server_supports_streaming,
            )
        )

    return BrainProviderRegistration(
        provider_id="llama_cpp_server",
        provider_name="llama.cpp server",
        factory=factory,
        lazy=True,
        setup_hint="Set LLAMA_CPP_SERVER_ENABLED=true and LLAMA_CPP_SERVER_MODEL for a user-managed llama.cpp server.",
        default_status="registered_lazy" if config.llama_cpp_server_enabled else "disabled",
    )


def make_ollama_registration(config: BrainRuntimeConfig) -> BrainProviderRegistration:
    def factory() -> BrainProvider:
        from agent.brain.providers.ollama import OllamaBrainProvider, OllamaConfig

        return OllamaBrainProvider(
            OllamaConfig(
                enabled=config.ollama_enabled,
                base_url=config.ollama_base_url,
                model=config.ollama_model,
                openai_compat_base_url=config.ollama_openai_compat_base_url,
                timeout_seconds=config.ollama_timeout_seconds,
                supports_tool_calls=config.ollama_supports_tool_calls,
                supports_streaming=config.ollama_supports_streaming,
            )
        )

    return BrainProviderRegistration(
        provider_id="ollama",
        provider_name="Ollama",
        factory=factory,
        lazy=True,
        setup_hint="Set OLLAMA_ENABLED=true and OLLAMA_MODEL for a user-managed local Ollama daemon.",
        default_status="registered_lazy" if config.ollama_enabled else "disabled",
    )


def make_llama_cpp_inprocess_registration(config: BrainRuntimeConfig) -> BrainProviderRegistration:
    def factory() -> BrainProvider:
        from agent.brain.providers.llama_cpp_inprocess import LlamaCppInProcessBrainProvider, LlamaCppInProcessConfig

        return LlamaCppInProcessBrainProvider(
            LlamaCppInProcessConfig(
                enabled=config.llama_cpp_inprocess_enabled,
                model_path=config.llama_cpp_inprocess_model_path,
                n_ctx=config.llama_cpp_inprocess_n_ctx,
                n_gpu_layers=config.llama_cpp_inprocess_n_gpu_layers,
                threads=config.llama_cpp_inprocess_threads,
                supports_tool_calls=config.llama_cpp_inprocess_supports_tool_calls,
                load_on_startup=config.llama_cpp_inprocess_load_on_startup,
                max_loaded_models=config.llama_cpp_inprocess_max_loaded_models,
            )
        )

    return BrainProviderRegistration(
        provider_id="llama_cpp_inprocess",
        provider_name="llama-cpp-python in-process",
        factory=factory,
        lazy=True,
        setup_hint="Set LLAMA_CPP_INPROCESS_ENABLED=true and LLAMA_CPP_INPROCESS_MODEL_PATH after installing the optional dependency yourself.",
        default_status="registered_lazy" if config.llama_cpp_inprocess_enabled else "disabled",
    )


def make_mlx_registration(config: BrainRuntimeConfig) -> BrainProviderRegistration:
    def factory() -> BrainProvider:
        from agent.brain.providers.mlx import MLXBrainProvider, MLXProviderConfig

        return MLXBrainProvider(
            MLXProviderConfig(
                enabled=config.mlx_provider_enabled,
                mode=config.mlx_provider_mode,
                server_base_url=config.mlx_server_base_url,
                model=config.mlx_model,
                supports_tool_calls=config.mlx_supports_tool_calls,
                load_on_startup=config.mlx_load_on_startup,
            )
        )

    return BrainProviderRegistration(
        provider_id="mlx",
        provider_name="MLX experimental stub",
        factory=factory,
        lazy=True,
        setup_hint="MLX is experimental; no MLX dependency, model, server, or in-process runtime is loaded by this stub.",
        default_status="registered_lazy" if config.mlx_provider_enabled else "disabled",
    )


def default_registry(config: BrainRuntimeConfig | None = None) -> BrainProviderRegistry:
    active_config = config or BrainRuntimeConfig.from_env()
    registrations: list[BrainProviderRegistration] = [
        make_lmstudio_registration(),
        make_llama_cpp_server_registration(active_config),
        make_ollama_registration(active_config),
        make_llama_cpp_inprocess_registration(active_config),
        make_mlx_registration(active_config),
    ]
    if active_config.mock_provider_enabled:
        registrations.append(make_mock_registration())
    return BrainProviderRegistry(registrations, config=active_config)


def _normalize_provider_id(provider_id: str) -> str:
    return provider_id.strip().casefold().replace("-", "_")
