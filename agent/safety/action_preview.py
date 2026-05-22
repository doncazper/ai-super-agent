from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent.safety.policy import RiskLevel
from agent.safety.redaction import SecretRedactor


class ActionPreviewError(ValueError):
    pass


@dataclass(frozen=True)
class ActionPreview:
    tool_name: str
    risk_level: RiskLevel
    title: str
    summary: str
    args: dict[str, Any]
    exact_args_required: bool = False
    rollback_available: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "risk_level": self.risk_level.value,
            "title": self.title,
            "summary": self.summary,
            "sanitized_args": SecretRedactor().redact(self.args),
            "exact_args_required": self.exact_args_required,
            "rollback_available": self.rollback_available,
        }


class ActionPreviewFormatter:
    def format(self, tool_name: str, args: dict[str, Any], risk_level: RiskLevel) -> ActionPreview:
        sanitized = SecretRedactor().redact(args)
        exact_required = risk_level is RiskLevel.CRITICAL
        if exact_required:
            self._validate_exact_args(tool_name, sanitized)
        if tool_name in {"filesystem.write", "filesystem.patch"}:
            return ActionPreview(
                tool_name,
                risk_level,
                "File change",
                f"path={sanitized.get('path', '')}",
                sanitized,
                exact_args_required=exact_required,
                rollback_available=True,
            )
        if tool_name == "web.fetch_url":
            return ActionPreview(
                tool_name,
                risk_level,
                "Web fetch",
                f"url={sanitized.get('url', '')}",
                sanitized,
                exact_args_required=exact_required,
            )
        if tool_name.startswith("calendar."):
            if tool_name in {"calendar.read_date_range", "calendar.find_availability"}:
                start = sanitized.get("start") or sanitized.get("start_date") or ""
                end = sanitized.get("end") or sanitized.get("end_date") or ""
                return ActionPreview(
                    tool_name,
                    risk_level,
                    "Calendar read",
                    f"selected_range={start} to {end}; filters={sanitized.get('calendar_filters', [])}",
                    sanitized,
                    exact_args_required=exact_required,
                )
            return ActionPreview(
                tool_name,
                risk_level,
                "Calendar event",
                (
                    f"title={sanitized.get('title', '')}; start={sanitized.get('start', '')}; "
                    f"end={sanitized.get('end', '')}; attendees={sanitized.get('attendees', [])}"
                ),
                sanitized,
                exact_args_required=exact_required,
            )
        if tool_name.startswith("contacts.") and tool_name != "contacts.update_selected":
            return ActionPreview(
                tool_name,
                risk_level,
                "Contacts read",
                (
                    f"query={sanitized.get('query', '')}; "
                    f"selected_scope_token={sanitized.get('selected_scope_token', '')}"
                ),
                sanitized,
                exact_args_required=exact_required,
            )
        if tool_name == "contacts.update_selected":
            return ActionPreview(
                tool_name,
                risk_level,
                "Contact update",
                f"fields_changed={sanitized.get('changes', sanitized)}",
                sanitized,
                exact_args_required=exact_required,
            )
        if tool_name in {"email.send", "email.send_approved"}:
            return ActionPreview(
                tool_name,
                risk_level,
                "Email send",
                (
                    f"recipient={sanitized.get('to', '')}; subject={sanitized.get('subject', '')}; "
                    f"body={sanitized.get('body', '')}; attachments={sanitized.get('attachments', [])}"
                ),
                sanitized,
                exact_args_required=exact_required,
            )
        if tool_name in {"messages.send", "messages.send_approved"}:
            return ActionPreview(
                tool_name,
                risk_level,
                "Message send",
                f"recipient={sanitized.get('to', '')}; exact_message={sanitized.get('body', '')}",
                sanitized,
                exact_args_required=exact_required,
            )
        return ActionPreview(
            tool_name,
            risk_level,
            "Tool call",
            f"{tool_name} with sanitized args",
            sanitized,
            exact_args_required=exact_required,
        )

    def _validate_exact_args(self, tool_name: str, args: dict[str, Any]) -> None:
        required: dict[str, tuple[str, ...]] = {
            "calendar.create_event": ("title", "start", "end"),
            "calendar.update_event": ("event_id", "changes"),
            "calendar.delete_event": ("event_id",),
            "contacts.update_selected": ("selected_scope_token", "changes"),
            "email.send": ("to", "subject", "body"),
            "email.send_approved": ("to", "subject", "body"),
            "messages.send": ("to", "body"),
            "messages.send_approved": ("to", "body"),
        }
        missing = [key for key in required.get(tool_name, ()) if not args.get(key)]
        if missing:
            raise ActionPreviewError(f"critical action preview missing exact args: {', '.join(missing)}")
