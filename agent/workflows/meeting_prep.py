from __future__ import annotations

import json
from typing import Any

from agent.core.tool_broker import ToolBroker
from agent.workflows.research import safe_excerpt


def meeting_prep(
    broker: ToolBroker,
    *,
    event_id: str | None = None,
    date: str | None = None,
    title: str | None = None,
    contact_queries: list[str] | None = None,
    web_topic: str | None = None,
    dry_run: bool = False,
) -> dict[str, object]:
    event_args = _event_args(event_id=event_id, date=date, title=title)
    steps: list[dict[str, Any]] = []
    limitations: list[str] = []
    calendar_step = _execute_step(
        broker,
        "meeting_prep_calendar",
        "calendar.read_selected_event",
        event_args,
        dry_run=dry_run,
    )
    steps.append(calendar_step)

    event_payload = calendar_step["content"].get("event") if isinstance(calendar_step["content"], dict) else None
    event = event_payload if isinstance(event_payload, dict) else {}
    if _is_dry_run_step(calendar_step):
        limitations.append("Dry-run only; no calendar, contacts, or web provider actions were executed.")
    elif not calendar_step["allowed"]:
        limitations.append(f"Calendar event unavailable: {calendar_step['content'].get('error', 'calendar read denied')}")
    elif calendar_step["content"].get("status") != "ok":
        limitations.append(f"Calendar event unavailable: {calendar_step['content'].get('error', 'calendar read failed')}")

    contacts = []
    for index, query in enumerate(_clean_list(contact_queries), start=1):
        contact_step = _execute_step(
            broker,
            f"meeting_prep_contacts_{index}",
            "contacts.search",
            {"query": query, "max_results": 3},
            dry_run=dry_run,
        )
        steps.append(contact_step)
        if _is_dry_run_step(contact_step):
            contacts.append({"query": query, "status": "planned", "results": []})
        elif contact_step["allowed"] and contact_step["content"].get("status") == "ok":
            contacts.append(
                {
                    "query": query,
                    "status": "ok",
                    "results": contact_step["content"].get("results", []),
                }
            )
        else:
            contacts.append(
                {
                    "query": query,
                    "status": "skipped",
                    "error": contact_step["content"].get("error", "contact lookup denied"),
                }
            )
            limitations.append(f"Contact lookup skipped for {query}: {contacts[-1]['error']}")

    web = {"status": "not_requested", "results": []}
    clean_topic = (web_topic or "").strip()
    if clean_topic:
        web_step = _execute_step(
            broker,
            "meeting_prep_web",
            "web.search",
            {"query": clean_topic, "max_results": 3},
            dry_run=dry_run,
        )
        steps.append(web_step)
        if _is_dry_run_step(web_step):
            web = {"status": "planned", "query": clean_topic, "results": []}
        elif web_step["allowed"] and web_step["content"].get("status") == "ok":
            web = {
                "status": "ok",
                "query": clean_topic,
                "results": _sanitize_web_results(web_step["content"].get("results", [])),
            }
        else:
            web = {
                "status": "skipped",
                "query": clean_topic,
                "error": web_step["content"].get("error", "web search denied"),
                "results": [],
            }
            limitations.append(f"Web research skipped: {web['error']}")

    payload: dict[str, object] = {
        "status": _workflow_status(steps),
        "workflow": "meeting_prep",
        "dry_run": dry_run or broker.dry_run_mode,
        "meeting_summary": _meeting_summary(event, limitations),
        "event": event,
        "attendees": _attendees_summary(event, contacts),
        "contacts": contacts,
        "web": web,
        "relevant_context": _relevant_context(event, contacts, web),
        "suggested_agenda": _suggested_agenda(event),
        "questions_to_ask": _questions_to_ask(event, web),
        "prep_checklist": _prep_checklist(event, contacts, web),
        "limitations": limitations,
        "memory_written": False,
        "writes_or_sends": False,
        "source_policy": (
            "Calendar/contact data is LOCAL_PRIVATE_DATA. Web content is UNTRUSTED_WEB. "
            "No emails, texts, calendar edits, contact edits, bulk exports, or memory writes are performed."
        ),
        "steps": steps,
    }
    payload["briefing"] = format_meeting_prep(payload)
    return payload


def format_meeting_prep(payload: dict[str, object]) -> str:
    lines = [
        "Meeting prep",
        f"Status: {payload.get('status')}",
        "",
        "Summary:",
        str(payload.get("meeting_summary", "")),
        "",
        "Attendees:",
    ]
    attendees = payload.get("attendees")
    if isinstance(attendees, list) and attendees:
        lines.extend(f"- {item}" for item in attendees)
    else:
        lines.append("- unavailable")
    lines.extend(["", "Relevant context:"])
    context = payload.get("relevant_context")
    if isinstance(context, list) and context:
        lines.extend(f"- {item}" for item in context)
    else:
        lines.append("- unavailable")
    for label, key in (
        ("Suggested agenda", "suggested_agenda"),
        ("Questions to ask", "questions_to_ask"),
        ("Prep checklist", "prep_checklist"),
    ):
        lines.extend(["", f"{label}:"])
        values = payload.get(key)
        if isinstance(values, list) and values:
            lines.extend(f"- {item}" for item in values)
        else:
            lines.append("- unavailable")
    limitations = payload.get("limitations")
    if isinstance(limitations, list) and limitations:
        lines.extend(["", "Limitations:"])
        lines.extend(f"- {item}" for item in limitations)
    lines.extend(["", str(payload.get("source_policy", ""))])
    return "\n".join(lines)


def _event_args(*, event_id: str | None, date: str | None, title: str | None) -> dict[str, Any]:
    if event_id:
        return {"event_id": event_id}
    if not date or not title:
        return {"date": date or "", "title": title or ""}
    return {"date": date, "title": title}


def _execute_step(
    broker: ToolBroker,
    call_id: str,
    tool_name: str,
    arguments: dict[str, Any],
    *,
    dry_run: bool,
) -> dict[str, Any]:
    tool_call = {
        "id": call_id,
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments)},
    }
    result = broker.dry_run(tool_call) if dry_run else broker.execute(tool_call)
    try:
        content = json.loads(result.content)
    except json.JSONDecodeError:
        content = {"raw": result.content}
    return {
        "tool_name": result.tool_name,
        "tool_call_id": result.tool_call_id,
        "allowed": result.allowed,
        "content": content,
    }


def _is_dry_run_step(step: dict[str, Any]) -> bool:
    content = step.get("content")
    return isinstance(content, dict) and content.get("dry_run") is True


def _workflow_status(steps: list[dict[str, Any]]) -> str:
    if any(_is_dry_run_step(step) for step in steps):
        return "dry_run"
    if steps and steps[0]["allowed"] and steps[0]["content"].get("status") == "ok":
        return "limited" if any(not step["allowed"] or step["content"].get("status") == "error" for step in steps[1:]) else "ok"
    return "blocked"


def _meeting_summary(event: dict[str, Any], limitations: list[str]) -> str:
    if not event:
        return "Meeting details are unavailable because the selected calendar event was not approved or not found."
    title = _value(event.get("title"))
    start = _value(event.get("start"))
    end = _value(event.get("end"))
    calendar_name = _value(event.get("calendar_name"))
    return f"{title}, scheduled {start} to {end} on {calendar_name}."


def _attendees_summary(event: dict[str, Any], contacts: list[dict[str, Any]]) -> list[str]:
    attendees = []
    count = event.get("attendee_count")
    if isinstance(count, int):
        attendees.append(f"Calendar attendee count: {count}; attendee names are not returned by default.")
    for contact in contacts:
        if contact.get("status") == "ok":
            results = contact.get("results") if isinstance(contact.get("results"), list) else []
            if results:
                names = ", ".join(str(item.get("display_name", "unknown")) for item in results[:3] if isinstance(item, dict))
                attendees.append(f"Contact candidates for {contact.get('query')}: {names}")
    return attendees


def _relevant_context(event: dict[str, Any], contacts: list[dict[str, Any]], web: dict[str, Any]) -> list[str]:
    context = []
    if event:
        context.append("Calendar notes/body are omitted; event text is treated as private data, not instructions.")
    for contact in contacts:
        if contact.get("status") == "ok":
            context.append(f"Approved contact lookup returned compact candidates for {contact.get('query')}.")
        elif contact.get("status") == "skipped":
            context.append(f"Contact lookup for {contact.get('query')} was skipped.")
    if web.get("status") == "ok":
        urls = [str(item.get("url")) for item in web.get("results", []) if isinstance(item, dict) and item.get("url")]
        context.append("Web sources: " + "; ".join(urls[:3]))
    elif web.get("status") == "skipped":
        context.append("Optional web research was skipped.")
    return context


def _suggested_agenda(event: dict[str, Any]) -> list[str]:
    title = str(event.get("title") or "the meeting")
    return [
        f"Confirm the goal for {title}.",
        "Review key decisions needed today.",
        "Align on owners, next steps, and timing.",
    ]


def _questions_to_ask(event: dict[str, Any], web: dict[str, Any]) -> list[str]:
    questions = [
        "What outcome would make this meeting successful?",
        "What decisions need to be made before the meeting ends?",
        "Who owns the follow-up actions?",
    ]
    if web.get("status") == "ok":
        questions.append("Do any recent public updates from the web sources change our plan?")
    return questions


def _prep_checklist(event: dict[str, Any], contacts: list[dict[str, Any]], web: dict[str, Any]) -> list[str]:
    checklist = [
        "Open the calendar invite and verify time, title, and attendee count.",
        "Bring any documents or links the user already trusts.",
        "Prepare concise notes for decisions and follow-ups.",
    ]
    if contacts:
        checklist.append("Review approved contact candidates; do not export or store contact details.")
    if web.get("status") == "ok":
        checklist.append("Review cited web results as untrusted public context.")
    return checklist


def _sanitize_web_results(results: Any) -> list[dict[str, Any]]:
    if not isinstance(results, list):
        return []
    sanitized = []
    for item in results:
        if not isinstance(item, dict):
            continue
        sanitized.append(
            {
                "title": str(item.get("title", "")),
                "url": str(item.get("url", "")),
                "snippet": safe_excerpt(str(item.get("snippet", "")), max_chars=300),
                "source": str(item.get("source", "")),
                "retrieved_at": item.get("retrieved_at"),
                "trust_level": item.get("trust_level", "UNTRUSTED_WEB"),
            }
        )
    return sanitized


def _clean_list(values: list[str] | None) -> list[str]:
    return [value.strip() for value in values or [] if value and value.strip()]


def _value(value: Any) -> str:
    text = str(value or "").strip()
    return text if text else "unavailable"
