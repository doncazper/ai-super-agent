from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
import re

from agent.natural_language.models import CommandSuggestion, NLRouteDecision
from agent.natural_language.router import route_request
from agent.safety.redaction import SecretRedactor
from agent.ui.command_registry import get_command


SAFE_RISKS = {"SAFE", "LOW"}
APPROVAL_RISKS = {"HIGH", "CRITICAL"}


@dataclass(frozen=True)
class NaturalLanguageExecutionPlan:
    plan_id: str
    original_request: str
    intent: str
    command: str
    args: tuple[str, ...]
    risk_level: str
    trust_level: str
    approval_required: bool
    dry_run_required: bool
    toolbroker_required: bool
    expected_side_effects: tuple[str, ...]
    provider_requirements: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    audit_preview: dict[str, object]
    memory_behavior: str
    safe_to_execute: bool
    reason: str
    command_id: str = ""
    docs_link: str = ""
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_execution_plan(request: str, *, no_tools: bool = False) -> NaturalLanguageExecutionPlan:
    decision = route_request(request, no_tools=no_tools)
    suggestion = decision.command_suggestions[0] if decision.command_suggestions else None
    record = get_command(suggestion.command_id) if suggestion else None
    command = suggestion.command if suggestion else 'python smart_agent.py commands search "<query>"'
    risk_level = _risk_level(decision, suggestion)
    approval_required = _approval_required(decision, suggestion, risk_level)
    dry_run_required = decision.dry_run_required or approval_required or risk_level in {"MEDIUM", "HIGH", "CRITICAL"}
    provider_requirements = _provider_requirements(suggestion, record)
    missing_requirements = _missing_requirements(decision, suggestion, record)
    safe_to_execute = (
        bool(suggestion)
        and decision.intent not in {"unknown", "ambiguous", "personal_data.request", "send_or_write.request"}
        and risk_level in SAFE_RISKS
        and not approval_required
        and not dry_run_required
        and not missing_requirements
        and suggestion.safe_to_run_directly
    )
    return NaturalLanguageExecutionPlan(
        plan_id=_plan_id(request, decision.intent, command),
        original_request=SecretRedactor().redact_text(request),
        intent=decision.intent,
        command=command,
        args=_extract_args(decision, request),
        risk_level=risk_level,
        trust_level=record.trust_level if record else "TRUSTED_USER request metadata",
        approval_required=approval_required,
        dry_run_required=dry_run_required,
        toolbroker_required=bool(record and record.toolbroker_path not in {"n/a", "none"}),
        expected_side_effects=_side_effects(record),
        provider_requirements=provider_requirements,
        missing_requirements=missing_requirements,
        audit_preview=_audit_preview(decision, suggestion, risk_level, approval_required, dry_run_required),
        memory_behavior=record.memory_behavior if record else "no memory write",
        safe_to_execute=safe_to_execute,
        reason=decision.reason,
        command_id=suggestion.command_id if suggestion else "",
        docs_link=suggestion.docs_link if suggestion else "docs/COMMAND_REGISTRY.md",
        notes=_notes(decision, suggestion, missing_requirements),
    )


def _plan_id(request: str, intent: str, command: str) -> str:
    digest = sha256(f"{request}\0{intent}\0{command}".encode("utf-8")).hexdigest()[:12]
    return f"nlplan_{digest}"


def _risk_level(decision: NLRouteDecision, suggestion: CommandSuggestion | None) -> str:
    if decision.risk_level in APPROVAL_RISKS or decision.intent in {"personal_data.request", "send_or_write.request"}:
        return decision.risk_level
    if suggestion and suggestion.risk_level in {"SAFE", "LOW", "MEDIUM", "HIGH", "CRITICAL", "FORBIDDEN"}:
        return suggestion.risk_level
    return decision.risk_level


def _approval_required(decision: NLRouteDecision, suggestion: CommandSuggestion | None, risk_level: str) -> bool:
    if decision.approval_required or risk_level in APPROVAL_RISKS:
        return True
    if suggestion and suggestion.approval_required.lower() not in {"", "no", "none", "n/a"}:
        return True
    return False


def _provider_requirements(suggestion: CommandSuggestion | None, record: object | None) -> tuple[str, ...]:
    requirements: list[str] = []
    if record is not None:
        connector = getattr(record, "requires_connector", "")
        provider = getattr(record, "requires_provider", "")
        if connector and connector.lower() not in {"none", "n/a"}:
            requirements.append(f"connector: {connector}")
        if provider and provider.lower() not in {"none", "n/a"}:
            requirements.append(f"provider: {provider}")
    if suggestion and suggestion.setup_hint:
        requirements.append(f"setup_hint: {suggestion.setup_hint}")
    return tuple(dict.fromkeys(requirements))


def _missing_requirements(
    decision: NLRouteDecision,
    suggestion: CommandSuggestion | None,
    record: object | None,
) -> tuple[str, ...]:
    missing: list[str] = []
    if decision.intent in {"unknown", "ambiguous"}:
        missing.append("deterministic intent or exact command")
    if decision.intent == "web.research":
        missing.append("configured web/search provider or local web index")
    if suggestion and suggestion.status == "stubbed":
        missing.append("implemented command")
    if suggestion and suggestion.status == "deprecated":
        missing.append("current replacement command")
    if record is not None and getattr(record, "status", "") in {"planned", "blocked", "removed"}:
        missing.append(f"command status is {record.status}")
    return tuple(dict.fromkeys(missing))


def _side_effects(record: object | None) -> tuple[str, ...]:
    if record is None:
        return ("none; no command selected",)
    side_effects = getattr(record, "side_effects", "none") or "none"
    return tuple(part.strip() for part in re.split(r",|;", side_effects) if part.strip()) or ("none",)


def _extract_args(decision: NLRouteDecision, request: str) -> tuple[str, ...]:
    if decision.intent == "weather.current":
        match = re.search(r"\b(?:in|for|at|near)\s+(.+)$", request, flags=re.IGNORECASE)
        if match:
            return (match.group(1).strip(" .?\"'"),)
    if decision.intent == "web.research":
        cleaned = re.sub(r"^\s*(look up|search for|verify|cite|with sources)\s+", "", request, flags=re.IGNORECASE).strip()
        return (cleaned,) if cleaned else ()
    return ()


def _audit_preview(
    decision: NLRouteDecision,
    suggestion: CommandSuggestion | None,
    risk_level: str,
    approval_required: bool,
    dry_run_required: bool,
) -> dict[str, object]:
    return {
        "event": "nl.preflight",
        "intent": decision.intent,
        "risk_level": risk_level,
        "approval_required": approval_required,
        "dry_run_required": dry_run_required,
        "command_id": suggestion.command_id if suggestion else "",
        "tools_called": [],
        "commands_executed": [],
        "personal_data_accessed": False,
    }


def _notes(
    decision: NLRouteDecision,
    suggestion: CommandSuggestion | None,
    missing_requirements: tuple[str, ...],
) -> tuple[str, ...]:
    notes = ["Preflight executes no tools or commands."]
    if missing_requirements:
        notes.append("Resolve missing requirements before execution.")
    if decision.approval_required:
        notes.append("Approval must be handled by the existing Action Center/ApprovalManager path.")
    if suggestion and not suggestion.safe_to_run_directly:
        notes.append("Command suggestion is not safe to run directly from natural language.")
    return tuple(notes)
