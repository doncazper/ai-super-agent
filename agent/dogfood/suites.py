from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from agent.dogfood.models import DogfoodSuite


DEFAULT_SUITES_DIR = "dogfood_suites"


def suites_dir(project_root: str | Path = ".", suites_path: str | Path = DEFAULT_SUITES_DIR) -> Path:
    path = Path(suites_path)
    if path.is_absolute():
        return path
    return Path(project_root) / path


def load_suite(
    suite_id: str,
    *,
    project_root: str | Path = ".",
    suites_path: str | Path = DEFAULT_SUITES_DIR,
) -> DogfoodSuite:
    path = suites_dir(project_root, suites_path) / f"{suite_id}.yaml"
    if not path.exists():
        raise ValueError(f"dogfood suite not found: {suite_id}")
    data = _load_yaml(path)
    suite = DogfoodSuite.from_dict(data)
    if suite.suite_id != suite_id:
        raise ValueError(f"dogfood suite filename {suite_id} does not match suite_id {suite.suite_id}")
    return suite


def load_all_suites(
    *,
    project_root: str | Path = ".",
    suites_path: str | Path = DEFAULT_SUITES_DIR,
) -> list[DogfoodSuite]:
    root = suites_dir(project_root, suites_path)
    if not root.exists():
        return []
    suites: list[DogfoodSuite] = []
    for path in sorted(root.glob("*.yaml")):
        data = _load_yaml(path)
        suite = DogfoodSuite.from_dict(data)
        if path.stem != suite.suite_id:
            raise ValueError(f"dogfood suite filename {path.name} does not match suite_id {suite.suite_id}")
        suites.append(suite)
    return suites


def list_suite_summaries(
    *,
    project_root: str | Path = ".",
    suites_path: str | Path = DEFAULT_SUITES_DIR,
) -> list[dict[str, Any]]:
    return [
        {
            "suite_id": suite.suite_id,
            "name": suite.name,
            "risk_level": suite.risk_level,
            "requires_live_lmstudio": suite.requires_live_lmstudio,
            "requires_web": suite.requires_web,
            "requires_personal_data": suite.requires_personal_data,
            "default_enabled": suite.default_enabled,
            "command_count": len(suite.commands),
        }
        for suite in load_all_suites(project_root=project_root, suites_path=suites_path)
    ]


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid dogfood suite YAML {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"dogfood suite YAML must be a mapping: {path}")
    return data
