from __future__ import annotations

import re
from typing import Any, Mapping

from .registry import default_secret_registry


REDACTED = "[REDACTED]"
KEY_VALUE_PATTERN = re.compile(
    r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|token|secret|password|authorization)\b\s*[:=]\s*([^\s,;'\"`]+)"
)
TOKEN_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bghp_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bxoxb-[A-Za-z0-9-]{16,}\b"),
    re.compile(r"\bya29\.[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bAIza[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\b\d{6,}:[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----.*?-----END (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----", re.DOTALL),
]
SECRET_KEY_RE = re.compile(r"(?i)(api[_-]?key|token|secret|password|authorization|credential|private[_-]?key)")


def redact_secret_value(value: str, *, preserve_last4: bool = False) -> str:
    if not value:
        return value
    if preserve_last4 and len(value) > 4:
        return f"{REDACTED}...{value[-4:]}"
    return REDACTED


class SecretRedactor:
    replacement = REDACTED

    def __init__(self, *, known_values: Mapping[str, str] | None = None, preserve_last4: bool = False) -> None:
        self.known_values = {
            key: value
            for key, value in (known_values or {}).items()
            if isinstance(value, str) and value and len(value) >= 4
        }
        self.preserve_last4 = preserve_last4
        self.known_env_names = default_secret_registry().known_env_names()

    def redact_text(self, value: str) -> str:
        redacted = value
        for raw in sorted(set(self.known_values.values()), key=len, reverse=True):
            redacted = redacted.replace(raw, redact_secret_value(raw, preserve_last4=self.preserve_last4))
        redacted = KEY_VALUE_PATTERN.sub(lambda match: f"{match.group(1)}={self.replacement}", redacted)
        for pattern in TOKEN_PATTERNS:
            redacted = pattern.sub(self.replacement, redacted)
        return redacted

    def redact(self, value: Any) -> Any:
        if isinstance(value, str):
            return self.redact_text(value)
        if isinstance(value, dict):
            output: dict[Any, Any] = {}
            for key, item in value.items():
                if self._looks_secret_key(str(key)):
                    output[key] = redact_secret_value(str(item), preserve_last4=self.preserve_last4) if item is not None else self.replacement
                else:
                    output[key] = self.redact(item)
            return output
        if isinstance(value, list):
            return [self.redact(item) for item in value]
        if isinstance(value, tuple):
            return tuple(self.redact(item) for item in value)
        return value

    def contains_secret(self, value: Any) -> bool:
        return self.redact(value) != value

    def _looks_secret_key(self, key: str) -> bool:
        normalized = key.casefold()
        if normalized.endswith("_status") or normalized.endswith("_configured") or normalized in {"credential_status"}:
            return False
        return bool(SECRET_KEY_RE.search(key)) or key in self.known_env_names
