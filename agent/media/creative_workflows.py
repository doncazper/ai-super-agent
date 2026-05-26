from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from agent.media.asset_manager import MediaAssetManager
from agent.media.licenses import build_license_report
from agent.media.models import MediaAsset, MediaAssetType, MediaPrompt
from agent.media.safety import MediaSafetyOutcome, check_media_prompt_safety


@dataclass(frozen=True)
class CreativeWorkflowTemplate:
    workflow_type: str
    name: str
    description: str
    aspect_ratio: str
    output_size: str
    prompt_template: str
    use_cases: tuple[str, ...]
    risk_notes: tuple[str, ...] = ()
    commercial_review_recommended: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_type": self.workflow_type,
            "name": self.name,
            "description": self.description,
            "aspect_ratio": self.aspect_ratio,
            "output_size": self.output_size,
            "prompt_template": self.prompt_template,
            "use_cases": list(self.use_cases),
            "risk_notes": list(self.risk_notes),
            "commercial_review_recommended": self.commercial_review_recommended,
        }


CREATIVE_WORKFLOW_TEMPLATES: tuple[CreativeWorkflowTemplate, ...] = (
    CreativeWorkflowTemplate(
        workflow_type="youtube_thumbnail",
        name="YouTube thumbnail",
        description="High-contrast thumbnail concept with title hierarchy and focal subject placeholder.",
        aspect_ratio="16:9",
        output_size="1280x720",
        prompt_template="Create a thumbnail plan for: {prompt}. Include focal subject, title text, contrast, and safe negative space.",
        use_cases=("youtube", "video", "creator"),
        risk_notes=("Do not use real-person likeness edits without future consent policy.", "Do not upload/publish from this workflow."),
        commercial_review_recommended=True,
    ),
    CreativeWorkflowTemplate(
        workflow_type="short_form_video_cover",
        name="Short-form video cover",
        description="Vertical cover layout for Reels, Shorts, TikTok-style clips, or story previews.",
        aspect_ratio="9:16",
        output_size="1080x1920",
        prompt_template="Create a vertical cover plan for: {prompt}. Include headline, subject framing, and mobile-safe margins.",
        use_cases=("shorts", "reels", "stories"),
        risk_notes=("No platform upload/posting is implemented.",),
        commercial_review_recommended=True,
    ),
    CreativeWorkflowTemplate(
        workflow_type="podcast_cover",
        name="Podcast cover",
        description="Square podcast cover concept with title, host/show metadata, and thumbnail legibility.",
        aspect_ratio="1:1",
        output_size="3000x3000",
        prompt_template="Create a podcast cover plan for: {prompt}. Include typography, cover hierarchy, and small-size legibility notes.",
        use_cases=("podcast", "cover art"),
        risk_notes=("Commercial/license review is required before production asset use.",),
        commercial_review_recommended=True,
    ),
    CreativeWorkflowTemplate(
        workflow_type="real_estate_listing_graphic",
        name="Real estate listing graphic",
        description="Listing card concept with property-photo placeholder, price/info blocks, and compliance caveats.",
        aspect_ratio="4:5",
        output_size="1080x1350",
        prompt_template="Create a real-estate listing graphic plan for: {prompt}. Include photo placeholder, key facts, and disclaimer area.",
        use_cases=("real estate", "listing", "marketing"),
        risk_notes=("Do not alter real property photos deceptively.", "Verify claims and required disclosures before publication."),
        commercial_review_recommended=True,
    ),
    CreativeWorkflowTemplate(
        workflow_type="food_review_thumbnail",
        name="Food review thumbnail",
        description="Food review card concept with dish/photo placeholder, rating/title treatment, and color direction.",
        aspect_ratio="16:9",
        output_size="1280x720",
        prompt_template="Create a food review thumbnail plan for: {prompt}. Include dish focus, rating/title area, and appetizing color notes.",
        use_cases=("food", "review", "video"),
        risk_notes=("Do not misrepresent restaurants, menus, or ratings.",),
    ),
    CreativeWorkflowTemplate(
        workflow_type="family_vlog_title_card",
        name="Family vlog title card",
        description="Warm title-card concept with generic family/travel/lifestyle placeholders.",
        aspect_ratio="16:9",
        output_size="1920x1080",
        prompt_template="Create a family vlog title-card plan for: {prompt}. Use generic placeholders and avoid identifying real people.",
        use_cases=("vlog", "title card"),
        risk_notes=("Do not use child likeness or private family photos without a future consent workflow.",),
    ),
    CreativeWorkflowTemplate(
        workflow_type="social_post_image",
        name="Social post image",
        description="Feed-post concept with headline, visual motif, and platform-neutral layout notes.",
        aspect_ratio="4:5",
        output_size="1080x1350",
        prompt_template="Create a social post image plan for: {prompt}. Include headline, visual motif, CTA placeholder, and crop safety.",
        use_cases=("social", "feed", "announcement"),
        risk_notes=("No upload, scheduling, or posting is implemented.",),
        commercial_review_recommended=True,
    ),
    CreativeWorkflowTemplate(
        workflow_type="ad_creative",
        name="Ad creative",
        description="Ad concept plan with CTA, value proposition, brand-safe placeholder, and compliance notes.",
        aspect_ratio="1:1",
        output_size="1080x1080",
        prompt_template="Create an ad creative plan for: {prompt}. Include value prop, CTA, brand-safe visual direction, and review caveats.",
        use_cases=("ad", "campaign", "marketing"),
        risk_notes=("Claims, pricing, endorsements, and brand assets require review before use.",),
        commercial_review_recommended=True,
    ),
    CreativeWorkflowTemplate(
        workflow_type="before_after_layout",
        name="Before/after layout",
        description="Comparison layout concept with clear labels and anti-deception caveats.",
        aspect_ratio="16:9",
        output_size="1920x1080",
        prompt_template="Create a before/after layout plan for: {prompt}. Include labels, comparison structure, and anti-deception notes.",
        use_cases=("comparison", "case study"),
        risk_notes=("Do not create deceptive transformations or unsupported claims.",),
        commercial_review_recommended=True,
    ),
    CreativeWorkflowTemplate(
        workflow_type="product_mockup",
        name="Product mockup",
        description="Product presentation concept with neutral background, callouts, and review placeholders.",
        aspect_ratio="1:1",
        output_size="1600x1600",
        prompt_template="Create a product mockup plan for: {prompt}. Include composition, callouts, and license/review notes.",
        use_cases=("product", "mockup", "commerce"),
        risk_notes=("Do not claim product features, endorsements, or brand rights without evidence.",),
        commercial_review_recommended=True,
    ),
)


def list_creative_templates() -> dict[str, Any]:
    templates = [template.to_dict() for template in CREATIVE_WORKFLOW_TEMPLATES]
    return {
        "status": "ok",
        "workflow_count": len(templates),
        "templates": templates,
        "real_editing_enabled": False,
        "real_generation_enabled": False,
        "upload_publish_enabled": False,
        "personal_image_inputs_enabled": False,
    }


def plan_creative_workflow(
    prompt: str,
    *,
    workflow_type: str = "auto",
    commercial_use: bool = False,
) -> dict[str, Any]:
    template = get_creative_template(workflow_type if workflow_type != "auto" else infer_workflow_type(prompt))
    effective_commercial = bool(commercial_use or template.commercial_review_recommended)
    safety = check_media_prompt_safety(
        prompt,
        provider_id="mock",
        commercial_use=effective_commercial,
    ).to_dict()
    license_report = build_license_report()
    request_id = f"creative_plan_{uuid.uuid4().hex[:12]}"
    status = "blocked" if safety["outcome"] == MediaSafetyOutcome.DENY.value else "dry_run"
    caution = _license_caution(safety=safety, template=template, commercial_use=effective_commercial)
    return {
        "status": status,
        "request_id": request_id,
        "workflow_type": template.workflow_type,
        "workflow": template.to_dict(),
        "prompt": MediaPrompt(prompt).to_safe_dict(),
        "safety": safety,
        "license_report": license_report,
        "commercial_use": effective_commercial,
        "license_caution": caution,
        "suggested_output": {
            "aspect_ratio": template.aspect_ratio,
            "output_size": template.output_size,
            "asset_type": MediaAssetType.IMAGE.value,
        },
        "plan_steps": _plan_steps(template),
        "dry_run": True,
        "real_editing": False,
        "real_generation": False,
        "upload_publish_enabled": False,
        "asset_write_performed": False,
        "setup_hint": "Dry-run creative workflow plan only; no image was edited, generated, uploaded, or published.",
    }


def plan_thumbnail(prompt: str, *, commercial_use: bool = False) -> dict[str, Any]:
    return plan_creative_workflow(
        prompt,
        workflow_type="youtube_thumbnail",
        commercial_use=commercial_use,
    )


def create_mock_workflow_asset(
    *,
    prompt: str,
    workflow_type: str,
    asset_manager: MediaAssetManager,
) -> MediaAsset:
    template = get_creative_template(workflow_type)
    return asset_manager.create_fake_asset(
        relative_path=f"creative_workflows/{template.workflow_type}-mock.txt",
        content=b"fake creative workflow metadata fixture; not an image",
        prompt=MediaPrompt(prompt),
        provider="mock_creative_workflow",
        asset_type=MediaAssetType.IMAGE,
        metadata={
            "mock": True,
            "workflow_type": template.workflow_type,
            "aspect_ratio": template.aspect_ratio,
            "output_size": template.output_size,
            "real_generation": False,
            "real_editing": False,
            "upload_publish_enabled": False,
        },
    )


def get_creative_template(workflow_type: str) -> CreativeWorkflowTemplate:
    normalized = (workflow_type or "social_post_image").strip().lower().replace("-", "_")
    for template in CREATIVE_WORKFLOW_TEMPLATES:
        if template.workflow_type == normalized:
            return template
    return next(template for template in CREATIVE_WORKFLOW_TEMPLATES if template.workflow_type == "social_post_image")


def infer_workflow_type(prompt: str) -> str:
    lowered = prompt.lower()
    if any(term in lowered for term in ("youtube", "thumbnail")):
        return "youtube_thumbnail"
    if any(term in lowered for term in ("short", "reel", "tiktok", "story")):
        return "short_form_video_cover"
    if "podcast" in lowered:
        return "podcast_cover"
    if any(term in lowered for term in ("real estate", "listing", "property", "house")):
        return "real_estate_listing_graphic"
    if any(term in lowered for term in ("food", "restaurant", "dish")):
        return "food_review_thumbnail"
    if "vlog" in lowered:
        return "family_vlog_title_card"
    if any(term in lowered for term in ("ad", "campaign")):
        return "ad_creative"
    if "before" in lowered and "after" in lowered:
        return "before_after_layout"
    if "product" in lowered:
        return "product_mockup"
    return "social_post_image"


def _license_caution(*, safety: dict[str, Any], template: CreativeWorkflowTemplate, commercial_use: bool) -> dict[str, Any]:
    review_required = bool(
        commercial_use
        or template.commercial_review_recommended
        or safety.get("license_review_required")
    )
    return {
        "review_required": review_required,
        "reason": (
            "Commercial/social creative use requires provider, model, brand, claim, and asset license review before production use."
            if review_required
            else "No commercial/license marker matched, but production use still needs source and provider review."
        ),
        "legal_advice": False,
    }


def _plan_steps(template: CreativeWorkflowTemplate) -> list[dict[str, Any]]:
    return [
        {
            "step": "select_template",
            "workflow_type": template.workflow_type,
            "side_effects": False,
        },
        {
            "step": "run_safety_preflight",
            "side_effects": False,
        },
        {
            "step": "review_license_and_consent",
            "side_effects": False,
        },
        {
            "step": "prepare_mock_asset_metadata_if_requested",
            "side_effects": "test/helper only",
        },
    ]
