from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from .diagnostics import (
    default_install_dir,
    default_repo_path,
    diagnose,
    format_path_help,
    install_dir_in_path,
    load_config,
    make_default_config,
    repo_candidate_statuses,
    save_config,
    validate_alias,
    verify_repo,
)
from .generator import generate_launcher_script, launcher_path
from .models import LAUNCHER_VERSION, LauncherConfig, config_path_for_home
from .repair import repair_venv, run_level1_repairs, write_shell_profile_path


def _print_json(data: object) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def _diagnosis_dict(diagnosis: object) -> dict[str, object]:
    from dataclasses import asdict

    return asdict(diagnosis)


def _load_or_default(config_path: Path, repo_path: str | Path | None = None, alias: str = "smartagent", install_dir: str | Path | None = None) -> LauncherConfig | None:
    config = load_config(config_path)
    if config:
        return config
    if repo_path:
        return make_default_config(repo_path, alias=alias, install_dir=install_dir)
    return None


def launch_agent(config: LauncherConfig, args: list[str]) -> int:
    repo = Path(config.repo_path).expanduser()
    scripts_agent = repo / "scripts" / "agent"
    if not scripts_agent.exists():
        print(f"scripts/agent missing at {scripts_agent}", file=sys.stderr)
        return 2
    launch_args = ["--interactive"] if not args else args
    result = subprocess.run([str(scripts_agent), *launch_args], cwd=repo, check=False)
    return int(result.returncode)


def _repo_status_payload(config: LauncherConfig | None) -> dict[str, object]:
    if config is None:
        return {"configured_repo_path": "", "valid": False, "reason": "launcher config missing"}
    status = verify_repo(config.repo_path)
    return {
        "configured_repo_path": config.repo_path,
        "last_known_good_repo_path": config.last_known_good_repo_path,
        "valid": status["valid"],
        "reason": status["reason"],
        "required_markers": status["required_markers"],
        "optional_markers": status["optional_markers"],
    }


def _set_repo_config(config: LauncherConfig | None, config_path: Path, repo_path: str, *, alias: str = "smartagent", install_dir: str | Path | None = None) -> int:
    status = verify_repo(repo_path)
    if not status["valid"]:
        _print_json({"set_repo": {"ok": False, "path": repo_path, "reason": status["reason"]}})
        return 2
    existing = config or make_default_config(repo_path, alias=alias, install_dir=install_dir)
    updated = existing.with_updates(
        repo_path=str(Path(repo_path).expanduser()),
        last_known_good_repo_path=str(Path(repo_path).expanduser()),
        last_repo_verification_status=str(status["reason"]),
    )
    save_config(updated, config_path)
    _print_json({"set_repo": {"ok": True, "path": updated.repo_path, "reason": status["reason"]}})
    return 0


def _repair_path_requires_choice(diagnosis: object, *, explicit_repo: str | None = None) -> dict[str, object] | None:
    candidates = list(getattr(diagnosis, "repo_candidates", ()))
    if explicit_repo:
        return None
    if len(candidates) > 1:
        return {
            "ok": False,
            "reason": "multiple valid repo candidates found; choose one explicitly",
            "candidates": candidates,
            "next_command": 'smartagent --set-repo "/path/to/repo"',
        }
    if not candidates and not bool(getattr(diagnosis, "repo_valid", False)):
        return {
            "ok": False,
            "reason": "no valid repo candidates found in safe likely locations",
            "candidates": [],
            "clone_setup": [
                "git clone https://github.com/doncazper/ai-super-agent.git",
                "cd ai-super-agent",
                "./scripts/install-smartagent-launcher --alias smartagent",
            ],
        }
    return None


def launcher_main(argv: list[str] | None = None) -> int:
    raw = list(argv if argv is not None else sys.argv[1:])
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--config", default=str(config_path_for_home()))
    parser.add_argument("--wrapper", default="")
    known, remaining = parser.parse_known_args(raw)
    config_path = Path(known.config).expanduser()
    wrapper_path = Path(known.wrapper).expanduser() if known.wrapper else None
    config = load_config(config_path)

    if remaining == ["--launcher-version"]:
        print(LAUNCHER_VERSION)
        return 0
    if remaining == ["--repo"]:
        if config and config.repo_path:
            print(config.repo_path)
            return 0
        print("launcher config missing repo_path", file=sys.stderr)
        return 2
    if remaining == ["--repo-status"]:
        _print_json(_repo_status_payload(config))
        return 0 if config and verify_repo(config.repo_path)["valid"] else 1
    if remaining == ["--find-repos"]:
        statuses = repo_candidate_statuses(config=config, cwd=Path.cwd())
        _print_json({"candidates": statuses, "scanned": "safe_likely_locations_only"})
        return 0
    if remaining and remaining[0] == "--set-repo":
        if len(remaining) != 2:
            print('usage: smartagent --set-repo "/path/to/repo"', file=sys.stderr)
            return 2
        return _set_repo_config(config, config_path, remaining[1])
    if remaining == ["--uninstall-help"]:
        alias = config.alias if config else "smartagent"
        install_dir = config.install_dir if config else str(default_install_dir())
        print(f"To uninstall: scripts/install-smartagent-launcher --alias {alias} --install-dir {install_dir} --uninstall")
        return 0
    if remaining and remaining[0] in {
        "--doctor",
        "--repair",
        "--repair-and-launch",
        "--repair-venv",
        "--repair-path",
        "--repair-wrapper",
        "--print-path-help",
    }:
        action = remaining[0]
        explicit_repo = None
        if action == "--repair-path":
            repair_parser = argparse.ArgumentParser(prog="smartagent --repair-path")
            repair_parser.add_argument("--repo", default="")
            try:
                repair_args = repair_parser.parse_args(remaining[1:])
            except SystemExit as exc:
                return int(exc.code)
            explicit_repo = repair_args.repo or None
        diagnosis = diagnose(config=config, config_path=config_path, explicit_repo=explicit_repo, wrapper_path=wrapper_path, cwd=Path.cwd())
        if action == "--doctor":
            _print_json(_diagnosis_dict(diagnosis))
            return 0 if diagnosis.ok else 1
        if action == "--print-path-help":
            install_dir = config.install_dir if config else str(default_install_dir())
            print(format_path_help(install_dir))
            return 0
        if action == "--repair":
            result = run_level1_repairs(diagnosis, config=config, config_path=config_path, wrapper_path=wrapper_path)
            _print_json({"repair": result.__dict__})
            return 0 if result.ok else 2
        if action == "--repair-path":
            blocked = _repair_path_requires_choice(diagnosis, explicit_repo=explicit_repo)
            if blocked:
                _print_json({"repair_path": blocked})
                return 2
            result = run_level1_repairs(diagnosis, config=config, config_path=config_path, wrapper_path=wrapper_path)
            _print_json({"repair_path": result.__dict__})
            return 0 if result.ok else 2
        if action == "--repair-wrapper":
            print("Run: scripts/install-smartagent-launcher --repair-wrapper --update")
            return 1
        if action == "--repair-venv":
            repo_path = diagnosis.repo_path or (config.repo_path if config else "")
            if not repo_path:
                print("repo path is unavailable; repair repo path first", file=sys.stderr)
                return 2
            result = repair_venv(repo_path)
            _print_json({"repair_venv": result.__dict__})
            return 0 if result.ok else 2
        if action == "--repair-and-launch":
            result = run_level1_repairs(diagnosis, config=config, config_path=config_path, wrapper_path=wrapper_path)
            if not result.ok:
                _print_json({"repair": result.__dict__})
                return 2
            repaired_config = load_config(config_path) or config
            if repaired_config is None:
                print("launcher config unavailable after repair", file=sys.stderr)
                return 2
            refreshed = diagnose(config=repaired_config, config_path=config_path, wrapper_path=wrapper_path, cwd=Path.cwd())
            if any(finding.code in {"venv_missing"} for finding in refreshed.findings):
                venv_result = repair_venv(repaired_config.repo_path)
                if not venv_result.ok:
                    _print_json({"repair": result.__dict__, "repair_venv": venv_result.__dict__})
                    return 2
            return launch_agent(repaired_config, [])

    if config is None:
        print("Launcher config is missing. Run: scripts/install-smartagent-launcher --update", file=sys.stderr)
        return 2
    diagnosis = diagnose(config=config, config_path=config_path, wrapper_path=wrapper_path, cwd=Path.cwd())
    level1_needed = [finding for finding in diagnosis.findings if finding.repair_level.value == "level_1_auto_repairable"]
    if level1_needed and config.auto_repair_safe_enabled:
        run_level1_repairs(diagnosis, config=config, config_path=config_path, wrapper_path=wrapper_path)
        config = load_config(config_path) or config
        diagnosis = diagnose(config=config, config_path=config_path, wrapper_path=wrapper_path, cwd=Path.cwd())
    if not diagnosis.ok:
        for finding in diagnosis.findings:
            print(f"{finding.repair_level.value}: {finding.message}", file=sys.stderr)
            if finding.next_command:
                print(f"next: {finding.next_command}", file=sys.stderr)
        return 2
    return launch_agent(config, remaining)


def installer_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install or repair the AI Super Agent global launcher.")
    parser.add_argument("--alias", default="smartagent")
    parser.add_argument("--install-dir", default=str(default_install_dir()))
    parser.add_argument("--repo", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--doctor", action="store_true")
    parser.add_argument("--repair", action="store_true")
    parser.add_argument("--repair-and-launch", action="store_true")
    parser.add_argument("--repair-path", action="store_true")
    parser.add_argument("--repair-wrapper", action="store_true")
    parser.add_argument("--repair-python", action="store_true")
    parser.add_argument("--repair-venv", action="store_true")
    parser.add_argument("--write-shell-profile", action="store_true")
    parser.add_argument("--print-path-help", action="store_true")
    args = parser.parse_args(argv)
    repo_arg = args.repo or str(default_repo_path())

    valid_alias, alias_error = validate_alias(args.alias)
    if not valid_alias:
        print(alias_error, file=sys.stderr)
        return 2

    install_dir = Path(args.install_dir).expanduser()
    wrapper = launcher_path(install_dir, args.alias)
    config_path = config_path_for_home()
    repo_verification = verify_repo(repo_arg)
    allow_invalid_repo_for_diagnostics = args.doctor or args.repair or args.repair_python or (args.repair_path and not args.repo)
    if not repo_verification["valid"] and not args.uninstall and not args.print_path_help and not allow_invalid_repo_for_diagnostics:
        print(f"invalid repo path: {repo_arg}", file=sys.stderr)
        print(f"reason: {repo_verification['reason']}", file=sys.stderr)
        print("Clone and install:", file=sys.stderr)
        print("  git clone https://github.com/doncazper/ai-super-agent.git", file=sys.stderr)
        print("  cd ai-super-agent", file=sys.stderr)
        print("  ./scripts/install-smartagent-launcher --alias smartagent", file=sys.stderr)
        return 2
    config = _load_or_default(config_path, repo_path=repo_arg, alias=args.alias, install_dir=install_dir)
    diagnosis = diagnose(
        config=config,
        config_path=config_path,
        explicit_repo=args.repo if args.repair_path else None,
        install_dir=install_dir,
        wrapper_path=wrapper,
        cwd=Path.cwd(),
    )

    if args.print_path_help:
        print(format_path_help(install_dir))
        return 0

    if args.doctor:
        _print_json(_diagnosis_dict(diagnosis))
        return 0 if diagnosis.ok else 1

    if args.repair_path and args.repo:
        return _set_repo_config(config, config_path, args.repo, alias=args.alias, install_dir=install_dir)

    if args.uninstall:
        if args.dry_run:
            print(f"would remove {wrapper}")
            return 0
        if wrapper.exists():
            wrapper.unlink()
            print(f"removed {wrapper}")
        else:
            print(f"launcher not found: {wrapper}")
        return 0

    if args.repair_venv:
        result = repair_venv(repo_arg, dry_run=args.dry_run)
        _print_json({"repair_venv": result.__dict__})
        return 0 if result.ok else 2

    if args.repair_wrapper:
        script = generate_launcher_script(repo_path=repo_arg, config_path=config_path)
        if wrapper.exists() and not args.update:
            print("--repair-wrapper requires --update when wrapper already exists", file=sys.stderr)
            return 2
        if args.dry_run:
            print(f"would rewrite {wrapper}")
            return 0
        install_dir.mkdir(parents=True, exist_ok=True)
        wrapper.write_text(script, encoding="utf-8")
        wrapper.chmod(wrapper.stat().st_mode | 0o755)
        save_config(make_default_config(repo_arg, alias=args.alias, install_dir=install_dir), config_path)
        print(f"rewrote launcher wrapper {wrapper}")
        return 0

    if args.repair or args.repair_and_launch or args.repair_path or args.repair_python:
        result = run_level1_repairs(
            diagnosis,
            config=config,
            config_path=config_path,
            alias=args.alias,
            install_dir=install_dir,
            wrapper_path=wrapper,
            dry_run=args.dry_run,
        )
        _print_json({"repair": result.__dict__})
        if not result.ok:
            return 2
        if args.repair_and_launch and not args.dry_run:
            repaired = load_config(config_path)
            if repaired is None:
                print("launcher config unavailable after repair", file=sys.stderr)
                return 2
            return launch_agent(repaired, [])
        return 0

    if args.write_shell_profile:
        result = write_shell_profile_path(Path.home() / ".zshrc", install_dir, dry_run=args.dry_run)
        _print_json({"shell_profile": result.__dict__})
        if not result.ok:
            return 2

    if shutil.which(args.alias) and not args.update and not wrapper.exists():
        print(f"alias conflicts with existing command in PATH: {args.alias}; pass --update to overwrite", file=sys.stderr)
        return 2

    script = generate_launcher_script(repo_path=repo_arg, config_path=config_path)
    if args.dry_run:
        print(f"would write {wrapper}")
        print(f"would write {config_path}")
        if not install_dir_in_path(install_dir):
            print(format_path_help(install_dir))
        return 0

    install_dir.mkdir(parents=True, exist_ok=True)
    wrapper.write_text(script, encoding="utf-8")
    wrapper.chmod(wrapper.stat().st_mode | 0o755)
    save_config(make_default_config(repo_arg, alias=args.alias, install_dir=install_dir), config_path)
    print(f"installed {args.alias} at {wrapper}")
    if not install_dir_in_path(install_dir):
        print(format_path_help(install_dir))
    return 0


def main(argv: list[str] | None = None) -> int:
    return launcher_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
