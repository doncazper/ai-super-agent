from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agent.platforms.config import PlatformRuntimeMode
from agent.platforms.models import PlatformKind


@dataclass(frozen=True)
class PlatformPaths:
    platform: PlatformKind
    runtime_mode: str
    config_dir: Path
    data_dir: Path
    cache_dir: Path
    logs_dir: Path
    workspace_dir: Path
    reports_dir: Path
    platform_state_dir: Path
    personal_data_scanned: bool = False
    directories_created: bool = False
    denied_path_policy: str = "Existing filesystem denied/sensitive path policies remain authoritative."
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "platform": self.platform.value,
            "runtime_mode": self.runtime_mode,
            "config_dir": str(self.config_dir),
            "data_dir": str(self.data_dir),
            "cache_dir": str(self.cache_dir),
            "logs_dir": str(self.logs_dir),
            "workspace_dir": str(self.workspace_dir),
            "reports_dir": str(self.reports_dir),
            "platform_state_dir": str(self.platform_state_dir),
            "personal_data_scanned": self.personal_data_scanned,
            "directories_created": self.directories_created,
            "denied_path_policy": self.denied_path_policy,
            "warnings": list(self.warnings),
        }


def get_platform_paths(
    *,
    project_root: str | Path | None = None,
    platform: PlatformKind | str = PlatformKind.UNKNOWN,
    runtime_mode: str = PlatformRuntimeMode.CLI.value,
) -> PlatformPaths:
    """Compute project-local platform paths without scanning or creating files."""

    root = _project_root(project_root)
    platform_kind = _parse_platform(platform)
    workspace_dir = root / "workspace"
    reports_dir = root / "reports"
    platform_state_dir = workspace_dir / "platform_state" / platform_kind.value

    return PlatformPaths(
        platform=platform_kind,
        runtime_mode=runtime_mode,
        config_dir=root / "config",
        data_dir=workspace_dir / "platform_data",
        cache_dir=workspace_dir / ".cache" / "platforms",
        logs_dir=reports_dir / "platforms",
        workspace_dir=workspace_dir,
        reports_dir=reports_dir,
        platform_state_dir=platform_state_dir,
        personal_data_scanned=False,
        directories_created=False,
        warnings=(
            "Windows denied/sensitive paths are planned metadata only; existing filesystem policy remains authoritative.",
        )
        if platform_kind is PlatformKind.WINDOWS
        else (),
    )


def _project_root(project_root: str | Path | None) -> Path:
    if project_root is not None:
        return Path(project_root).resolve()
    return Path(__file__).resolve().parents[2]


def _parse_platform(platform: PlatformKind | str) -> PlatformKind:
    if isinstance(platform, PlatformKind):
        return platform
    try:
        return PlatformKind(str(platform))
    except ValueError:
        return PlatformKind.UNKNOWN
