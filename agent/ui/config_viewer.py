from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent.config.loader import load_capabilities_config
from agent.config.runtime import RuntimeConfig
from agent.config.schema import validate_capabilities_config


def show_config(path: str | Path = "config/capabilities.yaml") -> dict[str, Any]:
    capabilities = load_capabilities_config(path)
    validate_capabilities_config(capabilities)
    runtime = RuntimeConfig.from_env()
    return {
        "runtime": {
            "lmstudio_base_url": runtime.lmstudio_base_url,
            "lmstudio_model_set": bool(runtime.lmstudio_model),
            "temperature": runtime.temperature,
            "top_p": runtime.top_p,
            "max_tokens": runtime.max_tokens,
            "tool_mode": runtime.tool_mode,
            "debug": runtime.debug,
            "audit_log_path": runtime.audit_log_path,
            "capabilities_path": runtime.capabilities_path,
        },
        "capabilities": capabilities,
    }


def config_as_json(path: str | Path = "config/capabilities.yaml") -> str:
    return json.dumps(show_config(path), indent=2, sort_keys=True)
