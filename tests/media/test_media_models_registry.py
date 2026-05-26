from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

from agent.media.models import MediaProviderCapability, MediaProviderStatus
from agent.media.provider_registry import MediaProviderRegistry, default_media_provider_registry
from agent.media.redaction import prompt_hash, redact_media_prompt
from agent.ui import cli_commands


ROOT = Path(__file__).resolve().parents[2]


def test_provider_registry_loads_mock_provider() -> None:
    registry = default_media_provider_registry()
    mock = registry.get_provider("mock")
    assert mock.provider_id == "mock"
    assert mock.status is MediaProviderStatus.STUBBED
    assert MediaProviderCapability.STATUS in mock.capabilities
    assert mock.default_enabled is False
    assert mock.paid_api is False


def test_unknown_provider_is_structured_and_unsupported() -> None:
    provider = MediaProviderRegistry().get_provider("missing")
    assert provider.provider_id == "missing"
    assert provider.status is MediaProviderStatus.UNSUPPORTED
    assert provider.default_enabled is False
    assert provider.risk_level == "FORBIDDEN"
    assert "Known providers" in provider.setup_hint


def test_prompt_redaction_and_hash_do_not_store_raw_secret() -> None:
    prompt = "make an icon api_key=sk-secretvalue123456789 email user@example.com"
    redacted = redact_media_prompt(prompt)
    assert "sk-secretvalue" not in redacted
    assert "user@example.com" not in redacted
    assert "[REDACTED" in redacted
    assert prompt_hash(prompt) == prompt_hash(prompt)


def test_media_import_does_not_load_heavy_provider_modules() -> None:
    before = set(sys.modules)
    importlib.import_module("agent.media.provider_registry")
    imported = set(sys.modules) - before
    forbidden = {"torch", "diffusers", "comfyui", "moviepy", "PIL", "cv2"}
    assert not (imported & forbidden)


def test_media_provider_cli_routes_through_safe_metadata_tools(capsys) -> None:
    assert cli_commands.dispatch_cli(["media", "providers"], project_root=ROOT) == 0
    providers = json.loads(capsys.readouterr().out)
    assert providers["provider_calls_performed"] is False
    assert providers["real_generation_enabled"] is False
    assert any(provider["provider_id"] == "mock" for provider in providers["providers"])

    assert cli_commands.dispatch_cli(["media", "doctor"], project_root=ROOT) == 0
    doctor = json.loads(capsys.readouterr().out)
    assert doctor["provider_calls_performed"] is False
    assert doctor["voice_cloning_enabled"] is False
    assert doctor["asset_manager"]["writes_bounded_to_media_root"] is True
