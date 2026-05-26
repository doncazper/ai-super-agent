from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Mapping
import re

from agent.config.runtime import env_bool


SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|token|secret|password|authorization)\s*[:=]\s*['\"]?([A-Za-z0-9_\-./+=]{8,})"
)
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)


@dataclass(frozen=True)
class SessionContinuityPolicy:
    enabled: bool = False
    carry_personal_data: bool = False
    redaction_required: bool = True
    memory_policy_bypass_allowed: bool = False
    tool_compatibility_required: bool = True
    cloud_or_paid_switch_allowed: bool = False
    storage_behavior: str = "no_store_by_default"

    def to_dict(self) -> dict[str, object]:
        return {
            "enabled": self.enabled,
            "carry_personal_data": self.carry_personal_data,
            "redaction_required": self.redaction_required,
            "memory_policy_bypass_allowed": self.memory_policy_bypass_allowed,
            "tool_compatibility_required": self.tool_compatibility_required,
            "cloud_or_paid_switch_allowed": self.cloud_or_paid_switch_allowed,
            "storage_behavior": self.storage_behavior,
        }


@dataclass(frozen=True)
class SessionContinuityExport:
    status: str
    redacted: bool
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    context_summary: str = ""
    source_session_id: str = ""
    included_fields: tuple[str, ...] = ()
    excluded_fields: tuple[str, ...] = ()
    memory_written: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "redacted": self.redacted,
            "generated_at": self.generated_at,
            "context_summary": self.context_summary,
            "source_session_id": self.source_session_id,
            "included_fields": list(self.included_fields),
            "excluded_fields": list(self.excluded_fields),
            "memory_written": self.memory_written,
        }


def continuity_policy(env: Mapping[str, str] | None = None) -> SessionContinuityPolicy:
    enabled = _env_bool("SESSION_CONTINUITY_ENABLED", False, env)
    carry_personal = _env_bool("SESSION_CONTINUITY_CARRY_PERSONAL_DATA", False, env)
    return SessionContinuityPolicy(
        enabled=enabled,
        carry_personal_data=False if not enabled else carry_personal,
        redaction_required=True,
        memory_policy_bypass_allowed=False,
        tool_compatibility_required=True,
        cloud_or_paid_switch_allowed=_env_bool("BRAIN_ALLOW_CLOUD_FALLBACK", False, env),
        storage_behavior="no_store_by_default" if not enabled else "redacted_opt_in_only",
    )


def continuity_status(env: Mapping[str, str] | None = None) -> dict[str, object]:
    policy = continuity_policy(env)
    return {
        "status": "disabled" if not policy.enabled else "enabled",
        "policy": policy.to_dict(),
        "personal_data_carried_by_default": False,
        "context_export_available": True,
        "clear_available": True,
        "model_call_performed": False,
        "tool_execution_performed": False,
        "memory_written": False,
        "notes": [
            "Session continuity is opt-in.",
            "Personal data is not carried across sessions by default.",
            "Context exports are redacted and do not bypass memory policy.",
        ],
    }


def export_redacted_continuity(
    *,
    source_session_id: str = "",
    context_summary: str = "",
    env: Mapping[str, str] | None = None,
) -> dict[str, object]:
    policy = continuity_policy(env)
    redacted = redact_context_summary(context_summary or "No stored continuity context is available by default.")
    export = SessionContinuityExport(
        status="ok",
        redacted=True,
        context_summary=redacted,
        source_session_id=source_session_id,
        included_fields=("redacted_context_summary", "source_session_id", "generated_at"),
        excluded_fields=(
            "raw_messages",
            "personal_data",
            "tool_outputs",
            "secrets",
            "unredacted_session_log",
        ),
        memory_written=False,
    )
    return {
        "status": export.status,
        "enabled": policy.enabled,
        "export": export.to_dict(),
        "policy": policy.to_dict(),
        "file_written": False,
        "memory_written": False,
    }


def clear_continuity(env: Mapping[str, str] | None = None) -> dict[str, object]:
    policy = continuity_policy(env)
    return {
        "status": "ok",
        "enabled": policy.enabled,
        "cleared": True,
        "entries_deleted": 0,
        "raw_context_deleted": False,
        "reason": "No persistent continuity context is stored by default.",
        "memory_written": False,
        "policy": policy.to_dict(),
    }


def redact_context_summary(text: str) -> str:
    redacted = SECRET_RE.sub(lambda match: f"{match.group(1)}=[REDACTED]", text)
    redacted = EMAIL_RE.sub("[REDACTED_EMAIL]", redacted)
    return " ".join(redacted.split())[:2000]


def _env_bool(name: str, default: bool, env: Mapping[str, str] | None) -> bool:
    if env is None:
        return env_bool(name, default=default)
    return str(env.get(name, "")).strip().casefold() in {"1", "true", "yes", "on"} if name in env else default
