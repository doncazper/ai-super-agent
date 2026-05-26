from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class NaturalLanguageRequest:
    original_text: str
    no_tools: bool = False
    source: str = "cli"


@dataclass(frozen=True)
class IntentCandidate:
    intent_id: str
    confidence: float
    reason: str
    evidence: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CommandSuggestion:
    command_id: str
    command: str
    description: str
    risk_level: str
    approval_required: str
    status: str
    safe_to_run_directly: bool
    dry_run_available: bool
    setup_hint: str = ""
    docs_link: str = ""
    replacement: str = ""


@dataclass(frozen=True)
class ClarificationQuestion:
    question: str
    reason: str
    clarification_type: str = "ambiguous_intent"
    choices: tuple[str, ...] = field(default_factory=tuple)
    command_examples: tuple[str, ...] = field(default_factory=tuple)
    setup_hint: str = ""
    approval_required: bool = False
    dry_run_required: bool = False


@dataclass(frozen=True)
class NLExecutionPlan:
    command: str = ""
    dry_run_first: bool = False
    approval_required: bool = False
    execution_allowed: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class NLRouteDecision:
    original_text: str
    normalized_text: str
    intent: str
    confidence: float
    command_suggestions: tuple[CommandSuggestion, ...]
    safety_outcome: str
    risk_level: str
    approval_required: bool
    dry_run_required: bool
    clarification_required: bool
    reason: str
    evidence: tuple[str, ...]
    audit_summary: dict[str, object]
    clarification_question: ClarificationQuestion | None = None
    execution_plan: NLExecutionPlan | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
