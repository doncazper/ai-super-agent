from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from agent.media.licenses import build_license_report
from agent.media.models import MediaAssetType, MediaGenerationRequest, MediaPrompt
from agent.media.providers.mock_image import MockImageProvider
from agent.media.safety import MediaSafetyOutcome, check_media_prompt_safety


IMAGE_PROVIDER_CANDIDATES: tuple[dict[str, Any], ...] = (
    {
        "provider_id": "mock_image",
        "name": "Mock image provider",
        "status": "stubbed",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "Test-only provider for fake metadata/results; no real images are generated.",
    },
    {
        "provider_id": "comfyui",
        "name": "ComfyUI workflows",
        "status": "stubbed",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "ComfyUI workflow submission remains disabled; use media comfyui doctor.",
    },
    {
        "provider_id": "diffusers",
        "name": "Diffusers local provider",
        "status": "planned",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "No diffusion libraries are installed or imported in MEDIA-05.",
    },
    {
        "provider_id": "sdxl",
        "name": "SDXL",
        "status": "planned",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "Model license, model files, and local provider are future work.",
    },
    {
        "provider_id": "flux",
        "name": "FLUX.1-schnell / FLUX.1-dev",
        "status": "planned",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "License/model-card review and local provider strategy are future work.",
    },
    {
        "provider_id": "stable_diffusion_3",
        "name": "Stable Diffusion 3.x",
        "status": "planned",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "License restrictions and local runtime strategy must be reviewed before use.",
    },
    {
        "provider_id": "qwen_image",
        "name": "Qwen-Image",
        "status": "planned",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "Model/provider review is future work.",
    },
    {
        "provider_id": "controlnet_lora",
        "name": "ControlNet/LoRA workflows",
        "status": "future",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "Personal-image and workflow-vetting policy must exist before use.",
    },
)


@dataclass(frozen=True)
class ImageGenerationPlan:
    status: str
    request: MediaGenerationRequest
    provider_id: str
    safety: dict[str, Any]
    license_report: dict[str, Any]
    setup_hint: str
    dry_run: bool = True
    real_generation: bool = False
    asset_manager_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "request": self.request.to_safe_dict(),
            "provider_id": self.provider_id,
            "safety": self.safety,
            "license_report": self.license_report,
            "setup_hint": self.setup_hint,
            "dry_run": self.dry_run,
            "real_generation": self.real_generation,
            "asset_manager_required": self.asset_manager_required,
        }


def image_provider_candidates() -> tuple[dict[str, Any], ...]:
    return IMAGE_PROVIDER_CANDIDATES


def plan_image_generation(
    prompt: str,
    *,
    provider_id: str = "auto",
    commercial_use: bool = False,
    dry_run: bool = True,
) -> ImageGenerationPlan:
    selected_provider = _select_provider(provider_id)
    request = MediaGenerationRequest(
        request_id=f"image_plan_{uuid.uuid4().hex[:12]}",
        provider=selected_provider,
        asset_type=MediaAssetType.IMAGE,
        prompt=MediaPrompt(prompt),
        dry_run=True,
    )
    safety = check_media_prompt_safety(prompt, provider_id="mock" if selected_provider == "mock_image" else selected_provider, commercial_use=commercial_use).to_dict()
    if safety["outcome"] == MediaSafetyOutcome.DENY.value:
        return ImageGenerationPlan(
            status="blocked",
            request=request,
            provider_id=selected_provider,
            safety=safety,
            license_report=build_license_report(),
            setup_hint="Prompt safety preflight denied this image generation request.",
            dry_run=True,
            real_generation=False,
        )
    if not dry_run:
        return ImageGenerationPlan(
            status="blocked",
            request=request,
            provider_id=selected_provider,
            safety=safety,
            license_report=build_license_report(),
            setup_hint="MEDIA-05 supports dry-run plans only. Re-run with --dry-run.",
            dry_run=False,
            real_generation=False,
        )
    provider = _candidate(selected_provider)
    if provider is None or selected_provider != "mock_image":
        return ImageGenerationPlan(
            status="requires_setup",
            request=request,
            provider_id=selected_provider,
            safety=safety,
            license_report=build_license_report(),
            setup_hint=(provider or {}).get("setup_hint", "No image provider is configured for real generation."),
            dry_run=True,
            real_generation=False,
        )
    return ImageGenerationPlan(
        status="dry_run",
        request=request,
        provider_id=selected_provider,
        safety=safety,
        license_report=build_license_report(),
        setup_hint="Mock image dry-run plan only; no real image is generated.",
        dry_run=True,
        real_generation=False,
    )


def dry_run_generate_image(prompt: str, *, provider_id: str = "auto", commercial_use: bool = False) -> dict[str, Any]:
    plan = plan_image_generation(prompt, provider_id=provider_id, commercial_use=commercial_use, dry_run=True)
    if plan.provider_id == "mock_image" and plan.status == "dry_run":
        mock_plan = MockImageProvider().plan(plan.request)
    else:
        mock_plan = None
    payload = plan.to_dict()
    payload["mock_provider_plan"] = mock_plan
    payload["generated_media"] = False
    return payload


def _select_provider(provider_id: str) -> str:
    normalized = (provider_id or "auto").strip().lower()
    if normalized in {"auto", "mock"}:
        return "mock_image"
    return normalized


def _candidate(provider_id: str) -> dict[str, Any] | None:
    for candidate in IMAGE_PROVIDER_CANDIDATES:
        if candidate["provider_id"] == provider_id:
            return candidate
    return None
