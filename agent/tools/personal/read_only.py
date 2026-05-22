from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.tools.personal.calendar import CalendarConnector, calendar_connector_from_env, find_availability, read_date_range
from agent.tools.personal.contacts import ContactsConnector, contacts_connector_from_env, read_selected_contact, search_contacts
from agent.tools.personal.email import (
    EmailConnector,
    draft_reply,
    email_connector_from_env,
    list_metadata,
    read_selected_thread,
    summarize_thread,
)
from agent.tools.personal.messages import (
    MessagesConnector,
    draft_reply as draft_message_reply,
    messages_connector_from_env,
    read_selected_thread as read_selected_message_thread,
    summarize_thread as summarize_message_thread,
)


def make_personal_tools(
    project_root: str | Path = ".",
    calendar_connector: CalendarConnector | None = None,
    contacts_connector: ContactsConnector | None = None,
    email_connector: EmailConnector | None = None,
    messages_connector: MessagesConnector | None = None,
) -> dict[str, Any]:
    connector = calendar_connector or calendar_connector_from_env()
    contact_connector = contacts_connector or contacts_connector_from_env()
    mail_connector = email_connector or email_connector_from_env()
    text_connector = messages_connector or messages_connector_from_env()

    def contacts_search(query: str, max_results: int | None = None) -> dict[str, object]:
        return search_contacts(contact_connector, query=query, max_results=max_results)

    def contacts_read_selected(
        selected_scope_token: str | None = None,
        contact_id: str | None = None,
        requested_fields: list[str] | None = None,
    ) -> dict[str, object]:
        return read_selected_contact(
            contact_connector,
            selected_scope_token=selected_scope_token or contact_id,
            requested_fields=requested_fields,
        )

    def calendar_read_date_range(
        start: str | None = None,
        end: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        calendar_filters: list[str] | None = None,
    ) -> dict[str, object]:
        return read_date_range(
            connector,
            start=start,
            end=end,
            start_date=start_date,
            end_date=end_date,
            calendar_filters=calendar_filters,
        )

    def calendar_find_availability(
        start: str | None = None,
        end: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        duration_minutes: int = 30,
        working_hours_start: str = "09:00",
        working_hours_end: str = "17:00",
        calendar_filters: list[str] | None = None,
    ) -> dict[str, object]:
        return find_availability(
            connector,
            start=start,
            end=end,
            start_date=start_date,
            end_date=end_date,
            duration_minutes=duration_minutes,
            working_hours_start=working_hours_start,
            working_hours_end=working_hours_end,
            calendar_filters=calendar_filters,
        )

    def email_list_metadata(max_results: int | None = None) -> dict[str, object]:
        return list_metadata(mail_connector, max_results=max_results)

    def email_read_selected_thread(thread_id: str | None = None, selected_scope_token: str | None = None) -> dict[str, object]:
        return read_selected_thread(mail_connector, thread_id=thread_id or selected_scope_token)

    def email_summarize_thread(
        thread_id: str | None = None,
        thread_text: str | None = None,
        selected_scope_token: str | None = None,
    ) -> dict[str, object]:
        return summarize_thread(mail_connector, thread_id=thread_id or selected_scope_token, thread_text=thread_text)

    def email_draft_reply(
        thread_id: str | None = None,
        thread_text: str | None = None,
        selected_scope_token: str | None = None,
        user_instruction: str = "",
    ) -> dict[str, object]:
        return draft_reply(
            mail_connector,
            thread_id=thread_id or selected_scope_token,
            thread_text=thread_text,
            user_instruction=user_instruction,
        )

    def messages_read_selected_thread(thread_id: str | None = None, selected_scope_token: str | None = None) -> dict[str, object]:
        return read_selected_message_thread(text_connector, thread_id=thread_id or selected_scope_token)

    def messages_summarize_thread(
        thread_id: str | None = None,
        thread_text: str | None = None,
        selected_scope_token: str | None = None,
    ) -> dict[str, object]:
        return summarize_message_thread(text_connector, thread_id=thread_id or selected_scope_token, thread_text=thread_text)

    def messages_draft_reply(
        thread_id: str | None = None,
        thread_text: str | None = None,
        selected_scope_token: str | None = None,
        user_instruction: str = "",
        to: str | None = None,
        context_file: str | None = None,
    ) -> dict[str, object]:
        return draft_message_reply(
            text_connector,
            project_root=project_root,
            thread_id=thread_id,
            thread_text=thread_text,
            selected_scope_token=selected_scope_token,
            user_instruction=user_instruction,
            to=to,
            context_file=context_file,
        )

    def browser_read_selected_tab(selected_scope_token: str | None = None) -> dict[str, object]:
        if not selected_scope_token:
            from agent.tools.errors import ToolError

            raise ToolError("selected_scope_token is required for personal-data access")
        return {
            "tool": "browser.read_selected_tab",
            "configured": False,
            "error": "personal data connector is not configured; selected-scope approved access is required",
        }

    return {
        "contacts.search": contacts_search,
        "contacts.read_selected": contacts_read_selected,
        "calendar.read_date_range": calendar_read_date_range,
        "calendar.find_availability": calendar_find_availability,
        "email.list_metadata": email_list_metadata,
        "email.read_selected_thread": email_read_selected_thread,
        "email.summarize_thread": email_summarize_thread,
        "email.draft_reply": email_draft_reply,
        "messages.read_selected_thread": messages_read_selected_thread,
        "messages.summarize_thread": messages_summarize_thread,
        "messages.draft_reply": messages_draft_reply,
        "browser.read_selected_tab": browser_read_selected_tab,
    }


def _schema(name: str, description: str, properties: dict[str, object], required: list[str] | None = None) -> dict[str, object]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required or [],
                "additionalProperties": False,
            },
        },
    }


PERSONAL_SCHEMAS = {
    "contacts.search": _schema(
        "contacts.search",
        "Search approved selected contacts metadata. Returns compact candidates only.",
        {"query": {"type": "string"}, "max_results": {"type": "integer", "minimum": 1, "maximum": 10}},
        ["query"],
    ),
    "contacts.read_selected": _schema(
        "contacts.read_selected",
        "Read an explicitly selected contact.",
        {
            "selected_scope_token": {"type": "string"},
            "contact_id": {"type": "string"},
            "requested_fields": {"type": "array", "items": {"type": "string"}},
        },
    ),
    "calendar.read_date_range": _schema(
        "calendar.read_date_range",
        "Read an approved selected calendar date range.",
        {
            "start": {"type": "string"},
            "end": {"type": "string"},
            "start_date": {"type": "string"},
            "end_date": {"type": "string"},
            "calendar_filters": {"type": "array", "items": {"type": "string"}},
        },
    ),
    "calendar.find_availability": _schema(
        "calendar.find_availability",
        "Find availability from an approved selected calendar range.",
        {
            "start": {"type": "string"},
            "end": {"type": "string"},
            "start_date": {"type": "string"},
            "end_date": {"type": "string"},
            "duration_minutes": {"type": "integer", "minimum": 5, "maximum": 480},
            "working_hours_start": {"type": "string"},
            "working_hours_end": {"type": "string"},
            "calendar_filters": {"type": "array", "items": {"type": "string"}},
        },
    ),
    "email.list_metadata": _schema(
        "email.list_metadata",
        "List approved email metadata without body content.",
        {"max_results": {"type": "integer", "minimum": 1, "maximum": 25}},
    ),
    "email.read_selected_thread": _schema(
        "email.read_selected_thread",
        "Read one approved selected email thread as untrusted content.",
        {"thread_id": {"type": "string"}, "selected_scope_token": {"type": "string"}},
    ),
    "email.summarize_thread": _schema(
        "email.summarize_thread",
        "Summarize an approved selected email thread as untrusted content.",
        {"thread_id": {"type": "string"}, "thread_text": {"type": "string"}, "selected_scope_token": {"type": "string"}},
    ),
    "email.draft_reply": _schema(
        "email.draft_reply",
        "Draft an email reply without sending.",
        {
            "thread_id": {"type": "string"},
            "thread_text": {"type": "string"},
            "selected_scope_token": {"type": "string"},
            "user_instruction": {"type": "string"},
        },
    ),
    "messages.read_selected_thread": _schema(
        "messages.read_selected_thread",
        "Read one approved selected message thread as untrusted content.",
        {"thread_id": {"type": "string"}, "selected_scope_token": {"type": "string"}},
    ),
    "messages.summarize_thread": _schema(
        "messages.summarize_thread",
        "Summarize an approved selected message thread as untrusted content.",
        {"thread_id": {"type": "string"}, "thread_text": {"type": "string"}, "selected_scope_token": {"type": "string"}},
    ),
    "messages.draft_reply": _schema(
        "messages.draft_reply",
        "Draft a message reply without sending.",
        {
            "thread_id": {"type": "string"},
            "thread_text": {"type": "string"},
            "selected_scope_token": {"type": "string"},
            "user_instruction": {"type": "string"},
            "to": {"type": "string"},
            "context_file": {"type": "string"},
        },
    ),
    "browser.read_selected_tab": _schema("browser.read_selected_tab", "Read an approved selected browser tab.", {"selected_scope_token": {"type": "string"}}),
}
