from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from agent.media.licenses import build_license_report
from agent.media.models import MediaAssetType, MediaGenerationRequest, MediaPrompt
from agent.media.providers.mock_audio import MockAudioProvider
from agent.media.safety import MediaSafetyOutcome, check_media_prompt_safety


AUDIO_PROVIDER_CANDIDATES: tuple[dict[str, Any], ...] = (
    {
        "provider_id": "mock_audio",
        "name": "Mock audio provider",
        "status": "stubbed",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "Test-only provider for fake audio metadata/results; no real audio is generated.",
        "license_notes": ["Mock provider grants no production usage rights."],
    },
    {
        "provider_id": "audiocraft_musicgen",
        "name": "AudioCraft / MusicGen / AudioGen",
        "status": "planned",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "Model/runtime/license review is future work; no models are downloaded.",
        "license_notes": ["Commercial use and training-data caveats require provider/model review."],
    },
    {
        "provider_id": "stable_audio_open",
        "name": "Stable Audio Open",
        "status": "planned",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "License/model/runtime review is future work.",
        "license_notes": ["Review model license and output usage terms before production use."],
    },
    {
        "provider_id": "stable_audio_open_small",
        "name": "Stable Audio Open Small",
        "status": "planned",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "License/model/runtime review is future work.",
        "license_notes": ["Small model does not remove license/commercial review requirements."],
    },
    {
        "provider_id": "ace_step",
        "name": "ACE-Step",
        "status": "planned",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "Provider/model review is future work.",
        "license_notes": ["Music generation has additional copyright/style imitation risk."],
    },
    {
        "provider_id": "comfyui_audio",
        "name": "ComfyUI audio workflows",
        "status": "stubbed",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "ComfyUI workflow submission remains disabled; audio workflows are metadata-only.",
        "license_notes": ["Workflow and model licenses must be reviewed before use."],
    },
    {
        "provider_id": "tts_future",
        "name": "TTS providers",
        "status": "future",
        "default_enabled": False,
        "real_generation": False,
        "setup_hint": "TTS is future-only in MEDIA-08; voice cloning remains denied/deferred.",
        "license_notes": ["Voice/likeness consent policy is required before TTS-like personal voice workflows."],
    },
)

ARTIST_IMITATION_MARKERS = (
    "in the style of",
    "sounds like",
    "sound like",
    "copy the song",
    "copy this song",
    "like taylor swift",
    "like drake",
    "like the beatles",
    "like beyonce",
)


@dataclass(frozen=True)
class AudioGenerationPlan:
    status: str
    request: MediaGenerationRequest
    provider_id: str
    mode: str
    safety: dict[str, Any]
    license_report: dict[str, Any]
    music_rights_warning: dict[str, Any]
    setup_hint: str
    dry_run: bool = True
    real_generation: bool = False
    upload_publish_enabled: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "request": self.request.to_safe_dict(),
            "provider_id": self.provider_id,
            "mode": self.mode,
            "safety": self.safety,
            "license_report": self.license_report,
            "music_rights_warning": self.music_rights_warning,
            "setup_hint": self.setup_hint,
            "dry_run": self.dry_run,
            "real_generation": self.real_generation,
            "upload_publish_enabled": self.upload_publish_enabled,
        }


def audio_provider_candidates() -> tuple[dict[str, Any], ...]:
    return AUDIO_PROVIDER_CANDIDATES


def plan_audio_generation(
    prompt: str,
    *,
    mode: str = "audio",
    provider_id: str = "auto",
    commercial_use: bool = False,
    dry_run: bool = True,
) -> AudioGenerationPlan:
    normalized_mode = "music" if (mode or "audio").strip().lower() == "music" else "audio"
    selected_provider = _select_provider(provider_id)
    asset_type = MediaAssetType.MUSIC if normalized_mode == "music" else MediaAssetType.AUDIO
    request = MediaGenerationRequest(
        request_id=f"{normalized_mode}_plan_{uuid.uuid4().hex[:12]}",
        provider=selected_provider,
        asset_type=asset_type,
        prompt=MediaPrompt(prompt),
        parameters={"mode": normalized_mode, "dry_run_audio_plan": True},
        dry_run=True,
    )
    safety = check_media_prompt_safety(
        prompt,
        provider_id="mock" if selected_provider == "mock_audio" else selected_provider,
        commercial_use=bool(commercial_use or normalized_mode == "music"),
    ).to_dict()
    music_warning = _music_rights_warning(prompt, mode=normalized_mode, commercial_use=commercial_use)
    if safety["outcome"] == MediaSafetyOutcome.DENY.value or music_warning["voice_clone_denied"]:
        return AudioGenerationPlan(
            status="blocked",
            request=request,
            provider_id=selected_provider,
            mode=normalized_mode,
            safety=safety,
            license_report=build_license_report(),
            music_rights_warning=music_warning,
            setup_hint="Audio/music safety preflight denied this request.",
        )
    if not dry_run:
        return AudioGenerationPlan(
            status="blocked",
            request=request,
            provider_id=selected_provider,
            mode=normalized_mode,
            safety=safety,
            license_report=build_license_report(),
            music_rights_warning=music_warning,
            setup_hint="MEDIA-08 supports dry-run audio/music plans only. Re-run with --dry-run.",
            dry_run=False,
        )
    provider = _candidate(selected_provider)
    if provider is None or selected_provider != "mock_audio":
        return AudioGenerationPlan(
            status="requires_setup",
            request=request,
            provider_id=selected_provider,
            mode=normalized_mode,
            safety=safety,
            license_report=build_license_report(),
            music_rights_warning=music_warning,
            setup_hint=(provider or {}).get("setup_hint", "No audio/music provider is configured for real generation."),
        )
    plan_status = "requires_license_review" if music_warning["artist_imitation_flagged"] else "dry_run"
    return AudioGenerationPlan(
        status=plan_status,
        request=request,
        provider_id=selected_provider,
        mode=normalized_mode,
        safety=safety,
        license_report=build_license_report(),
        music_rights_warning=music_warning,
        setup_hint="Mock audio dry-run plan only; no real audio or music is generated.",
    )


def dry_run_generate_audio(prompt: str, *, provider_id: str = "auto", commercial_use: bool = False) -> dict[str, Any]:
    return _dry_run_generate(prompt, mode="audio", provider_id=provider_id, commercial_use=commercial_use)


def dry_run_generate_music(prompt: str, *, provider_id: str = "auto", commercial_use: bool = False) -> dict[str, Any]:
    return _dry_run_generate(prompt, mode="music", provider_id=provider_id, commercial_use=commercial_use)


def _dry_run_generate(prompt: str, *, mode: str, provider_id: str, commercial_use: bool) -> dict[str, Any]:
    plan = plan_audio_generation(prompt, mode=mode, provider_id=provider_id, commercial_use=commercial_use, dry_run=True)
    if plan.provider_id == "mock_audio" and plan.status in {"dry_run", "requires_license_review"}:
        mock_plan = MockAudioProvider().plan(plan.request)
    else:
        mock_plan = None
    payload = plan.to_dict()
    payload["mock_provider_plan"] = mock_plan
    payload["generated_media"] = False
    return payload


def _select_provider(provider_id: str) -> str:
    normalized = (provider_id or "auto").strip().lower()
    if normalized in {"auto", "mock"}:
        return "mock_audio"
    return normalized


def _candidate(provider_id: str) -> dict[str, Any] | None:
    for candidate in AUDIO_PROVIDER_CANDIDATES:
        if candidate["provider_id"] == provider_id:
            return candidate
    return None


def _music_rights_warning(prompt: str, *, mode: str, commercial_use: bool) -> dict[str, Any]:
    lowered = prompt.lower()
    artist_flagged = any(marker in lowered for marker in ARTIST_IMITATION_MARKERS)
    voice_clone_denied = any(marker in lowered for marker in ("clone voice", "voice clone", "sound exactly like my", "imitate the voice"))
    review_required = bool(mode == "music" or commercial_use or artist_flagged)
    return {
        "review_required": review_required,
        "artist_imitation_flagged": artist_flagged,
        "voice_clone_denied": voice_clone_denied,
        "commercial_use_requires_evidence": True,
        "copyrighted_song_or_artist_imitation_for_commercial_output_allowed": False,
        "legal_advice": False,
        "notes": [
            "Do not claim commercial rights without provider/model/license evidence.",
            "Do not imitate living artists, copyrighted tracks, or recognizable recordings as commercial output.",
            "Voice cloning remains denied/deferred until a future consent workflow exists.",
        ],
    }
