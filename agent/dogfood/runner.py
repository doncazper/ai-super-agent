from __future__ import annotations

import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from agent.dogfood.models import DogfoodCommand
from agent.dogfood.suites import load_suite
from agent.session_logs.recorder import SessionRecorder


@dataclass(frozen=True)
class CommandExecution:
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int


Executor = Callable[[list[str], DogfoodCommand], CommandExecution]


def run_suite(
    suite_id: str,
    *,
    project_root: str | Path = ".",
    suites_path: str | Path = "dogfood_suites",
    dry_run: bool = False,
    use_session: bool = False,
    timeout_seconds: int = 120,
    executor: Executor | None = None,
    session_recorder: SessionRecorder | None = None,
) -> dict[str, Any]:
    root = Path(project_root)
    suite = load_suite(suite_id, project_root=root, suites_path=suites_path)
    results: list[dict[str, Any]] = []
    failures = 0
    skipped = 0
    session = session_recorder or SessionRecorder(project_root=root)
    if use_session and session.store.get_active() is None:
        raise ValueError("dogfood --session requires an active session; run `python smart_agent.py session start --name dogfood` first")
    for command in suite.commands:
        try:
            args = parse_agent_command(command.command)
        except ValueError as exc:
            failures += 1
            results.append(_result(command, "failed", 2, "", str(exc), 0))
            continue
        if dry_run:
            skipped += 1
            results.append(
                {
                    "id": command.id,
                    "status": "skipped",
                    "command": command.command,
                    "parsed_args": args,
                    "expected_behavior": command.expected_behavior,
                    "reason": "dry_run",
                }
            )
            continue
        if use_session:
            started = time.monotonic()
            record = session.run_command(args, timeout_seconds=timeout_seconds)
            duration_ms = int((time.monotonic() - started) * 1000)
            execution = CommandExecution(
                exit_code=record.exit_code,
                stdout=record.stdout_preview,
                stderr=record.stderr_preview,
                duration_ms=duration_ms,
            )
        else:
            execution = executor(args, command) if executor else _execute(root, args, timeout_seconds)
        status = "passed" if execution.exit_code in command.expected_exit_codes else "failed"
        if status == "failed":
            failures += 1
        results.append(_result(command, status, execution.exit_code, execution.stdout, execution.stderr, execution.duration_ms))
    return {
        "suite": {
            "suite_id": suite.suite_id,
            "name": suite.name,
            "risk_level": suite.risk_level,
            "requires_live_lmstudio": suite.requires_live_lmstudio,
            "requires_web": suite.requires_web,
            "requires_personal_data": suite.requires_personal_data,
            "default_enabled": suite.default_enabled,
        },
        "dry_run": dry_run,
        "session": use_session,
        "summary": {
            "total": len(suite.commands),
            "passed": len(suite.commands) - failures - skipped,
            "failed": failures,
            "skipped": skipped,
        },
        "results": results,
        "status": "ok" if failures == 0 else "failed",
    }


def parse_agent_command(command: str) -> list[str]:
    parts = shlex.split(command)
    if len(parts) < 2:
        raise ValueError("dogfood commands must invoke python smart_agent.py")
    executable = Path(parts[0]).name
    if executable not in {"python", "python3"}:
        raise ValueError("dogfood commands may only invoke python smart_agent.py")
    script = Path(parts[1]).name
    if script != "smart_agent.py":
        raise ValueError("dogfood commands may only invoke smart_agent.py")
    return parts[2:]


def _execute(project_root: Path, args: list[str], timeout_seconds: int) -> CommandExecution:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            [sys.executable, str(project_root / "smart_agent.py"), *args],
            cwd=project_root,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_seconds,
        )
        return CommandExecution(
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            duration_ms=int((time.monotonic() - started) * 1000),
        )
    except subprocess.TimeoutExpired as exc:
        return CommandExecution(
            exit_code=124,
            stdout=exc.stdout or "",
            stderr=(exc.stderr or "") + f"\nCommand timed out after {timeout_seconds}s",
            duration_ms=int((time.monotonic() - started) * 1000),
        )


def _preview(text: str, limit: int = 2000) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[truncated]"


def _result(command: DogfoodCommand, status: str, exit_code: int, stdout: str, stderr: str, duration_ms: int) -> dict[str, Any]:
    return {
        "id": command.id,
        "status": status,
        "command": command.command,
        "exit_code": exit_code,
        "expected_exit_codes": list(command.expected_exit_codes),
        "duration_ms": duration_ms,
        "stdout_preview": _preview(stdout),
        "stderr_preview": _preview(stderr),
        "expected_behavior": command.expected_behavior,
        "failure_signals": command.failure_signals,
        "tags": list(command.tags),
    }
