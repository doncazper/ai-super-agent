from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent.safety.contact_redaction import redact_contact_args
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
        if tool_name == "filesystem.delete":
            return ActionPreview(
                tool_name,
                risk_level,
                "File delete",
                f"path={sanitized.get('path', '')}; rollback=not_available",
                sanitized,
                exact_args_required=exact_required,
                rollback_available=False,
            )
        if tool_name == "git.commit":
            return ActionPreview(
                tool_name,
                risk_level,
                "Git commit",
                f"message={sanitized.get('message', '')}",
                sanitized,
                exact_args_required=exact_required,
                rollback_available=True,
            )
        if tool_name == "memory.store_personal":
            return ActionPreview(
                tool_name,
                risk_level,
                "Personal memory write",
                f"category={sanitized.get('category', '')}; scope={sanitized.get('scope', 'personal')}",
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
            if tool_name == "calendar.read_selected_event":
                return ActionPreview(
                    tool_name,
                    risk_level,
                    "Calendar event read",
                    f"selected_event={'provided' if sanitized.get('event_id') else 'date/title selector'}; date={sanitized.get('date', '')}",
                    sanitized,
                    exact_args_required=exact_required,
                )
            return ActionPreview(
                tool_name,
                risk_level,
                "Calendar event",
                (
                    f"calendar={sanitized.get('calendar_name', sanitized.get('calendar', 'default'))}; "
                    f"title={sanitized.get('title', '')}; start={sanitized.get('start', '')}; "
                    f"end={sanitized.get('end', '')}; attendees={sanitized.get('attendees', [])}; "
                    f"location={sanitized.get('location', '')}; notes={sanitized.get('notes', '')}; "
                    f"changed_fields={list(sanitized.get('changes', {}).keys()) if isinstance(sanitized.get('changes'), dict) else []}"
                ),
                sanitized,
                exact_args_required=exact_required,
                rollback_available=(
                    True
                    if tool_name == "calendar.create_event"
                    else bool(sanitized.get("rollback_data")) if tool_name == "calendar.update_event" else False
                ),
            )
        if tool_name.startswith("contacts.") and tool_name not in {"contacts.update_selected", "contacts.create"}:
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
            contact_args = redact_contact_args(sanitized)
            return ActionPreview(
                tool_name,
                risk_level,
                "Contact update",
                _contact_diff_summary(contact_args),
                contact_args,
                exact_args_required=exact_required,
            )
        if tool_name == "contacts.create":
            contact_args = redact_contact_args(sanitized)
            fields = contact_args.get("fields", {})
            field_names = list(fields.keys()) if isinstance(fields, dict) else []
            return ActionPreview(
                tool_name,
                risk_level,
                "Contact create",
                f"display_name={contact_args.get('display_name', '')}; fields={field_names}",
                contact_args,
                exact_args_required=exact_required,
            )
        if tool_name.startswith("email.") and tool_name not in {"email.send", "email.send_approved"}:
            return ActionPreview(
                tool_name,
                risk_level,
                "Email assistant",
                (
                    f"thread_id={sanitized.get('thread_id', sanitized.get('selected_scope_token', ''))}; "
                    f"draft_only={tool_name == 'email.draft_reply'}"
                ),
                sanitized,
                exact_args_required=exact_required,
            )
        if tool_name.startswith("messages.") and tool_name not in {"messages.send", "messages.send_approved"}:
            if tool_name == "messages.save_draft":
                return ActionPreview(
                    tool_name,
                    risk_level,
                    "Message draft save",
                    (
                        f"recipient={sanitized.get('to', '')}; path={sanitized.get('path', 'workspace/message_drafts')}; "
                        f"draft={sanitized.get('draft', '')}; send=false"
                    ),
                    sanitized,
                    exact_args_required=exact_required,
                    rollback_available=True,
                )
            if tool_name == "messages.copy_draft":
                return ActionPreview(
                    tool_name,
                    risk_level,
                    "Message draft clipboard copy",
                    f"recipient={sanitized.get('to', '')}; draft={sanitized.get('draft', '')}; send=false",
                    sanitized,
                    exact_args_required=exact_required,
                    rollback_available=False,
                )
            return ActionPreview(
                tool_name,
                risk_level,
                "Messages assistant",
                (
                    f"thread_id={sanitized.get('thread_id', sanitized.get('selected_scope_token', ''))}; "
                    f"context_file={sanitized.get('context_file', '')}; "
                    f"draft_only={tool_name in {'messages.draft_reply', 'messages.draft_from_text'}}"
                ),
                sanitized,
                exact_args_required=exact_required,
            )
        if tool_name in {"email.send", "email.send_approved"}:
            return ActionPreview(
                tool_name,
                risk_level,
                "Email send",
                (
                    f"from={sanitized.get('from_account', sanitized.get('from', 'configured_default'))}; "
                    f"provider={sanitized.get('provider', 'configured_default')}; "
                    f"recipient={sanitized.get('to', '')}; cc={sanitized.get('cc', [])}; bcc={sanitized.get('bcc', [])}; "
                    f"subject={sanitized.get('subject', '')}; body={sanitized.get('body', '')}; "
                    f"attachments={sanitized.get('attachments', [])}; thread={sanitized.get('thread_id', '')}; "
                    f"reply_context={sanitized.get('reply_context', '')}; rollback=impossible"
                ),
                sanitized,
                exact_args_required=exact_required,
                rollback_available=False,
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
        if tool_name in {"messaging.send_approved", "messages.macos.send_approved"}:
            return ActionPreview(
                tool_name,
                risk_level,
                "Message send approval",
                (
                    f"channel={sanitized.get('channel', '')}; recipient={sanitized.get('to', '')}; "
                    f"body={sanitized.get('body', '')}; attachments={sanitized.get('attachments', [])}; "
                    f"rollback=impossible; approval=explicit_per_action; "
                    f"allowlist={sanitized.get('allowlist_status', 'not_configured')}; "
                    f"rate_limit={sanitized.get('rate_limit_status', 'not_configured')}; "
                    f"send={bool(sanitized.get('send_supported', False))}"
                ),
                sanitized,
                exact_args_required=exact_required,
                rollback_available=False,
            )
        if tool_name.startswith("tasks."):
            return ActionPreview(
                tool_name,
                risk_level,
                "Task action",
                (
                    f"title={sanitized.get('title', '')}; task_id={sanitized.get('task_id', '')}; "
                    f"due={sanitized.get('due', '')}; list={sanitized.get('list_name', '')}; "
                    f"changed_fields={list(sanitized.get('changes', {}).keys()) if isinstance(sanitized.get('changes'), dict) else []}"
                ),
                sanitized,
                exact_args_required=exact_required,
                rollback_available=tool_name == "tasks.create",
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
            "contacts.create": ("display_name",),
            "email.send": ("to", "subject", "body"),
            "email.send_approved": ("to", "subject", "body"),
            "messages.send": ("to", "body"),
            "messages.send_approved": ("to", "body"),
            "messaging.send_approved": ("draft_id", "channel", "to", "body"),
            "messages.macos.send_approved": ("draft_id", "channel", "to", "body"),
            "messages.save_draft": ("to", "draft"),
            "messages.copy_draft": ("to", "draft"),
            "tasks.create": ("title",),
            "tasks.update": ("task_id", "changes"),
            "tasks.complete": ("task_id",),
            "tasks.delete": ("task_id",),
        }
        missing = [key for key in required.get(tool_name, ()) if not args.get(key)]
        if missing:
            raise ActionPreviewError(f"critical action preview missing exact args: {', '.join(missing)}")


def _contact_diff_summary(args: dict[str, Any]) -> str:
    diffs = args.get("field_diff")
    if isinstance(diffs, list) and diffs:
        parts = []
        for item in diffs:
            if not isinstance(item, dict):
                continue
            parts.append(f"{item.get('field', '')}: {item.get('old', '')} -> {item.get('new', '')}")
        if parts:
            return "field_diff=" + "; ".join(parts)
    changes = args.get("changes", {})
    if isinstance(changes, dict):
        return f"fields_changed={list(changes.keys())}"
    return "fields_changed=[]"
