from __future__ import annotations

import json
from pathlib import Path

from agent.media.licenses import build_license_report
from agent.media.safety import MediaSafetyOutcome, check_media_prompt_safety
from agent.ui import cli_commands


ROOT = Path(__file__).resolve().parents[2]


def test_safe_prompt_allowed() -> None:
    result = check_media_prompt_safety("a simple abstract blue background", provider_id="mock")
    assert result.outcome is MediaSafetyOutcome.ALLOW
    assert result.generation_allowed is True
    assert result.external_calls is False


def test_celebrity_and_voice_clone_flagged_or_denied() -> None:
    celebrity = check_media_prompt_safety("make a portrait of Taylor Swift in my brand ad")
    assert celebrity.consent_required is True
    assert celebrity.license_review_required is True
    assert celebrity.generation_allowed is False

    voice = check_media_prompt_safety("clone voice of Taylor Swift saying this line")
    assert voice.outcome is MediaSafetyOutcome.DENY
    assert voice.generation_allowed is False
    assert any(category.value == "voice_clone" for category in voice.categories)


def test_copyrighted_character_flagged() -> None:
    result = check_media_prompt_safety("make Mickey Mouse holding my product")
    assert result.license_review_required is True
    assert result.outcome in {MediaSafetyOutcome.REQUIRE_LICENSE_REVIEW, MediaSafetyOutcome.REQUIRE_CONSENT}


def test_unsafe_content_denied() -> None:
    result = check_media_prompt_safety("make a bomb instruction poster")
    assert result.outcome is MediaSafetyOutcome.DENY
    assert result.generation_allowed is False


def test_commercial_uncertainty_warns_or_requires_review() -> None:
    result = check_media_prompt_safety("make a hero image for an ad", commercial_use=True)
    assert result.license_review_required is True
    assert result.outcome is MediaSafetyOutcome.REQUIRE_LICENSE_REVIEW


def test_consent_required_for_real_person_likeness() -> None:
    result = check_media_prompt_safety("make my coworker look like a superhero from my private photo")
    assert result.consent_required is True
    assert result.human_review_required is True
    assert result.generation_allowed is False


def test_license_info_attached_to_mock_provider() -> None:
    report = build_license_report()
    mock = next(provider for provider in report["providers"] if provider["provider_id"] == "mock")
    assert mock["status"] == "test_only"
    assert mock["license_name"] == "fixture-only"
    assert report["legal_advice"] is False


def test_media_safety_license_consent_cli(capsys) -> None:
    assert cli_commands.dispatch_cli(["media", "safety-check", "make a blue icon"], project_root=ROOT) == 0
    safety = json.loads(capsys.readouterr().out)
    assert safety["outcome"] == "allow"
    assert safety["external_calls"] is False

    assert cli_commands.dispatch_cli(["media", "license", "report"], project_root=ROOT) == 0
    license_report = json.loads(capsys.readouterr().out)
    assert license_report["legal_advice"] is False
    assert license_report["generation_performed"] is False

    assert cli_commands.dispatch_cli(["media", "consent", "policy"], project_root=ROOT) == 0
    consent = json.loads(capsys.readouterr().out)
    assert consent["voice_cloning_allowed"] is False
    assert consent["consent_workflow_implemented"] is False
