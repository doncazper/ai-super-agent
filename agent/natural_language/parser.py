from __future__ import annotations

import re

from agent.natural_language.models import IntentCandidate, NaturalLanguageRequest


EXACT_COMMAND_PREFIXES = ("python smart_agent.py", "./scripts/agent", "make ")
VAGUE_LOOKUPS = {"look this up", "look it up", "search this", "search it", "verify this"}


def normalize_text(text: str) -> str:
    return " ".join(text.strip().casefold().split())


def parse_request(request: NaturalLanguageRequest) -> IntentCandidate:
    normalized = normalize_text(request.original_text)
    if request.no_tools:
        return IntentCandidate("chat.no_tools", 1.0, "no-tools mode disables command routing", ("no_tools",))
    if _is_exact_command(normalized):
        return IntentCandidate("command.exact", 1.0, "input already looks like an exact command", ("exact_command",))
    if not normalized:
        return IntentCandidate("ambiguous", 0.2, "empty request needs clarification", ("empty",))
    if _weather_missing_location(normalized):
        return IntentCandidate("weather.current", 0.55, "weather request is missing a location", ("missing_location", "weather"))
    if len(normalized.split()) <= 2 and normalized not in {"help", "status", "doctor"}:
        return IntentCandidate("ambiguous", 0.35, "short request lacks enough intent detail", ("short_request",))
    if any(phrase in normalized for phrase in ("send this email", "send an email", "email this", "send message", "send a text")):
        return IntentCandidate("send_or_write.request", 0.9, "send/write request requires explicit preflight and approval", ("send_or_write",))
    if any(phrase in normalized for phrase in ("read my email", "my calendar", "my contacts", "my messages", "my inbox")):
        return IntentCandidate("personal_data.request", 0.85, "personal-data request cannot route automatically", ("personal_data",))
    if _file_write_request(normalized):
        return IntentCandidate("file.write", 0.82, "workspace file write request requires preflight", ("file_write",))
    if "commands" in normalized and "memory" in normalized:
        return IntentCandidate("command.search", 0.9, "request asks for commands related to memory", ("commands", "memory"))
    if "fix" in normalized and "session" in normalized and ("bug" in normalized or "bugs" in normalized):
        return IntentCandidate("session.review", 0.82, "request asks to inspect last session bug evidence", ("session", "bug"))
    if _weather_current(normalized):
        return IntentCandidate("weather.current", 0.88, "weather request with location-like phrase", ("weather",))
    if normalized in VAGUE_LOOKUPS:
        return IntentCandidate("web.research", 0.6, "lookup request is missing the query/source to look up", ("lookup_missing_query",))
    if any(phrase in normalized for phrase in ("look up", "search for", "verify", "with sources", "cite", "citation")):
        return IntentCandidate("web.research", 0.78, "source/search request", ("search_or_source",))
    if _media_request(normalized):
        return IntentCandidate("media.plan", 0.82, "media creation request routes to dry-run planning only", ("media", "dry_run_plan"))
    if "remember" in normalized or "store this memory" in normalized:
        return IntentCandidate("memory.add", 0.75, "memory storage request needs policy preflight", ("memory",))
    if "memory" in normalized:
        return IntentCandidate("memory.search", 0.72, "memory search request", ("memory",))
    if normalized in {"help", "what can you do", "commands"} or "how do i" in normalized:
        return IntentCandidate("command.help", 0.7, "help request", ("help",))
    return IntentCandidate("unknown", 0.4, "no deterministic intent matched", ("fallback",))


def _is_exact_command(normalized: str) -> bool:
    if normalized.startswith(("python smart_agent.py", "./scripts/agent")):
        return True
    if normalized.startswith("make "):
        if normalized.startswith(("make me ", "make a ", "make an ", "make the ")):
            return False
        return re.match(r"^make\s+[a-z0-9_.:/-]+(\s+[a-z0-9_.:/=-]+)*$", normalized) is not None
    return False


def _weather_current(normalized: str) -> bool:
    if not any(term in normalized for term in ("weather", "temperature", "forecast", "rain", "raining")):
        return False
    if re.search(r"\b(in|for|at|near)\s+[a-z][a-z .,'-]+", normalized):
        return True
    return False


def _weather_missing_location(normalized: str) -> bool:
    return normalized in {"weather", "forecast", "temperature", "rain"} or (
        any(term in normalized for term in ("weather", "forecast", "temperature"))
        and not re.search(r"\b(in|for|at|near)\s+[a-z][a-z .,'-]+", normalized)
    )


def _file_write_request(normalized: str) -> bool:
    if not any(term in normalized for term in ("write", "create", "edit", "patch", "update", "save")):
        return False
    return "file" in normalized or "workspace" in normalized or re.search(r"\./workspace|workspace/", normalized) is not None


def _media_request(normalized: str) -> bool:
    if not any(term in normalized for term in ("make", "create", "generate", "turn", "build")):
        return False
    return any(
        term in normalized
        for term in (
            "thumbnail",
            "intro animation",
            "animation",
            "video",
            "image",
            "graphic",
            "podcast cover",
            "real estate listing",
            "music bed",
            "lo-fi",
            "lofi",
            "sound effect",
            "voiceover",
            "tts",
        )
    )
