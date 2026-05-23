from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from agent.config.runtime import env_value
from agent.tools.errors import ToolError


def _not_configured(action: str, rollback_available: bool = False) -> dict[str, object]:
    return {
        "action": action,
        "executed": False,
        "connector_configured": False,
        "rollback_available": rollback_available,
        "error": "approved write connector is not configured; no external change was made",
        "timestamp": datetime.now(UTC).isoformat(),
    }


def make_write_action_tools() -> dict[str, Any]:
    def calendar_create_event(
        title: str,
        start: str,
        end: str,
        attendees: list[str] | None = None,
        notes: str = "",
        calendar_name: str = "",
        location: str = "",
        send_invites: bool = False,
        recurrence: str | None = None,
    ):
        return {
            **_not_configured("calendar.create_event", rollback_available=False),
            "event": {
                "calendar_name": calendar_name,
                "title": title,
                "start": start,
                "end": end,
                "attendees": attendees or [],
                "location": location,
                "notes": notes,
                "recurrence": recurrence,
            },
            "invites_sent": False if not send_invites else False,
            "recurring_events_supported": False,
            "_audit": {"result_summary": "Calendar create action reached approved write connector stub; no external change was made."},
        }

    def calendar_update_event(
        event_id: str,
        changes: dict[str, Any],
        rollback_data: dict[str, Any] | None = None,
        send_invites: bool = False,
        recurrence: str | None = None,
    ):
        return {
            **_not_configured("calendar.update_event", rollback_available=False),
            "event_id": event_id,
            "changes": changes,
            "rollback_data_captured": bool(rollback_data),
            "rollback_data": rollback_data or {},
            "invites_sent": False if not send_invites else False,
            "recurrence": recurrence,
            "_audit": {"result_summary": "Calendar update action reached approved write connector stub; no external change was made."},
        }

    def calendar_delete_event(
        event_id: str,
        rollback_data: dict[str, Any] | None = None,
        rollback_availability: bool = False,
    ):
        return {
            **_not_configured("calendar.delete_event", rollback_available=rollback_availability),
            "event_id": event_id,
            "rollback_data_captured": bool(rollback_data),
            "rollback_data": rollback_data or {},
            "_audit": {"result_summary": "Calendar delete action reached approved write connector stub; no external change was made."},
        }

    def contacts_update_selected(
        selected_scope_token: str,
        changes: dict[str, Any],
        field_diff: list[dict[str, Any]] | None = None,
        bulk_edit: bool = False,
        stored_in_memory: bool = False,
    ):
        return {
            **_not_configured("contacts.update_selected", rollback_available=False),
            "selected_scope_token": selected_scope_token,
            "changes": changes,
            "field_diff": field_diff or [],
            "bulk_edit": bulk_edit,
            "stored_in_memory": stored_in_memory,
            "_audit": {"result_summary": "Contact update action reached approved write connector stub; no external change was made."},
        }

    def contacts_create(display_name: str, fields: dict[str, Any] | None = None, stored_in_memory: bool = False):
        return {
            **_not_configured("contacts.create", rollback_available=False),
            "display_name": display_name,
            "fields": fields or {},
            "created": False,
            "stored_in_memory": stored_in_memory,
            "_audit": {"result_summary": "Contact create action reached approved write connector stub; no external change was made."},
        }

    def email_send_approved(
        to: str,
        subject: str,
        body: str,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        attachments: list[str] | None = None,
        from_account: str = "",
        provider: str = "",
        thread_id: str = "",
        reply_context: str = "",
        action_id: str = "",
        source_trust_level: str = "",
        stored_in_memory: bool = False,
        rollback_available: bool = False,
        rollback_note: str = "Email sending is irreversible after provider acceptance.",
    ):
        if not action_id:
            raise ToolError("email.send_approved must originate from an approved Action Center item")
        if not to.strip():
            raise ToolError("email.send_approved requires exactly one recipient")
        if "," in to or ";" in to:
            raise ToolError("bulk email sends are denied")
        if not subject.strip():
            raise ToolError("email.send_approved requires a subject")
        if not body.strip():
            raise ToolError("email.send_approved requires the full body")
        if attachments:
            raise ToolError("email.send_approved v1 blocks attachments")
        selected_provider = (provider or env_value("EMAIL_SEND_PROVIDER", default="")).strip().casefold()
        if selected_provider == "mock":
            return {
                "status": "ok",
                "action": "email.send_approved",
                "executed": True,
                "sent": True,
                "provider": "mock",
                "from_account": from_account or "mock",
                "to": to,
                "cc": cc or [],
                "bcc": bcc or [],
                "subject": subject,
                "body": body,
                "attachments": [],
                "thread_id": thread_id,
                "reply_context": reply_context,
                "action_id": action_id,
                "source_trust_level": source_trust_level,
                "stored_in_memory": stored_in_memory,
                "rollback_available": False,
                "rollback_note": rollback_note,
                "timestamp": datetime.now(UTC).isoformat(),
                "_audit": {"result_summary": "Mock email send executed from an approved Action Center record."},
            }
        return {
            **_not_configured("email.send_approved", rollback_available=False),
            "status": "error",
            "provider": selected_provider or "not_configured",
            "from_account": from_account,
            "to": to,
            "cc": cc or [],
            "bcc": bcc or [],
            "subject": subject,
            "body": body,
            "attachments": attachments or [],
            "thread_id": thread_id,
            "reply_context": reply_context,
            "action_id": action_id,
            "source_trust_level": source_trust_level,
            "stored_in_memory": stored_in_memory,
            "rollback_available": rollback_available,
            "rollback_note": rollback_note,
            "sent": False,
            "setup": [
                "Email send remains disabled unless an approved send provider is configured.",
                "For local tests only, set provider=mock or EMAIL_SEND_PROVIDER=mock.",
                "Do not store credentials in this project and do not scrape private Mail databases.",
            ],
            "_audit": {"result_summary": "Email send reached approved Action Center path but no send provider is configured."},
        }

    def messages_send_approved(to: str, body: str, attachments: list[str] | None = None):
        return {
            **_not_configured("messages.send_approved", rollback_available=False),
            "to": to,
            "body": body,
            "attachments": attachments or [],
            "sent": False,
        }

    return {
        "calendar.create_event": calendar_create_event,
        "calendar.update_event": calendar_update_event,
        "calendar.delete_event": calendar_delete_event,
        "contacts.update_selected": contacts_update_selected,
        "contacts.create": contacts_create,
        "email.send_approved": email_send_approved,
        "messages.send_approved": messages_send_approved,
    }


def _schema(name: str, description: str, properties: dict[str, object], required: list[str]) -> dict[str, object]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
        },
    }


WRITE_ACTION_SCHEMAS = {
    "calendar.create_event": _schema(
        "calendar.create_event",
        "Create a calendar event after explicit per-action approval.",
        {
            "title": {"type": "string"},
            "start": {"type": "string"},
            "end": {"type": "string"},
            "attendees": {"type": "array", "items": {"type": "string"}},
            "notes": {"type": "string"},
            "calendar_name": {"type": "string"},
            "location": {"type": "string"},
            "send_invites": {"type": "boolean"},
            "recurrence": {"type": ["string", "null"]},
        },
        ["title", "start", "end"],
    ),
    "calendar.update_event": _schema(
        "calendar.update_event",
        "Update a calendar event after explicit per-action approval.",
        {
            "event_id": {"type": "string"},
            "changes": {"type": "object"},
            "rollback_data": {"type": "object"},
            "send_invites": {"type": "boolean"},
            "recurrence": {"type": ["string", "null"]},
        },
        ["event_id", "changes"],
    ),
    "calendar.delete_event": _schema(
        "calendar.delete_event",
        "Delete a calendar event after explicit per-action approval.",
        {
            "event_id": {"type": "string"},
            "rollback_data": {"type": "object"},
            "rollback_availability": {"type": "boolean"},
        },
        ["event_id"],
    ),
    "contacts.update_selected": _schema(
        "contacts.update_selected",
        "Update an explicitly selected contact after approval.",
        {
            "selected_scope_token": {"type": "string"},
            "changes": {"type": "object"},
            "field_diff": {"type": "array", "items": {"type": "object"}},
            "bulk_edit": {"type": "boolean"},
            "stored_in_memory": {"type": "boolean"},
        },
        ["selected_scope_token", "changes"],
    ),
    "contacts.create": _schema(
        "contacts.create",
        "Create one contact from an approved Action Center record. Stubbed until a safe native connector is configured.",
        {"display_name": {"type": "string"}, "fields": {"type": "object"}, "stored_in_memory": {"type": "boolean"}},
        ["display_name"],
    ),
    "email.send_approved": _schema(
        "email.send_approved",
        "Send an approved email after explicit per-action approval.",
        {
            "to": {"type": "string"},
            "subject": {"type": "string"},
            "body": {"type": "string"},
            "cc": {"type": "array", "items": {"type": "string"}},
            "bcc": {"type": "array", "items": {"type": "string"}},
            "attachments": {"type": "array", "items": {"type": "string"}},
            "from_account": {"type": "string"},
            "provider": {"type": "string"},
            "thread_id": {"type": "string"},
            "reply_context": {"type": "string"},
            "action_id": {"type": "string"},
            "source_trust_level": {"type": "string"},
            "stored_in_memory": {"type": "boolean"},
            "rollback_available": {"type": "boolean"},
            "rollback_note": {"type": "string"},
        },
        ["to", "subject", "body"],
    ),
    "messages.send_approved": _schema(
        "messages.send_approved",
        "Send an approved message after explicit per-action approval.",
        {"to": {"type": "string"}, "body": {"type": "string"}, "attachments": {"type": "array", "items": {"type": "string"}}},
        ["to", "body"],
    ),
}
