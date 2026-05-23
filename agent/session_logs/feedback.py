from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent.safety.audit import AuditEvent, AuditLogger
from agent.session_logs.models import FeedbackRecord, new_bug_id, new_feedback_id, utc_now_iso
from agent.session_logs.redaction import redact_text
from agent.session_logs.store import SessionLogStore


VALID_FEEDBACK_TAGS = {
    "poor_response",
    "wrong_tool",
    "missing_tool",
    "bad_routing",
    "hallucination",
    "no_citation",
    "bad_error_message",
    "command_failed",
    "command_hung",
    "approval_confusing",
    "unsafe_behavior",
    "too_slow",
    "UX_confusing",
    "docs_gap",
    "test_gap",
}


@dataclass(frozen=True)
class FeedbackInput:
    tags: list[str]
    rating: int | None = None
    reason: str = ""
    expected_behavior: str = ""
    actual_behavior: str = ""
    user_note: str = ""
    severity: str = "low"
    linked_bug_id: str = ""


class FeedbackManager:
    def __init__(self, store: SessionLogStore | None = None, *, audit_logger: AuditLogger | None = None) -> None:
        self.store = store or SessionLogStore()
        self.audit_logger = audit_logger or AuditLogger()

    def add_feedback(
        self,
        command_id: str | None,
        feedback: FeedbackInput,
        *,
        use_last: bool = False,
        session_id: str | None = None,
    ) -> FeedbackRecord:
        session_id = session_id or self._default_session_id()
        if not session_id:
            raise ValueError("no active or recent session found")
        commands = self.store.load_commands(session_id)
        if not commands:
            raise ValueError("session has no commands")
        target_command_id = commands[-1].command_id if use_last else command_id
        if not target_command_id:
            raise ValueError("feedback requires --last or <command_id>")
        if target_command_id not in {command.command_id for command in commands}:
            raise ValueError("command not found in session")
        record = _build_feedback_record(session_id, target_command_id, feedback)
        saved = self.store.append_feedback(record)
        self._audit("feedback.add", saved)
        return saved

    def list_feedback(self, *, session_id: str) -> list[FeedbackRecord]:
        records = self.store.load_feedback(session_id)
        self._audit(
            "feedback.list",
            FeedbackRecord(
                feedback_id="summary",
                session_id=session_id,
                command_id="",
                timestamp=utc_now_iso(),
                user_note=f"{len(records)} feedback records",
            ),
        )
        return records

    def export_feedback(self, *, session_id: str) -> dict[str, Any]:
        session = self.store.get(session_id)
        if session is None:
            raise ValueError("session not found")
        records = [record.to_dict() for record in self.list_feedback(session_id=session_id)]
        return {"session": session.to_dict(), "feedback": records}

    def _default_session_id(self) -> str | None:
        active = self.store.get_active()
        if active is not None:
            return active.session_id
        last = self.store.last_session()
        return last.session_id if last else None

    def _audit(self, tool_name: str, record: FeedbackRecord) -> None:
        self.audit_logger.log(
            AuditEvent(
                session_id=record.session_id,
                request_id=record.feedback_id,
                route="feedback_cli",
                model="none",
                tool_name=tool_name,
                capability=tool_name,
                risk_level="LOW",
                trust_level="TRUSTED_USER",
                policy_decision="ALLOW",
                sanitized_args={
                    "command_id": record.command_id,
                    "tags": record.tags,
                    "rating": record.rating,
                    "severity": record.severity,
                    "linked_bug_id": record.linked_bug_id,
                },
                result_summary=f"feedback {record.feedback_id} {record.severity}",
            )
        )


def make_feedback(
    *,
    tags: list[str],
    rating: int | None = None,
    reason: str = "",
    expected_behavior: str = "",
    actual_behavior: str = "",
    user_note: str = "",
    severity: str = "low",
    linked_bug_id: str = "",
) -> FeedbackInput:
    if rating is not None and not 1 <= rating <= 5:
        raise ValueError("feedback score must be between 1 and 5")
    invalid_tags = [tag for tag in tags if tag not in VALID_FEEDBACK_TAGS]
    if invalid_tags:
        raise ValueError(f"invalid feedback tag(s): {', '.join(invalid_tags)}")
    normalized_severity = _severity_for(tags, severity)
    return FeedbackInput(
        tags=tags,
        rating=rating,
        reason=reason,
        expected_behavior=expected_behavior,
        actual_behavior=actual_behavior,
        user_note=user_note,
        severity=normalized_severity,
        linked_bug_id=linked_bug_id,
    )


def _build_feedback_record(session_id: str, command_id: str, feedback: FeedbackInput) -> FeedbackRecord:
    return FeedbackRecord(
        feedback_id=new_feedback_id(),
        session_id=session_id,
        command_id=command_id,
        timestamp=utc_now_iso(),
        rating=feedback.rating,
        tags=sorted(set(feedback.tags)),
        reason=redact_text(feedback.reason),
        expected_behavior=redact_text(feedback.expected_behavior),
        actual_behavior=redact_text(feedback.actual_behavior),
        severity=feedback.severity,
        user_note=redact_text(feedback.user_note),
        linked_bug_id=feedback.linked_bug_id,
        redaction_status="redacted",
    )


def _severity_for(tags: list[str], requested: str) -> str:
    if "unsafe_behavior" in tags:
        return "high"
    if any(tag in tags for tag in ("command_failed", "command_hung", "hallucination")):
        return "medium" if requested == "low" else requested
    return requested


def bug_feedback(title: str, *, reason: str = "") -> FeedbackInput:
    note = title if not reason else f"{title}: {reason}"
    return make_feedback(tags=["command_failed"], user_note=note, severity="medium", linked_bug_id=new_bug_id())
