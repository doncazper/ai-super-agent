from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class CommandIntentEntry:
    command_id: str
    command: str
    group: str
    description: str
    examples: tuple[str, ...]
    aliases: tuple[str, ...]
    natural_language_triggers: tuple[str, ...]
    intent_ids: tuple[str, ...]
    risk_level: str
    approval_required: str
    provider_required: str
    connector_required: str
    safe_to_run_directly: bool
    dry_run_available: bool
    docs_link: str
    status: str
    setup_hint: str = ""
    replacement: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CommandSuggestion:
    entry: CommandIntentEntry
    score: int
    matched_terms: tuple[str, ...] = field(default_factory=tuple)
    primary: bool = False
    safety_note: str = ""

    def to_dict(self) -> dict[str, object]:
        payload = self.entry.to_dict()
        payload.update(
            {
                "score": self.score,
                "matched_terms": list(self.matched_terms),
                "primary": self.primary,
                "safety_note": self.safety_note,
            }
        )
        return payload
