from __future__ import annotations

import uuid
from typing import Any

from agent.media.audio_generation import plan_audio_generation
from agent.media.creative_workflows import infer_workflow_type, plan_creative_workflow, plan_thumbnail
from agent.media.image_generation import plan_image_generation
from agent.media.models import MediaPrompt
from agent.media.safety import MediaSafetyOutcome, check_media_prompt_safety
from agent.media.tts import plan_tts
from agent.media.video_generation import plan_video_generation


MEDIA_WORKFLOW_TARGETS = (
    "thumbnail",
    "creative_image",
    "image",
    "video",
    "image_to_video",
    "audio",
    "music",
    "tts",
)


def plan_media_request(
    request: str,
    *,
    commercial_use: bool = False,
) -> dict[str, Any]:
    """Build a media workflow plan without executing generation or provider calls."""
    target = infer_media_target(request)
    safety = check_media_prompt_safety(
        request,
        provider_id="mock",
        commercial_use=bool(commercial_use),
    ).to_dict()
    request_id = f"media_plan_{uuid.uuid4().hex[:12]}"
    base: dict[str, Any] = {
        "status": "blocked" if safety["outcome"] == MediaSafetyOutcome.DENY.value else "dry_run_plan",
        "request_id": request_id,
        "target": target,
        "request": MediaPrompt(request).to_safe_dict(),
        "safety_preflight_first": True,
        "safety": safety,
        "dry_run": True,
        "real_generation": False,
        "provider_calls_performed": False,
        "generated_media": False,
        "asset_write_performed": False,
        "upload_publish_enabled": False,
        "natural_language_safe_to_execute": False,
        "toolbroker_required_for_execution": True,
        "provider_configured_for_real_generation": False,
        "setup_hint": "Media planning is dry-run only. Real generation remains blocked until a reviewed provider is configured in a future milestone.",
        "recommended_exact_command": recommended_command_for_target(target, request),
        "next_safe_step": "Review the plan, then run the exact dry-run command if useful. Real generation is not available in this track yet.",
    }
    if safety["outcome"] == MediaSafetyOutcome.DENY.value:
        base["setup_hint"] = "Prompt safety preflight denied this media workflow request; no generation planning was executed."
        base["plan"] = None
        return base

    base["plan"] = _build_target_plan(target, request, commercial_use=bool(commercial_use))
    base["source_label"] = "planning_only"
    base["supported_targets"] = list(MEDIA_WORKFLOW_TARGETS)
    return base


def infer_media_target(request: str) -> str:
    normalized = request.casefold()
    if "thumbnail" in normalized:
        return "thumbnail"
    if "podcast cover" in normalized or "cover art" in normalized or "real estate" in normalized or "listing graphic" in normalized:
        return "creative_image"
    if "image to video" in normalized or "turn this image" in normalized:
        return "image_to_video"
    if any(term in normalized for term in ("music", "lo-fi", "lofi", "bed", "theme song")):
        return "music"
    if any(term in normalized for term in ("sound effect", "sfx", "audio", "chime")):
        return "audio"
    if any(term in normalized for term in ("video", "animation", "intro animation", "clip")):
        return "video"
    if any(term in normalized for term in ("tts", "text to speech", "voiceover", "read this", "narration")):
        return "tts"
    if any(term in normalized for term in ("image", "graphic", "poster", "mockup")):
        return "image"
    workflow_type = infer_workflow_type(request)
    if workflow_type != "social_post_image":
        return "creative_image"
    return "creative_image"


def recommended_command_for_target(target: str, request: str) -> str:
    escaped = request.replace('"', '\\"')
    if target == "thumbnail":
        return f'python smart_agent.py media thumbnail "{escaped}" --dry-run'
    if target == "video":
        return f'python smart_agent.py media generate video "{escaped}" --dry-run'
    if target == "image_to_video":
        return f'python smart_agent.py media generate video "{escaped}" --dry-run'
    if target == "audio":
        return f'python smart_agent.py media generate audio "{escaped}" --dry-run'
    if target == "music":
        return f'python smart_agent.py media generate music "{escaped}" --dry-run'
    if target == "tts":
        return f'python smart_agent.py media tts plan "{escaped}"'
    if target == "image":
        return f'python smart_agent.py media generate image "{escaped}" --dry-run'
    return f'python smart_agent.py media creative plan "{escaped}"'


def _build_target_plan(target: str, request: str, *, commercial_use: bool) -> dict[str, Any]:
    if target == "thumbnail":
        return plan_thumbnail(request, commercial_use=commercial_use)
    if target == "creative_image":
        return plan_creative_workflow(request, workflow_type="auto", commercial_use=commercial_use)
    if target == "image":
        return plan_image_generation(request, commercial_use=commercial_use, dry_run=True).to_dict()
    if target in {"video", "image_to_video"}:
        plan = plan_video_generation(request, commercial_use=commercial_use, dry_run=True).to_dict()
        if target == "image_to_video":
            plan["source_image_inputs_enabled"] = False
            plan["setup_hint"] = "Image-to-video is planned only; source image input handling is not implemented."
        return plan
    if target == "audio":
        return plan_audio_generation(request, mode="audio", commercial_use=commercial_use, dry_run=True).to_dict()
    if target == "music":
        return plan_audio_generation(request, mode="music", commercial_use=commercial_use, dry_run=True).to_dict()
    if target == "tts":
        return plan_tts(request)
    return plan_creative_workflow(request, workflow_type="auto", commercial_use=commercial_use)
