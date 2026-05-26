from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

from agent.media.errors import MediaProviderError
from agent.media.providers.comfyui import ComfyUIConfig, ComfyUIProvider, ComfyUIProviderStatus
from agent.media.provider_registry import default_media_provider_registry
from agent.ui import cli_commands


ROOT = Path(__file__).resolve().parents[2]


def test_comfyui_provider_disabled_by_default() -> None:
    provider = ComfyUIProvider(ComfyUIConfig.from_env({}))
    status = provider.doctor()
    assert status["status"] == ComfyUIProviderStatus.DISABLED.value
    assert status["workflow_submitted"] is False
    assert status["generation_enabled"] is False


def test_comfyui_missing_config_setup_hint() -> None:
    provider = ComfyUIProvider(ComfyUIConfig.from_env({"COMFYUI_ENABLED": "true", "COMFYUI_BASE_URL": ""}))
    status = provider.doctor()
    assert status["status"] == ComfyUIProviderStatus.NOT_CONFIGURED.value
    assert "COMFYUI_BASE_URL" in status["setup_hint"]


def test_comfyui_mock_server_reachable() -> None:
    provider = ComfyUIProvider(
        ComfyUIConfig.from_env({"COMFYUI_ENABLED": "true"}),
        health_checker=lambda base_url, timeout: True,
    )
    status = provider.doctor(check_server=True)
    assert status["status"] == ComfyUIProviderStatus.REACHABLE.value
    assert status["health_check_submits_workflow"] is False


def test_comfyui_workflow_submit_denied_by_default() -> None:
    provider = ComfyUIProvider(ComfyUIConfig.from_env({}))
    with pytest.raises(MediaProviderError):
        provider.submit_workflow({"prompt": {}})


def test_comfyui_custom_nodes_warning() -> None:
    provider = ComfyUIProvider(ComfyUIConfig.from_env({"COMFYUI_ENABLED": "true"}))
    status = provider.doctor()
    assert status["custom_nodes_warning"] is True
    assert any("Custom nodes" in warning for warning in status["warnings"])


def test_provider_registry_lists_comfyui() -> None:
    registry = default_media_provider_registry()
    provider = registry.get_provider("comfyui")
    assert provider.provider_id == "comfyui"
    assert provider.default_enabled is False


def test_comfyui_cli_and_workflow_stub(capsys) -> None:
    assert cli_commands.dispatch_cli(["media", "comfyui", "doctor"], project_root=ROOT) == 0
    doctor = json.loads(capsys.readouterr().out)
    assert doctor["workflow_submitted"] is False
    assert doctor["models_downloaded"] is False

    assert cli_commands.dispatch_cli(["media", "workflows", "list", "--provider", "comfyui"], project_root=ROOT) == 0
    workflows = json.loads(capsys.readouterr().out)
    assert workflows["workflow_submission_enabled"] is False
    assert workflows["workflow_json_trust_level"] == "UNTRUSTED_DOCUMENT"


def test_comfyui_import_does_not_load_heavy_modules() -> None:
    before = set(sys.modules)
    importlib.import_module("agent.media.providers.comfyui")
    imported = set(sys.modules) - before
    forbidden = {"torch", "diffusers", "comfyui", "moviepy", "PIL", "cv2"}
    assert not (imported & forbidden)
