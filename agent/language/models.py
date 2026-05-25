from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


DEFAULT_FORUM_TRUST_LEVEL = "UNTRUSTED_WEB"
DOCUMENT_TRUST_LEVEL = "UNTRUSTED_DOCUMENT"
MODEL_TRANSLATION_LABEL = "MODEL_GENERATED_TRANSLATION"


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


@dataclass(frozen=True)
class LanguageDetectionResult:
    language: str
    language_name: str
    script: str
    confidence: float
    source_id: str
    trust_level: str = DEFAULT_FORUM_TRUST_LEVEL
    variant: str | None = None
    alternatives: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TextChunk:
    source_id: str
    chunk_id: str
    text: str
    index: int
    trust_level: str = DEFAULT_FORUM_TRUST_LEVEL

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TranslationResult:
    status: str
    source_language: str
    target_language: str
    translated_text: str
    translation_label: str
    provider: str
    source_references: list[str]
    chunks: list[dict[str, Any]]
    retrieved_at: str
    trust_level: str = DEFAULT_FORUM_TRUST_LEVEL
    generated_by_model: bool = True
    external_provider_used: bool = False
    paid_api_used: bool = False
    memory_written: bool = False
    prompt_injection_ignored: bool = True
    warnings: list[str] = field(default_factory=list)
    setup_hint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GlossaryTerm:
    term: str
    language: str
    source_ids: list[str]
    note: str
    romanization: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
