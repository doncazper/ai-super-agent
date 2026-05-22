from __future__ import annotations

import re
from typing import Any


SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*([^\s,;]+)"),
    re.compile(r"sk-[A-Za-z0-9_\-]{16,}"),
]


class SecretRedactor:
    replacement = "[REDACTED]"

    def redact_text(self, value: str) -> str:
        redacted = value
        for pattern in SECRET_PATTERNS:
            if pattern.groups >= 2:
                redacted = pattern.sub(lambda match: f"{match.group(1)}={self.replacement}", redacted)
            else:
                redacted = pattern.sub(self.replacement, redacted)
        return redacted

    def redact(self, value: Any) -> Any:
        if isinstance(value, str):
            return self.redact_text(value)
        if isinstance(value, dict):
            redacted: dict[Any, Any] = {}
            for key, item in value.items():
                if self._looks_secret_key(str(key)):
                    redacted[key] = self.replacement
                else:
                    redacted[key] = self.redact(item)
            return redacted
        if isinstance(value, list):
            return [self.redact(item) for item in value]
        return value

    def contains_secret(self, value: Any) -> bool:
        return self.redact(value) != value

    def _looks_secret_key(self, key: str) -> bool:
        return bool(re.search(r"(?i)(api[_-]?key|token|secret|password|authorization)", key))
