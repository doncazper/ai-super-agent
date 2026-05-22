from __future__ import annotations

import json

from agent.core.tool_broker import ToolBroker
from agent.safety.approvals import ApprovalManager, ApprovalResult
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.safety.redaction import SecretRedactor
from agent.tools.registry import ToolRegistry, ToolSpec


def echo_secret(secret: str = "") -> dict[str, str]:
    return {"received": secret}


def make_registry(name: str, capability: str) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            name=name,
            capability=capability,
            schema={
                "type": "function",
                "function": {
                    "name": name,
                    "description": "test tool",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            handler=echo_secret,
        )
    )
    return registry


def test_high_action_requests_approval_and_denial_is_audited(tmp_path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    approvals = ApprovalManager()
    broker = ToolBroker(
        make_registry("email.read_selected_thread", "email.read_selected_thread"),
        PolicyEngine(
            {
                "email.read_selected_thread": Capability(
                    name="email.read_selected_thread",
                    risk_level=RiskLevel.HIGH,
                    default_enabled=True,
                    approval_required=True,
                )
            }
        ),
        AuditLogger(audit_path),
        session_id="test-session",
        approval_manager=approvals,
    )

    result = broker.execute(
        {
            "id": "call_high",
            "type": "function",
            "function": {"name": "email.read_selected_thread", "arguments": "{}"},
        }
    )

    assert result.allowed is False
    assert len(approvals.requests) == 1
    assert approvals.requests[0].risk_level is RiskLevel.HIGH
    event = json.loads(audit_path.read_text(encoding="utf-8").splitlines()[0])
    assert event["approval_result"] == ApprovalResult.DENIED.value
    assert event["policy_decision"] == "DENY"


def test_critical_action_requests_per_action_approval(tmp_path) -> None:
    approvals = ApprovalManager()
    broker = ToolBroker(
        make_registry("email.send", "email.send"),
        PolicyEngine(
            {
                "email.send": Capability(
                    name="email.send",
                    risk_level=RiskLevel.CRITICAL,
                    default_enabled=True,
                    approval_required="per_action",
                    approval_reuse_allowed=False,
                )
            }
        ),
        AuditLogger(tmp_path / "audit.jsonl"),
        session_id="test-session",
        approval_manager=approvals,
    )

    result = broker.execute(
        {
            "id": "call_critical",
            "type": "function",
            "function": {"name": "email.send", "arguments": "{}"},
        }
    )

    assert result.allowed is False
    assert len(approvals.requests) == 1
    assert approvals.requests[0].per_action is True


def test_secrets_are_redacted_from_audit_logs(tmp_path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    broker = ToolBroker(
        make_registry("test.secret_echo", "test.secret_echo"),
        PolicyEngine(
            {
                "test.secret_echo": Capability(
                    name="test.secret_echo",
                    risk_level=RiskLevel.SAFE,
                    default_enabled=True,
                )
            }
        ),
        AuditLogger(audit_path, redactor=SecretRedactor()),
        session_id="test-session",
    )

    broker.execute(
        {
            "id": "call_secret",
            "type": "function",
            "function": {
                "name": "test.secret_echo",
                "arguments": json.dumps({"api_key": "sk-verysecretvalue123456"}),
            },
        }
    )

    raw_log = audit_path.read_text(encoding="utf-8")
    assert "sk-verysecretvalue123456" not in raw_log
    event = json.loads(raw_log.splitlines()[0])
    assert event["sanitized_args"]["api_key"] == "[REDACTED]"
