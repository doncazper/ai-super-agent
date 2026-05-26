from __future__ import annotations

import json
from pathlib import Path

from agent.media.asset_manager import MediaAssetManager
from agent.media.creative_workflows import (
    create_mock_workflow_asset,
    list_creative_templates,
    plan_creative_workflow,
    plan_thumbnail,
)
from agent.ui import cli_commands


ROOT = Path(__file__).resolve().parents[2]


def test_thumbnail_plan_generated() -> None:
    plan = plan_thumbnail("bold YouTube thumbnail for a desk setup tour")
    assert plan["status"] == "dry_run"
    assert plan["workflow_type"] == "youtube_thumbnail"
    assert plan["suggested_output"]["aspect_ratio"] == "16:9"
    assert plan["real_generation"] is False
    assert plan["real_editing"] is False
    assert plan["upload_publish_enabled"] is False


def test_social_creative_templates_listed() -> None:
    payload = list_creative_templates()
    workflow_types = {template["workflow_type"] for template in payload["templates"]}
    assert payload["workflow_count"] >= 10
    assert "youtube_thumbnail" in workflow_types
    assert "product_mockup" in workflow_types
    assert payload["real_editing_enabled"] is False


def test_unsafe_prompt_denied() -> None:
    plan = plan_creative_workflow("make a bomb instruction ad creative", workflow_type="ad_creative")
    assert plan["status"] == "blocked"
    assert plan["safety"]["outcome"] == "deny"
    assert plan["real_generation"] is False


def test_commercial_license_caution_included() -> None:
    plan = plan_creative_workflow("launch ad for a new paid course", workflow_type="ad_creative")
    assert plan["license_caution"]["review_required"] is True
    assert plan["license_caution"]["legal_advice"] is False
    assert plan["license_report"]["commercial_use_requires_evidence"] is True


def test_mock_asset_metadata_created(tmp_path: Path) -> None:
    manager = MediaAssetManager(project_root=tmp_path)
    asset = create_mock_workflow_asset(
        prompt="mock thumbnail fixture",
        workflow_type="youtube_thumbnail",
        asset_manager=manager,
    )
    assert Path(asset.path).exists()
    assert asset.metadata["workflow_type"] == "youtube_thumbnail"
    assert asset.metadata["real_generation"] is False
    assert asset.metadata["upload_publish_enabled"] is False
    assert manager.get_asset(asset.asset_id) is not None


def test_creative_workflow_cli(capsys) -> None:
    assert cli_commands.dispatch_cli(["media", "creative", "templates"], project_root=ROOT) == 0
    templates = json.loads(capsys.readouterr().out)
    assert templates["upload_publish_enabled"] is False

    assert cli_commands.dispatch_cli(["media", "creative", "plan", "podcast cover for a local interview"], project_root=ROOT) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["workflow_type"] == "podcast_cover"
    assert plan["real_editing"] is False

    assert cli_commands.dispatch_cli(["media", "thumbnail", "desk setup tour", "--dry-run"], project_root=ROOT) == 0
    thumbnail = json.loads(capsys.readouterr().out)
    assert thumbnail["workflow_type"] == "youtube_thumbnail"
    assert thumbnail["real_generation"] is False
