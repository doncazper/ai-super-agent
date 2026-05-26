from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class SecretSourceStatus:
    source_id: str
    enabled: bool
    available: bool
    priority: int
    description: str
    warnings: list[dict[str, str]]

    def to_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "enabled": self.enabled,
            "available": self.available,
            "priority": self.priority,
            "description": self.description,
            "warnings": self.warnings,
        }


def source_statuses(
    *,
    project_root: str | Path = ".",
    environ: Mapping[str, str] | None = None,
    env_path: str | Path | None = None,
) -> list[SecretSourceStatus]:
    root = Path(project_root).resolve()
    env = environ or os.environ
    local_env = Path(env_path) if env_path is not None else root / ".env"
    return [
        SecretSourceStatus(
            "runtime_config",
            enabled=True,
            available=False,
            priority=1,
            description="Explicit safe runtime config supplied by caller; not persisted by secrets layer.",
            warnings=[],
        ),
        SecretSourceStatus(
            "environment",
            enabled=True,
            available=bool(env),
            priority=2,
            description="Process environment variables.",
            warnings=[],
        ),
        SecretSourceStatus(
            "local_env",
            enabled=True,
            available=local_env.exists(),
            priority=3,
            description="Local .env file, allowed only when ignored and untracked.",
            warnings=_local_env_warnings(root, local_env),
        ),
        SecretSourceStatus(
            "macos_keychain",
            enabled=False,
            available=False,
            priority=4,
            description="Future optional macOS Keychain adapter; not accessed in SECRETS-03.",
            warnings=[],
        ),
        SecretSourceStatus(
            "password_manager_manual",
            enabled=True,
            available=True,
            priority=5,
            description="Manual password-manager entry copied into environment outside the repo.",
            warnings=[],
        ),
    ]


def env_file_tracked(project_root: str | Path, env_path: str | Path = ".env") -> bool:
    root = Path(project_root).resolve()
    path = Path(env_path)
    rel = str(path if not path.is_absolute() else path.relative_to(root)) if _inside(path, root) else str(path)
    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", rel],
            cwd=root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            text=True,
        )
    except (OSError, ValueError):
        return False
    return result.returncode == 0


def _local_env_warnings(root: Path, env_path: Path) -> list[dict[str, str]]:
    warnings: list[dict[str, str]] = []
    if env_path.exists() and env_file_tracked(root, env_path):
        warnings.append(
            {
                "code": "env_tracked",
                "severity": "high",
                "message": ".env appears tracked; remove it from git and rotate exposed credentials.",
            }
        )
    return warnings


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root)
        return True
    except ValueError:
        return False
