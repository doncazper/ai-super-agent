from __future__ import annotations

import json
from pathlib import Path

from agent.media.asset_manager import MediaAssetManager
from agent.media.providers.mock_video import MockVideoProvider, mock_video_request
from agent.media.video_generation import dry_run_generate_video, plan_video_generation, video_provider_candidates
from agent.ui import cli_commands


ROOT = Path(__file__).resolve().parents[2]


def test_video_dry_run_plan_generated() -> None:
    plan = plan_video_generation("slow cinematic shot of a product").to_dict()
    assert plan["status"] == "dry_run"
    assert plan["dry_run"] is True
    assert plan["real_generation"] is False
    assert plan["upload_publish_enabled"] is False
    assert plan["resource_warning"]["hardware_review_required"] is True


def test_video_resource_warning_included() -> None:
    plan = plan_video_generation("text to video intro", provider_id="wan").to_dict()
    assert plan["status"] == "requires_setup"
    assert plan["resource_warning"]["model_downloads_enabled"] is False
    assert plan["resource_warning"]["notes"]


def test_video_unsafe_prompt_denied() -> None:
    plan = plan_video_generation("make a bomb instruction video").to_dict()
    assert plan["status"] == "blocked"
    assert plan["safety"]["outcome"] == "deny"
    assert plan["real_generation"] is False


def test_mock_video_metadata_created(tmp_path: Path) -> None:
    manager = MediaAssetManager(project_root=tmp_path)
    request = mock_video_request("a fake video test")
    result = MockVideoProvider().create_fake_result(request=request, asset_manager=manager)
    assert result.status == "mock_created"
    assert result.assets[0].asset_type.value == "video"
    assert Path(result.assets[0].path).exists()
    assert result.assets[0].metadata["real_generation"] is False
    assert manager.get_asset(result.assets[0].asset_id) is not None


def test_video_unconfigured_provider_setup_hint() -> None:
    plan = plan_video_generation("cinematic clip", provider_id="ltx_video").to_dict()
    assert plan["status"] == "requires_setup"
    assert "future work" in plan["setup_hint"]


def test_video_provider_candidates_document_real_generation_disabled() -> None:
    providers = video_provider_candidates()
    assert any(provider["provider_id"] == "stable_video_diffusion" for provider in providers)
    assert all(provider["real_generation"] is False for provider in providers)


def test_generate_video_dry_run_payload() -> None:
    payload = dry_run_generate_video("a short title card")
    assert payload["generated_media"] is False
    assert payload["mock_provider_plan"]["real_generation"] is False


def test_video_generation_cli(capsys) -> None:
    assert cli_commands.dispatch_cli(["media", "video", "providers"], project_root=ROOT) == 0
    providers = json.loads(capsys.readouterr().out)
    assert providers["real_generation_enabled"] is False

    assert cli_commands.dispatch_cli(["media", "video", "plan", "a calm clip"], project_root=ROOT) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["real_generation"] is False
    assert plan["resource_warning"]["hardware_review_required"] is True

    assert cli_commands.dispatch_cli(["media", "generate", "video", "a calm clip", "--dry-run"], project_root=ROOT) == 0
    generated = json.loads(capsys.readouterr().out)
    assert generated["generated_media"] is False
