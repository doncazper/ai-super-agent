from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent.media.asset_manager import MediaAssetManager
from agent.media.models import MediaAssetType, MediaGenerationRequest, MediaGenerationResult, MediaPrompt, MediaSafetyReview


@dataclass(frozen=True)
class MockAudioProvider:
    provider_id: str = "mock_audio"
    name: str = "Mock audio provider"

    def plan(self, request: MediaGenerationRequest) -> dict[str, Any]:
        safe = request.prompt.to_safe_dict()
        return {
            "status": "dry_run",
            "provider": self.provider_id,
            "request": request.to_safe_dict(),
            "prompt_hash": safe["prompt_hash"],
            "prompt_redacted": safe["prompt_redacted"],
            "real_generation": False,
            "upload_publish_enabled": False,
            "setup_hint": "Mock audio provider is for tests only and creates no real audio.",
        }

    def create_fake_result(
        self,
        *,
        request: MediaGenerationRequest,
        asset_manager: MediaAssetManager,
        relative_path: str = "mock_audio/mock-audio.txt",
    ) -> MediaGenerationResult:
        asset = asset_manager.create_fake_asset(
            relative_path=relative_path,
            content=b"fake audio metadata fixture; not audio",
            prompt=request.prompt,
            provider=self.provider_id,
            asset_type=request.asset_type,
            metadata={
                "mock": True,
                "real_generation": False,
                "upload_publish_enabled": False,
                "request_id": request.request_id,
            },
        )
        return MediaGenerationResult(
            status="mock_created",
            request_id=request.request_id,
            provider=self.provider_id,
            assets=(asset,),
            safety_review=MediaSafetyReview(
                status="allow",
                blocked=False,
                warnings=("Mock output only; no real audio was generated.",),
                reviewer="mock_audio_provider",
            ),
            warnings=("Fake asset metadata only; no audio or music generation occurred.",),
        )


def mock_audio_request(prompt: str, *, mode: str = "audio", request_id: str = "mock_audio_request") -> MediaGenerationRequest:
    asset_type = MediaAssetType.MUSIC if mode == "music" else MediaAssetType.AUDIO
    return MediaGenerationRequest(
        request_id=request_id,
        provider="mock_audio",
        asset_type=asset_type,
        prompt=MediaPrompt(prompt),
        parameters={"mode": mode},
        dry_run=True,
    )
