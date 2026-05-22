from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from agent.safety.policy import RiskLevel


class ApprovalResult(StrEnum):
    APPROVED = "approved"
    DENIED = "denied"
    NOT_REQUIRED = "not_required"


@dataclass(frozen=True)
class ApprovalRequest:
    capability: str
    tool_name: str
    risk_level: RiskLevel
    summary: str
    per_action: bool = False


class ApprovalManager:
    """Conservative M1 approval manager.

    Non-interactive by default: anything that asks for approval is denied until
    a UI-backed implementation is added in a later milestone.
    """

    def __init__(self, auto_approve: set[str] | None = None) -> None:
        self.auto_approve = auto_approve or set()
        self.requests: list[ApprovalRequest] = []

    def request_approval(self, request: ApprovalRequest) -> ApprovalResult:
        self.requests.append(request)
        if request.risk_level is RiskLevel.CRITICAL and request.capability not in self.auto_approve:
            return ApprovalResult.DENIED
        if request.capability in self.auto_approve:
            return ApprovalResult.APPROVED
        return ApprovalResult.DENIED
