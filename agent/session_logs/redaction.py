from __future__ import annotations

import re
from collections.abc import Iterable


SECRET_PATTERNS = (
    re.compile(r"(?i)(authorization:\s*bearer\s+)[A-Za-z0-9._~+/=-]{8,}"),
    re.compile(r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|password|passwd|secret)\b\s*[:=]\s*([^\s,;]+)"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{12,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{12,}\b"),
)
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\w)(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}(?!\w)")


def redact_text(text: str) -> str:
    redacted = text
    redacted = SECRET_PATTERNS[0].sub(r"\1<REDACTED_SECRET>", redacted)
    for pattern in SECRET_PATTERNS[1:]:
        redacted = pattern.sub(lambda match: _redact_secret_match(match), redacted)
    redacted = EMAIL_RE.sub("<REDACTED_EMAIL>", redacted)
    redacted = PHONE_RE.sub("<REDACTED_PHONE>", redacted)
    return redacted


def redact_args(args: Iterable[str]) -> list[str]:
    values = list(args)
    redacted: list[str] = []
    redact_next = False
    secret_flags = {"--api-key", "--token", "--password", "--secret", "--access-token", "--refresh-token"}
    for value in values:
        if redact_next:
            redacted.append("<REDACTED_SECRET>")
            redact_next = False
            continue
        if value in secret_flags:
            redacted.append(value)
            redact_next = True
            continue
        if any(value.startswith(f"{flag}=") for flag in secret_flags):
            flag = value.split("=", 1)[0]
            redacted.append(f"{flag}=<REDACTED_SECRET>")
            continue
        redacted.append(redact_text(value))
    return redacted


def _redact_secret_match(match: re.Match[str]) -> str:
    if len(match.groups()) >= 2:
        return f"{match.group(1)}=<REDACTED_SECRET>"
    return "<REDACTED_SECRET>"
