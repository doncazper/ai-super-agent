from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from agent.config.runtime import env_bool
from agent.safety.action_preview import ActionPreviewError, ActionPreviewFormatter
from agent.safety.audit import AuditEvent, AuditLogger, new_request_id
from agent.safety.approvals import ApprovalManager, ApprovalRequest, ApprovalResult
from agent.safety.policy import PolicyDecision, PolicyEngine, RiskLevel
from agent.safety.rate_limits import RateLimiter
from agent.safety.trust import TrustLevel
from agent.tools.errors import ToolError
from agent.tools.registry import ToolRegistry


@dataclass(frozen=True)
class ToolExecutionResult:
    tool_call_id: str
    tool_name: str
    allowed: bool
    content: str
    debug: dict[str, Any] | None = None


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
        dry_run: bool = False,
    ) -> None:
        self.registry = registry
        self.policy_engine = policy_engine
        self.audit_logger = audit_logger
        self.session_id = session_id
        self.model = model
        self.route = route
        self.dry_run_mode = dry_run
        self.approval_manager = approval_manager or ApprovalManager()
        self.approval_manager.configure_audit(
            audit_logger,
            session_id=session_id,
            model=model,
            route=route,
        )
        self._rate_limiters: dict[str, RateLimiter] = {}
        self.preview_formatter = ActionPreviewFormatter()

    def dry_run(self, tool_call: dict[str, Any]) -> ToolExecutionResult:
        tool_call_id = str(tool_call.get("id", ""))
        function = tool_call.get("function") or {}
        tool_name = str(function.get("name", ""))
        raw_arguments = function.get("arguments") or "{}"
        tool = self.registry.get(tool_name)
        if tool is None:
            audit = self._log(
                tool_name=tool_name,
                capability="unknown",
                decision=PolicyDecision.DENY,
                risk_level=RiskLevel.FORBIDDEN,
                args={},
                summary="Dry-run denied unknown tool.",
                dry_run=True,
            )
            return ToolExecutionResult(
                tool_call_id,
                tool_name,
                False,
                json.dumps({"dry_run": True, "would_execute": False, "error": "unknown tool denied"}),
                debug=self._debug_from_audit(audit),
            )
        args = self._parse_arguments(raw_arguments)
        if isinstance(args, str):
            audit = self._log(
                tool_name=tool_name,
                capability=tool.capability,
                decision=PolicyDecision.DENY,
                risk_level=RiskLevel.LOW,
                args={},
                summary=f"Dry-run invalid arguments: {args}",
                dry_run=True,
            )
            return ToolExecutionResult(
                tool_call_id,
                tool_name,
                False,
                json.dumps({"dry_run": True, "would_execute": False, "error": args}),
                debug=self._debug_from_audit(audit),
            )
        policy = self.policy_engine.evaluate(tool.capability)
        risk = policy.capability.risk_level if policy.capability else RiskLevel.FORBIDDEN
        approval_required = policy.decision is PolicyDecision.ASK
        would_execute = policy.decision is PolicyDecision.ALLOW
        try:
            preview = self.preview_formatter.format(tool_name, args, risk).to_dict()
            preview["sanitized_args"] = self._sanitize_args(tool_name, args)
        except ActionPreviewError as exc:
            audit = self._log(
                tool_name=tool_name,
                capability=tool.capability,
                decision=PolicyDecision.DENY,
                risk_level=risk,
                args=self._sanitize_args(tool_name, args),
                summary=f"Dry-run blocked: {exc}",
                dry_run=True,
            )
            return ToolExecutionResult(
                tool_call_id,
                tool_name,
                False,
                json.dumps({"dry_run": True, "would_execute": False, "error": str(exc)}),
                debug=self._debug_from_audit(audit),
            )
        audit = self._log(
            tool_name=tool_name,
            capability=tool.capability,
            decision=policy.decision,
            risk_level=risk,
            args=self._sanitize_args(tool_name, args),
            summary="Dry-run evaluated tool call.",
            dry_run=True,
        )
        return ToolExecutionResult(
            tool_call_id,
            tool_name,
            would_execute,
            json.dumps(
                {
                    "dry_run": True,
                    "tool_name": tool_name,
                    "capability": tool.capability,
                    "risk_level": risk.value,
                    "policy_decision": policy.decision.value,
                    "approval_required": approval_required,
                    "approval_type": "per_action" if risk is RiskLevel.CRITICAL else ("once" if approval_required else "none"),
                    "would_execute": would_execute,
                    "sanitized_args": self._sanitize_args(tool_name, args),
                    "preview": preview,
                }
            ),
            debug=self._debug_from_audit(audit),
        )

    def execute(self, tool_call: dict[str, Any]) -> ToolExecutionResult:
        if self.dry_run_mode:
            return self.dry_run(tool_call)
        tool_call_id = str(tool_call.get("id", ""))
        function = tool_call.get("function") or {}
        tool_name = str(function.get("name", ""))
        raw_arguments = function.get("arguments") or "{}"

        tool = self.registry.get(tool_name)
        if tool is None:
            audit = self._log(
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
                debug=self._debug_from_audit(audit),
            )

        args = self._parse_arguments(raw_arguments)
        if isinstance(args, str):
            audit = self._log(
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
                debug=self._debug_from_audit(audit),
            )

        policy = self.policy_engine.evaluate(tool.capability)
        risk = policy.capability.risk_level if policy.capability else RiskLevel.FORBIDDEN
        approval_result = ApprovalResult.NOT_REQUIRED
        approval_request: ApprovalRequest | None = None
        try:
            preview = self.preview_formatter.format(tool_name, args, risk)
        except ActionPreviewError as exc:
            audit = self._log(
                tool_name=tool_name,
                capability=tool.capability,
                decision=PolicyDecision.DENY,
                risk_level=risk,
                args=self._sanitize_args(tool_name, args),
                summary=f"Blocked by action preview: {exc}",
            )
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                allowed=False,
                content=json.dumps({"error": str(exc), "decision": PolicyDecision.DENY.value}),
                debug=self._debug_from_audit(audit),
            )
        if policy.decision is PolicyDecision.ASK:
            approval_request = ApprovalRequest(
                capability=tool.capability,
                tool_name=tool_name,
                risk_level=risk,
                summary=self._approval_summary(tool_name, args, risk, preview),
                per_action=risk is RiskLevel.CRITICAL,
                session_id=self.session_id,
                trust_level=self._trust_level_for_tool(tool_name),
                args_preview=self._sanitize_args(tool_name, args),
                rollback_available=preview.rollback_available,
            )
            approval_result = self.approval_manager.request_approval(approval_request)
            if approval_result is ApprovalResult.APPROVED:
                policy_decision = PolicyDecision.ALLOW
            else:
                audit = self._log(
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
                            "detail": "approval required but approval UI unavailable, denied, aborted, or expired",
                            "decision": PolicyDecision.ASK.value,
                            "approval_result": approval_result.value,
                            "approval_request_id": approval_request.request_id,
                        }
                    ),
                    debug=self._debug_from_audit(audit),
                )
        else:
            policy_decision = policy.decision

        if policy_decision is not PolicyDecision.ALLOW:
            audit = self._log(
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
                debug=self._debug_from_audit(audit),
            )

        requires_web_access = bool(policy.capability and policy.capability.metadata.get("requires_web_access"))
        if requires_web_access and not env_bool("WEB_ACCESS_ENABLED", default=True):
            audit = self._log(
                tool_name=tool_name,
                capability=tool.capability,
                decision=PolicyDecision.DENY,
                risk_level=risk,
                args=self._sanitize_args(tool_name, args),
                summary="Denied by policy: web access disabled",
                approval_result=approval_result.value,
            )
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                allowed=False,
                content=json.dumps({"error": "web access disabled", "decision": PolicyDecision.DENY.value}),
                debug=self._debug_from_audit(audit),
            )

        if not self._rate_limit_allowed(tool.capability):
            audit = self._log(
                tool_name=tool_name,
                capability=tool.capability,
                decision=PolicyDecision.DENY,
                risk_level=risk,
                args=self._sanitize_args(tool_name, args),
                summary="Denied by policy: rate limit exceeded",
                approval_result=approval_result.value,
            )
            return ToolExecutionResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                allowed=False,
                content=json.dumps({"error": "rate limit exceeded", "decision": PolicyDecision.DENY.value}),
                debug=self._debug_from_audit(audit),
            )

        try:
            result = tool.handler(**args)
            result_payload, audit_metadata = self._split_audit_metadata(result)
            content = json.dumps(result_payload)
            if approval_request is not None and approval_result is ApprovalResult.APPROVED:
                self.approval_manager.mark_used(approval_request)
            audit = self._log(
                tool_name=tool_name,
                capability=tool.capability,
                decision=policy_decision,
                risk_level=risk,
                args=self._sanitize_args(tool_name, args),
                summary=str(audit_metadata.get("result_summary") or "Tool executed successfully."),
                approval_result=approval_result.value,
                files_read=audit_metadata.get("files_read", []),
                files_written=audit_metadata.get("files_written", []),
                commands_run=audit_metadata.get("commands_run", []),
                network_domains=audit_metadata.get("network_domains", []),
            )
            return ToolExecutionResult(tool_call_id, tool_name, True, content, debug=self._debug_from_audit(audit))
        except ToolError as exc:
            audit = self._log(
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
                debug=self._debug_from_audit(audit),
            )
        except Exception as exc:
            audit = self._log(
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
                debug=self._debug_from_audit(audit),
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
        dry_run: bool = False,
    ) -> dict[str, Any]:
        return self.audit_logger.log(
            AuditEvent(
                session_id=self.session_id,
                request_id=new_request_id(),
                route=self.route,
                model=self.model,
                tool_name=tool_name,
                capability=capability,
                risk_level=risk_level.value,
                trust_level=self._trust_level_for_tool(tool_name).value,
                policy_decision=decision.value,
                approval_result=approval_result,
                sanitized_args=args,
                result_summary=summary,
                files_read=files_read or [],
                files_written=files_written or [],
                commands_run=commands_run or [],
                network_domains=network_domains or [],
                dry_run=dry_run,
            )
        )

    def _split_audit_metadata(self, result: Any) -> tuple[Any, dict[str, Any]]:
        if isinstance(result, dict) and isinstance(result.get("_audit"), dict):
            result_copy = dict(result)
            audit = result_copy.pop("_audit")
            return result_copy, {
                "files_read": list(audit.get("files_read", [])),
                "files_written": list(audit.get("files_written", [])),
                "commands_run": list(audit.get("commands_run", [])),
                "network_domains": list(audit.get("network_domains", [])),
                "result_summary": audit.get("result_summary"),
            }
        return result, {}

    def _sanitize_args(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        sanitized = dict(args)
        if tool_name == "web.search" and "query" in sanitized and not env_bool(
            "WEB_SEARCH_AUDIT_QUERIES",
            default=False,
        ):
            sanitized["query"] = "[WEB_SEARCH_QUERY_REDACTED]"
        if tool_name.startswith("weather.") and "location" in sanitized:
            sanitized["location"] = "[WEATHER_LOCATION_REDACTED]"
        if tool_name.startswith("memory.") and "content" in sanitized:
            sanitized["content"] = "[MEMORY_CONTENT_REDACTED]"
        if tool_name.startswith(("email.", "messages.")):
            for key in ("thread_text", "body", "content"):
                if key in sanitized:
                    sanitized[key] = "[PERSONAL_CONTENT_REDACTED]"
        return sanitized

    def _trust_level_for_tool(self, tool_name: str) -> TrustLevel:
        if tool_name.startswith("calendar."):
            return TrustLevel.LOCAL_PRIVATE_DATA
        if tool_name.startswith("email."):
            return TrustLevel.UNTRUSTED_EMAIL
        if tool_name.startswith("messages."):
            return TrustLevel.UNTRUSTED_MESSAGE
        if tool_name.startswith(("web.", "weather.")):
            return TrustLevel.UNTRUSTED_WEB
        if tool_name.startswith(("contacts.", "browser.")):
            return TrustLevel.LOCAL_PRIVATE_DATA
        return TrustLevel.MODEL_OUTPUT

    def _rate_limit_allowed(self, capability_name: str) -> bool:
        capability = self.policy_engine.get_capability(capability_name)
        if capability is None:
            return False
        raw_rate_limit = capability.metadata.get("rate_limit")
        if not isinstance(raw_rate_limit, dict):
            return True
        requests_per_minute = raw_rate_limit.get("requests_per_minute")
        if not isinstance(requests_per_minute, int) or requests_per_minute <= 0:
            return True
        limiter = self._rate_limiters.setdefault(capability_name, RateLimiter(requests_per_minute))
        return limiter.allow(capability_name)

    def _approval_summary(
        self,
        tool_name: str,
        args: dict[str, Any],
        risk: RiskLevel,
        preview: Any | None = None,
    ) -> str:
        preview = preview or self.preview_formatter.format(tool_name, args, risk)
        return (
            f"Preflight for {tool_name}: {preview.summary}; risk={risk.value}; "
            f"rollback_available={preview.rollback_available}; approval_choices=approve,deny,abort"
        )

    def _approval_args_preview(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        from agent.safety.redaction import SecretRedactor

        preview = SecretRedactor().redact(args)
        if tool_name == "messages.send_approved" and "body" in preview:
            preview["exact_message"] = preview["body"]
        return preview

    def _rollback_available(self, tool_name: str) -> bool:
        return tool_name in {"filesystem.write", "filesystem.patch"}

    def _debug_from_audit(self, audit: dict[str, Any]) -> dict[str, Any]:
        return {
            "policy_decision": audit.get("policy_decision"),
            "approval_result": audit.get("approval_result"),
            "risk_level": audit.get("risk_level"),
            "audit_path": str(self.audit_logger.path),
            "audit_request_id": audit.get("request_id"),
            "audit_hash": audit.get("hash_current"),
        }
