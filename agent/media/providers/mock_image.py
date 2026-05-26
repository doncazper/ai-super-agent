from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent.media.asset_manager import MediaAssetManager
from agent.media.models import MediaAssetType, MediaGenerationRequest, MediaGenerationResult, MediaPrompt, MediaSafetyReview


@dataclass(frozen=True)
class MockImageProvider:
    provider_id: str = "mock_image"
    name: str = "Mock image provider"

    def plan(self, request: MediaGenerationRequest) -> dict[str, Any]:
        safe = request.prompt.to_safe_dict()
        return {
            "status": "dry_run",
            "provider": self.provider_id,
            "request": request.to_safe_dict(),
            "prompt_hash": safe["prompt_hash"],
            "prompt_redacted": safe["prompt_redacted"],
            "real_generation": False,
            "setup_hint": "Mock image provider is for tests only and creates no real image.",
        }

    def create_fake_result(
        self,
        *,
        request: MediaGenerationRequest,
        asset_manager: MediaAssetManager,
        relative_path: str = "mock_images/mock-image.txt",
    ) -> MediaGenerationResult:
        asset = asset_manager.create_fake_asset(
            relative_path=relative_path,
            content=b"fake image metadata fixture; not an image",
            prompt=request.prompt,
            provider=self.provider_id,
            asset_type=MediaAssetType.IMAGE,
            metadata={
                "mock": True,
                "real_generation": False,
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
                warnings=("Mock output only; no real image was generated.",),
                reviewer="mock_image_provider",
            ),
            warnings=("Fake asset metadata only; no image generation occurred.",),
        )


def mock_image_request(prompt: str, *, request_id: str = "mock_image_request") -> MediaGenerationRequest:
    return MediaGenerationRequest(
        request_id=request_id,
        provider="mock_image",
        asset_type=MediaAssetType.IMAGE,
        prompt=MediaPrompt(prompt),
        dry_run=True,
    )
