from __future__ import annotations

import json
import os
import re
import shutil
import stat
import subprocess
from pathlib import Path

from .models import (
    CODEX_BUNDLED_PYTHON,
    LAUNCHER_VERSION,
    DiagnosticFinding,
    LauncherConfig,
    LauncherDiagnosis,
    PythonCandidate,
    RepairLevel,
    config_path_for_home,
    utc_now_iso,
)


ALIAS_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
SHELL_META_CHARS = set(";&|<>(){}[]$`'\"\\!*?")


def validate_alias(alias: str) -> tuple[bool, str]:
    if not alias:
        return False, "alias cannot be empty"
    if "/" in alias:
        return False, "alias cannot contain slashes"
    if any(char.isspace() for char in alias):
        return False, "alias cannot contain spaces"
    if any(char in SHELL_META_CHARS for char in alias):
        return False, "alias cannot contain shell metacharacters"
    if not ALIAS_PATTERN.match(alias):
        return False, "alias must start with a letter and contain only letters, numbers, underscores, or hyphens"
    return True, ""


def default_install_dir(home: str | Path | None = None) -> Path:
    return (Path(home).expanduser() if home else Path.home()) / "bin"


def load_config(path: str | Path | None = None) -> LauncherConfig | None:
    config_path = Path(path) if path else config_path_for_home()
    if not config_path.exists():
        return None
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return LauncherConfig.from_dict(data)


def save_config(config: LauncherConfig, path: str | Path | None = None) -> Path:
    config_path = Path(path) if path else config_path_for_home()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    data = config.with_updates(launcher_version=LAUNCHER_VERSION).to_dict()
    config_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return config_path


REQUIRED_REPO_MARKERS = ("smart_agent.py", "scripts/agent")
OPTIONAL_REPO_MARKERS = ("pyproject.toml", "AGENTS.md", "docs/PROJECT_STATE.md", "docs/COMMAND_REGISTRY.md", ".git")


def git_repo_root(cwd: str | Path | None = None) -> Path | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=Path(cwd).expanduser() if cwd else None,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0 or not result.stdout or not result.stdout.strip():
        return None
    return Path(result.stdout.strip()).expanduser()


def _resolved(path: Path) -> Path:
    try:
        return path.resolve()
    except OSError:
        return path.expanduser().absolute()


def verify_repo(path: str | Path | None) -> dict[str, object]:
    if not path:
        return {"path": "", "valid": False, "reason": "missing path", "required_markers": [], "optional_markers": []}
    repo = Path(path).expanduser()
    required = [marker for marker in REQUIRED_REPO_MARKERS if (repo / marker).exists()]
    optional = [marker for marker in OPTIONAL_REPO_MARKERS if (repo / marker).exists()]
    if not repo.is_dir():
        return {"path": str(repo), "valid": False, "reason": "not a directory", "required_markers": required, "optional_markers": optional}
    missing_required = [marker for marker in REQUIRED_REPO_MARKERS if marker not in required]
    if missing_required:
        return {
            "path": str(repo),
            "valid": False,
            "reason": "missing required markers: " + ", ".join(missing_required),
            "required_markers": required,
            "optional_markers": optional,
        }
    if len(optional) < 2:
        return {
            "path": str(repo),
            "valid": False,
            "reason": "fewer than two strong optional markers present",
            "required_markers": required,
            "optional_markers": optional,
        }
    if (repo / ".git").exists():
        root = git_repo_root(repo)
        if root is None:
            return {
                "path": str(repo),
                "valid": False,
                "reason": "git rev-parse --show-toplevel failed",
                "required_markers": required,
                "optional_markers": optional,
            }
        if _resolved(root) != _resolved(repo):
            return {
                "path": str(repo),
                "valid": False,
                "reason": f"git root mismatch: {root}",
                "required_markers": required,
                "optional_markers": optional,
            }
    return {"path": str(repo), "valid": True, "reason": "ok", "required_markers": required, "optional_markers": optional}


def is_valid_repo(path: str | Path | None) -> bool:
    return bool(verify_repo(path)["valid"])


def default_repo_path(cwd: str | Path | None = None) -> Path:
    root = git_repo_root(cwd or Path.cwd())
    if root:
        return root
    candidate = Path(cwd).expanduser() if cwd else Path.cwd()
    return candidate


def is_valid_repo_legacy(path: str | Path | None) -> bool:
    if not path:
        return False
    repo = Path(path).expanduser()
    if not repo.is_dir():
        return False
    if not (repo / "smart_agent.py").is_file():
        return False
    if not (repo / "scripts" / "agent").is_file():
        return False
    return (repo / "pyproject.toml").is_file() or (repo / ".git").exists()


def repo_candidates(
    *,
    config: LauncherConfig | None = None,
    explicit_repo: str | Path | None = None,
    cwd: str | Path | None = None,
    home: str | Path | None = None,
) -> list[Path]:
    home_path = Path(home).expanduser() if home else Path.home()
    candidates: list[Path] = []
    if config and config.repo_path:
        candidates.append(Path(config.repo_path).expanduser())
    if config and config.last_known_good_repo_path:
        candidates.append(Path(config.last_known_good_repo_path).expanduser())
    if cwd:
        cwd_path = Path(cwd).expanduser()
        cwd_root = git_repo_root(cwd_path)
        candidates.append(cwd_root or cwd_path)
    candidates.extend(
        [
            home_path / "Documents" / "AI Super Agent",
            home_path / "Documents" / "ai-super-agent",
            home_path / "AI Super Agent",
            home_path / "ai-super-agent",
            home_path / "Desktop" / "AI Super Agent",
            home_path / "Desktop" / "ai-super-agent",
        ]
    )
    if explicit_repo:
        candidates.append(Path(explicit_repo).expanduser())

    seen: set[str] = set()
    unique: list[Path] = []
    for candidate in candidates:
        try:
            key = str(candidate.resolve())
        except OSError:
            key = str(candidate)
        if key not in seen:
            seen.add(key)
            unique.append(candidate)
    return unique


def valid_repo_candidates(**kwargs: object) -> list[Path]:
    return [path for path in repo_candidates(**kwargs) if is_valid_repo(path)]


def repo_candidate_statuses(**kwargs: object) -> list[dict[str, object]]:
    statuses: list[dict[str, object]] = []
    for path in repo_candidates(**kwargs):
        statuses.append(verify_repo(path))
    return statuses


def install_dir_in_path(install_dir: str | Path, env_path: str | None = None) -> bool:
    target = str(Path(install_dir).expanduser())
    path_value = env_path if env_path is not None else os.environ.get("PATH", "")
    return target in [str(Path(part).expanduser()) for part in path_value.split(os.pathsep) if part]


def executable(path: str | Path) -> bool:
    try:
        mode = Path(path).stat().st_mode
    except OSError:
        return False
    return bool(mode & stat.S_IXUSR)


def probe_python_version(executable_path: str | Path) -> tuple[int, int, int] | None:
    try:
        result = subprocess.run(
            [str(executable_path), "-c", "import sys; print('.'.join(map(str, sys.version_info[:3])))"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    if not result.stdout:
        return None
    parts = result.stdout.strip().split(".")
    if len(parts) < 2 or not all(part.isdigit() for part in parts[:2]):
        return None
    patch = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
    return int(parts[0]), int(parts[1]), patch


def python_candidate_paths(repo_path: str | Path | None) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    if repo_path:
        candidates.append((str(Path(repo_path).expanduser() / ".venv" / "bin" / "python"), "repo_venv"))
    for command in ("python3.12", "python3.11"):
        found = shutil.which(command)
        if found:
            candidates.append((found, command))
    if Path(CODEX_BUNDLED_PYTHON).exists():
        candidates.append((CODEX_BUNDLED_PYTHON, "codex_bundled_runtime"))
    found_python3 = shutil.which("python3")
    if found_python3:
        candidates.append((found_python3, "python3"))
    return candidates


def choose_python(repo_path: str | Path | None) -> PythonCandidate | None:
    first_bad: PythonCandidate | None = None
    seen: set[str] = set()
    for executable_path, source in python_candidate_paths(repo_path):
        if executable_path in seen:
            continue
        seen.add(executable_path)
        if not Path(executable_path).exists() and not shutil.which(executable_path):
            candidate = PythonCandidate(executable_path, None, source, False, "not found")
            first_bad = first_bad or candidate
            continue
        version = probe_python_version(executable_path)
        usable = version is not None and version >= (3, 11, 0)
        reason = "" if usable else "requires Python 3.11 or newer"
        candidate = PythonCandidate(executable_path, version, source, usable, reason)
        if usable:
            return candidate
        first_bad = first_bad or candidate
    return first_bad


def diagnose(
    *,
    config: LauncherConfig | None,
    config_path: str | Path | None = None,
    explicit_repo: str | Path | None = None,
    cwd: str | Path | None = None,
    home: str | Path | None = None,
    install_dir: str | Path | None = None,
    wrapper_path: str | Path | None = None,
    env_path: str | None = None,
) -> LauncherDiagnosis:
    resolved_config_path = Path(config_path) if config_path else config_path_for_home(home)
    valid_candidates = valid_repo_candidates(config=config, explicit_repo=explicit_repo, cwd=cwd, home=home)
    configured_repo = Path(explicit_repo or (config.repo_path if config else "")).expanduser() if (explicit_repo or config) else None
    repo_valid = is_valid_repo(configured_repo)
    if repo_valid and configured_repo:
        repo_path = str(configured_repo)
    elif len(valid_candidates) == 1:
        repo_path = str(valid_candidates[0])
    else:
        repo_path = None
    scripts_agent = Path(repo_path) / "scripts" / "agent" if repo_path else None
    install_path = Path(install_dir or (config.install_dir if config and config.install_dir else default_install_dir(home))).expanduser()
    python = choose_python(repo_path)
    findings: list[DiagnosticFinding] = []

    if config is None:
        findings.append(
            DiagnosticFinding(
                "missing_config",
                "launcher config is missing or unreadable",
                RepairLevel.LEVEL_1_AUTO_REPAIRABLE,
                "smartagent --repair",
            )
        )
    if not repo_valid:
        if len(valid_candidates) == 1:
            findings.append(
                DiagnosticFinding(
                    "repo_path_auto_repair",
                    f"configured repo path is invalid; one valid fallback was found: {valid_candidates[0]}",
                    RepairLevel.LEVEL_1_AUTO_REPAIRABLE,
                    "smartagent --repair",
                )
            )
        elif len(valid_candidates) > 1:
            findings.append(
                DiagnosticFinding(
                    "multiple_repo_candidates",
                    "multiple valid repo candidates found; choose one explicitly",
                    RepairLevel.LEVEL_2_COMMAND_REQUIRED,
                    'smartagent --repair-path --repo "/path/to/AI Super Agent"',
                )
            )
        else:
            findings.append(
                DiagnosticFinding(
                    "repo_missing",
                    "configured repo path is invalid and no safe fallback repo was found",
                    RepairLevel.NOT_REPAIRABLE_BY_LAUNCHER,
                    'scripts/install-smartagent-launcher --repo "/path/to/AI Super Agent" --update',
                )
            )

    if python is None or not python.usable:
        findings.append(
            DiagnosticFinding(
                "python_missing",
                "no Python 3.11+ runtime was found",
                RepairLevel.LEVEL_3_MANUAL_REQUIRED,
                "brew install python@3.12",
            )
        )
    elif config and config.last_known_good_python != python.executable:
        findings.append(
            DiagnosticFinding(
                "python_update",
                f"selected Python {python.executable} from {python.source}",
                RepairLevel.LEVEL_1_AUTO_REPAIRABLE,
                "smartagent --repair",
            )
        )

    if repo_path and not (Path(repo_path) / ".venv" / "bin" / "python").exists():
        findings.append(
            DiagnosticFinding(
                "venv_missing",
                ".venv is missing; launcher can use another Python but venv repair is explicit",
                RepairLevel.LEVEL_2_COMMAND_REQUIRED,
                "smartagent --repair-venv",
            )
        )

    scripts_executable = bool(scripts_agent and scripts_agent.exists() and executable(scripts_agent))
    if scripts_agent and scripts_agent.exists() and not scripts_executable:
        findings.append(
            DiagnosticFinding(
                "scripts_agent_not_executable",
                "scripts/agent exists but is not executable",
                RepairLevel.LEVEL_1_AUTO_REPAIRABLE,
                "smartagent --repair",
            )
        )
    if repo_path and not scripts_agent.exists():
        findings.append(
            DiagnosticFinding(
                "scripts_agent_missing",
                "scripts/agent is missing; repo appears damaged",
                RepairLevel.NOT_REPAIRABLE_BY_LAUNCHER,
                "git status --short",
            )
        )

    wrapper_executable = bool(wrapper_path and Path(wrapper_path).exists() and executable(wrapper_path))
    if wrapper_path and Path(wrapper_path).exists() and not wrapper_executable:
        findings.append(
            DiagnosticFinding(
                "wrapper_not_executable",
                "launcher wrapper exists but is not executable",
                RepairLevel.LEVEL_1_AUTO_REPAIRABLE,
                "smartagent --repair",
            )
        )

    in_path = install_dir_in_path(install_path, env_path=env_path)
    if not in_path:
        findings.append(
            DiagnosticFinding(
                "install_dir_not_in_path",
                f"{install_path} is not in PATH",
                RepairLevel.LEVEL_2_COMMAND_REQUIRED,
                "smartagent --print-path-help",
            )
        )

    return LauncherDiagnosis(
        config_path=str(resolved_config_path),
        repo_path=repo_path,
        repo_valid=bool(repo_path and is_valid_repo(repo_path)),
        repo_candidates=tuple(str(path) for path in valid_candidates),
        python=python,
        scripts_agent_executable=scripts_executable,
        wrapper_executable=wrapper_executable,
        install_dir_in_path=in_path,
        findings=tuple(findings),
    )


def make_default_config(repo_path: str | Path, *, alias: str = "smartagent", install_dir: str | Path | None = None) -> LauncherConfig:
    repo = str(Path(repo_path).expanduser())
    verification = verify_repo(repo)
    return LauncherConfig(
        repo_path=repo,
        alias=alias,
        install_dir=str(Path(install_dir).expanduser()) if install_dir else str(default_install_dir()),
        created_at=utc_now_iso(),
        updated_at=utc_now_iso(),
        launcher_version=LAUNCHER_VERSION,
        last_known_good_repo_path=repo,
        last_repo_verification_status=str(verification["reason"] if verification["valid"] else "invalid: " + str(verification["reason"])),
    )


def format_path_help(install_dir: str | Path) -> str:
    directory = str(Path(install_dir).expanduser())
    if directory == str(Path.home() / "bin"):
        export_line = 'export PATH="$HOME/bin:$PATH"'
    else:
        export_line = f'export PATH="{directory}:$PATH"'
    return "\n".join(
        [
            "Launcher install directory is not in PATH.",
            "",
            "For zsh, run:",
            f"  echo '{export_line}' >> ~/.zshrc",
            "  source ~/.zshrc",
            "",
            "The installer will not edit shell profiles unless --write-shell-profile is passed.",
        ]
    )
