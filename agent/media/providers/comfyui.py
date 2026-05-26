from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Callable
from urllib.error import URLError
from urllib.request import urlopen

from agent.media.errors import MediaProviderError


class ComfyUIProviderStatus(StrEnum):
    DISABLED = "disabled"
    NOT_CONFIGURED = "not_configured"
    SERVER_UNREACHABLE = "server_unreachable"
    REACHABLE = "reachable"
    WORKFLOW_SUBMIT_DISABLED = "workflow_submit_disabled"
    READY_MOCK_ONLY = "ready_mock_only"
    READY = "ready"


@dataclass(frozen=True)
class ComfyUIConfig:
    enabled: bool = False
    base_url: str = "http://127.0.0.1:8188"
    timeout_seconds: int = 120
    output_dir: str = ""
    allow_workflow_submit: bool = False
    allow_custom_nodes: bool = False
    require_safety_preflight: bool = True

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "ComfyUIConfig":
        source = env if env is not None else os.environ
        return cls(
            enabled=_env_bool(source, "COMFYUI_ENABLED", default=False),
            base_url=source.get("COMFYUI_BASE_URL", "http://127.0.0.1:8188").strip(),
            timeout_seconds=_env_int(source, "COMFYUI_TIMEOUT_SECONDS", default=120),
            output_dir=source.get("COMFYUI_OUTPUT_DIR", "").strip(),
            allow_workflow_submit=_env_bool(source, "COMFYUI_ALLOW_WORKFLOW_SUBMIT", default=False),
            allow_custom_nodes=_env_bool(source, "COMFYUI_ALLOW_CUSTOM_NODES", default=False),
            require_safety_preflight=_env_bool(source, "COMFYUI_REQUIRE_SAFETY_PREFLIGHT", default=True),
        )

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "base_url": self.base_url,
            "timeout_seconds": self.timeout_seconds,
            "output_dir_configured": bool(self.output_dir),
            "allow_workflow_submit": self.allow_workflow_submit,
            "allow_custom_nodes": self.allow_custom_nodes,
            "require_safety_preflight": self.require_safety_preflight,
        }


class ComfyUIProvider:
    provider_id = "comfyui"

    def __init__(
        self,
        config: ComfyUIConfig | None = None,
        *,
        health_checker: Callable[[str, int], bool] | None = None,
    ) -> None:
        self.config = config or ComfyUIConfig.from_env()
        self._health_checker = health_checker or _default_health_checker

    def status(self, *, check_server: bool = False) -> dict[str, Any]:
        status = self._status(check_server=check_server)
        return {
            "provider_id": self.provider_id,
            "status": status.value,
            "config": self.config.to_safe_dict(),
            "generation_enabled": False,
            "workflow_submit_allowed": self.config.allow_workflow_submit,
            "workflow_submitted": False,
            "custom_nodes_allowed": self.config.allow_custom_nodes,
            "custom_nodes_warning": not self.config.allow_custom_nodes,
            "workflow_json_trust_level": "UNTRUSTED_DOCUMENT",
            "setup_hint": self._setup_hint(status),
        }

    def doctor(self, *, check_server: bool = False) -> dict[str, Any]:
        payload = self.status(check_server=check_server)
        payload.update(
            {
                "server_started": False,
                "models_downloaded": False,
                "provider_imports_heavy_runtime": False,
                "health_check_submits_workflow": False,
                "safety_preflight_required": self.config.require_safety_preflight,
                "warnings": self._warnings(),
            }
        )
        return payload

    def list_workflows(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "status": self._status(check_server=False).value,
            "workflows": [],
            "workflow_json_trust_level": "UNTRUSTED_DOCUMENT",
            "workflow_submission_enabled": False,
            "setup_hint": "No ComfyUI workflows are vetted or executable in MEDIA-04.",
        }

    def submit_workflow(self, workflow: dict[str, Any]) -> dict[str, Any]:
        if not self.config.allow_workflow_submit:
            raise MediaProviderError("ComfyUI workflow submission is disabled by COMFYUI_ALLOW_WORKFLOW_SUBMIT=false")
        raise MediaProviderError("ComfyUI workflow submission is not implemented in MEDIA-04")

    def _status(self, *, check_server: bool) -> ComfyUIProviderStatus:
        if not self.config.enabled:
            return ComfyUIProviderStatus.DISABLED
        if not self.config.base_url:
            return ComfyUIProviderStatus.NOT_CONFIGURED
        if not self.config.allow_workflow_submit:
            if check_server:
                return ComfyUIProviderStatus.REACHABLE if self._server_reachable() else ComfyUIProviderStatus.SERVER_UNREACHABLE
            return ComfyUIProviderStatus.WORKFLOW_SUBMIT_DISABLED
        if not self.config.require_safety_preflight:
            return ComfyUIProviderStatus.NOT_CONFIGURED
        return ComfyUIProviderStatus.READY_MOCK_ONLY

    def _server_reachable(self) -> bool:
        return self._health_checker(self.config.base_url, self.config.timeout_seconds)

    def _setup_hint(self, status: ComfyUIProviderStatus) -> str:
        if status is ComfyUIProviderStatus.DISABLED:
            return "Set COMFYUI_ENABLED=true only after reviewing the ComfyUI provider docs; MEDIA-04 still does not submit workflows."
        if status is ComfyUIProviderStatus.NOT_CONFIGURED:
            return "Set COMFYUI_BASE_URL and keep COMFYUI_REQUIRE_SAFETY_PREFLIGHT=true."
        if status is ComfyUIProviderStatus.SERVER_UNREACHABLE:
            return "ComfyUI was not reachable at the configured localhost URL; no server was started by this command."
        if status is ComfyUIProviderStatus.WORKFLOW_SUBMIT_DISABLED:
            return "Workflow submission remains disabled by COMFYUI_ALLOW_WORKFLOW_SUBMIT=false."
        return "ComfyUI status metadata is available; workflow submission remains future gated."

    def _warnings(self) -> list[str]:
        warnings = [
            "MEDIA-04 never installs ComfyUI, starts a server, downloads models, submits workflows, or generates media.",
            "ComfyUI workflow JSON is treated as UNTRUSTED_DOCUMENT until vetted.",
        ]
        if not self.config.allow_custom_nodes:
            warnings.append("Custom nodes are disabled by default and treated as supply-chain risk.")
        if self.config.allow_workflow_submit:
            warnings.append("Workflow submit config is true, but MEDIA-04 submit_workflow still raises until future implementation.")
        return warnings


def _default_health_checker(base_url: str, timeout_seconds: int) -> bool:
    try:
        with urlopen(base_url.rstrip("/") + "/system_stats", timeout=min(timeout_seconds, 10)) as response:
            return 200 <= int(response.status) < 500
    except (OSError, URLError, ValueError):
        return False


def _env_bool(env: dict[str, str], name: str, *, default: bool) -> bool:
    value = env.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(env: dict[str, str], name: str, *, default: int) -> int:
    try:
        return int(env.get(name, str(default)))
    except ValueError:
        return default
