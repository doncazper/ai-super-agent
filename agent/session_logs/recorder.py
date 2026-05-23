from __future__ import annotations

import os
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from agent.config.runtime import RuntimeConfig, RuntimeConfigError
from agent.session_logs.models import CommandRecord, SessionRecord, new_command_id, utc_now_iso
from agent.session_logs.redaction import redact_args, redact_text
from agent.session_logs.replay import format_replay
from agent.session_logs.reviewer import audit_ids_from_log, detect_tool_calls, extract_audit_ids
from agent.session_logs.store import SessionLogStore

MAX_PREVIEW_CHARS = 4000


class SessionRecorder:
    def __init__(self, store: SessionLogStore | None = None, *, project_root: str | Path = ".") -> None:
        self.project_root = Path(project_root)
        self.store = store or SessionLogStore(project_root=self.project_root)

    def start(self, *, name: str, tags: list[str] | None = None) -> SessionRecord:
        session = SessionRecord.start(
            name=name,
            git_commit=_git_value(self.project_root, ["rev-parse", "--short", "HEAD"]),
            branch=_git_value(self.project_root, ["branch", "--show-current"]),
            model=_runtime_value("lmstudio_model"),
            base_url=_runtime_value("lmstudio_base_url"),
            config_summary=_config_summary(),
            tags=tags,
        )
        return self.store.start(session)

    def status(self) -> dict[str, Any]:
        active = self.store.get_active()
        sessions = self.store.list_sessions()
        return {
            "active": active.to_dict() if active else None,
            "session_count": len(sessions),
            "storage_path": str(self.store.root),
        }

    def end(self) -> SessionRecord:
        return self.store.end_active()

    def list(self) -> list[dict[str, Any]]:
        return [session.to_dict() for session in self.store.list_sessions()]

    def show(self, session_id: str) -> dict[str, Any]:
        return self.store.export(session_id)

    def last(self) -> dict[str, Any] | None:
        session = self.store.last_session()
        return session.to_dict() if session else None

    def replay(self, session_id: str) -> str:
        session = self.store.get(session_id)
        if session is None:
            raise ValueError("session not found")
        return format_replay(session, self.store.load_commands(session_id), self.store.load_feedback(session_id))

    def export(self, session_id: str) -> dict[str, Any]:
        return self.store.export(session_id)

    def run_command(
        self,
        args: list[str],
        *,
        unsafe_raw: bool = False,
        timeout_seconds: int = 120,
        agent_script: str | Path | None = None,
        python_executable: str | None = None,
    ) -> CommandRecord:
        if not args:
            raise ValueError("session run requires command arguments after --")
        if args[0] == "session":
            raise ValueError("nested session commands are not supported")
        session = self.store.get_active()
        if session is None:
            raise ValueError("no active session")
        script = Path(agent_script) if agent_script else self.project_root / "smart_agent.py"
        executable = python_executable or sys.executable
        command = [executable, str(script), *args]
        command_line = shlex.join(["python", "smart_agent.py", *args])
        sanitized_command_line = shlex.join(["python", "smart_agent.py", *redact_args(args)])
        started = time.monotonic()
        timestamp = utc_now_iso()
        try:
            completed = subprocess.run(
                command,
                cwd=self.project_root,
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
                check=False,
            )
            exit_code = completed.returncode
            stdout = completed.stdout
            stderr = completed.stderr
        except subprocess.TimeoutExpired as exc:
            exit_code = 124
            stdout = exc.stdout or ""
            stderr = (exc.stderr or "") + f"\nCommand timed out after {timeout_seconds}s"
        duration_ms = int((time.monotonic() - started) * 1000)
        stdout_for_log = stdout if unsafe_raw else redact_text(stdout)
        stderr_for_log = stderr if unsafe_raw else redact_text(stderr)
        full_output = f"$ {sanitized_command_line}\n\n[stdout]\n{stdout_for_log}\n\n[stderr]\n{stderr_for_log}\n"
        linked_audit_ids = sorted(
            set(
                extract_audit_ids(stdout + "\n" + stderr)
                + audit_ids_from_log(Path(_runtime_value("audit_log_path") or self.project_root / "logs" / "audit.jsonl"))
            )
        )
        record = CommandRecord(
            command_id=new_command_id(),
            timestamp=timestamp,
            command_line=command_line if unsafe_raw else sanitized_command_line,
            sanitized_command_line=sanitized_command_line,
            exit_code=exit_code,
            duration_ms=duration_ms,
            stdout_preview=_preview(stdout_for_log),
            stderr_preview=_preview(stderr_for_log),
            tool_calls_detected=detect_tool_calls(stdout + "\n" + stderr),
            linked_audit_ids=linked_audit_ids,
            suspected_bug=exit_code != 0,
        )
        if unsafe_raw:
            session.redaction_status = "unredacted"
            self.store._write_session(session)
        return self.store.append_command(session.session_id, record, full_output=full_output)


def _preview(text: str) -> str:
    if len(text) <= MAX_PREVIEW_CHARS:
        return text
    return text[:MAX_PREVIEW_CHARS] + "\n...[truncated]"


def _git_value(project_root: Path, args: list[str]) -> str:
    try:
        result = subprocess.run(["git", *args], cwd=project_root, text=True, capture_output=True, check=False, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    return result.stdout.strip() or "unknown"


def _runtime_value(name: str) -> str:
    try:
        runtime = RuntimeConfig.from_env()
    except RuntimeConfigError:
        return os.environ.get(name.upper(), "")
    return str(getattr(runtime, name, ""))


def _config_summary() -> dict[str, Any]:
    try:
        runtime = RuntimeConfig.from_env()
    except RuntimeConfigError as exc:
        return {"config_loaded": False, "error": redact_text(str(exc))}
    return {
        "config_loaded": True,
        "lmstudio_model_set": bool(runtime.lmstudio_model),
        "lmstudio_base_url_set": bool(runtime.lmstudio_base_url),
        "audit_log_path": redact_text(str(runtime.audit_log_path)),
        "capabilities_path": redact_text(str(runtime.capabilities_path)),
    }
