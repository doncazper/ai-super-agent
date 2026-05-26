from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from agent.media.redaction import prompt_hash, redact_media_prompt


class MediaProviderStatus(StrEnum):
    AVAILABLE = "available"
    CONFIGURED = "configured"
    DISABLED = "disabled"
    PLANNED = "planned"
    STUBBED = "stubbed"
    BLOCKED = "blocked"
    UNSUPPORTED = "unsupported"
    REQUIRES_SETUP = "requires_setup"


class MediaProviderCapability(StrEnum):
    STATUS = "status"
    IMAGE_GENERATION = "image_generation"
    IMAGE_EDITING = "image_editing"
    THUMBNAIL = "thumbnail"
    VIDEO_GENERATION = "video_generation"
    AUDIO_GENERATION = "audio_generation"
    MUSIC_GENERATION = "music_generation"
    TTS = "tts"
    SAFETY_CHECK = "safety_check"
    LICENSE_REPORT = "license_report"


class MediaAssetType(StrEnum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    MUSIC = "music"
    TEXT = "text"
    METADATA = "metadata"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class MediaProvider:
    provider_id: str
    name: str
    status: MediaProviderStatus
    capabilities: tuple[MediaProviderCapability, ...]
    default_enabled: bool
    local_only: bool
    paid_api: bool
    requires_model_download: bool
    setup_hint: str
    docs_path: str
    risk_level: str = "MEDIUM"
    trust_level: str = "MODEL_OUTPUT"
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "name": self.name,
            "status": self.status.value,
            "capabilities": [capability.value for capability in self.capabilities],
            "default_enabled": self.default_enabled,
            "local_only": self.local_only,
            "paid_api": self.paid_api,
            "requires_model_download": self.requires_model_download,
            "setup_hint": self.setup_hint,
            "docs_path": self.docs_path,
            "risk_level": self.risk_level,
            "trust_level": self.trust_level,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class MediaPrompt:
    text: str
    source: str = "trusted_user"
    source_ids: tuple[str, ...] = ()

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "prompt_hash": prompt_hash(self.text),
            "prompt_redacted": redact_media_prompt(self.text),
            "source": self.source,
            "source_ids": list(self.source_ids),
        }


@dataclass(frozen=True)
class MediaSafetyReview:
    status: str
    blocked: bool
    reasons: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    reviewer: str = "policy_scaffold"

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "blocked": self.blocked,
            "reasons": list(self.reasons),
            "warnings": list(self.warnings),
            "reviewer": self.reviewer,
        }


@dataclass(frozen=True)
class MediaLicenseInfo:
    status: str
    license_name: str = "unknown"
    usage: str = "not reviewed"
    attribution_required: bool = False
    source: str = "provider metadata unavailable"
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "license_name": self.license_name,
            "usage": self.usage,
            "attribution_required": self.attribution_required,
            "source": self.source,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class MediaGenerationRequest:
    request_id: str
    provider: str
    asset_type: MediaAssetType
    prompt: MediaPrompt
    parameters: dict[str, Any] = field(default_factory=dict)
    source_inputs: tuple[dict[str, Any], ...] = ()
    dry_run: bool = True

    def to_safe_dict(self) -> dict[str, Any]:
        prompt = self.prompt.to_safe_dict()
        return {
            "request_id": self.request_id,
            "provider": self.provider,
            "asset_type": self.asset_type.value,
            "prompt_hash": prompt["prompt_hash"],
            "prompt_redacted": prompt["prompt_redacted"],
            "parameters": dict(self.parameters),
            "source_inputs": list(self.source_inputs),
            "dry_run": self.dry_run,
        }


@dataclass(frozen=True)
class MediaAsset:
    asset_id: str
    asset_type: MediaAssetType
    path: str
    created_at: str
    provider: str
    prompt_hash: str
    prompt_redacted: str
    source_inputs: tuple[dict[str, Any], ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    license_info: MediaLicenseInfo = field(default_factory=lambda: MediaLicenseInfo(status="unknown"))
    safety_status: str = "not_reviewed"
    audit_ids: tuple[str, ...] = ()
    retention_status: str = "ttl_pending"

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "asset_type": self.asset_type.value,
            "path": self.path,
            "created_at": self.created_at,
            "provider": self.provider,
            "prompt_hash": self.prompt_hash,
            "prompt_redacted": self.prompt_redacted,
            "source_inputs": list(self.source_inputs),
            "metadata": dict(self.metadata),
            "license_info": self.license_info.to_dict(),
            "safety_status": self.safety_status,
            "audit_ids": list(self.audit_ids),
            "retention_status": self.retention_status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MediaAsset":
        license_data = data.get("license_info") if isinstance(data.get("license_info"), dict) else {}
        return cls(
            asset_id=str(data["asset_id"]),
            asset_type=MediaAssetType(str(data.get("asset_type", MediaAssetType.UNKNOWN.value))),
            path=str(data["path"]),
            created_at=str(data["created_at"]),
            provider=str(data["provider"]),
            prompt_hash=str(data["prompt_hash"]),
            prompt_redacted=str(data["prompt_redacted"]),
            source_inputs=tuple(item for item in data.get("source_inputs", []) if isinstance(item, dict)),
            metadata=dict(data.get("metadata", {})) if isinstance(data.get("metadata"), dict) else {},
            license_info=MediaLicenseInfo(
                status=str(license_data.get("status", "unknown")),
                license_name=str(license_data.get("license_name", "unknown")),
                usage=str(license_data.get("usage", "not reviewed")),
                attribution_required=bool(license_data.get("attribution_required", False)),
                source=str(license_data.get("source", "provider metadata unavailable")),
                notes=tuple(str(note) for note in license_data.get("notes", [])),
            ),
            safety_status=str(data.get("safety_status", "not_reviewed")),
            audit_ids=tuple(str(audit_id) for audit_id in data.get("audit_ids", [])),
            retention_status=str(data.get("retention_status", "ttl_pending")),
        )


@dataclass(frozen=True)
class MediaGenerationResult:
    status: str
    request_id: str
    provider: str
    assets: tuple[MediaAsset, ...] = ()
    safety_review: MediaSafetyReview | None = None
    warnings: tuple[str, ...] = ()
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "request_id": self.request_id,
            "provider": self.provider,
            "assets": [asset.to_dict() for asset in self.assets],
            "safety_review": self.safety_review.to_dict() if self.safety_review else None,
            "warnings": list(self.warnings),
            "error": self.error,
        }
