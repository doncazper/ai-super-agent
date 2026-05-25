from __future__ import annotations

import importlib.util
import os
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping

from agent.native_skills.models import NativeSkillManifest


@dataclass(frozen=True)
class DependencyCheck:
    dependency_type: str
    name: str
    status: str
    redacted_value: str = ""
    setup_hint: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class DependencyCheckResult:
    skill_id: str
    status: str
    checks: list[DependencyCheck]

    def to_dict(self) -> dict[str, object]:
        return {
            "skill_id": self.skill_id,
            "status": self.status,
            "checks": [check.to_dict() for check in self.checks],
        }


def check_dependencies(
    manifest: NativeSkillManifest,
    *,
    project_root: str | Path = ".",
    env: Mapping[str, str] | None = None,
    known_capabilities: set[str] | None = None,
    configured_connectors: set[str] | None = None,
    configured_providers: set[str] | None = None,
) -> DependencyCheckResult:
    root = Path(project_root)
    environment = os.environ if env is None else env
    capabilities = known_capabilities or set()
    connectors = configured_connectors or set()
    providers = configured_providers or set()
    checks: list[DependencyCheck] = []

    for name in manifest.required_env:
        present = name in environment and bool(environment.get(name))
        checks.append(
            DependencyCheck(
                dependency_type="env",
                name=name,
                status="available" if present else "requires_setup",
                redacted_value="[set]" if present else "",
                setup_hint=f"Set {name} in the environment; value is checked by presence only.",
            )
        )

    for key in manifest.required_config:
        present = _config_key_exists(root, key)
        checks.append(
            DependencyCheck(
                dependency_type="config",
                name=key,
                status="available" if present else "requires_setup",
                setup_hint=f"Add config key {key} if this skill is approved.",
            )
        )

    for binary in manifest.required_binaries:
        present = shutil.which(binary) is not None
        checks.append(
            DependencyCheck(
                dependency_type="binary",
                name=binary,
                status="available" if present else "requires_setup",
                setup_hint=f"Install or configure binary {binary}; dependency checks do not install it automatically.",
            )
        )

    for file_name in manifest.required_files:
        candidate = root / file_name
        present = candidate.exists() and candidate.resolve().is_relative_to(root.resolve())
        checks.append(
            DependencyCheck(
                dependency_type="workspace_file",
                name=file_name,
                status="available" if present else "requires_setup",
                setup_hint=f"Provide workspace/project file {file_name}; no broad personal file scan is performed.",
            )
        )

    for capability in manifest.required_capabilities:
        checks.append(
            DependencyCheck(
                dependency_type="capability",
                name=capability,
                status="available" if capability in capabilities else "blocked",
                setup_hint="Capability must exist in config/capabilities.yaml before execution.",
            )
        )

    for platform in manifest.required_platforms:
        current = _current_platform()
        checks.append(
            DependencyCheck(
                dependency_type="platform",
                name=platform,
                status="available" if platform == current or platform == "any" else "unsupported",
                setup_hint=f"Requires platform {platform}; current platform is {current}.",
            )
        )

    for connector in manifest.required_connectors:
        checks.append(
            DependencyCheck(
                dependency_type="connector",
                name=connector,
                status="available" if connector in connectors else "requires_setup",
                setup_hint=f"Configure connector {connector}; checks do not call the connector.",
            )
        )

    for provider in manifest.provenance.get("required_providers", []) if isinstance(manifest.provenance, dict) else []:
        provider_name = str(provider)
        checks.append(
            DependencyCheck(
                dependency_type="provider",
                name=provider_name,
                status="available" if provider_name in providers else "requires_setup",
                setup_hint=f"Configure provider {provider_name}; provider checks do not call live APIs.",
            )
        )

    if manifest.required_python:
        checks.append(
            DependencyCheck(
                dependency_type="python",
                name=manifest.required_python,
                status="available" if _python_requirement_ok(manifest.required_python) else "requires_setup",
                setup_hint=f"Requires Python {manifest.required_python}; current version is {sys.version_info.major}.{sys.version_info.minor}.",
            )
        )

    for feature in manifest.required_model_features:
        checks.append(
            DependencyCheck(
                dependency_type="model_feature",
                name=feature,
                status="requires_setup",
                setup_hint=f"Model feature {feature} must be verified by a separate model/runtime check.",
            )
        )

    status = "available" if all(check.status == "available" for check in checks) else "requires_setup"
    if any(check.status in {"blocked", "unsupported"} for check in checks):
        status = "blocked"
    return DependencyCheckResult(skill_id=manifest.skill_id, status=status, checks=checks)


def python_package_available(package_name: str) -> bool:
    return importlib.util.find_spec(package_name) is not None


def _config_key_exists(root: Path, key: str) -> bool:
    config_path = root / "config" / "capabilities.yaml"
    if not config_path.exists():
        return False
    return key in config_path.read_text(encoding="utf-8", errors="replace")


def _current_platform() -> str:
    if sys.platform == "darwin":
        return "macos"
    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform.startswith("linux"):
        return "linux"
    return "unknown"


def _python_requirement_ok(requirement: str) -> bool:
    normalized = requirement.strip().removeprefix(">=").strip()
    parts = normalized.split(".")
    if len(parts) < 2 or not parts[0].isdigit() or not parts[1].isdigit():
        return True
    required = (int(parts[0]), int(parts[1]))
    return (sys.version_info.major, sys.version_info.minor) >= required
