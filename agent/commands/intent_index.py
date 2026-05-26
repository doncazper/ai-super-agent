from __future__ import annotations

import json
import re
from collections.abc import Iterable, Sequence
from dataclasses import asdict
from typing import Any

from agent.commands.models import CommandIntentEntry, CommandSuggestion
from agent.ui.command_registry import CommandRecord, list_commands


ACTIVE_STATUSES = {"active", "experimental"}
NON_PRIMARY_STATUSES = {"planned", "stubbed", "deprecated", "legacy", "removed", "blocked"}
HIGH_RISK = {"HIGH", "CRITICAL", "FORBIDDEN"}

EXPLICIT_ALIASES: dict[str, tuple[str, ...]] = {
    "Weather": ("weather", "forecast", "temperature", "alerts", "rain", "storm"),
    "Web/research": ("search", "research", "look up", "verify", "browse", "source", "citations"),
    "News": ("news", "headlines", "brief", "timeline", "current events"),
    "Forum": ("forum", "reddit", "v2ex", "discussion", "thread"),
    "Forums": ("forum", "reddit", "v2ex", "discussion", "thread"),
    "Language": ("translate", "language", "detect language", "glossary"),
    "PromptOps/workbench": ("prompt", "queue", "prompt pack", "next prompt"),
    "Quality/evals": ("commands", "qa", "validate", "eval", "test"),
    "Session logging": ("session", "log", "replay"),
    "Feedback": ("feedback", "bug", "confusing", "unsafe"),
    "Core runtime": ("chat", "no tools", "debug", "setup"),
    "Doctor/status/config": ("doctor", "status", "setup", "config"),
    "Memory": ("memory", "remember", "recall", "context"),
    "Workspace/files": ("file", "workspace", "read file", "summarize file"),
    "Self-improvement": ("git", "diff", "tests", "commit", "improve"),
    "Creative media": ("media", "thumbnail", "image", "video", "audio", "music", "tts", "creative", "podcast cover"),
}

INTENT_BY_GROUP_KEYWORD: tuple[tuple[str, str], ...] = (
    ("weather", "weather.current"),
    ("web", "web.research"),
    ("research", "web.research"),
    ("news", "news.brief"),
    ("reddit", "reddit.search"),
    ("forum", "reddit.search"),
    ("v2ex", "reddit.search"),
    ("language", "docs.lookup"),
    ("prompt", "prompt.queue"),
    ("command", "command.search"),
    ("quality", "command.search"),
    ("eval", "test.run"),
    ("test", "test.run"),
    ("session", "session.review"),
    ("feedback", "bug.report"),
    ("bug", "bug.report"),
    ("memory", "memory.search"),
    ("file", "file.read"),
    ("workspace", "file.read"),
    ("backup", "file.read"),
    ("doctor", "doctor.status"),
    ("status", "doctor.status"),
    ("core", "chat.general"),
    ("brain", "doctor.status"),
    ("platform", "doctor.status"),
    ("git", "git.status"),
    ("self-improvement", "git.status"),
    ("media", "media.plan"),
    ("thumbnail", "media.plan"),
    ("creative", "media.plan"),
)


def build_intent_index(records: Sequence[CommandRecord] | None = None) -> list[CommandIntentEntry]:
    """Build a metadata-only command intent index from command registry records."""
    source_records = list(records) if records is not None else list_commands()
    return [_entry_from_record(record) for record in source_records]


def suggest_commands(query: str, *, records: Sequence[CommandRecord] | None = None, limit: int = 10) -> list[CommandSuggestion]:
    entries = build_intent_index(records)
    query_terms = _tokenize(query)
    suggestions: list[CommandSuggestion] = []
    for entry in entries:
        score, matched = _score_entry(query_terms, entry)
        if score <= 0:
            continue
        primary = entry.status in ACTIVE_STATUSES and score > 0
        suggestions.append(
            CommandSuggestion(
                entry=entry,
                score=score + (5 if primary else 0),
                matched_terms=tuple(sorted(matched)),
                primary=primary,
                safety_note=_safety_note(entry),
            )
        )
    suggestions.sort(key=lambda item: (item.primary, item.score, item.entry.status == "active"), reverse=True)
    return suggestions[:limit]


def format_intent_index_json(entries: Sequence[CommandIntentEntry]) -> str:
    return json.dumps({"commands": [entry.to_dict() for entry in entries], "count": len(entries)}, indent=2, sort_keys=True)


def format_suggestions_json(suggestions: Sequence[CommandSuggestion]) -> str:
    return json.dumps({"suggestions": [suggestion.to_dict() for suggestion in suggestions]}, indent=2, sort_keys=True)


def _entry_from_record(record: Any) -> CommandIntentEntry:
    group = str(getattr(record, "group", ""))
    command = str(getattr(record, "command", ""))
    description = str(getattr(record, "description", ""))
    example = str(getattr(record, "example", ""))
    status = str(getattr(record, "status", ""))
    risk = str(getattr(record, "risk_level", ""))
    approval = str(getattr(record, "requires_approval", ""))
    provider = _optional_field(getattr(record, "requires_provider", ""))
    connector = _optional_field(getattr(record, "requires_connector", ""))
    aliases = _aliases_for(group, command, description)
    triggers = _triggers_for(group, command, description, aliases)
    intents = _intent_ids_for(group, command, description)
    dry_run_available = _has_dry_run(record, risk, approval)
    safe_to_run_directly = _safe_to_run_directly(status, risk, approval)
    return CommandIntentEntry(
        command_id=str(getattr(record, "command_id", "")),
        command=command,
        group=group,
        description=description,
        examples=tuple(value for value in (example,) if value),
        aliases=aliases,
        natural_language_triggers=triggers,
        intent_ids=intents,
        risk_level=risk,
        approval_required=approval,
        provider_required=provider,
        connector_required=connector,
        safe_to_run_directly=safe_to_run_directly,
        dry_run_available=dry_run_available,
        docs_link=str(getattr(record, "docs_link", "")),
        status=status,
        setup_hint=_setup_hint(provider, connector),
        replacement=_optional_field(getattr(record, "replacement", "")),
    )


def _aliases_for(group: str, command: str, description: str) -> tuple[str, ...]:
    aliases: set[str] = set()
    group_lower = group.lower()
    for key, values in EXPLICIT_ALIASES.items():
        if key.lower() in group_lower:
            aliases.update(values)
    command_words = command.replace("python smart_agent.py", "").replace("<", " ").replace(">", " ")
    aliases.update(_tokenize(command_words))
    if "doctor" in command or "status" in command:
        aliases.update({"doctor", "status", "is it configured", "is it working"})
    if "search" in command or "search" in description.lower():
        aliases.update({"search", "find", "look for"})
    return tuple(sorted(aliases))


def _triggers_for(group: str, command: str, description: str, aliases: Iterable[str]) -> tuple[str, ...]:
    terms = set(aliases)
    terms.update(_tokenize(group))
    terms.update(_tokenize(command))
    terms.update(_tokenize(description))
    stop = {"python", "smart_agent", "py", "the", "and", "with", "for", "one", "run", "show"}
    return tuple(sorted(term for term in terms if len(term) > 2 and term not in stop))


def _intent_ids_for(group: str, command: str, description: str) -> tuple[str, ...]:
    haystack = " ".join([group, command, description]).lower()
    intents = {intent for keyword, intent in INTENT_BY_GROUP_KEYWORD if keyword in haystack}
    if "forecast" in haystack:
        intents.add("weather.forecast")
    if "write" in haystack or "send" in haystack or "delete" in haystack or "commit" in haystack:
        intents.add("send_or_write.request")
    if "approval" in haystack or "preflight" in haystack or "dry-run" in haystack:
        intents.add("action.preflight")
    if not intents:
        intents.add("unknown")
    return tuple(sorted(intents))


def _has_dry_run(record: Any, risk: str, approval: str) -> bool:
    haystack = " ".join(
        str(getattr(record, name, ""))
        for name in ("command", "example", "description", "side_effects", "notes")
    ).lower()
    if "dry-run" in haystack or "preflight" in haystack:
        return True
    if _risk_parts(risk) & HIGH_RISK:
        return True
    return _approval_required(approval)


def _safe_to_run_directly(status: str, risk: str, approval: str) -> bool:
    if status not in ACTIVE_STATUSES:
        return False
    if _risk_parts(risk) & HIGH_RISK:
        return False
    if _approval_required(approval):
        return False
    return any(part in {"SAFE", "LOW"} for part in _risk_parts(risk))


def _safety_note(entry: CommandIntentEntry) -> str:
    if entry.status in NON_PRIMARY_STATUSES:
        return f"{entry.status} command; show as non-primary suggestion only."
    if not entry.safe_to_run_directly and entry.dry_run_available:
        return "Use dry-run/preflight or existing approval flow; do not execute directly from natural language."
    if not entry.safe_to_run_directly:
        return "Suggest command/help only; do not execute directly from natural language."
    return "Eligible for safe suggestion; execution still goes through normal CLI and policy."


def _score_entry(query_terms: set[str], entry: CommandIntentEntry) -> tuple[int, set[str]]:
    fields = {
        "command": _tokenize(entry.command),
        "description": _tokenize(entry.description),
        "group": _tokenize(entry.group),
        "aliases": set(entry.aliases),
        "triggers": set(entry.natural_language_triggers),
        "intents": set(entry.intent_ids),
    }
    score = 0
    matched: set[str] = set()
    for term in query_terms:
        for field, terms in fields.items():
            if term in terms:
                matched.add(term)
                score += 5 if field in {"aliases", "intents"} else 2
    phrase = " ".join(sorted(query_terms))
    for alias in entry.aliases:
        if alias in phrase:
            matched.add(alias)
            score += 6
    command_lower = entry.command.lower()
    status_terms = {"doctor", "status", "configured", "working", "setup"}
    if "weather" in query_terms and "weather current" in command_lower:
        score += 8
    if ("doctor" in command_lower or "status" in command_lower) and not (query_terms & status_terms):
        score -= 4
    return score, matched


def _tokenize(value: str) -> set[str]:
    stop = {"a", "an", "and", "for", "in", "is", "it", "of", "or", "the", "to", "what", "with"}
    return {
        token
        for token in re.split(r"[^a-zA-Z0-9_.-]+", value.lower())
        if len(token) > 1 and token not in stop
    }


def _optional_field(value: object) -> str:
    text = str(value).strip()
    return "" if text.lower() in {"", "none", "n/a", "no"} else text


def _approval_required(value: str) -> bool:
    normalized = value.strip().lower()
    return normalized not in {"", "no", "n/a", "none"}


def _risk_parts(value: str) -> set[str]:
    return {part.strip().upper() for part in re.split(r"[/, ]+", value) if part.strip()}


def _setup_hint(provider: str, connector: str) -> str:
    required = provider or connector
    if not required:
        return ""
    return f"Requires configured {required}; use the matching doctor/status command first."
