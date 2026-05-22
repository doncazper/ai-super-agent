from __future__ import annotations

import json
import sys

import pytest

from agent.core.lmstudio_client import LMStudioConfig, LMStudioClient
from agent.core.tool_broker import ToolBroker
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry
from agent.workflows.self_improvement import SelfImprovementManager
from agent.tools.errors import ToolError


def call(tool_name: str, arguments: dict[str, object] | None = None) -> dict[str, object]:
    return {
        "id": f"call_{tool_name}",
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments or {})},
    }


def broad_policy() -> PolicyEngine:
    return PolicyEngine(
        {
            "time.get_current_time": Capability("time.get_current_time", RiskLevel.SAFE),
            "filesystem.read": Capability("filesystem.read", RiskLevel.LOW),
            "web.fetch_url": Capability("web.fetch_url", RiskLevel.MEDIUM),
            "email.send_approved": Capability("email.send_approved", RiskLevel.CRITICAL, approval_required="per_action"),
            "messages.send_approved": Capability("messages.send_approved", RiskLevel.CRITICAL, approval_required="per_action"),
            "calendar.create_event": Capability("calendar.create_event", RiskLevel.CRITICAL, approval_required="per_action"),
            "contacts.update_selected": Capability("contacts.update_selected", RiskLevel.CRITICAL, approval_required="per_action"),
            "memory.store": Capability("memory.store", RiskLevel.LOW),
        }
    )


def make_broker(tmp_path) -> ToolBroker:
    return ToolBroker(
        default_registry(project_root=tmp_path, memory_path=tmp_path / "memory.sqlite3"),
        broad_policy(),
        AuditLogger(tmp_path / "audit.jsonl"),
        session_id="release-gate",
        model="test-model",
        route="release",
    )


def test_release_gate_normal_chat_payload_attaches_no_tools() -> None:
    payload = LMStudioClient(LMStudioConfig(model="test-model")).build_payload(
        [{"role": "user", "content": "hello"}],
        tools=None,
    )

    assert "tools" not in payload


def test_release_gate_unknown_tool_denied_and_audited(tmp_path) -> None:
    broker = make_broker(tmp_path)

    result = broker.execute(call("unknown.tool"))

    assert result.allowed is False
    event = json.loads((tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert event["policy_decision"] == "DENY"


def test_release_gate_path_and_denied_file_blocked(tmp_path) -> None:
    broker = make_broker(tmp_path)
    (tmp_path / ".env").write_text("SECRET=value", encoding="utf-8")

    traversal = broker.execute(call("filesystem.read", {"path": "../outside"}))
    denied = broker.execute(call("filesystem.read", {"path": ".env"}))

    assert json.loads(traversal.content)["error"] == "path traversal is blocked"
    assert json.loads(denied.content)["error"] == "access to denied filename is blocked"


def test_release_gate_write_actions_require_approval(tmp_path) -> None:
    broker = make_broker(tmp_path)

    assert broker.execute(call("email.send_approved", {"to": "a@example.com", "subject": "s", "body": "b"})).allowed is False
    assert broker.execute(call("messages.send_approved", {"to": "+1555", "body": "b"})).allowed is False
    assert broker.execute(call("calendar.create_event", {"title": "t", "start": "s", "end": "e"})).allowed is False
    assert broker.execute(call("contacts.update_selected", {"selected_scope_token": "s", "changes": {"name": "n"}})).allowed is False


def test_release_gate_memory_refuses_secrets(tmp_path) -> None:
    broker = make_broker(tmp_path)

    result = broker.execute(call("memory.store", {"content": "password=hunter2", "category": "project_fact"}))

    assert result.allowed is False
    assert "secret" in json.loads(result.content)["error"]


def test_release_gate_self_improvement_policy_reduction_blocked(tmp_path) -> None:
    project = tmp_path / "repo"
    project.mkdir()
    manager = SelfImprovementManager(project, python_executable=sys.executable)

    with pytest.raises(ToolError):
        manager.implement(
            approved_feature="weaken",
            branch_name="codex/weaken-policy",
            file_writes={"config/capabilities.yaml": "tools: {}\n"},
        )
