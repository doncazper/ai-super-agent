from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_MEDIA_DOCS = [
    ROOT / "docs/media/CREATIVE_MEDIA_GENERATION_TRACK.md",
    ROOT / "docs/media/MEDIA_PROVIDER_STRATEGY.md",
    ROOT / "docs/media/MEDIA_RISK_MODEL.md",
    ROOT / "docs/media/MEDIA_LICENSE_POLICY.md",
    ROOT / "docs/media/MEDIA_ASSET_POLICY.md",
    ROOT / "docs/media/MEDIA_SAFETY_POLICY.md",
    ROOT / "docs/decisions/creative_media_generation_architecture.md",
]


def test_creative_media_docs_exist_and_capture_safety_boundary():
    for path in REQUIRED_MEDIA_DOCS:
        text = path.read_text()
        assert "ToolBroker" in text or "docs-only" in text or "Status: specified only" in text
        assert "no" in text.lower()


def test_creative_media_track_lists_planned_commands_and_provider_categories():
    text = (ROOT / "docs/media/CREATIVE_MEDIA_GENERATION_TRACK.md").read_text()
    for command in [
        "media providers",
        "media doctor",
        "media assets list",
        "media generate image",
        "media safety-check",
        "media dogfood",
    ]:
        assert command in text
    for category in [
        "image_generation",
        "image_editing",
        "text_to_video",
        "music_generation",
        "voice_generation",
        "mock/test",
    ]:
        assert category in text


def test_creative_media_risk_model_blocks_voice_cloning_and_uploads():
    text = (ROOT / "docs/media/MEDIA_RISK_MODEL.md").read_text()
    assert "Voice cloning" in text
    assert "CRITICAL or FORBIDDEN" in text
    assert "Social posting/uploading" in text
    assert "CRITICAL" in text
