from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


LAUNCHER_VERSION = "1.0.0"
CONFIG_DIR = ".config/ai-super-agent"
CONFIG_FILE = "launcher.json"
CODEX_BUNDLED_PYTHON = "/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"


class RepairLevel(str, Enum):
    LEVEL_1_AUTO_REPAIRABLE = "level_1_auto_repairable"
    LEVEL_2_COMMAND_REQUIRED = "level_2_command_required"
    LEVEL_3_MANUAL_REQUIRED = "level_3_manual_required"
    NOT_REPAIRABLE_BY_LAUNCHER = "not_repairable_by_launcher"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class LauncherConfig:
    repo_path: str
    alias: str = "smartagent"
    install_dir: str = ""
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    launcher_version: str = LAUNCHER_VERSION
    last_known_good_repo_path: str = ""
    last_repo_verification_status: str = ""
    last_known_good_python: str = ""
    last_repair_result: str = ""
    auto_repair_safe_enabled: bool = True
    venv_repair_requires_explicit: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LauncherConfig":
        return cls(
            repo_path=str(data.get("repo_path", "")),
            alias=str(data.get("alias", "smartagent")),
            install_dir=str(data.get("install_dir", "")),
            created_at=str(data.get("created_at") or utc_now_iso()),
            updated_at=str(data.get("updated_at") or utc_now_iso()),
            launcher_version=str(data.get("launcher_version", LAUNCHER_VERSION)),
            last_known_good_repo_path=str(data.get("last_known_good_repo_path", "")),
            last_repo_verification_status=str(data.get("last_repo_verification_status", "")),
            last_known_good_python=str(data.get("last_known_good_python", "")),
            last_repair_result=str(data.get("last_repair_result", "")),
            auto_repair_safe_enabled=bool(data.get("auto_repair_safe_enabled", True)),
            venv_repair_requires_explicit=bool(data.get("venv_repair_requires_explicit", True)),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def with_updates(self, **updates: Any) -> "LauncherConfig":
        data = self.to_dict()
        data.update(updates)
        data["updated_at"] = utc_now_iso()
        return LauncherConfig.from_dict(data)


@dataclass(frozen=True)
class PythonCandidate:
    executable: str
    version: tuple[int, int, int] | None
    source: str
    usable: bool
    reason: str = ""

    @property
    def version_text(self) -> str:
        if self.version is None:
            return "unknown"
        return ".".join(str(part) for part in self.version)


@dataclass(frozen=True)
class DiagnosticFinding:
    code: str
    message: str
    repair_level: RepairLevel
    next_command: str = ""


@dataclass(frozen=True)
class LauncherDiagnosis:
    config_path: str
    repo_path: str | None
    repo_valid: bool
    repo_candidates: tuple[str, ...]
    python: PythonCandidate | None
    scripts_agent_executable: bool
    wrapper_executable: bool
    install_dir_in_path: bool
    findings: tuple[DiagnosticFinding, ...]

    @property
    def ok(self) -> bool:
        return self.repo_valid and self.python is not None and self.python.usable and self.scripts_agent_executable


@dataclass(frozen=True)
class RepairResult:
    changed: tuple[str, ...]
    skipped: tuple[str, ...]
    errors: tuple[str, ...]
    next_commands: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def config_path_for_home(home: str | Path | None = None) -> Path:
    base = Path(home).expanduser() if home else Path.home()
    return base / CONFIG_DIR / CONFIG_FILE
