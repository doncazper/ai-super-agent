from __future__ import annotations

import re


SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password|refresh[_-]?token)(\s*[:=]\s*)([^\s\"']+)"),
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"ghp_[A-Za-z0-9_]{12,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{12,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{12,}"),
    re.compile(r"ya29\.[A-Za-z0-9_-]{12,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{12,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.DOTALL),
]
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b")


def redact_text(text: str, *, max_chars: int | None = None) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS:
        if pattern.groups >= 3:
            redacted = pattern.sub(r"\1\2[REDACTED]", redacted)
        else:
            redacted = pattern.sub("[REDACTED_SECRET]", redacted)
    redacted = EMAIL_RE.sub("[REDACTED_EMAIL]", redacted)
    redacted = PHONE_RE.sub("[REDACTED_PHONE]", redacted)
    if max_chars is not None and len(redacted) > max_chars:
        return redacted[:max_chars] + "\n[TRUNCATED]"
    return redacted
