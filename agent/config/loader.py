from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


DEFAULT_CAPABILITIES_PATH = Path("config/capabilities.yaml")


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError("configuration root must be an object")
    return loaded


def load_capabilities_config(path: str | Path = DEFAULT_CAPABILITIES_PATH) -> dict[str, Any]:
    return load_yaml(path)
