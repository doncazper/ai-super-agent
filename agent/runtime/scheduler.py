from __future__ import annotations

from dataclasses import dataclass


SAFE_CATEGORIES = {"diagnostics", "evals", "briefing", "maintenance", "backup"}
FORBIDDEN_CATEGORIES = {"email_send", "message_send", "calendar_write", "contact_write", "policy_relaxation", "persistence"}


@dataclass(frozen=True)
class ScheduleDecision:
    allowed: bool
    status: str
    approval_required: bool
    reason: str
    background_persistence: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "allowed": self.allowed,
            "status": self.status,
            "approval_required": self.approval_required,
            "reason": self.reason,
            "background_persistence": self.background_persistence,
        }


class SchedulerPolicy:
    def evaluate(self, category: str, risk_level: str = "SAFE", personal_data: bool = False, background_persistence: bool = False) -> ScheduleDecision:
        if background_persistence:
            return ScheduleDecision(False, "blocked", True, "System-level cron/launch agent persistence requires a separate decision record and approval.", False)
        if category in FORBIDDEN_CATEGORIES or risk_level == "CRITICAL":
            return ScheduleDecision(False, "blocked", True, "CRITICAL/write/send workflows cannot run automatically in scheduler v1.")
        if personal_data or risk_level == "HIGH":
            return ScheduleDecision(False, "approval_required", True, "Personal-data or HIGH-risk scheduled workflows require explicit approval/config before each run.")
        if category not in SAFE_CATEGORIES:
            return ScheduleDecision(False, "unsupported", False, "Workflow category is not allowlisted for scheduler v1.")
        return ScheduleDecision(True, "manual_run_only", False, "Allowed only as an explicitly invoked manual scheduler run in v1.")

