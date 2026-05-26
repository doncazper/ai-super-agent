from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path
from typing import Callable, Sequence

from .diagnostics import choose_python, diagnose, format_path_help, is_valid_repo, make_default_config, save_config, verify_repo
from .models import LauncherConfig, LauncherDiagnosis, RepairLevel, RepairResult


Runner = Callable[..., subprocess.CompletedProcess[str]]


def _chmod_user_exec(path: Path) -> None:
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR)


def run_level1_repairs(
    diagnosis: LauncherDiagnosis,
    *,
    config: LauncherConfig | None,
    config_path: str | Path,
    alias: str = "smartagent",
    install_dir: str | Path | None = None,
    wrapper_path: str | Path | None = None,
    dry_run: bool = False,
) -> RepairResult:
    changed: list[str] = []
    skipped: list[str] = []
    errors: list[str] = []
    next_commands: list[str] = []

    repo_path = diagnosis.repo_path
    if not repo_path and len(diagnosis.repo_candidates) == 1:
        repo_path = diagnosis.repo_candidates[0]
    if repo_path and is_valid_repo(repo_path):
        selected_python = choose_python(repo_path)
        existing = config or make_default_config(repo_path, alias=alias, install_dir=install_dir)
        updated = existing.with_updates(
            repo_path=repo_path,
            alias=alias or existing.alias,
            install_dir=str(install_dir or existing.install_dir),
            last_known_good_repo_path=repo_path,
            last_repo_verification_status=str(verify_repo(repo_path)["reason"]),
            last_known_good_python=selected_python.executable if selected_python and selected_python.usable else existing.last_known_good_python,
            last_repair_result="level1_ok",
        )
        if dry_run:
            changed.append(f"would update launcher config {config_path}")
        else:
            save_config(updated, config_path)
            changed.append(f"updated launcher config {config_path}")
    else:
        skipped.append("repo path could not be repaired automatically")

    if repo_path:
        scripts_agent = Path(repo_path) / "scripts" / "agent"
        if scripts_agent.exists() and not os.access(scripts_agent, os.X_OK):
            if dry_run:
                changed.append(f"would chmod +x {scripts_agent}")
            else:
                _chmod_user_exec(scripts_agent)
                changed.append(f"chmod +x {scripts_agent}")
        elif not scripts_agent.exists():
            errors.append("scripts/agent is missing")

    if wrapper_path:
        wrapper = Path(wrapper_path)
        if wrapper.exists() and not os.access(wrapper, os.X_OK):
            if dry_run:
                changed.append(f"would chmod +x {wrapper}")
            else:
                _chmod_user_exec(wrapper)
                changed.append(f"chmod +x {wrapper}")

    for finding in diagnosis.findings:
        if finding.repair_level is RepairLevel.LEVEL_2_COMMAND_REQUIRED and finding.next_command:
            next_commands.append(finding.next_command)
        if finding.repair_level is RepairLevel.LEVEL_3_MANUAL_REQUIRED and finding.next_command:
            next_commands.append(f"manual: {finding.next_command}")

    return RepairResult(tuple(changed), tuple(skipped), tuple(errors), tuple(dict.fromkeys(next_commands)))


def repair_venv(
    repo_path: str | Path,
    *,
    dry_run: bool = False,
    runner: Runner = subprocess.run,
) -> RepairResult:
    repo = Path(repo_path).expanduser()
    venv_dir = repo / ".venv"
    venv_python = venv_dir / "bin" / "python"
    if venv_dir.exists() and not venv_python.exists():
        return RepairResult(
            (),
            ("existing .venv appears broken and will not be deleted automatically",),
            (),
            (
                f"cd {repo}",
                "mv .venv .venv.backup",
                "python3.12 -m venv .venv",
                "source .venv/bin/activate",
                "python -m pip install -e '.[dev]'",
            ),
        )
    if venv_python.exists():
        candidate = choose_python(repo)
        if candidate and candidate.source == "repo_venv" and candidate.usable:
            return RepairResult(("existing .venv is already valid",), (), (), ())
        return RepairResult(
            (),
            ("existing .venv appears broken and will not be deleted automatically",),
            (),
            (
                f"cd {repo}",
                "mv .venv .venv.backup",
                "python3.12 -m venv .venv",
                "source .venv/bin/activate",
                "python -m pip install -e '.[dev]'",
            ),
        )

    base_python = choose_python(None)
    if base_python is None or not base_python.usable:
        return RepairResult((), (), ("no Python 3.11+ available to create .venv",), ("brew install python@3.12",))

    commands: list[Sequence[str]] = [
        [base_python.executable, "-m", "venv", str(venv_dir)],
        [str(venv_python), "-m", "pip", "install", "-e", ".[dev]"],
        [str(repo / "scripts" / "agent"), "doctor"],
    ]
    if dry_run:
        return RepairResult(tuple("would run: " + " ".join(command) for command in commands), (), (), ())

    for command in commands:
        result = runner(command, cwd=repo, check=False, text=True, capture_output=True, timeout=300)
        if result.returncode != 0:
            return RepairResult((), (), (f"command failed: {' '.join(command)}",), ("smartagent --repair-venv",))
    return RepairResult(("created .venv and installed editable dev package",), (), (), ())


def write_shell_profile_path(profile_path: str | Path, install_dir: str | Path, *, dry_run: bool = False) -> RepairResult:
    profile = Path(profile_path).expanduser()
    directory = str(Path(install_dir).expanduser())
    export_line = 'export PATH="$HOME/bin:$PATH"' if directory == str(Path.home() / "bin") else f'export PATH="{directory}:$PATH"'
    if dry_run:
        return RepairResult((f"would ensure {export_line} in {profile}",), (), (), ())
    existing = profile.read_text(encoding="utf-8") if profile.exists() else ""
    if export_line in existing:
        return RepairResult((f"{profile} already contains launcher PATH entry",), (), (), ())
    profile.parent.mkdir(parents=True, exist_ok=True)
    suffix = "\n" if existing and not existing.endswith("\n") else ""
    profile.write_text(existing + suffix + export_line + "\n", encoding="utf-8")
    return RepairResult((f"updated {profile}",), (), (), ())


def repair_and_launch_plan(config: LauncherConfig | None, *, config_path: str | Path, wrapper_path: str | Path | None = None) -> tuple[LauncherDiagnosis, RepairResult]:
    diagnosis = diagnose(config=config, config_path=config_path, wrapper_path=wrapper_path)
    result = run_level1_repairs(diagnosis, config=config, config_path=config_path, wrapper_path=wrapper_path)
    return diagnosis, result


def path_help_result(install_dir: str | Path) -> RepairResult:
    return RepairResult((), (), (), (format_path_help(install_dir),))
