from __future__ import annotations

from agent.natural_language.models import ClarificationQuestion, CommandSuggestion, IntentCandidate


def build_clarification(
    candidate: IntentCandidate,
    suggestions: tuple[CommandSuggestion, ...] = (),
) -> ClarificationQuestion:
    evidence = set(candidate.evidence)
    examples = tuple(suggestion.command for suggestion in suggestions[:3])
    if "missing_location" in evidence:
        return ClarificationQuestion(
            question="Which location should I use?",
            reason=candidate.reason,
            clarification_type="missing_required_argument",
            choices=("Provide a city/state or city/country", "Use weather config show", "Ask for help"),
            command_examples=examples,
        )
    if "lookup_missing_query" in evidence:
        return ClarificationQuestion(
            question="What should I look up or verify?",
            reason=candidate.reason,
            clarification_type="missing_required_argument",
            choices=("Provide a query", "Provide a URL", "Search command help"),
            command_examples=examples,
        )
    if candidate.intent_id == "personal_data.request":
        return ClarificationQuestion(
            question="Which selected, approval-gated source should I inspect?",
            reason=candidate.reason,
            clarification_type="personal_data_request",
            choices=("Run a connector doctor", "Use a selected approved item", "Cancel"),
            command_examples=examples,
            approval_required=True,
            dry_run_required=True,
        )
    if candidate.intent_id == "send_or_write.request":
        return ClarificationQuestion(
            question="Do you want a dry-run/preflight preview for this send or write action?",
            reason=candidate.reason,
            clarification_type="risky_action",
            choices=("Show preflight", "Create/review an Action Center draft if supported", "Cancel"),
            command_examples=examples,
            approval_required=True,
            dry_run_required=True,
        )
    if suggestions:
        first = suggestions[0]
        if first.status == "deprecated":
            replacement = first.replacement or "Search the command registry for a current replacement."
            return ClarificationQuestion(
                question="That command is deprecated. Use the replacement instead?",
                reason=candidate.reason,
                clarification_type="command_is_deprecated",
                choices=(replacement, "Search command registry", "Cancel"),
                command_examples=examples,
            )
        if first.status == "stubbed":
            return ClarificationQuestion(
                question="That command is not implemented yet. Do you want setup/status help instead?",
                reason=candidate.reason,
                clarification_type="command_is_stubbed",
                choices=("Show setup/status command", "Search command registry", "Cancel"),
                command_examples=examples,
            )
        if first.setup_hint:
            return ClarificationQuestion(
                question="This command may require provider or connector setup. Run a doctor/status command first?",
                reason=candidate.reason,
                clarification_type="provider_missing",
                choices=("Run doctor/status manually", "Show setup docs", "Choose another command"),
                command_examples=examples,
                setup_hint=first.setup_hint,
            )
        if len(suggestions) > 1:
            return ClarificationQuestion(
                question="Which command did you mean?",
                reason=candidate.reason,
                clarification_type="multiple_matching_commands",
                choices=tuple(suggestion.command for suggestion in suggestions[:3]),
                command_examples=examples,
            )
    if candidate.intent_id == "unknown":
        return ClarificationQuestion(
            question="I am not sure which command matches. Search command help?",
            reason=candidate.reason,
            clarification_type="unsupported_capability",
            choices=('python smart_agent.py commands search "<query>"', "Ask a general question", "Cancel"),
            command_examples=examples,
        )
    return ClarificationQuestion(
        question="What would you like me to do?",
        reason=candidate.reason,
        clarification_type="ambiguous_intent",
        choices=("Ask a general question", "Search commands", "Run a safe preflight"),
        command_examples=examples,
    )
