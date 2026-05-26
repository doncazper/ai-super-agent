from __future__ import annotations

import json
from pathlib import Path

from agent.media.asset_manager import MediaAssetManager
from agent.media.audio_generation import (
    audio_provider_candidates,
    dry_run_generate_audio,
    dry_run_generate_music,
    plan_audio_generation,
)
from agent.media.providers.mock_audio import MockAudioProvider, mock_audio_request
from agent.ui import cli_commands


ROOT = Path(__file__).resolve().parents[2]


def test_music_plan_generated() -> None:
    plan = plan_audio_generation("short upbeat intro bed", mode="music").to_dict()
    assert plan["mode"] == "music"
    assert plan["dry_run"] is True
    assert plan["real_generation"] is False
    assert plan["music_rights_warning"]["review_required"] is True


def test_sound_effect_plan_generated() -> None:
    plan = plan_audio_generation("soft notification chime", mode="audio").to_dict()
    assert plan["mode"] == "audio"
    assert plan["request"]["asset_type"] == "audio"
    assert plan["real_generation"] is False


def test_voice_clone_request_denied() -> None:
    plan = plan_audio_generation("clone voice of my boss for an intro", mode="audio").to_dict()
    assert plan["status"] == "blocked"
    assert plan["music_rights_warning"]["voice_clone_denied"] is True
    assert plan["real_generation"] is False


def test_artist_imitation_flagged() -> None:
    plan = plan_audio_generation("make a song in the style of Taylor Swift", mode="music").to_dict()
    assert plan["status"] == "requires_license_review"
    assert plan["music_rights_warning"]["artist_imitation_flagged"] is True
    assert plan["music_rights_warning"]["copyrighted_song_or_artist_imitation_for_commercial_output_allowed"] is False


def test_mock_audio_metadata_created(tmp_path: Path) -> None:
    manager = MediaAssetManager(project_root=tmp_path)
    request = mock_audio_request("a fake music test", mode="music")
    result = MockAudioProvider().create_fake_result(request=request, asset_manager=manager)
    assert result.status == "mock_created"
    assert result.assets[0].asset_type.value == "music"
    assert Path(result.assets[0].path).exists()
    assert result.assets[0].metadata["real_generation"] is False
    assert manager.get_asset(result.assets[0].asset_id) is not None


def test_audio_provider_candidates_document_generation_disabled() -> None:
    providers = audio_provider_candidates()
    assert any(provider["provider_id"] == "audiocraft_musicgen" for provider in providers)
    assert all(provider["real_generation"] is False for provider in providers)


def test_generate_audio_music_dry_run_payloads() -> None:
    audio = dry_run_generate_audio("soft chime")
    music = dry_run_generate_music("short intro bed")
    assert audio["generated_media"] is False
    assert music["generated_media"] is False
    assert audio["mock_provider_plan"]["real_generation"] is False
    assert music["mock_provider_plan"]["real_generation"] is False


def test_audio_generation_cli(capsys) -> None:
    assert cli_commands.dispatch_cli(["media", "audio", "providers"], project_root=ROOT) == 0
    providers = json.loads(capsys.readouterr().out)
    assert providers["voice_cloning_enabled"] is False

    assert cli_commands.dispatch_cli(["media", "music", "plan", "short intro bed"], project_root=ROOT) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["mode"] == "music"
    assert plan["real_generation"] is False

    assert cli_commands.dispatch_cli(["media", "generate", "audio", "soft chime", "--dry-run"], project_root=ROOT) == 0
    audio = json.loads(capsys.readouterr().out)
    assert audio["generated_media"] is False

    assert cli_commands.dispatch_cli(["media", "generate", "music", "short intro bed", "--dry-run"], project_root=ROOT) == 0
    music = json.loads(capsys.readouterr().out)
    assert music["generated_media"] is False
