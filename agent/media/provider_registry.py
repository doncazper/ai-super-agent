from __future__ import annotations

from collections.abc import Iterable

from agent.media.models import MediaProvider, MediaProviderCapability, MediaProviderStatus


class MediaProviderRegistry:
    """Static, provider-neutral creative media registry.

    Registry operations are metadata-only. They do not import provider SDKs,
    download models, generate media, upload assets, or call paid APIs.
    """

    def __init__(self, providers: Iterable[MediaProvider] | None = None) -> None:
        configured = tuple(providers) if providers is not None else tuple(_default_providers())
        self._providers = {provider.provider_id: provider for provider in configured}

    def list_providers(self) -> tuple[MediaProvider, ...]:
        return tuple(sorted(self._providers.values(), key=lambda provider: provider.provider_id))

    def get_provider(self, provider_id: str) -> MediaProvider:
        normalized = provider_id.strip().lower()
        provider = self._providers.get(normalized)
        if provider is not None:
            return provider
        return MediaProvider(
            provider_id=normalized or "unknown",
            name="Unknown media provider",
            status=MediaProviderStatus.UNSUPPORTED,
            capabilities=(),
            default_enabled=False,
            local_only=False,
            paid_api=False,
            requires_model_download=False,
            setup_hint=f"Unknown media provider. Known providers: {', '.join(sorted(self._providers))}.",
            docs_path="docs/media/MEDIA_PROVIDER_REGISTRY.md",
            risk_level="FORBIDDEN",
            trust_level="MODEL_OUTPUT",
            notes=("Unsupported provider records are never executable.",),
        )

    def doctor(self) -> dict[str, object]:
        providers = self.list_providers()
        return {
            "status": "ok",
            "provider_count": len(providers),
            "providers": [provider.to_dict() for provider in providers],
            "real_generation_enabled": False,
            "paid_apis_enabled": False,
            "model_downloads_enabled": False,
            "uploads_or_publishing_enabled": False,
            "voice_cloning_enabled": False,
            "real_person_likeness_workflows_enabled": False,
            "provider_calls_performed": False,
            "heavy_runtime_imports": False,
            "warnings": [
                "MEDIA-02 is a scaffold: provider records are metadata only.",
                "Generation, editing, video, audio, music, TTS, uploads, and publishing remain future gated work.",
                "Mock provider records are for tests and dogfood planning only; they do not generate media.",
            ],
            "next_setup_steps": [
                "Use MEDIA-03 for prompt/output safety, copyright, consent, and license policy before generation.",
                "Use provider-specific future prompts for ComfyUI/image/video/audio/TTS stubs before any real provider wiring.",
                "Declare every future executable media capability in config/capabilities.yaml before ToolBroker execution.",
            ],
        }


def default_media_provider_registry() -> MediaProviderRegistry:
    return MediaProviderRegistry()


def _default_providers() -> tuple[MediaProvider, ...]:
    return (
        MediaProvider(
            provider_id="mock",
            name="Mock media provider",
            status=MediaProviderStatus.STUBBED,
            capabilities=(MediaProviderCapability.STATUS, MediaProviderCapability.SAFETY_CHECK),
            default_enabled=False,
            local_only=True,
            paid_api=False,
            requires_model_download=False,
            setup_hint="Mock provider is available only for tests/dogfood scaffolds and does not generate media.",
            docs_path="docs/media/MEDIA_PROVIDER_REGISTRY.md",
            risk_level="SAFE",
            trust_level="MODEL_OUTPUT",
            notes=("No real media output is produced.",),
        ),
        MediaProvider(
            provider_id="comfyui",
            name="ComfyUI",
            status=MediaProviderStatus.PLANNED,
            capabilities=(MediaProviderCapability.IMAGE_GENERATION, MediaProviderCapability.IMAGE_EDITING),
            default_enabled=False,
            local_only=True,
            paid_api=False,
            requires_model_download=False,
            setup_hint="ComfyUI strategy/stub is deferred to MEDIA-04; do not import or start ComfyUI in MEDIA-02.",
            docs_path="docs/media/MEDIA_PROVIDER_STRATEGY.md",
            risk_level="MEDIUM",
            trust_level="MODEL_OUTPUT",
            notes=("No ComfyUI runtime import, server call, model download, or workflow execution exists.",),
        ),
        MediaProvider(
            provider_id="external_paid",
            name="External paid media APIs",
            status=MediaProviderStatus.BLOCKED,
            capabilities=(
                MediaProviderCapability.IMAGE_GENERATION,
                MediaProviderCapability.VIDEO_GENERATION,
                MediaProviderCapability.AUDIO_GENERATION,
            ),
            default_enabled=False,
            local_only=False,
            paid_api=True,
            requires_model_download=False,
            setup_hint="Paid/cloud media APIs are blocked by default and require a future explicit policy and approval milestone.",
            docs_path="docs/media/MEDIA_RISK_MODEL.md",
            risk_level="HIGH",
            trust_level="MODEL_OUTPUT",
            notes=("No paid API calls are allowed by default.",),
        ),
    )
