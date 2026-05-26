from __future__ import annotations

from agent.commands.intent_index import suggest_commands
from agent.natural_language.models import (
    ClarificationQuestion,
    CommandSuggestion,
    NaturalLanguageRequest,
    NLExecutionPlan,
    NLRouteDecision,
)
from agent.natural_language.clarification import build_clarification
from agent.natural_language.parser import normalize_text, parse_request
from agent.natural_language.safety import outcome_for_intent


QUERY_BY_INTENT: dict[str, str] = {
    "weather.current": "weather current",
    "web.research": "research web search",
    "command.search": "commands search",
    "session.review": "session review bugs",
    "send_or_write.request": "email send approved action preflight",
    "personal_data.request": "doctor status connector approval",
    "file.write": "files write",
    "memory.add": "memory store preflight",
    "memory.search": "memory search",
    "command.help": "commands help",
    "media.plan": "media plan thumbnail image video audio music dry-run",
}


def route_request(text: str, *, no_tools: bool = False) -> NLRouteDecision:
    request = NaturalLanguageRequest(original_text=text, no_tools=no_tools)
    candidate = parse_request(request)
    outcome, risk, approval, dry_run, clarification = outcome_for_intent(candidate, no_tools=no_tools)
    command_suggestions = _command_suggestions(candidate.intent_id)
    clarification_question = build_clarification(candidate, command_suggestions) if clarification or _needs_clarification(candidate, command_suggestions) else None
    if clarification_question is not None:
        clarification = True
        outcome = "ask_clarifying_question"
    execution_plan = _execution_plan(command_suggestions, approval, dry_run, outcome)
    return NLRouteDecision(
        original_text=text,
        normalized_text=normalize_text(text),
        intent=candidate.intent_id,
        confidence=candidate.confidence,
        command_suggestions=command_suggestions,
        safety_outcome=outcome,
        risk_level=risk,
        approval_required=approval,
        dry_run_required=dry_run,
        clarification_required=clarification,
        reason=candidate.reason,
        evidence=candidate.evidence,
        audit_summary={
            "intent": candidate.intent_id,
            "risk_level": risk,
            "safety_outcome": outcome,
            "approval_required": approval,
            "dry_run_required": dry_run,
            "command_count": len(command_suggestions),
            "tools_called": [],
            "personal_data_accessed": False,
            "commands_executed": [],
        },
        clarification_question=clarification_question,
        execution_plan=execution_plan,
    )


def _command_suggestions(intent_id: str) -> tuple[CommandSuggestion, ...]:
    if intent_id == "chat.no_tools":
        return ()
    query = QUERY_BY_INTENT.get(intent_id, intent_id)
    suggestions = suggest_commands(query, limit=20 if intent_id == "media.plan" else 5)
    if intent_id == "media.plan":
        suggestions = sorted(
            suggestions,
            key=lambda item: (
                not item.entry.command.startswith("python smart_agent.py media plan"),
                item.entry.command,
            ),
        )
    return tuple(
        CommandSuggestion(
            command_id=item.entry.command_id,
            command=item.entry.command,
            description=item.entry.description,
            risk_level=item.entry.risk_level,
            approval_required=item.entry.approval_required,
            status=item.entry.status,
            safe_to_run_directly=item.entry.safe_to_run_directly and intent_id not in {"send_or_write.request", "personal_data.request"},
            dry_run_available=item.entry.dry_run_available,
            setup_hint=item.entry.setup_hint,
            docs_link=item.entry.docs_link,
            replacement=item.entry.replacement,
        )
        for item in suggestions
    )


def _needs_clarification(candidate: object, suggestions: tuple[CommandSuggestion, ...]) -> bool:
    evidence = getattr(candidate, "evidence", ())
    if "lookup_missing_query" in evidence or "missing_location" in evidence:
        return True
    if getattr(candidate, "intent_id", "") in {"personal_data.request", "send_or_write.request"}:
        return True
    if len(suggestions) > 1 and getattr(candidate, "confidence", 0.0) < 0.8:
        return True
    if suggestions and suggestions[0].status in {"deprecated", "stubbed"}:
        return True
    return False


def _execution_plan(
    suggestions: tuple[CommandSuggestion, ...],
    approval_required: bool,
    dry_run_required: bool,
    outcome: str,
) -> NLExecutionPlan:
    command = suggestions[0].command if suggestions else ""
    return NLExecutionPlan(
        command=command,
        dry_run_first=dry_run_required,
        approval_required=approval_required,
        execution_allowed=False,
        notes=(
            "Natural-language routing only prepares suggestions.",
            f"Safety outcome: {outcome}.",
            "Any real execution must use the exact command path and existing safety gates.",
        ),
    )
