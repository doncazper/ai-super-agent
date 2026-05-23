from __future__ import annotations

from agent.session_logs.models import CommandRecord, FeedbackRecord, SessionRecord


def format_replay(session: SessionRecord, commands: list[CommandRecord], feedback: list[FeedbackRecord] | None = None) -> str:
    feedback_by_command: dict[str, list[FeedbackRecord]] = {}
    for record in feedback or []:
        feedback_by_command.setdefault(record.command_id, []).append(record)
    lines = [
        f"# Session Replay: {session.name}",
        "",
        f"- session_id: {session.session_id}",
        f"- status: {session.status}",
        f"- started_at: {session.started_at}",
        f"- ended_at: {session.ended_at or 'active'}",
        f"- branch: {session.branch}",
        f"- git_commit: {session.git_commit}",
        f"- model: {session.model or 'not configured'}",
        f"- commands: {session.command_count}",
        f"- failures: {session.failure_count}",
        f"- feedback: {session.feedback_count}",
        f"- redaction_status: {session.redaction_status}",
        "",
    ]
    for command in commands:
        lines.extend(
            [
                f"## {command.command_id}",
                "",
                f"- timestamp: {command.timestamp}",
                f"- command: `{command.sanitized_command_line}`",
                f"- exit_code: {command.exit_code}",
                f"- duration_ms: {command.duration_ms}",
                f"- rating: {command.user_rating if command.user_rating is not None else 'none'}",
                f"- feedback_tags: {', '.join(command.feedback_tags) if command.feedback_tags else 'none'}",
                f"- audit_ids: {', '.join(command.linked_audit_ids) if command.linked_audit_ids else 'none'}",
                "",
            ]
        )
        command_feedback = feedback_by_command.get(command.command_id, [])
        if command_feedback:
            lines.extend(["feedback:", ""])
            for record in command_feedback:
                lines.append(
                    f"- {record.feedback_id}: severity={record.severity}; "
                    f"rating={record.rating if record.rating is not None else 'none'}; "
                    f"tags={', '.join(record.tags) if record.tags else 'none'}"
                )
                if record.reason:
                    lines.append(f"  reason: {record.reason}")
                if record.user_note:
                    lines.append(f"  note: {record.user_note}")
            lines.append("")
        lines.extend(
            [
                "stdout:",
                "```text",
                command.stdout_preview or "",
                "```",
                "",
                "stderr:",
                "```text",
                command.stderr_preview or "",
                "```",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"
