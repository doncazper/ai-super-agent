from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from agent.safety.policy import PolicyDecision, RiskLevel
from agent.safety.redaction import SecretRedactor
from agent.safety.trust import TrustLevel


class AuditLogError(RuntimeError):
    pass


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class AuditEvent:
    session_id: str
    request_id: str
    route: str
    model: str
    tool_name: str
    capability: str
    risk_level: str = RiskLevel.SAFE.value
    trust_level: str = TrustLevel.MODEL_OUTPUT.value
    policy_decision: str = PolicyDecision.DENY.value
    approval_result: str = "not_required"
    sanitized_args: dict[str, Any] = field(default_factory=dict)
    result_summary: str = ""
    files_read: list[str] = field(default_factory=list)
    files_written: list[str] = field(default_factory=list)
    commands_run: list[str] = field(default_factory=list)
    network_domains: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=utc_now_iso)


class AuditLogger:
    """Append-only JSONL audit logger with hash chaining."""

    def __init__(self, path: str | Path = "logs/audit.jsonl", redactor: SecretRedactor | None = None) -> None:
        self.path = Path(path)
        self.redactor = redactor or SecretRedactor()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._last_hash = self._read_last_hash()

    def log(self, event: AuditEvent) -> dict[str, Any]:
        payload = self.redactor.redact(event.__dict__.copy())
        payload["hash_previous"] = self._last_hash
        payload["hash_current"] = self._hash_payload(payload)
        try:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, sort_keys=True) + "\n")
        except OSError as exc:
            raise AuditLogError(f"Audit log is not writable at {self.path}: {exc.strerror}") from exc
        self._last_hash = payload["hash_current"]
        return payload

    def _read_last_hash(self) -> str:
        if not self.path.exists():
            return ""
        last = ""
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    last = line
        if not last:
            return ""
        try:
            return str(json.loads(last).get("hash_current", ""))
        except json.JSONDecodeError:
            return ""

    def _hash_payload(self, payload: dict[str, Any]) -> str:
        stable = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(stable.encode("utf-8")).hexdigest()


def new_request_id() -> str:
    return str(uuid4())
