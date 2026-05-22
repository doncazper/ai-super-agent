from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent.config.loader import load_capabilities_config
from agent.config.schema import validate_capabilities_config


def show_config(path: str | Path = "config/capabilities.yaml") -> dict[str, Any]:
    config = load_capabilities_config(path)
    validate_capabilities_config(config)
    return config


def config_as_json(path: str | Path = "config/capabilities.yaml") -> str:
    return json.dumps(show_config(path), indent=2, sort_keys=True)
