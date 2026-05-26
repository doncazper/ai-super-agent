from __future__ import annotations

from typing import Any, Callable

from agent.media.audio_generation import (
    audio_provider_candidates,
    dry_run_generate_audio,
    dry_run_generate_music,
    plan_audio_generation,
)
from agent.media.asset_manager import MediaAssetManager
from agent.media.creative_workflows import list_creative_templates, plan_creative_workflow, plan_thumbnail
from agent.media.errors import MediaAssetError
from agent.media.image_generation import dry_run_generate_image, image_provider_candidates, plan_image_generation
from agent.media.licenses import build_license_report
from agent.media.provider_registry import MediaProviderRegistry, default_media_provider_registry
from agent.media.providers.comfyui import ComfyUIProvider
from agent.media.safety import build_consent_policy, check_media_prompt_safety
from agent.media.tts import list_voice_providers, plan_tts, voice_consent_policy
from agent.media.video_generation import dry_run_generate_video, plan_video_generation, video_provider_candidates
from agent.media.workflow_planner import plan_media_request
from agent.tools.errors import ToolError


def _schema(
    name: str,
    description: str,
    properties: dict[str, Any] | None = None,
    required: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties or {},
                "required": required or [],
                "additionalProperties": False,
            },
        },
    }


MEDIA_SCHEMAS: dict[str, dict[str, Any]] = {
    "media.providers": _schema(
        "media.providers",
        "List creative media provider metadata without provider calls, model downloads, or media generation.",
    ),
    "media.doctor": _schema(
        "media.doctor",
        "Show creative media scaffold status and safety gates without provider calls or media generation.",
    ),
    "media.plan": _schema(
        "media.plan",
        "Plan a media workflow from a natural-language request without provider calls, generation, upload, or publishing.",
        {
            "request": {"type": "string"},
            "commercial_use": {"type": "boolean"},
        },
        ["request"],
    ),
    "media.assets.list": _schema(
        "media.assets.list",
        "List generated-media asset metadata under the controlled media workspace.",
    ),
    "media.assets.show": _schema(
        "media.assets.show",
        "Show one media asset metadata record from the controlled media workspace.",
        {"asset_id": {"type": "string"}},
        ["asset_id"],
    ),
    "media.assets.cleanup": _schema(
        "media.assets.cleanup",
        "Dry-run cleanup of media asset metadata under the controlled media workspace.",
        {"dry_run": {"type": "boolean"}, "older_than_seconds": {"type": "integer", "minimum": 0}},
        ["dry_run"],
    ),
    "media.safety_check": _schema(
        "media.safety_check",
        "Classify a media prompt with deterministic local safety, consent, and license checks; no generation.",
        {
            "prompt": {"type": "string"},
            "provider_id": {"type": "string"},
            "commercial_use": {"type": "boolean"},
        },
        ["prompt"],
    ),
    "media.license.report": _schema(
        "media.license.report",
        "Report provider/model license metadata and uncertainty without legal advice or media generation.",
    ),
    "media.consent.policy": _schema(
        "media.consent.policy",
        "Show operational consent policy for likeness and voice workflows without enabling generation.",
    ),
    "media.comfyui.doctor": _schema(
        "media.comfyui.doctor",
        "Show ComfyUI provider stub status without starting ComfyUI, downloading models, submitting workflows, or generating media.",
        {"check_server": {"type": "boolean"}},
    ),
    "media.workflows.list": _schema(
        "media.workflows.list",
        "List vetted media workflow metadata for a provider without reading unvetted workflow bodies or submitting workflows.",
        {"provider": {"type": "string"}},
    ),
    "media.generate.image": _schema(
        "media.generate.image",
        "Create a dry-run image generation plan only; MEDIA-05 never generates real images.",
        {
            "prompt": {"type": "string"},
            "provider": {"type": "string"},
            "commercial_use": {"type": "boolean"},
            "dry_run": {"type": "boolean"},
        },
        ["prompt", "dry_run"],
    ),
    "media.image.providers": _schema(
        "media.image.providers",
        "List image provider candidates and setup hints without importing generation runtimes.",
    ),
    "media.image.plan": _schema(
        "media.image.plan",
        "Build an image generation dry-run plan with safety and license metadata.",
        {
            "prompt": {"type": "string"},
            "provider": {"type": "string"},
            "commercial_use": {"type": "boolean"},
        },
        ["prompt"],
    ),
    "media.thumbnail": _schema(
        "media.thumbnail",
        "Build a dry-run thumbnail/social creative plan; MEDIA-06 never edits or generates real images.",
        {
            "prompt": {"type": "string"},
            "dry_run": {"type": "boolean"},
            "commercial_use": {"type": "boolean"},
        },
        ["prompt", "dry_run"],
    ),
    "media.creative.plan": _schema(
        "media.creative.plan",
        "Build a dry-run creative workflow plan with template, safety, license, and size metadata.",
        {
            "prompt": {"type": "string"},
            "workflow_type": {"type": "string"},
            "commercial_use": {"type": "boolean"},
        },
        ["prompt"],
    ),
    "media.creative.templates": _schema(
        "media.creative.templates",
        "List creative workflow templates without generating, editing, uploading, or publishing media.",
    ),
    "media.generate.video": _schema(
        "media.generate.video",
        "Create a dry-run video generation plan only; MEDIA-07 never generates real videos.",
        {
            "prompt": {"type": "string"},
            "provider": {"type": "string"},
            "commercial_use": {"type": "boolean"},
            "dry_run": {"type": "boolean"},
        },
        ["prompt", "dry_run"],
    ),
    "media.video.providers": _schema(
        "media.video.providers",
        "List video provider candidates and resource/setup hints without importing video runtimes.",
    ),
    "media.video.plan": _schema(
        "media.video.plan",
        "Build a video generation dry-run plan with safety, license, and resource metadata.",
        {
            "prompt": {"type": "string"},
            "provider": {"type": "string"},
            "commercial_use": {"type": "boolean"},
        },
        ["prompt"],
    ),
    "media.generate.audio": _schema(
        "media.generate.audio",
        "Create a dry-run audio generation plan only; MEDIA-08 never generates real audio.",
        {
            "prompt": {"type": "string"},
            "provider": {"type": "string"},
            "commercial_use": {"type": "boolean"},
            "dry_run": {"type": "boolean"},
        },
        ["prompt", "dry_run"],
    ),
    "media.generate.music": _schema(
        "media.generate.music",
        "Create a dry-run music generation plan only; MEDIA-08 never generates real music.",
        {
            "prompt": {"type": "string"},
            "provider": {"type": "string"},
            "commercial_use": {"type": "boolean"},
            "dry_run": {"type": "boolean"},
        },
        ["prompt", "dry_run"],
    ),
    "media.audio.providers": _schema(
        "media.audio.providers",
        "List audio/music provider candidates and license/setup hints without importing audio runtimes.",
    ),
    "media.music.plan": _schema(
        "media.music.plan",
        "Build a music generation dry-run plan with safety and license metadata.",
        {
            "prompt": {"type": "string"},
            "provider": {"type": "string"},
            "commercial_use": {"type": "boolean"},
        },
        ["prompt"],
    ),
    "media.tts.plan": _schema(
        "media.tts.plan",
        "Build a TTS/voice strategy plan without generating voice audio.",
        {
            "text": {"type": "string"},
            "voice_category": {"type": "string"},
        },
        ["text"],
    ),
    "media.voice.consent_policy": _schema(
        "media.voice.consent_policy",
        "Show voice consent policy without enabling voice cloning or generation.",
    ),
    "media.voice.providers": _schema(
        "media.voice.providers",
        "List TTS/voice provider candidates without importing runtimes or generating voice audio.",
    ),
}


def _with_audit(payload: dict[str, Any], summary: str, *, files_read: list[str] | None = None) -> dict[str, Any]:
    payload["_audit"] = {
        "files_read": files_read or [],
        "files_written": [],
        "commands_run": [],
        "network_domains": [],
        "result_summary": summary,
    }
    return payload


def make_media_tools(
    *,
    project_root: str = ".",
    provider_registry: MediaProviderRegistry | None = None,
    asset_manager: MediaAssetManager | None = None,
) -> dict[str, Callable[..., dict[str, Any]]]:
    registry = provider_registry or default_media_provider_registry()
    assets = asset_manager or MediaAssetManager(project_root=project_root)

    def providers() -> dict[str, Any]:
        provider_records = [provider.to_dict() for provider in registry.list_providers()]
        return _with_audit(
            {
                "status": "ok",
                "provider_count": len(provider_records),
                "providers": provider_records,
                "provider_calls_performed": False,
                "real_generation_enabled": False,
                "paid_apis_enabled": False,
            },
            f"Listed {len(provider_records)} creative media provider records without provider calls.",
        )

    def doctor() -> dict[str, Any]:
        payload = registry.doctor()
        payload["asset_manager"] = assets.status()
        payload["asset_manager"]["raw_prompt_storage"] = False
        payload["asset_manager"]["auto_publish_enabled"] = False
        return _with_audit(payload, "Ran creative media doctor without provider calls or media generation.")

    def media_plan(request: str, commercial_use: bool = False) -> dict[str, Any]:
        payload = plan_media_request(request, commercial_use=bool(commercial_use))
        return _with_audit(
            payload,
            f"Built media workflow plan for {payload['target']} with status {payload['status']}; no media was generated.",
        )

    def assets_list() -> dict[str, Any]:
        records = [asset.to_dict() for asset in assets.list_assets()]
        return _with_audit(
            {
                "status": "ok",
                "asset_count": len(records),
                "assets": records,
                "media_root": str(assets.media_root),
                "raw_prompts_returned": False,
                "personal_inputs_returned": False,
            },
            f"Listed {len(records)} media asset metadata records.",
            files_read=[str(assets.media_root)],
        )

    def assets_show(asset_id: str) -> dict[str, Any]:
        asset = assets.get_asset(asset_id)
        if asset is None:
            return _with_audit(
                {
                    "status": "not_found",
                    "asset_id": asset_id,
                    "media_root": str(assets.media_root),
                    "raw_prompts_returned": False,
                },
                f"Media asset {asset_id!r} was not found.",
                files_read=[str(assets.media_root)],
            )
        return _with_audit(
            {"status": "ok", "asset": asset.to_dict(), "raw_prompts_returned": False},
            f"Read media asset metadata for {asset_id!r}.",
            files_read=[asset.path],
        )

    def assets_cleanup(dry_run: bool = True, older_than_seconds: int = 0) -> dict[str, Any]:
        try:
            payload = assets.cleanup(dry_run=dry_run, older_than_seconds=older_than_seconds)
        except MediaAssetError as exc:
            raise ToolError(str(exc)) from exc
        return _with_audit(
            payload,
            "Planned media asset cleanup in dry-run mode; no files were deleted.",
            files_read=[str(assets.media_root)],
        )

    def safety_check(prompt: str, provider_id: str = "mock", commercial_use: bool = False) -> dict[str, Any]:
        payload = check_media_prompt_safety(
            prompt,
            provider_id=provider_id or "mock",
            commercial_use=bool(commercial_use),
        ).to_dict()
        return _with_audit(
            payload,
            f"Ran deterministic media safety check with outcome {payload['outcome']}; no media was generated.",
        )

    def license_report() -> dict[str, Any]:
        payload = build_license_report(registry)
        return _with_audit(
            payload,
            "Read media provider license metadata without legal advice, provider calls, or generation.",
        )

    def consent_policy() -> dict[str, Any]:
        payload = build_consent_policy()
        return _with_audit(
            payload,
            "Read media consent policy without enabling likeness or voice workflows.",
        )

    def comfyui_doctor(check_server: bool = False) -> dict[str, Any]:
        payload = ComfyUIProvider().doctor(check_server=bool(check_server))
        return _with_audit(
            payload,
            "Read ComfyUI provider stub status without workflow submission or media generation.",
        )

    def workflows_list(provider: str = "comfyui") -> dict[str, Any]:
        normalized = (provider or "comfyui").strip().lower()
        if normalized != "comfyui":
            return _with_audit(
                {
                    "status": "unsupported_provider",
                    "provider": normalized,
                    "workflows": [],
                    "workflow_submission_enabled": False,
                    "setup_hint": "MEDIA-04 only defines the ComfyUI workflow metadata stub.",
                },
                f"Rejected workflow list for unsupported media provider {normalized!r}.",
            )
        payload = ComfyUIProvider().list_workflows()
        return _with_audit(
            payload,
            "Listed ComfyUI workflow metadata stub without reading or submitting workflow JSON.",
        )

    def generate_image(prompt: str, dry_run: bool, provider: str = "auto", commercial_use: bool = False) -> dict[str, Any]:
        if not dry_run:
            return _with_audit(
                {
                    "status": "blocked",
                    "generated_media": False,
                    "dry_run": False,
                    "setup_hint": "MEDIA-05 image generation requires --dry-run; real generation is not implemented.",
                },
                "Blocked non-dry-run image generation request.",
            )
        payload = dry_run_generate_image(prompt, provider_id=provider, commercial_use=bool(commercial_use))
        return _with_audit(
            payload,
            f"Built image generation dry-run plan with status {payload['status']}; no image was generated.",
        )

    def image_providers() -> dict[str, Any]:
        providers = list(image_provider_candidates())
        return _with_audit(
            {
                "status": "ok",
                "provider_count": len(providers),
                "providers": providers,
                "real_generation_enabled": False,
                "paid_apis_enabled": False,
                "model_downloads_enabled": False,
            },
            f"Listed {len(providers)} image provider candidates without runtime imports.",
        )

    def image_plan(prompt: str, provider: str = "auto", commercial_use: bool = False) -> dict[str, Any]:
        payload = plan_image_generation(
            prompt,
            provider_id=provider,
            commercial_use=bool(commercial_use),
            dry_run=True,
        ).to_dict()
        return _with_audit(
            payload,
            f"Built image generation plan with status {payload['status']}; no image was generated.",
        )

    def thumbnail(prompt: str, dry_run: bool, commercial_use: bool = False) -> dict[str, Any]:
        if not dry_run:
            return _with_audit(
                {
                    "status": "blocked",
                    "dry_run": False,
                    "real_generation": False,
                    "real_editing": False,
                    "upload_publish_enabled": False,
                    "setup_hint": "MEDIA-06 thumbnail workflows require --dry-run; real editing/generation is not implemented.",
                },
                "Blocked non-dry-run thumbnail workflow request.",
            )
        payload = plan_thumbnail(prompt, commercial_use=bool(commercial_use))
        return _with_audit(
            payload,
            f"Built thumbnail creative workflow dry-run plan with status {payload['status']}; no image was edited or generated.",
        )

    def creative_plan(prompt: str, workflow_type: str = "auto", commercial_use: bool = False) -> dict[str, Any]:
        payload = plan_creative_workflow(
            prompt,
            workflow_type=workflow_type or "auto",
            commercial_use=bool(commercial_use),
        )
        return _with_audit(
            payload,
            f"Built creative workflow dry-run plan for {payload['workflow_type']} with status {payload['status']}.",
        )

    def creative_templates() -> dict[str, Any]:
        payload = list_creative_templates()
        return _with_audit(
            payload,
            f"Listed {payload['workflow_count']} creative workflow templates without media side effects.",
        )

    def generate_video(prompt: str, dry_run: bool, provider: str = "auto", commercial_use: bool = False) -> dict[str, Any]:
        if not dry_run:
            return _with_audit(
                {
                    "status": "blocked",
                    "generated_media": False,
                    "dry_run": False,
                    "setup_hint": "MEDIA-07 video generation requires --dry-run; real generation is not implemented.",
                },
                "Blocked non-dry-run video generation request.",
            )
        payload = dry_run_generate_video(prompt, provider_id=provider, commercial_use=bool(commercial_use))
        return _with_audit(
            payload,
            f"Built video generation dry-run plan with status {payload['status']}; no video was generated.",
        )

    def video_providers() -> dict[str, Any]:
        providers = list(video_provider_candidates())
        return _with_audit(
            {
                "status": "ok",
                "provider_count": len(providers),
                "providers": providers,
                "real_generation_enabled": False,
                "paid_apis_enabled": False,
                "model_downloads_enabled": False,
                "upload_publish_enabled": False,
            },
            f"Listed {len(providers)} video provider candidates without runtime imports.",
        )

    def video_plan(prompt: str, provider: str = "auto", commercial_use: bool = False) -> dict[str, Any]:
        payload = plan_video_generation(
            prompt,
            provider_id=provider,
            commercial_use=bool(commercial_use),
            dry_run=True,
        ).to_dict()
        return _with_audit(
            payload,
            f"Built video generation plan with status {payload['status']}; no video was generated.",
        )

    def generate_audio(prompt: str, dry_run: bool, provider: str = "auto", commercial_use: bool = False) -> dict[str, Any]:
        if not dry_run:
            return _with_audit(
                {
                    "status": "blocked",
                    "generated_media": False,
                    "dry_run": False,
                    "setup_hint": "MEDIA-08 audio generation requires --dry-run; real generation is not implemented.",
                },
                "Blocked non-dry-run audio generation request.",
            )
        payload = dry_run_generate_audio(prompt, provider_id=provider, commercial_use=bool(commercial_use))
        return _with_audit(
            payload,
            f"Built audio generation dry-run plan with status {payload['status']}; no audio was generated.",
        )

    def generate_music(prompt: str, dry_run: bool, provider: str = "auto", commercial_use: bool = False) -> dict[str, Any]:
        if not dry_run:
            return _with_audit(
                {
                    "status": "blocked",
                    "generated_media": False,
                    "dry_run": False,
                    "setup_hint": "MEDIA-08 music generation requires --dry-run; real generation is not implemented.",
                },
                "Blocked non-dry-run music generation request.",
            )
        payload = dry_run_generate_music(prompt, provider_id=provider, commercial_use=bool(commercial_use))
        return _with_audit(
            payload,
            f"Built music generation dry-run plan with status {payload['status']}; no music was generated.",
        )

    def audio_providers() -> dict[str, Any]:
        providers = list(audio_provider_candidates())
        return _with_audit(
            {
                "status": "ok",
                "provider_count": len(providers),
                "providers": providers,
                "real_generation_enabled": False,
                "paid_apis_enabled": False,
                "model_downloads_enabled": False,
                "voice_cloning_enabled": False,
                "upload_publish_enabled": False,
            },
            f"Listed {len(providers)} audio/music provider candidates without runtime imports.",
        )

    def music_plan(prompt: str, provider: str = "auto", commercial_use: bool = False) -> dict[str, Any]:
        payload = plan_audio_generation(
            prompt,
            mode="music",
            provider_id=provider,
            commercial_use=bool(commercial_use),
            dry_run=True,
        ).to_dict()
        return _with_audit(
            payload,
            f"Built music generation plan with status {payload['status']}; no music was generated.",
        )

    def tts_plan(text: str, voice_category: str = "generic_tts") -> dict[str, Any]:
        payload = plan_tts(text, voice_category=voice_category)
        return _with_audit(
            payload,
            f"Built TTS/voice plan with status {payload['status']}; no voice audio was generated.",
        )

    def voice_policy() -> dict[str, Any]:
        payload = voice_consent_policy()
        return _with_audit(
            payload,
            "Read voice consent policy without enabling voice cloning or generation.",
        )

    def voice_providers() -> dict[str, Any]:
        payload = list_voice_providers()
        return _with_audit(
            payload,
            f"Listed {payload['provider_count']} TTS/voice provider candidates without runtime imports.",
        )

    return {
        "media.providers": providers,
        "media.doctor": doctor,
        "media.plan": media_plan,
        "media.assets.list": assets_list,
        "media.assets.show": assets_show,
        "media.assets.cleanup": assets_cleanup,
        "media.safety_check": safety_check,
        "media.license.report": license_report,
        "media.consent.policy": consent_policy,
        "media.comfyui.doctor": comfyui_doctor,
        "media.workflows.list": workflows_list,
        "media.generate.image": generate_image,
        "media.image.providers": image_providers,
        "media.image.plan": image_plan,
        "media.thumbnail": thumbnail,
        "media.creative.plan": creative_plan,
        "media.creative.templates": creative_templates,
        "media.generate.video": generate_video,
        "media.video.providers": video_providers,
        "media.video.plan": video_plan,
        "media.generate.audio": generate_audio,
        "media.generate.music": generate_music,
        "media.audio.providers": audio_providers,
        "media.music.plan": music_plan,
        "media.tts.plan": tts_plan,
        "media.voice.consent_policy": voice_policy,
        "media.voice.providers": voice_providers,
    }
