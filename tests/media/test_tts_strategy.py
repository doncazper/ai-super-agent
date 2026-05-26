from __future__ import annotations

import json
from pathlib import Path

from agent.media.tts import list_voice_providers, plan_tts, voice_consent_policy
from agent.ui import cli_commands


ROOT = Path(__file__).resolve().parents[2]


def test_generic_tts_plan_allowed_stubbed() -> None:
    plan = plan_tts("Read this announcement in a neutral voice.")
    assert plan["status"] == "stubbed_allowed"
    assert plan["voice_category"] == "generic_tts"
    assert plan["real_generation"] is False
    assert plan["watermark_or_provenance_required"] is True


def test_public_figure_voice_denied() -> None:
    plan = plan_tts("Read this like Taylor Swift.")
    assert plan["status"] == "denied_deferred"
    assert plan["voice_category"] == "public_figure_voice"
    assert plan["consent_required"] is True


def test_private_person_voice_denied() -> None:
    plan = plan_tts("Make it sound like my boss.")
    assert plan["status"] == "denied_deferred"
    assert plan["voice_category"] == "private_person_voice"
    assert plan["voice_cloning_enabled"] is False


def test_user_owned_voice_requires_consent_system() -> None:
    plan = plan_tts("Use my recorded voice.", voice_category="user_owned_voice_with_consent")
    assert plan["status"] == "requires_consent_system"
    assert plan["consent_required"] is True
    assert "consent record system" in plan["setup_hint"]


def test_voice_consent_policy_and_providers() -> None:
    policy = voice_consent_policy()
    providers = list_voice_providers()
    assert policy["consent_system_implemented"] is False
    assert policy["watermark_or_provenance_required_for_future_outputs"] is True
    assert providers["voice_cloning_enabled"] is False
    assert all(provider["real_generation"] is False for provider in providers["providers"])


def test_tts_cli(capsys) -> None:
    assert cli_commands.dispatch_cli(["media", "tts", "plan", "Read a launch note."], project_root=ROOT) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["status"] == "stubbed_allowed"
    assert plan["real_generation"] is False

    assert cli_commands.dispatch_cli(["media", "voice", "consent-policy"], project_root=ROOT) == 0
    policy = json.loads(capsys.readouterr().out)
    assert policy["consent_system_implemented"] is False

    assert cli_commands.dispatch_cli(["media", "voice", "providers"], project_root=ROOT) == 0
    providers = json.loads(capsys.readouterr().out)
    assert providers["voice_cloning_enabled"] is False
