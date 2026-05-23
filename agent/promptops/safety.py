from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from agent.promptops.models import (
    ALLOWED_AUTOPILOT_CATEGORIES,
    FORBIDDEN_AUTOPILOT_CATEGORIES,
    FORBIDDEN_AUTOPILOT_RISKS,
    SAFE_AUTOPILOT_RISKS,
)
from agent.ui.prompts import PromptRecord


SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*([^\s,;]+)"),
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
)


@dataclass(frozen=True)
class SafetyDecision:
    allowed: bool
    reason: str


def redact_secrets(value: str) -> str:
    redacted = value
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub(lambda match: f"{match.group(1)}=<redacted>" if match.lastindex and match.lastindex >= 2 else "<redacted>", redacted)
    return redacted


def autopilot_decision(record: PromptRecord, metadata: dict[str, Any] | None = None) -> SafetyDecision:
    payload = metadata or {}
    risk = str(payload.get("risk_level") or "LOW").upper()
    category = (payload.get("category") or record.category or "").strip().lower()
    approval_gate = str(payload.get("approval_gate") or record.approval_gate or "").strip().lower()
    if risk in FORBIDDEN_AUTOPILOT_RISKS:
        return SafetyDecision(False, f"risk level {risk} is not allowed in autopilot")
    if risk not in SAFE_AUTOPILOT_RISKS:
        return SafetyDecision(False, f"risk level {risk} is not recognized as safe for autopilot")
    if category in FORBIDDEN_AUTOPILOT_CATEGORIES:
        return SafetyDecision(False, f"category {category} is forbidden in autopilot")
    if category and category not in ALLOWED_AUTOPILOT_CATEGORIES:
        return SafetyDecision(False, f"category {category} is not in the autopilot allowlist")
    if approval_gate in {"true", "yes", "approval required", "blocked"}:
        return SafetyDecision(False, "approval gate is blocking")
    return SafetyDecision(True, "safe for autopilot")


def imported_prompt_trust_level() -> str:
    return "UNTRUSTED_DOCUMENT"

