from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from agent.media.models import MediaPrompt
from agent.media.safety import check_media_prompt_safety


class VoiceCategory(StrEnum):
    GENERIC_TTS = "generic_tts"
    CHARACTER_VOICE = "character_voice"
    USER_OWNED_VOICE_WITH_CONSENT = "user_owned_voice_with_consent"
    PUBLIC_FIGURE_VOICE = "public_figure_voice"
    PRIVATE_PERSON_VOICE = "private_person_voice"
    VOICE_CLONE = "voice_clone"
    IMPERSONATION = "impersonation"


@dataclass(frozen=True)
class TTSProviderCandidate:
    provider_id: str
    name: str
    status: str
    default_enabled: bool
    real_generation: bool
    supports_voice_cloning: bool
    setup_hint: str
    docs_path: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "name": self.name,
            "status": self.status,
            "default_enabled": self.default_enabled,
            "real_generation": self.real_generation,
            "supports_voice_cloning": self.supports_voice_cloning,
            "setup_hint": self.setup_hint,
            "docs_path": self.docs_path,
        }


TTS_PROVIDER_CANDIDATES: tuple[TTSProviderCandidate, ...] = (
    TTSProviderCandidate(
        provider_id="generic_tts_future",
        name="Generic TTS provider",
        status="future",
        default_enabled=False,
        real_generation=False,
        supports_voice_cloning=False,
        setup_hint="Future generic TTS provider only; no audio generation exists in MEDIA-09.",
        docs_path="docs/media/TTS_VOICE_GENERATION_STRATEGY.md",
    ),
    TTSProviderCandidate(
        provider_id="local_tts_future",
        name="Local TTS runtime",
        status="planned",
        default_enabled=False,
        real_generation=False,
        supports_voice_cloning=False,
        setup_hint="Local runtime/model review is future work; no models are installed or downloaded.",
        docs_path="docs/media/TTS_VOICE_GENERATION_STRATEGY.md",
    ),
    TTSProviderCandidate(
        provider_id="voice_clone_future",
        name="Voice cloning provider",
        status="blocked",
        default_enabled=False,
        real_generation=False,
        supports_voice_cloning=False,
        setup_hint="Voice cloning is denied/deferred until an explicit consent system exists.",
        docs_path="docs/media/VOICE_CONSENT_POLICY.md",
    ),
)


def list_voice_providers() -> dict[str, Any]:
    return {
        "status": "ok",
        "provider_count": len(TTS_PROVIDER_CANDIDATES),
        "providers": [provider.to_dict() for provider in TTS_PROVIDER_CANDIDATES],
        "real_generation_enabled": False,
        "voice_cloning_enabled": False,
        "upload_publish_enabled": False,
    }


def voice_consent_policy() -> dict[str, Any]:
    return {
        "status": "ok",
        "consent_system_implemented": False,
        "generic_tts_future_risk": "MEDIUM",
        "voice_cloning_risk": "CRITICAL_OR_FORBIDDEN_UNTIL_CONSENT_SYSTEM",
        "watermark_or_provenance_required_for_future_outputs": True,
        "rules": [
            "Generic TTS may be future MEDIUM risk after provider review and release gate.",
            "Voice cloning is denied/deferred until an explicit consent system exists.",
            "Public-figure and private-person voice imitation is denied/deferred.",
            "User-owned voice cloning requires recorded consent evidence before any future generation.",
            "Future voice outputs require watermark/provenance strategy.",
            "MEDIA-09 performs no real voice generation.",
        ],
    }


def plan_tts(text: str, *, voice_category: str = "generic_tts") -> dict[str, Any]:
    category = _normalize_category(voice_category, text)
    safety = check_media_prompt_safety(text, provider_id="mock", commercial_use=False).to_dict()
    decision = _decision_for(category)
    return {
        "status": decision["status"],
        "request_id": f"tts_plan_{uuid.uuid4().hex[:12]}",
        "voice_category": category.value,
        "text": MediaPrompt(text).to_safe_dict(),
        "safety": safety,
        "risk_level": decision["risk_level"],
        "approval_required_future": decision["approval_required_future"],
        "consent_required": decision["consent_required"],
        "watermark_or_provenance_required": True,
        "real_generation": False,
        "voice_cloning_enabled": False,
        "upload_publish_enabled": False,
        "setup_hint": decision["setup_hint"],
    }


def _normalize_category(category: str, text: str) -> VoiceCategory:
    normalized = (category or "generic_tts").strip().lower().replace("-", "_")
    lowered = text.lower()
    if "public figure" in lowered or any(name in lowered for name in ("taylor swift", "donald trump", "joe biden", "beyonce")):
        return VoiceCategory.PUBLIC_FIGURE_VOICE
    if any(marker in lowered for marker in ("my boss", "my coworker", "my neighbor", "private person")):
        return VoiceCategory.PRIVATE_PERSON_VOICE
    if any(marker in lowered for marker in ("clone voice", "voice clone", "sound exactly like", "imitate the voice")):
        return VoiceCategory.VOICE_CLONE
    if any(marker in lowered for marker in ("impersonate", "fake endorsement", "make it sound like they said")):
        return VoiceCategory.IMPERSONATION
    try:
        return VoiceCategory(normalized)
    except ValueError:
        return VoiceCategory.GENERIC_TTS


def _decision_for(category: VoiceCategory) -> dict[str, Any]:
    if category is VoiceCategory.GENERIC_TTS:
        return {
            "status": "stubbed_allowed",
            "risk_level": "MEDIUM_FUTURE",
            "approval_required_future": True,
            "consent_required": False,
            "setup_hint": "Generic TTS is planned only; no voice audio is generated in MEDIA-09.",
        }
    if category is VoiceCategory.CHARACTER_VOICE:
        return {
            "status": "requires_review",
            "risk_level": "HIGH_FUTURE",
            "approval_required_future": True,
            "consent_required": False,
            "setup_hint": "Character voice workflows need license and impersonation review before future implementation.",
        }
    if category is VoiceCategory.USER_OWNED_VOICE_WITH_CONSENT:
        return {
            "status": "requires_consent_system",
            "risk_level": "CRITICAL_FUTURE",
            "approval_required_future": True,
            "consent_required": True,
            "setup_hint": "User-owned voice cloning requires a consent record system before any future generation.",
        }
    return {
        "status": "denied_deferred",
        "risk_level": "CRITICAL_OR_FORBIDDEN",
        "approval_required_future": True,
        "consent_required": True,
        "setup_hint": "Public/private person voice imitation, voice cloning, and impersonation are denied/deferred.",
    }
