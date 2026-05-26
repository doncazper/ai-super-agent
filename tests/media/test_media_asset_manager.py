from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent.media.asset_manager import MediaAssetManager
from agent.media.errors import MediaAssetError, MediaPathError
from agent.media.models import MediaAssetType, MediaPrompt
from agent.ui import cli_commands


ROOT = Path(__file__).resolve().parents[2]


def test_asset_path_is_bounded_to_workspace_media(tmp_path: Path) -> None:
    manager = MediaAssetManager(project_root=tmp_path)
    path = manager.resolve_asset_path("images/fake.png")
    assert path == tmp_path.resolve() / "workspace" / "media" / "images" / "fake.png"


def test_path_traversal_blocked(tmp_path: Path) -> None:
    manager = MediaAssetManager(project_root=tmp_path)
    with pytest.raises(MediaPathError):
        manager.resolve_asset_path("../outside.png")
    with pytest.raises(MediaPathError):
        MediaAssetManager(project_root=tmp_path, media_root=tmp_path / "outside")


def test_metadata_written_for_fake_asset_with_redacted_prompt(tmp_path: Path) -> None:
    manager = MediaAssetManager(project_root=tmp_path)
    asset = manager.create_fake_asset(
        relative_path="images/fake.png",
        content=b"not real image bytes",
        prompt=MediaPrompt("make a test image token=supersecretvalue user@example.com"),
        provider="mock",
        asset_type=MediaAssetType.IMAGE,
        metadata={"api_key": "secret", "fixture": True},
    )
    metadata_path = manager.metadata_path(Path(asset.path))
    assert metadata_path.exists()
    data = json.loads(metadata_path.read_text())
    assert data["asset_id"] == asset.asset_id
    assert data["asset_type"] == "image"
    assert "supersecretvalue" not in data["prompt_redacted"]
    assert "user@example.com" not in data["prompt_redacted"]
    assert data["metadata"]["api_key"] == "[REDACTED]"
    assert manager.get_asset(asset.asset_id) is not None


def test_cleanup_dry_run_writes_nothing(tmp_path: Path) -> None:
    manager = MediaAssetManager(project_root=tmp_path)
    asset = manager.create_fake_asset(
        relative_path="images/fake.png",
        prompt="make a fake image",
        provider="mock",
    )
    output_path = Path(asset.path)
    metadata_path = manager.metadata_path(output_path)
    result = manager.cleanup(dry_run=True)
    assert result["dry_run"] is True
    assert result["writes_performed"] is False
    assert output_path.exists()
    assert metadata_path.exists()
    with pytest.raises(MediaAssetError):
        manager.cleanup(dry_run=False)


def test_media_asset_cli_read_only_and_dry_run(capsys) -> None:
    assert cli_commands.dispatch_cli(["media", "assets", "list"], project_root=ROOT) == 0
    listed = json.loads(capsys.readouterr().out)
    assert listed["raw_prompts_returned"] is False
    assert listed["personal_inputs_returned"] is False

    assert cli_commands.dispatch_cli(["media", "assets", "show", "media_missing"], project_root=ROOT) == 0
    shown = json.loads(capsys.readouterr().out)
    assert shown["status"] == "not_found"

    assert cli_commands.dispatch_cli(["media", "assets", "cleanup", "--dry-run"], project_root=ROOT) == 0
    cleanup = json.loads(capsys.readouterr().out)
    assert cleanup["dry_run"] is True
    assert cleanup["writes_performed"] is False
