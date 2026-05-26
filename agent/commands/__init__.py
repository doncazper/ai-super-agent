"""Command registry helpers for natural-language command understanding."""

from agent.commands.intent_index import (
    build_intent_index,
    format_intent_index_json,
    format_suggestions_json,
    suggest_commands,
)
from agent.commands.models import CommandIntentEntry, CommandSuggestion

__all__ = [
    "CommandIntentEntry",
    "CommandSuggestion",
    "build_intent_index",
    "format_intent_index_json",
    "format_suggestions_json",
    "suggest_commands",
]
