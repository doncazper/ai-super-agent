from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_session_id() -> str:
    return f"sess_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid4().hex[:8]}"


def new_command_id() -> str:
    return f"cmd_{uuid4().hex[:12]}"


def new_feedback_id() -> str:
    return f"fb_{uuid4().hex[:12]}"


def new_bug_id() -> str:
    return f"bug_{uuid4().hex[:12]}"


@dataclass
class CommandRecord:
    command_id: str
    timestamp: str
    command_line: str
    sanitized_command_line: str
    exit_code: int
    duration_ms: int
    stdout_preview: str
    stderr_preview: str
    full_output_path: str | None = None
    tool_calls_detected: list[str] = field(default_factory=list)
    linked_audit_ids: list[str] = field(default_factory=list)
    user_rating: int | None = None
    feedback_tags: list[str] = field(default_factory=list)
    suspected_bug: bool = False
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CommandRecord":
        return cls(
            command_id=str(data.get("command_id", "")),
            timestamp=str(data.get("timestamp", "")),
            command_line=str(data.get("command_line", "")),
            sanitized_command_line=str(data.get("sanitized_command_line", "")),
            exit_code=int(data.get("exit_code", 0)),
            duration_ms=int(data.get("duration_ms", 0)),
            stdout_preview=str(data.get("stdout_preview", "")),
            stderr_preview=str(data.get("stderr_preview", "")),
            full_output_path=data.get("full_output_path"),
            tool_calls_detected=list(data.get("tool_calls_detected", [])),
            linked_audit_ids=list(data.get("linked_audit_ids", [])),
            user_rating=data.get("user_rating"),
            feedback_tags=list(data.get("feedback_tags", [])),
            suspected_bug=bool(data.get("suspected_bug", False)),
            notes=str(data.get("notes", "")),
        )


@dataclass
class FeedbackRecord:
    feedback_id: str
    session_id: str
    command_id: str
    timestamp: str
    rating: int | None = None
    tags: list[str] = field(default_factory=list)
    reason: str = ""
    expected_behavior: str = ""
    actual_behavior: str = ""
    severity: str = "low"
    user_note: str = ""
    linked_bug_id: str = ""
    redaction_status: str = "redacted"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FeedbackRecord":
        rating = data.get("rating")
        return cls(
            feedback_id=str(data.get("feedback_id", "")),
            session_id=str(data.get("session_id", "")),
            command_id=str(data.get("command_id", "")),
            timestamp=str(data.get("timestamp", "")),
            rating=int(rating) if rating is not None else None,
            tags=list(data.get("tags", [])),
            reason=str(data.get("reason", "")),
            expected_behavior=str(data.get("expected_behavior", "")),
            actual_behavior=str(data.get("actual_behavior", "")),
            severity=str(data.get("severity", "low")),
            user_note=str(data.get("user_note", "")),
            linked_bug_id=str(data.get("linked_bug_id", "")),
            redaction_status=str(data.get("redaction_status", "redacted")),
        )


@dataclass
class SessionRecord:
    session_id: str
    name: str
    started_at: str
    ended_at: str | None
    status: str
    git_commit: str
    branch: str
    model: str
    base_url: str
    config_summary: dict[str, Any]
    command_count: int = 0
    failure_count: int = 0
    bug_count: int = 0
    feedback_count: int = 0
    tags: list[str] = field(default_factory=list)
    linked_audit_ids: list[str] = field(default_factory=list)
    redaction_status: str = "redacted"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def start(
        cls,
        *,
        name: str,
        git_commit: str,
        branch: str,
        model: str,
        base_url: str,
        config_summary: dict[str, Any],
        tags: list[str] | None = None,
    ) -> "SessionRecord":
        return cls(
            session_id=new_session_id(),
            name=name,
            started_at=utc_now_iso(),
            ended_at=None,
            status="active",
            git_commit=git_commit,
            branch=branch,
            model=model,
            base_url=base_url,
            config_summary=config_summary,
            tags=tags or [],
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SessionRecord":
        return cls(
            session_id=str(data.get("session_id", "")),
            name=str(data.get("name", "")),
            started_at=str(data.get("started_at", "")),
            ended_at=data.get("ended_at"),
            status=str(data.get("status", "unknown")),
            git_commit=str(data.get("git_commit", "unknown")),
            branch=str(data.get("branch", "unknown")),
            model=str(data.get("model", "")),
            base_url=str(data.get("base_url", "")),
            config_summary=dict(data.get("config_summary", {})),
            command_count=int(data.get("command_count", 0)),
            failure_count=int(data.get("failure_count", 0)),
            bug_count=int(data.get("bug_count", 0)),
            feedback_count=int(data.get("feedback_count", 0)),
            tags=list(data.get("tags", [])),
            linked_audit_ids=list(data.get("linked_audit_ids", [])),
            redaction_status=str(data.get("redaction_status", "redacted")),
        )
