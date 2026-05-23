from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent.session_logs.models import CommandRecord, FeedbackRecord, SessionRecord, utc_now_iso


class SessionLogStore:
    def __init__(self, root: str | Path = "reports/sessions", *, project_root: str | Path = ".") -> None:
        self.project_root = Path(project_root)
        self.root = Path(root)
        if not self.root.is_absolute():
            self.root = self.project_root / self.root
        self.root.mkdir(parents=True, exist_ok=True)

    @property
    def active_path(self) -> Path:
        return self.root / "active_session.json"

    def session_dir(self, session_id: str) -> Path:
        return self.root / session_id

    def session_path(self, session_id: str) -> Path:
        return self.session_dir(session_id) / "session.json"

    def commands_path(self, session_id: str) -> Path:
        return self.session_dir(session_id) / "commands.jsonl"

    def feedback_path(self, session_id: str) -> Path:
        return self.session_dir(session_id) / "feedback.jsonl"

    def outputs_dir(self, session_id: str) -> Path:
        return self.session_dir(session_id) / "outputs"

    def start(self, session: SessionRecord) -> SessionRecord:
        if self.active_session_id():
            raise ValueError("a session is already active")
        self.session_dir(session.session_id).mkdir(parents=True, exist_ok=True)
        self.outputs_dir(session.session_id).mkdir(exist_ok=True)
        self._write_session(session)
        self.active_path.write_text(json.dumps({"session_id": session.session_id}, indent=2), encoding="utf-8")
        return session

    def end_active(self) -> SessionRecord:
        session = self.get_active()
        if session is None:
            raise ValueError("no active session")
        session.status = "ended"
        session.ended_at = utc_now_iso()
        self._write_session(session)
        if self.active_path.exists():
            self.active_path.unlink()
        return session

    def active_session_id(self) -> str | None:
        if not self.active_path.exists():
            return None
        try:
            data = json.loads(self.active_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
        value = data.get("session_id")
        return str(value) if value else None

    def get_active(self) -> SessionRecord | None:
        session_id = self.active_session_id()
        return self.get(session_id) if session_id else None

    def get(self, session_id: str | None) -> SessionRecord | None:
        if not session_id:
            return None
        path = self.session_path(session_id)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return SessionRecord.from_dict(data)

    def list_sessions(self) -> list[SessionRecord]:
        sessions: list[SessionRecord] = []
        for path in sorted(self.root.glob("sess_*/session.json")):
            try:
                sessions.append(SessionRecord.from_dict(json.loads(path.read_text(encoding="utf-8"))))
            except (json.JSONDecodeError, OSError, TypeError, ValueError):
                continue
        return sorted(sessions, key=lambda session: session.started_at, reverse=True)

    def last_session(self) -> SessionRecord | None:
        active = self.get_active()
        if active is not None:
            return active
        sessions = self.list_sessions()
        return sessions[0] if sessions else None

    def append_command(self, session_id: str, command: CommandRecord, *, full_output: str | None = None) -> CommandRecord:
        session = self.get(session_id)
        if session is None:
            raise ValueError("session not found")
        if full_output is not None:
            self.outputs_dir(session_id).mkdir(exist_ok=True)
            output_path = self.outputs_dir(session_id) / f"{command.command_id}.txt"
            output_path.write_text(full_output, encoding="utf-8")
            command.full_output_path = str(output_path.relative_to(self.project_root))
        with self.commands_path(session_id).open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(command.to_dict(), sort_keys=True) + "\n")
        session.command_count += 1
        if command.exit_code != 0:
            session.failure_count += 1
        if command.suspected_bug:
            session.bug_count += 1
        if command.user_rating is not None or command.feedback_tags:
            session.feedback_count += 1
        session.linked_audit_ids = sorted(set(session.linked_audit_ids + command.linked_audit_ids))
        self._write_session(session)
        return command

    def load_commands(self, session_id: str) -> list[CommandRecord]:
        path = self.commands_path(session_id)
        if not path.exists():
            return []
        records: list[CommandRecord] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                records.append(CommandRecord.from_dict(json.loads(line)))
            except (json.JSONDecodeError, TypeError, ValueError):
                continue
        return records

    def append_feedback(self, feedback: FeedbackRecord) -> FeedbackRecord:
        session = self.get(feedback.session_id)
        if session is None:
            raise ValueError("session not found")
        commands = self.load_commands(feedback.session_id)
        command_index = next((index for index, command in enumerate(commands) if command.command_id == feedback.command_id), None)
        if command_index is None:
            raise ValueError("command not found in session")
        with self.feedback_path(feedback.session_id).open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(feedback.to_dict(), sort_keys=True) + "\n")
        command = commands[command_index]
        if feedback.rating is not None:
            command.user_rating = feedback.rating
        command.feedback_tags = sorted(set(command.feedback_tags + feedback.tags))
        if feedback.linked_bug_id or feedback.severity in {"high", "critical"} or "unsafe_behavior" in feedback.tags:
            command.suspected_bug = True
        note_parts = [value for value in (feedback.reason, feedback.user_note) if value]
        if note_parts:
            addition = " | ".join(note_parts)
            command.notes = f"{command.notes}\n{addition}".strip() if command.notes else addition
        commands[command_index] = command
        self._write_commands(feedback.session_id, commands)
        session.feedback_count += 1
        if feedback.linked_bug_id or "command_failed" in feedback.tags or "unsafe_behavior" in feedback.tags:
            session.bug_count += 1
        self._write_session(session)
        return feedback

    def load_feedback(self, session_id: str) -> list[FeedbackRecord]:
        path = self.feedback_path(session_id)
        if not path.exists():
            return []
        records: list[FeedbackRecord] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                records.append(FeedbackRecord.from_dict(json.loads(line)))
            except (json.JSONDecodeError, TypeError, ValueError):
                continue
        return records

    def export(self, session_id: str) -> dict[str, Any]:
        session = self.get(session_id)
        if session is None:
            raise ValueError("session not found")
        return {
            "session": session.to_dict(),
            "commands": [record.to_dict() for record in self.load_commands(session_id)],
            "feedback": [record.to_dict() for record in self.load_feedback(session_id)],
        }

    def _write_session(self, session: SessionRecord) -> None:
        self.session_dir(session.session_id).mkdir(parents=True, exist_ok=True)
        self.session_path(session.session_id).write_text(json.dumps(session.to_dict(), indent=2, sort_keys=True), encoding="utf-8")

    def _write_commands(self, session_id: str, commands: list[CommandRecord]) -> None:
        path = self.commands_path(session_id)
        with path.open("w", encoding="utf-8") as handle:
            for command in commands:
                handle.write(json.dumps(command.to_dict(), sort_keys=True) + "\n")
