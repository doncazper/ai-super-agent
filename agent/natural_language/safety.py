from __future__ import annotations

from agent.natural_language.models import IntentCandidate


HIGH_RISK_INTENTS = {"personal_data.request", "send_or_write.request"}
CLARIFICATION_INTENTS = {"ambiguous"}
HELP_INTENTS = {"unknown", "command.help", "command.search"}


def outcome_for_intent(candidate: IntentCandidate, *, no_tools: bool = False) -> tuple[str, str, bool, bool, bool]:
    """Return safety outcome, risk, approval, dry-run, clarification flags."""
    if no_tools:
        return "answer_directly", "SAFE", False, False, False
    if candidate.intent_id == "ambiguous":
        return "ask_clarifying_question", "SAFE", False, False, True
    if candidate.intent_id == "unknown":
        return "handoff_to_help", "SAFE", False, False, False
    if candidate.intent_id == "personal_data.request":
        return "require_approval", "HIGH", True, True, False
    if candidate.intent_id == "send_or_write.request":
        return "dry_run_only", "CRITICAL", True, True, False
    if candidate.intent_id == "file.write":
        return "dry_run_only", "MEDIUM", True, True, False
    if candidate.intent_id == "media.plan":
        return "dry_run_only", "LOW", False, True, False
    if candidate.intent_id in {"file.read", "file.summarize", "memory.add"}:
        return "dry_run_only", "MEDIUM", False, True, False
    if candidate.intent_id in HELP_INTENTS:
        return "show_command_suggestion", "SAFE", False, False, False
    return "show_command_suggestion", "LOW", False, False, False
