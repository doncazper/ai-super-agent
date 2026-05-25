from __future__ import annotations

from agent.leads.models import LeadClassification, LeadPriority, LeadRecord


INJECTION_MARKERS = (
    "ignore previous",
    "ignore all previous",
    "change policy",
    "disable audit",
    "approve this",
    "approve action",
    "call tool",
    "execute tool",
    "reveal secret",
    "send immediately",
    "auto-send",
)


def classify_lead(lead: LeadRecord) -> LeadClassification:
    text = f"{lead.subject_or_context} {lead.message_preview}".casefold()
    reasons: list[str] = []
    tags = set(lead.tags)
    priority = lead.priority
    if any(term in text for term in ("urgent", "asap", "today", "deadline")):
        priority = LeadPriority.URGENT
        tags.add("time_sensitive")
        reasons.append("time-sensitive language")
    if any(term in text for term in ("pricing", "quote", "budget", "proposal")):
        if priority is LeadPriority.NORMAL:
            priority = LeadPriority.HIGH
        tags.add("sales")
        reasons.append("sales or quote intent")
    if any(term in text for term in ("meeting", "call", "schedule", "demo")):
        tags.add("meeting_request")
        reasons.append("meeting or scheduling intent")
    if any(marker in text for marker in INJECTION_MARKERS):
        tags.add("prompt_injection_attempt")
        reasons.append("untrusted instructions were treated as data")
    if not reasons:
        reasons.append("no high-risk or urgent signals detected")
    return LeadClassification(
        lead_id=lead.lead_id,
        priority=priority,
        tags=sorted(tags),
        reasons=reasons,
        suggested_next_step=_next_step(priority, tags),
    )


def sanitize_untrusted_lead_text(value: str) -> str:
    safe_lines: list[str] = []
    for line in value.splitlines() or [value]:
        lowered = line.casefold()
        if any(marker in lowered for marker in INJECTION_MARKERS):
            continue
        safe_lines.append(line.strip())
    cleaned = " ".join(part for part in safe_lines if part)
    return cleaned or "[untrusted instruction-like content omitted]"


def _next_step(priority: LeadPriority, tags: set[str]) -> str:
    if "prompt_injection_attempt" in tags:
        return "review manually before drafting"
    if "meeting_request" in tags:
        return "draft response and optionally suggest meeting times"
    if priority in {LeadPriority.HIGH, LeadPriority.URGENT}:
        return "draft response for user review"
    return "review when convenient"
