from __future__ import annotations

from typing import Any

from agent.language.detection import detect_language
from agent.language.translation import extract_terms, summarize_multilingual, translate_text


def _schema(name: str, description: str, properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
        },
    }


LANGUAGE_SCHEMAS: dict[str, dict[str, Any]] = {
    "language.detect": _schema(
        "language.detect",
        "Detect language for forum/web/document text without external APIs.",
        {
            "text": {"type": "string"},
            "source_id": {"type": "string", "default": "inline"},
            "trust_level": {"type": "string", "default": "UNTRUSTED_WEB"},
        },
        ["text"],
    ),
    "language.translate_text": _schema(
        "language.translate_text",
        "Translate untrusted multilingual text through the local model by default; no external translation API.",
        {
            "text": {"type": "string"},
            "from_language": {"type": "string", "default": "auto"},
            "to_language": {"type": "string", "default": "en"},
            "source_id": {"type": "string", "default": "inline"},
            "trust_level": {"type": "string", "default": "UNTRUSTED_WEB"},
        },
        ["text"],
    ),
    "language.summarize_multilingual": _schema(
        "language.summarize_multilingual",
        "Translate and summarize untrusted multilingual source text with source references.",
        {
            "text": {"type": "string"},
            "source_id": {"type": "string", "default": "inline"},
            "target_language": {"type": "string", "default": "en"},
            "trust_level": {"type": "string", "default": "UNTRUSTED_WEB"},
        },
        ["text"],
    ),
    "language.extract_terms": _schema(
        "language.extract_terms",
        "Extract glossary terms from multilingual forum/web/document text without storing source content.",
        {
            "text": {"type": "string"},
            "source_id": {"type": "string", "default": "inline"},
            "trust_level": {"type": "string", "default": "UNTRUSTED_WEB"},
            "max_terms": {"type": "integer", "default": 20},
        },
        ["text"],
    ),
}


def make_language_tools() -> dict[str, Any]:
    return {
        "language.detect": lambda text, source_id="inline", trust_level="UNTRUSTED_WEB": {
            **detect_language(text, source_id=source_id, trust_level=trust_level).to_dict(),
            "memory_written": False,
            "external_provider_used": False,
        },
        "language.translate_text": lambda text, from_language="auto", to_language="en", source_id="inline", trust_level="UNTRUSTED_WEB": translate_text(
            text,
            from_language=from_language,
            to_language=to_language,
            source_id=source_id,
            trust_level=trust_level,
        ),
        "language.summarize_multilingual": lambda text, source_id="inline", target_language="en", trust_level="UNTRUSTED_WEB": summarize_multilingual(
            text,
            source_id=source_id,
            target_language=target_language,
            trust_level=trust_level,
        ),
        "language.extract_terms": lambda text, source_id="inline", trust_level="UNTRUSTED_WEB", max_terms=20: extract_terms(
            text,
            source_id=source_id,
            trust_level=trust_level,
            max_terms=max_terms,
        ),
    }
