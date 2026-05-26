from __future__ import annotations

from agent.natural_language.clarification import build_clarification
from agent.natural_language.models import ClarificationQuestion, IntentCandidate, NLRouteDecision
from agent.safety.redaction import SecretRedactor


def clarification_for_decision(decision: NLRouteDecision) -> ClarificationQuestion:
    if decision.clarification_question is not None:
        return decision.clarification_question
    return build_clarification(
        IntentCandidate(decision.intent, decision.confidence, decision.reason, decision.evidence),
        decision.command_suggestions,
    )


def format_clarification_preview(decision: NLRouteDecision) -> str:
    redactor = SecretRedactor()
    question = clarification_for_decision(decision)
    lines = [
        f"Intent: {redactor.redact_text(decision.intent)}",
        f"Safety outcome: {decision.safety_outcome}",
        f"Clarification type: {question.clarification_type}",
        f"Question: {redactor.redact_text(question.question)}",
        f"Reason: {redactor.redact_text(question.reason)}",
    ]
    if question.approval_required or question.dry_run_required:
        lines.append(
            f"Safety: approval_required={question.approval_required}, dry_run_required={question.dry_run_required}"
        )
    if question.setup_hint:
        lines.append(f"Setup hint: {redactor.redact_text(question.setup_hint)}")
    if question.choices:
        lines.append("Choices:")
        lines.extend(f"- {redactor.redact_text(choice)}" for choice in question.choices)
    if question.command_examples:
        lines.append("Command examples:")
        lines.extend(f"- {redactor.redact_text(example)}" for example in question.command_examples)
    lines.append("No commands have been executed.")
    return "\n".join(lines)
