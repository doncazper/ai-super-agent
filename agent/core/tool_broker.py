from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from agent.safety.audit import AuditEvent, AuditLogger, new_request_id
from agent.safety.approvals import ApprovalManager, ApprovalRequest, ApprovalResult
from agent.safety.policy import PolicyDecision, PolicyEngine, RiskLevel
from agent.safety.trust import TrustLevel
from agent.tools.errors import ToolError
from agent.tools.registry import ToolRegistry


@dataclass(frozen=True)
class ToolExecutionResult:
    tool_call_id: str
    tool_name: str
    allowed: bool
    content: str


class ToolBroker:
    def __init__(
        self,
        registry: ToolRegistry,
        policy_engine: PolicyEngine,
        audit_logger: AuditLogger,
        *,
        session_id: str,
        model: str = "",
        route: str = "default",
        approval_manager: ApprovalManager | None = None,
    ) -> None:
        self.registry = registry
        self.policy_engine = policy_engine
        self.audit_logger = audit_logger
        self.session_id = session_id
        self.model = model
        self.route = route
        self.approval_manager = approval_manager or ApprovalManager()

    def execute(self, tool_call: dict[str, Any]) -> ToolExecutionResult:
        tool_call_id = str(tool_call.get("id", ""))
        function = tool_call.get("function") or {}
        tool_name = str(function.get("name", ""))
        raw_arguments = function.get("arguments") or "{}"

        tool = self.registry.get(tool_name)
        if tool is None:
            self._log(
                tool_name=tool_name,
                capability="unknown",
                decision=PolicyDecision.DENY,
                risk_level=RiskLevel.FORBIDDEN,
                args={},
                summary="Denied unknown tool.",
            )
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                allowed=False,
                content=json.dumps({"error": "unknown tool denied", "tool_name": tool_name}),
            )

        args = self._parse_arguments(raw_arguments)
        if isinstance(args, str):
            self._log(
                tool_name=tool_name,
                capability=tool.capability,
                decision=PolicyDecision.DENY,
                risk_level=RiskLevel.LOW,
                args={},
                summary=args,
            )
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                allowed=False,
                content=json.dumps({"error": args}),
            )

        policy = self.policy_engine.evaluate(tool.capability)
        risk = policy.capability.risk_level if policy.capability else RiskLevel.FORBIDDEN
        approval_result = ApprovalResult.NOT_REQUIRED
        if policy.decision is PolicyDecision.ASK:
            approval_result = self.approval_manager.request_approval(
                ApprovalRequest(
                    capability=tool.capability,
                    tool_name=tool_name,
                    risk_level=risk,
                    summary=self._approval_summary(tool_name, args, risk),
                    per_action=risk is RiskLevel.CRITICAL,
                )
            )
            if approval_result is ApprovalResult.APPROVED:
                policy_decision = PolicyDecision.ALLOW
            else:
                self._log(
                    tool_name=tool_name,
                    capability=tool.capability,
                    decision=PolicyDecision.DENY,
                    risk_level=risk,
                    args=self._sanitize_args(tool_name, args),
                    summary=f"Approval {approval_result.value}: {policy.reason}",
                    approval_result=approval_result.value,
                )
                return ToolExecutionResult(
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    allowed=False,
                    content=json.dumps(
                        {
                            "error": "approval required",
                            "decision": PolicyDecision.ASK.value,
                            "approval_result": approval_result.value,
                        }
                    ),
                )
        else:
            policy_decision = policy.decision

        if policy_decision is not PolicyDecision.ALLOW:
            self._log(
                tool_name=tool_name,
                capability=tool.capability,
                decision=policy_decision,
                risk_level=risk,
                args=self._sanitize_args(tool_name, args),
                summary=f"Denied by policy: {policy.reason}",
                approval_result=approval_result.value,
            )
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                allowed=False,
                content=json.dumps({"error": policy.reason, "decision": policy_decision.value}),
            )

        try:
            result = tool.handler(**args)
            result_payload, audit_metadata = self._split_audit_metadata(result)
            content = json.dumps(result_payload)
            self._log(
                tool_name=tool_name,
                capability=tool.capability,
                decision=policy_decision,
                risk_level=risk,
                args=self._sanitize_args(tool_name, args),
                summary="Tool executed successfully.",
                approval_result=approval_result.value,
                files_read=audit_metadata.get("files_read", []),
                files_written=audit_metadata.get("files_written", []),
                commands_run=audit_metadata.get("commands_run", []),
                network_domains=audit_metadata.get("network_domains", []),
            )
            return ToolExecutionResult(tool_call_id, tool_name, True, content)
        except ToolError as exc:
            self._log(
                tool_name=tool_name,
                capability=tool.capability,
                decision=PolicyDecision.DENY,
                risk_level=risk,
                args=self._sanitize_args(tool_name, args),
                summary=str(exc),
                approval_result=approval_result.value,
            )
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                allowed=False,
                content=json.dumps({"error": str(exc)}),
            )
        except Exception as exc:
            self._log(
                tool_name=tool_name,
                capability=tool.capability,
                decision=PolicyDecision.DENY,
                risk_level=risk,
                args=self._sanitize_args(tool_name, args),
                summary=f"Tool execution failed: {type(exc).__name__}",
                approval_result=approval_result.value,
            )
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                allowed=False,
                content=json.dumps({"error": "tool execution failed", "type": type(exc).__name__}),
            )

    def _parse_arguments(self, raw_arguments: str | dict[str, Any]) -> dict[str, Any] | str:
        if isinstance(raw_arguments, dict):
            return raw_arguments
        try:
            parsed = json.loads(raw_arguments)
        except json.JSONDecodeError:
            return "invalid tool arguments"
        if not isinstance(parsed, dict):
            return "tool arguments must be an object"
        return parsed

    def _log(
        self,
        *,
        tool_name: str,
        capability: str,
        decision: PolicyDecision,
        risk_level: RiskLevel,
        args: dict[str, Any],
        summary: str,
        approval_result: str = "not_required",
        files_read: list[str] | None = None,
        files_written: list[str] | None = None,
        commands_run: list[str] | None = None,
        network_domains: list[str] | None = None,
    ) -> None:
        self.audit_logger.log(
            AuditEvent(
                session_id=self.session_id,
                request_id=new_request_id(),
                route=self.route,
                model=self.model,
                tool_name=tool_name,
                capability=capability,
                risk_level=risk_level.value,
                trust_level=TrustLevel.MODEL_OUTPUT.value,
                policy_decision=decision.value,
                approval_result=approval_result,
                sanitized_args=args,
                result_summary=summary,
                files_read=files_read or [],
                files_written=files_written or [],
                commands_run=commands_run or [],
                network_domains=network_domains or [],
            )
        )

    def _split_audit_metadata(self, result: Any) -> tuple[Any, dict[str, list[str]]]:
        if isinstance(result, dict) and isinstance(result.get("_audit"), dict):
            result_copy = dict(result)
            audit = result_copy.pop("_audit")
            return result_copy, {
                "files_read": list(audit.get("files_read", [])),
                "files_written": list(audit.get("files_written", [])),
                "commands_run": list(audit.get("commands_run", [])),
                "network_domains": list(audit.get("network_domains", [])),
            }
        return result, {}

    def _sanitize_args(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        sanitized = dict(args)
        if tool_name.startswith("memory.") and "content" in sanitized:
            sanitized["content"] = "[MEMORY_CONTENT_REDACTED]"
        if tool_name.startswith(("email.", "messages.")):
            for key in ("thread_text", "body", "content"):
                if key in sanitized:
                    sanitized[key] = "[PERSONAL_CONTENT_REDACTED]"
        return sanitized

    def _approval_summary(self, tool_name: str, args: dict[str, Any], risk: RiskLevel) -> str:
        sanitized = self._sanitize_args(tool_name, args)
        if tool_name in {"email.send_approved", "messages.send_approved"}:
            return (
                f"Preflight for {tool_name}: recipient={args.get('to', '')}; "
                f"subject={args.get('subject', '')}; body={args.get('body', '')}; "
                f"attachments={args.get('attachments', [])}; risk={risk.value}; "
                "rollback_available=False; approval_choices=approve,deny,abort"
            )
        if tool_name.startswith("calendar."):
            return (
                f"Preflight for {tool_name}: fields={sanitized}; risk={risk.value}; "
                "rollback_available=False; approval_choices=approve,deny,abort"
            )
        if tool_name == "contacts.update_selected":
            return (
                f"Preflight for {tool_name}: fields={sanitized}; risk={risk.value}; "
                "rollback_available=False; approval_choices=approve,deny,abort"
            )
        return f"Model requested {tool_name}."
