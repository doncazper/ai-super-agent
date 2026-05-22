from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


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
    def calendar_create_event(title: str, start: str, end: str, attendees: list[str] | None = None, notes: str = ""):
        return {**_not_configured("calendar.create_event", rollback_available=False), "event": {"title": title, "start": start, "end": end, "attendees": attendees or [], "notes": notes}}

    def calendar_update_event(event_id: str, changes: dict[str, Any]):
        return {**_not_configured("calendar.update_event", rollback_available=False), "event_id": event_id, "changes": changes}

    def calendar_delete_event(event_id: str):
        return {**_not_configured("calendar.delete_event", rollback_available=False), "event_id": event_id}

    def contacts_update_selected(selected_scope_token: str, changes: dict[str, Any]):
        return {**_not_configured("contacts.update_selected", rollback_available=False), "selected_scope_token": selected_scope_token, "changes": changes}

    def email_send_approved(to: str, subject: str, body: str, cc: list[str] | None = None, attachments: list[str] | None = None):
        return {
            **_not_configured("email.send_approved", rollback_available=False),
            "to": to,
            "cc": cc or [],
            "subject": subject,
            "body": body,
            "attachments": attachments or [],
            "sent": False,
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
        {"title": {"type": "string"}, "start": {"type": "string"}, "end": {"type": "string"}, "attendees": {"type": "array", "items": {"type": "string"}}, "notes": {"type": "string"}},
        ["title", "start", "end"],
    ),
    "calendar.update_event": _schema(
        "calendar.update_event",
        "Update a calendar event after explicit per-action approval.",
        {"event_id": {"type": "string"}, "changes": {"type": "object"}},
        ["event_id", "changes"],
    ),
    "calendar.delete_event": _schema(
        "calendar.delete_event",
        "Delete a calendar event after explicit per-action approval.",
        {"event_id": {"type": "string"}},
        ["event_id"],
    ),
    "contacts.update_selected": _schema(
        "contacts.update_selected",
        "Update an explicitly selected contact after approval.",
        {"selected_scope_token": {"type": "string"}, "changes": {"type": "object"}},
        ["selected_scope_token", "changes"],
    ),
    "email.send_approved": _schema(
        "email.send_approved",
        "Send an approved email after explicit per-action approval.",
        {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}, "cc": {"type": "array", "items": {"type": "string"}}, "attachments": {"type": "array", "items": {"type": "string"}}},
        ["to", "subject", "body"],
    ),
    "messages.send_approved": _schema(
        "messages.send_approved",
        "Send an approved message after explicit per-action approval.",
        {"to": {"type": "string"}, "body": {"type": "string"}, "attachments": {"type": "array", "items": {"type": "string"}}},
        ["to", "body"],
    ),
}
