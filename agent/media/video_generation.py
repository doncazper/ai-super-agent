from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from agent.media.licenses import build_license_report
from agent.media.models import MediaAssetType, MediaGenerationRequest, MediaPrompt
from agent.media.providers.mock_video import MockVideoProvider
from agent.media.safety import MediaSafetyOutcome, check_media_prompt_safety


VIDEO_PROVIDER_CANDIDATES: tuple[dict[str, Any], ...] = (
    {
        "provider_id": "mock_video",
        "name": "Mock video provider",
        "status": "stubbed",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "Test-only provider for fake video metadata/results; no real videos are generated.",
        "resource_notes": ["No GPU or model runtime is used by the mock provider."],
    },
    {
        "provider_id": "comfyui_video",
        "name": "ComfyUI video workflows",
        "status": "stubbed",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "ComfyUI workflow submission remains disabled; video workflows are metadata-only.",
        "resource_notes": ["Video workflows can require significant VRAM, disk, and execution time."],
    },
    {
        "provider_id": "wan",
        "name": "Wan video models",
        "status": "planned",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "Model/license/hardware review is future work; no model files are downloaded.",
        "resource_notes": ["Likely large model files and GPU memory requirements; validate license before use."],
    },
    {
        "provider_id": "ltx_video",
        "name": "LTX-Video",
        "status": "planned",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "Provider/runtime integration is future work.",
        "resource_notes": ["Local video generation can be slow and hardware-sensitive."],
    },
    {
        "provider_id": "hunyuan_video",
        "name": "HunyuanVideo",
        "status": "planned",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "Model/provider review is future work.",
        "resource_notes": ["Large model/runtime footprint expected; explicit setup required before use."],
    },
    {
        "provider_id": "stable_video_diffusion",
        "name": "Stable Video Diffusion",
        "status": "planned",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "License/model/runtime review is future work.",
        "resource_notes": ["Image-to-video workflows require vetted source-image policy and hardware review."],
    },
    {
        "provider_id": "image_to_video",
        "name": "Image-to-video workflow",
        "status": "future",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "Personal-image, consent, and source-asset policy must exist before use.",
        "resource_notes": ["Source images can contain personal data; disabled until a future consent/input policy exists."],
    },
    {
        "provider_id": "text_to_video",
        "name": "Text-to-video workflow",
        "status": "future",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "Text-to-video execution remains future work after provider/runtime review.",
        "resource_notes": ["Generation cost, latency, and moderation requirements must be release-gated."],
    },
)


@dataclass(frozen=True)
class VideoGenerationPlan:
    status: str
    request: MediaGenerationRequest
    provider_id: str
    safety: dict[str, Any]
    license_report: dict[str, Any]
    resource_warning: dict[str, Any]
    setup_hint: str
    dry_run: bool = True
    real_generation: bool = False
    upload_publish_enabled: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "request": self.request.to_safe_dict(),
            "provider_id": self.provider_id,
            "safety": self.safety,
            "license_report": self.license_report,
            "resource_warning": self.resource_warning,
            "setup_hint": self.setup_hint,
            "dry_run": self.dry_run,
            "real_generation": self.real_generation,
            "upload_publish_enabled": self.upload_publish_enabled,
        }


def video_provider_candidates() -> tuple[dict[str, Any], ...]:
    return VIDEO_PROVIDER_CANDIDATES


def plan_video_generation(
    prompt: str,
    *,
    provider_id: str = "auto",
    commercial_use: bool = False,
    dry_run: bool = True,
) -> VideoGenerationPlan:
    selected_provider = _select_provider(provider_id)
    request = MediaGenerationRequest(
        request_id=f"video_plan_{uuid.uuid4().hex[:12]}",
        provider=selected_provider,
        asset_type=MediaAssetType.VIDEO,
        prompt=MediaPrompt(prompt),
        parameters={"mode": "dry_run_video_plan"},
        dry_run=True,
    )
    safety = check_media_prompt_safety(
        prompt,
        provider_id="mock" if selected_provider == "mock_video" else selected_provider,
        commercial_use=bool(commercial_use),
    ).to_dict()
    resource_warning = _resource_warning(selected_provider)
    if safety["outcome"] == MediaSafetyOutcome.DENY.value:
        return VideoGenerationPlan(
            status="blocked",
            request=request,
            provider_id=selected_provider,
            safety=safety,
            license_report=build_license_report(),
            resource_warning=resource_warning,
            setup_hint="Prompt safety preflight denied this video generation request.",
        )
    if not dry_run:
        return VideoGenerationPlan(
            status="blocked",
            request=request,
            provider_id=selected_provider,
            safety=safety,
            license_report=build_license_report(),
            resource_warning=resource_warning,
            setup_hint="MEDIA-07 supports dry-run video plans only. Re-run with --dry-run.",
            dry_run=False,
        )
    provider = _candidate(selected_provider)
    if provider is None or selected_provider != "mock_video":
        return VideoGenerationPlan(
            status="requires_setup",
            request=request,
            provider_id=selected_provider,
            safety=safety,
            license_report=build_license_report(),
            resource_warning=resource_warning,
            setup_hint=(provider or {}).get("setup_hint", "No video provider is configured for real generation."),
        )
    return VideoGenerationPlan(
        status="dry_run",
        request=request,
        provider_id=selected_provider,
        safety=safety,
        license_report=build_license_report(),
        resource_warning=resource_warning,
        setup_hint="Mock video dry-run plan only; no real video is generated.",
    )


def dry_run_generate_video(prompt: str, *, provider_id: str = "auto", commercial_use: bool = False) -> dict[str, Any]:
    plan = plan_video_generation(prompt, provider_id=provider_id, commercial_use=commercial_use, dry_run=True)
    if plan.provider_id == "mock_video" and plan.status == "dry_run":
        mock_plan = MockVideoProvider().plan(plan.request)
    else:
        mock_plan = None
    payload = plan.to_dict()
    payload["mock_provider_plan"] = mock_plan
    payload["generated_media"] = False
    return payload


def _select_provider(provider_id: str) -> str:
    normalized = (provider_id or "auto").strip().lower()
    if normalized in {"auto", "mock"}:
        return "mock_video"
    return normalized


def _candidate(provider_id: str) -> dict[str, Any] | None:
    for candidate in VIDEO_PROVIDER_CANDIDATES:
        if candidate["provider_id"] == provider_id:
            return candidate
    return None


def _resource_warning(provider_id: str) -> dict[str, Any]:
    provider = _candidate(provider_id) or {}
    return {
        "review_required": True,
        "hardware_review_required": True,
        "model_downloads_enabled": False,
        "estimated_runtime_known": False,
        "notes": list(provider.get("resource_notes", ())) or [
            "Video generation can require large models, significant VRAM, disk space, and long runtimes."
        ],
    }
