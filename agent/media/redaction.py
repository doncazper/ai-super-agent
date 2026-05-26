from __future__ import annotations

import hashlib
import re

from agent.safety.redaction import SecretRedactor


EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b")


def prompt_hash(prompt_text: str) -> str:
    return hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()


def redact_media_prompt(prompt_text: str, *, max_chars: int = 240) -> str:
    redactor = SecretRedactor()
    redacted = redactor.redact_text(prompt_text)
    redacted = EMAIL_RE.sub("[REDACTED_EMAIL]", redacted)
    redacted = PHONE_RE.sub("[REDACTED_PHONE]", redacted)
    if len(redacted) > max_chars:
        return redacted[:max_chars].rstrip() + " [TRUNCATED]"
    return redacted
