from __future__ import annotations

import json
from pathlib import Path

from agent.media.asset_manager import MediaAssetManager
from agent.media.image_generation import dry_run_generate_image, image_provider_candidates, plan_image_generation
from agent.media.providers.mock_image import MockImageProvider, mock_image_request
from agent.ui import cli_commands


ROOT = Path(__file__).resolve().parents[2]


def test_dry_run_plan_generated() -> None:
    plan = plan_image_generation("a calm abstract wallpaper").to_dict()
    assert plan["status"] == "dry_run"
    assert plan["dry_run"] is True
    assert plan["real_generation"] is False
    assert plan["safety"]["outcome"] == "allow"


def test_unsafe_prompt_blocked() -> None:
    plan = plan_image_generation("make a bomb instruction poster").to_dict()
    assert plan["status"] == "blocked"
    assert plan["safety"]["outcome"] == "deny"
    assert plan["real_generation"] is False


def test_license_uncertainty_warning() -> None:
    plan = plan_image_generation("make Mickey Mouse for a client campaign").to_dict()
    assert plan["safety"]["license_review_required"] is True
    assert plan["real_generation"] is False


def test_mock_image_result_metadata_created(tmp_path: Path) -> None:
    manager = MediaAssetManager(project_root=tmp_path)
    request = mock_image_request("a fake test image")
    result = MockImageProvider().create_fake_result(request=request, asset_manager=manager)
    assert result.status == "mock_created"
    assert result.assets[0].provider == "mock_image"
    assert Path(result.assets[0].path).exists()
    assert manager.get_asset(result.assets[0].asset_id) is not None


def test_unconfigured_provider_setup_hint() -> None:
    plan = plan_image_generation("a landscape", provider_id="diffusers").to_dict()
    assert plan["status"] == "requires_setup"
    assert "diffusion libraries" in plan["setup_hint"]


def test_image_provider_candidates_document_real_generation_disabled() -> None:
    providers = image_provider_candidates()
    assert any(provider["provider_id"] == "comfyui" for provider in providers)
    assert all(provider["real_generation"] is False for provider in providers)


def test_generate_image_dry_run_payload() -> None:
    payload = dry_run_generate_image("a blue icon")
    assert payload["generated_media"] is False
    assert payload["mock_provider_plan"]["real_generation"] is False


def test_image_generation_cli(capsys) -> None:
    assert cli_commands.dispatch_cli(["media", "image", "providers"], project_root=ROOT) == 0
    providers = json.loads(capsys.readouterr().out)
    assert providers["real_generation_enabled"] is False

    assert cli_commands.dispatch_cli(["media", "image", "plan", "a blue icon"], project_root=ROOT) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["real_generation"] is False

    assert cli_commands.dispatch_cli(["media", "generate", "image", "a blue icon", "--dry-run"], project_root=ROOT) == 0
    generated = json.loads(capsys.readouterr().out)
    assert generated["generated_media"] is False
