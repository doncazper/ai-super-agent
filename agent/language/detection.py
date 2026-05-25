from __future__ import annotations

import re
from collections import Counter

from agent.language.models import DEFAULT_FORUM_TRUST_LEVEL, LanguageDetectionResult


_HIRAGANA_KATAKANA_RE = re.compile(r"[\u3040-\u30ff]")
_HANGUL_RE = re.compile(r"[\uac00-\ud7af]")
_CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
_LATIN_RE = re.compile(r"[A-Za-z]")

_SIMPLIFIED_HINTS = set("这为个们国学时会说对后发见过门车书网汉语")
_TRADITIONAL_HINTS = set("這為個們國學時會說對後發見過門車書網漢語")
_SPANISH_WORDS = {
    "el",
    "la",
    "los",
    "las",
    "un",
    "una",
    "que",
    "de",
    "para",
    "con",
    "hola",
    "gracias",
    "porque",
    "producto",
    "opiniones",
}
_ENGLISH_WORDS = {
    "the",
    "and",
    "that",
    "with",
    "for",
    "this",
    "from",
    "hello",
    "thanks",
    "product",
    "discussion",
}


def detect_language(
    text: str,
    *,
    source_id: str | None = None,
    trust_level: str = DEFAULT_FORUM_TRUST_LEVEL,
) -> LanguageDetectionResult:
    source = source_id or "inline"
    sample = (text or "").strip()
    if not sample:
        return LanguageDetectionResult(
            language="unknown",
            language_name="Unknown",
            script="unknown",
            confidence=0.0,
            source_id=source,
            trust_level=trust_level,
            warnings=["empty_text"],
        )

    if _HIRAGANA_KATAKANA_RE.search(sample):
        return LanguageDetectionResult("ja", "Japanese", "Japanese", 0.92, source, trust_level)
    if _HANGUL_RE.search(sample):
        return LanguageDetectionResult("ko", "Korean", "Hangul", 0.92, source, trust_level)
    if _CJK_RE.search(sample):
        simplified = sum(1 for char in sample if char in _SIMPLIFIED_HINTS)
        traditional = sum(1 for char in sample if char in _TRADITIONAL_HINTS)
        if traditional > simplified:
            return LanguageDetectionResult(
                "zh",
                "Chinese",
                "Han",
                0.86,
                source,
                trust_level,
                variant="traditional",
                alternatives=[{"language": "zh-Hant", "score": traditional}],
            )
        variant = "simplified" if simplified or not traditional else "unknown"
        return LanguageDetectionResult(
            "zh",
            "Chinese",
            "Han",
            0.84,
            source,
            trust_level,
            variant=variant,
            alternatives=[{"language": "zh-Hans", "score": simplified}],
        )

    words = re.findall(r"[A-Za-zÀ-ÿ']+", sample.lower())
    counts = Counter(words)
    accented_spanish = bool(re.search(r"[áéíóúñü¿¡]", sample.lower()))
    spanish_score = sum(counts[word] for word in _SPANISH_WORDS) + (2 if accented_spanish else 0)
    english_score = sum(counts[word] for word in _ENGLISH_WORDS)
    if spanish_score > english_score and spanish_score > 0:
        return LanguageDetectionResult("es", "Spanish", "Latin", min(0.55 + spanish_score * 0.08, 0.94), source, trust_level)
    if _LATIN_RE.search(sample):
        return LanguageDetectionResult("en", "English", "Latin", min(0.56 + english_score * 0.06, 0.9), source, trust_level)
    return LanguageDetectionResult(
        "unknown",
        "Unknown",
        "unknown",
        0.2,
        source,
        trust_level,
        warnings=["low_confidence"],
    )
