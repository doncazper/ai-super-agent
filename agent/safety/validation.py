from __future__ import annotations

from pathlib import Path

from agent.config.loader import load_capabilities_config
from agent.config.schema import validate_capabilities_config


def validate_startup_policy(path: str | Path = "config/capabilities.yaml") -> None:
    validate_capabilities_config(load_capabilities_config(path))
