from __future__ import annotations

import json

from agent.core.tool_broker import ToolBroker
from agent.safety.action_preview import ActionPreviewError, ActionPreviewFormatter
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry


def call(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    return {
        "id": f"call_{tool_name}",
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments)},
    }


def test_action_preview_redacts_secrets() -> None:
    preview = ActionPreviewFormatter().format(
        "web.fetch_url",
        {"url": "https://example.com", "api_key": "sk-verysecretvalue123456"},
        RiskLevel.MEDIUM,
    )

    payload = preview.to_dict()
    assert payload["sanitized_args"]["api_key"] == "[REDACTED]"
    assert "sk-verysecretvalue123456" not in json.dumps(payload)


def test_critical_preview_requires_exact_args() -> None:
    formatter = ActionPreviewFormatter()

    try:
        formatter.format("email.send_approved", {"to": "a@example.com", "subject": "Hi"}, RiskLevel.CRITICAL)
    except ActionPreviewError as exc:
        assert "body" in str(exc)
    else:
        raise AssertionError("expected exact arg validation")


def test_missing_exact_args_blocks_critical_execution(tmp_path) -> None:
    broker = ToolBroker(
        default_registry(project_root=tmp_path),
        PolicyEngine(
            {
                "email.send_approved": Capability(
                    "email.send_approved",
                    RiskLevel.CRITICAL,
                    default_enabled=True,
                    approval_required="per_action",
                    approval_reuse_allowed=False,
                )
            }
        ),
        AuditLogger(tmp_path / "audit.jsonl"),
        session_id="test-session",
        model="test-model",
        route="test",
    )

    result = broker.execute(call("email.send_approved", {"to": "a@example.com", "subject": "Hi"}))

    assert result.allowed is False
    assert "missing exact args" in json.loads(result.content)["error"]


def test_dry_run_shows_approval_requirements(tmp_path) -> None:
    broker = ToolBroker(
        default_registry(project_root=tmp_path),
        PolicyEngine(
            {
                "git.commit": Capability(
                    "git.commit",
                    RiskLevel.HIGH,
                    default_enabled=True,
                    approval_required=True,
                )
            }
        ),
        AuditLogger(tmp_path / "audit.jsonl"),
        session_id="test-session",
        model="test-model",
        route="test",
        dry_run=True,
    )

    result = broker.execute(call("git.commit", {"message": "checkpoint"}))

    payload = json.loads(result.content)
    assert payload["dry_run"] is True
    assert payload["approval_required"] is True
    assert payload["would_execute"] is False
    assert payload["sanitized_args"]["message"] == "checkpoint"
