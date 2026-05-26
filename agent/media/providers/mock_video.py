from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent.media.asset_manager import MediaAssetManager
from agent.media.models import MediaAssetType, MediaGenerationRequest, MediaGenerationResult, MediaPrompt, MediaSafetyReview


@dataclass(frozen=True)
class MockVideoProvider:
    provider_id: str = "mock_video"
    name: str = "Mock video provider"

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
            "setup_hint": "Mock video provider is for tests only and creates no real video.",
        }

    def create_fake_result(
        self,
        *,
        request: MediaGenerationRequest,
        asset_manager: MediaAssetManager,
        relative_path: str = "mock_videos/mock-video.txt",
    ) -> MediaGenerationResult:
        asset = asset_manager.create_fake_asset(
            relative_path=relative_path,
            content=b"fake video metadata fixture; not a video",
            prompt=request.prompt,
            provider=self.provider_id,
            asset_type=MediaAssetType.VIDEO,
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
                warnings=("Mock output only; no real video was generated.",),
                reviewer="mock_video_provider",
            ),
            warnings=("Fake asset metadata only; no video generation occurred.",),
        )


def mock_video_request(prompt: str, *, request_id: str = "mock_video_request") -> MediaGenerationRequest:
    return MediaGenerationRequest(
        request_id=request_id,
        provider="mock_video",
        asset_type=MediaAssetType.VIDEO,
        prompt=MediaPrompt(prompt),
        dry_run=True,
    )
