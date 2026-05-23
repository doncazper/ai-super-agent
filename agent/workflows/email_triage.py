from __future__ import annotations

import json
from typing import Any

from agent.core.tool_broker import ToolBroker


def email_triage(
    broker: ToolBroker,
    *,
    selected_thread: str | None = None,
    max_results: int = 10,
    dry_run: bool = False,
) -> dict[str, object]:
    steps: list[dict[str, Any]] = []
    limitations: list[str] = []
    metadata_step = _execute_step(
        broker,
        "email_triage_metadata",
        "email.list_metadata",
        {"max_results": max_results},
        dry_run=dry_run,
    )
    steps.append(metadata_step)
    metadata = metadata_step["content"]
    categories: list[dict[str, object]] = []
    if _is_dry_run_step(metadata_step):
        limitations.append("Dry-run only; no email provider actions were executed.")
    elif metadata_step["allowed"] and metadata.get("status") == "ok":
        categories = [_classify_metadata(item) for item in _messages(metadata)]
    else:
        limitations.append(f"Email metadata unavailable: {metadata.get('error', 'metadata read denied')}")

    selected: dict[str, object] | None = None
    summary: dict[str, object] | None = None
    draft: dict[str, object] | None = None
    thread_id = (selected_thread or "").strip()
    if thread_id:
        read_step = _execute_step(
            broker,
            "email_triage_read_selected",
            "email.read_selected_thread",
            {"thread_id": thread_id},
            dry_run=dry_run,
        )
        steps.append(read_step)
        read_content = read_step["content"]
        if _is_dry_run_step(read_step):
            selected = {"status": "planned", "thread_id": thread_id}
        elif read_step["allowed"] and read_content.get("status") == "ok":
            selected = {
                "status": "ok",
                "thread": read_content.get("thread", {}),
                "body_included": False,
                "content_safety_notice": read_content.get("content_safety_notice"),
                "trust_level": read_content.get("trust_level", "UNTRUSTED_EMAIL"),
                "stored_in_memory": False,
            }
            thread_text = str(read_content.get("content", ""))
            read_step["content"] = _redact_thread_content(read_content)
            summary_step = _execute_step(
                broker,
                "email_triage_summarize_selected",
                "email.summarize_thread",
                {"thread_id": thread_id, "thread_text": thread_text},
                dry_run=dry_run,
            )
            steps.append(summary_step)
            if summary_step["allowed"] and summary_step["content"].get("status") == "ok":
                summary = summary_step["content"]
            else:
                limitations.append(f"Selected thread summary unavailable: {summary_step['content'].get('error', 'summary denied')}")
            draft_step = _execute_step(
                broker,
                "email_triage_draft_selected",
                "email.draft_reply",
                {
                    "thread_id": thread_id,
                    "thread_text": thread_text,
                    "user_instruction": "Draft a concise, professional reply. Do not include secrets or commitments not supported by the email.",
                },
                dry_run=dry_run,
            )
            steps.append(draft_step)
            if draft_step["allowed"] and draft_step["content"].get("status") == "ok":
                draft = draft_step["content"]
            else:
                limitations.append(f"Selected thread draft unavailable: {draft_step['content'].get('error', 'draft denied')}")
        else:
            selected = {"status": "skipped", "thread_id": thread_id, "error": read_content.get("error", "thread read denied")}
            limitations.append(f"Selected thread unavailable: {selected['error']}")

    payload: dict[str, object] = {
        "status": _status(steps, limitations),
        "workflow": "email_triage_v1",
        "dry_run": dry_run or broker.dry_run_mode,
        "metadata_only": not bool(thread_id),
        "metadata": {
            "status": metadata.get("status", "unknown"),
            "configured": metadata.get("configured"),
            "messages": _metadata_summaries(metadata),
            "body_included": False,
            "trust_level": metadata.get("trust_level", "UNTRUSTED_EMAIL"),
            "stored_in_memory": False,
            "setup": metadata.get("setup", []),
        },
        "priority": categories,
        "selected_thread": selected,
        "summary": summary,
        "draft_reply": draft,
        "limitations": limitations,
        "memory_written": False,
        "sends_or_mutations": False,
        "source_policy": (
            "Email metadata and bodies are UNTRUSTED_EMAIL. Metadata triage never reads bodies. "
            "Selected thread bodies are read only when explicitly selected and approved. "
            "No email is sent, deleted, moved, archived, or stored in memory by default."
        ),
        "steps": steps,
    }
    payload["briefing"] = format_email_triage(payload)
    return payload


def format_email_triage(payload: dict[str, object]) -> str:
    lines = [
        "Email triage",
        f"Status: {payload.get('status')}",
        "",
        "Priority:",
    ]
    priorities = payload.get("priority")
    if isinstance(priorities, list) and priorities:
        for item in priorities:
            if isinstance(item, dict):
                lines.append(
                    f"- {item.get('priority')}: {item.get('subject')} "
                    f"from {item.get('sender_display')} ({item.get('reason')})"
                )
    else:
        lines.append("- unavailable")
    selected = payload.get("selected_thread")
    if isinstance(selected, dict) and selected:
        lines.extend(["", "Selected thread:", f"- status: {selected.get('status')}"])
    summary = payload.get("summary")
    if isinstance(summary, dict) and summary.get("summary"):
        lines.extend(["", "Summary:", str(summary["summary"])])
    draft = payload.get("draft_reply")
    if isinstance(draft, dict) and draft.get("draft"):
        lines.extend(["", "Draft reply:", str(draft["draft"])])
    limitations = payload.get("limitations")
    if isinstance(limitations, list) and limitations:
        lines.extend(["", "Limitations:"])
        lines.extend(f"- {item}" for item in limitations)
    lines.extend(["", str(payload.get("source_policy", ""))])
    return "\n".join(lines)


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


def _status(steps: list[dict[str, Any]], limitations: list[str]) -> str:
    if any(_is_dry_run_step(step) for step in steps):
        return "dry_run"
    if not steps or not steps[0]["allowed"]:
        return "blocked"
    if limitations:
        return "limited"
    return "ok"


def _messages(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    messages = metadata.get("messages")
    return [item for item in messages if isinstance(item, dict)] if isinstance(messages, list) else []


def _metadata_summaries(metadata: dict[str, Any]) -> list[dict[str, object]]:
    summaries = []
    for item in _messages(metadata):
        summaries.append(
            {
                "thread_id": item.get("thread_id", ""),
                "sender_display": item.get("sender_display", ""),
                "subject": item.get("subject", ""),
                "date": item.get("date", ""),
                "snippet_included": bool(item.get("snippet")),
            }
        )
    return summaries


def _classify_metadata(item: dict[str, Any]) -> dict[str, object]:
    subject = str(item.get("subject", ""))
    sender = str(item.get("sender_display", ""))
    snippet = str(item.get("snippet", ""))
    haystack = f"{subject} {sender} {snippet}".casefold()
    if any(word in haystack for word in ("urgent", "asap", "action required", "deadline", "overdue")):
        priority = "high"
        reason = "urgent/action language in metadata"
    elif any(word in haystack for word in ("meeting", "invoice", "proposal", "review", "contract")):
        priority = "medium"
        reason = "work/decision-related metadata"
    elif any(word in haystack for word in ("newsletter", "digest", "promo", "sale", "unsubscribe")):
        priority = "low"
        reason = "broadcast or promotional metadata"
    else:
        priority = "normal"
        reason = "no high-priority signal in metadata"
    return {
        "thread_id": item.get("thread_id", ""),
        "sender_display": sender,
        "subject": subject,
        "date": item.get("date", ""),
        "priority": priority,
        "reason": reason,
        "body_read": False,
    }


def _redact_thread_content(content: dict[str, Any]) -> dict[str, Any]:
    redacted = dict(content)
    if "content" in redacted:
        redacted["content"] = "[UNTRUSTED_EMAIL_BODY_REDACTED_FROM_TRIAGE_REPORT]"
    return redacted
