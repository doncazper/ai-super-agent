from __future__ import annotations

from agent.safety.approvals import ApprovalRequest, ApprovalResult
from agent.safety.policy import RiskLevel


class ConsoleApprovalPrompt:
    def prompt(self, request: ApprovalRequest, response: str | None = None) -> ApprovalResult:
        if request.risk_level is RiskLevel.CRITICAL and response != "approve":
            return ApprovalResult.DENIED
        if response == "approve":
            return ApprovalResult.APPROVED
        return ApprovalResult.DENIED
