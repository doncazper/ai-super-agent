from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .models import RuntimeMode, RuntimeStatus, now_iso


_SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*[^,\s}]+"),
    re.compile(r"sk-[A-Za-z0-9_-]{8,}"),
]


def redact_runtime_value(value: Any) -> Any:
    if isinstance(value, str):
        redacted = value
        for pattern in _SECRET_PATTERNS:
            redacted = pattern.sub(lambda match: match.group(0).split(match.group(0).split()[-1])[0] + "[REDACTED]" if " " in match.group(0) else "[REDACTED]", redacted)
        return redacted
    if isinstance(value, dict):
        return {k: ("[REDACTED]" if re.search(r"(?i)(api|token|secret|password|key)", str(k)) else redact_runtime_value(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_runtime_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_runtime_value(item) for item in value)
    return value


@dataclass
class RuntimeState:
    mode: RuntimeMode = RuntimeMode.CLI
    status: RuntimeStatus = RuntimeStatus.CREATED
    started_at: str | None = None
    updated_at: str = field(default_factory=now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)

    def boot(self) -> None:
        self.status = RuntimeStatus.READY
        self.started_at = self.started_at or now_iso()
        self.updated_at = now_iso()

    def stop(self) -> None:
        self.status = RuntimeStatus.STOPPED
        self.updated_at = now_iso()

    def set_status(self, status: RuntimeStatus) -> None:
        self.status = status
        self.updated_at = now_iso()

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode.value,
            "status": self.status.value,
            "started_at": self.started_at,
            "updated_at": self.updated_at,
            "metadata": redact_runtime_value(self.metadata),
        }

