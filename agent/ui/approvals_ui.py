from __future__ import annotations

import json
import sys
from typing import Callable

from agent.safety.approvals import ApprovalRequest, ApprovalResult, ApprovalStatus
from agent.safety.policy import RiskLevel
from agent.safety.redaction import SecretRedactor


class ConsoleApprovalPrompt:
    def __init__(
        self,
        *,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
        interactive: bool = False,
    ) -> None:
        self.input_fn = input_fn
        self.output_fn = output_fn
        self.interactive = interactive

    def prompt(self, request: ApprovalRequest, response: str | None = None) -> ApprovalResult:
        if response is None:
            if not self.interactive:
                return ApprovalResult.DENIED
            self.output_fn(format_approval_preview(request))
            while True:
                response = self.input_fn("approval> ").strip()
                if is_details_response(response):
                    self.output_fn(format_approval_details(request))
                    continue
                return approval_result_from_response(request, response)
        return approval_result_from_response(request, response)


def is_details_response(response: str) -> bool:
    return response.strip().casefold() in {"details", "detail", "show details", "d"}


def approval_result_from_response(request: ApprovalRequest, response: str) -> ApprovalResult:
    normalized = response.strip().casefold()
    if is_details_response(response):
        return ApprovalResult.DENIED
    if normalized in {"deny", "denied", "no", "n"}:
        return ApprovalResult.DENIED
    if normalized in {"abort", "a", "cancel"}:
        return ApprovalResult.ABORTED
    if normalized in {"approve", "approve once", "yes", "y"}:
        return ApprovalResult.APPROVED
    if request.risk_level is RiskLevel.CRITICAL and normalized in {"approve all", "always", "reuse"}:
        return ApprovalResult.DENIED
    return ApprovalResult.DENIED


def format_approval_preview(request: ApprovalRequest) -> str:
    choices = ["approve once", "deny", "abort", "show details"]
    if request.risk_level is RiskLevel.CRITICAL:
        choices = ["approve once only", "deny", "abort", "edit draft later", "show details"]
    return "\n".join(
        [
            "Approval required",
            f"Request: {request.request_id}",
            f"Status: {request.status.value}",
            f"Tool: {request.tool_name}",
            f"Capability: {request.capability}",
            f"Risk: {request.risk_level.value}",
            f"Trust: {request.trust_level.value}",
            f"Summary: {request.summary}",
            f"Rollback available: {request.rollback_available}",
            f"Expires: {request.expires_at}",
            "Args preview:",
            json.dumps(SecretRedactor().redact(request.args_preview), indent=2, sort_keys=True),
            "Choices: " + ", ".join(choices),
        ]
    )


def format_approval_details(request: ApprovalRequest) -> str:
    return "\n".join(
        [
            "Approval details",
            json.dumps(SecretRedactor().redact(request.to_dict()), indent=2, sort_keys=True),
        ]
    )


def print_request(request: ApprovalRequest) -> None:
    print(format_approval_preview(request))


def print_requests(requests: list[ApprovalRequest]) -> None:
    payload = [
        {
            "request_id": request.request_id,
            "timestamp": request.timestamp,
            "tool_name": request.tool_name,
            "capability": request.capability,
            "risk_level": request.risk_level.value,
            "status": request.status.value,
            "expires_at": request.expires_at,
        }
        for request in requests
    ]
    print(json.dumps({"approvals": payload}, indent=2, sort_keys=True))


def print_cli_error(message: str) -> None:
    print(message, file=sys.stderr)
