from __future__ import annotations

import json

from agent.config.loader import load_capabilities_config
from agent.connectors.registry import default_connector_registry
from agent.core.tool_broker import ToolBroker
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry
from smart_agent import _run_messages_command


def _call(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    return {
        "id": f"call_{tool_name}",
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments)},
    }


def _broker(tmp_path) -> ToolBroker:
    capabilities = {
        "messages.inbox.import_manual": Capability(
            "messages.inbox.import_manual",
            RiskLevel.MEDIUM,
            default_enabled=True,
            stores_data=True,
        ),
        "messages.inbox.list": Capability("messages.inbox.list", RiskLevel.LOW, default_enabled=True),
        "messages.inbox.show": Capability("messages.inbox.show", RiskLevel.MEDIUM, default_enabled=True),
        "messages.inbox.draft_reply": Capability(
            "messages.inbox.draft_reply",
            RiskLevel.MEDIUM,
            default_enabled=True,
            stores_data=True,
        ),
    }
    return ToolBroker(
        default_registry(project_root=tmp_path),
        PolicyEngine(capabilities),
        AuditLogger(tmp_path / "broker-audit.jsonl"),
        session_id="incoming-message-test",
        model="test-model",
        route="test",
    )


def test_import_from_workspace_works_and_labels_untrusted(tmp_path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    source = workspace / "incoming_message.md"
    source.write_text("Hey, can you follow up tomorrow?", encoding="utf-8")

    result = _broker(tmp_path).execute(
        _call("messages.inbox.import_manual", {"from_file": "workspace/incoming_message.md"})
    )

    payload = json.loads(result.content)
    assert result.allowed is True
    assert payload["status"] == "ok"
    assert payload["message"]["trust_level"] == "UNTRUSTED_MESSAGE"
    assert payload["message"]["stored_in_memory"] is False
    assert payload["private_messages_database_accessed"] is False
    assert payload["full_disk_access_required"] is False
    assert payload["background_watcher"] is False
    event = [json.loads(line) for line in (tmp_path / "broker-audit.jsonl").read_text(encoding="utf-8").splitlines()][-1]
    assert str(source) in event["files_read"]
    assert event["tool_name"] == "messages.inbox.import_manual"


def test_unsafe_paths_and_private_messages_database_are_blocked(tmp_path) -> None:
    broker = _broker(tmp_path)

    traversal = broker.execute(_call("messages.inbox.import_manual", {"from_file": "../incoming.md"}))
    private_db = broker.execute(
        _call("messages.inbox.import_manual", {"from_file": "~/Library/Messages/chat.db"})
    )

    assert traversal.allowed is False
    assert "inside ./workspace" in json.loads(traversal.content)["error"]
    assert private_db.allowed is False
    assert "private Messages database" in json.loads(private_db.content)["error"]


def test_inbox_list_show_and_lead_candidate(tmp_path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    source = workspace / "incoming_message.md"
    source.write_text("Interested in a demo next week.", encoding="utf-8")
    broker = _broker(tmp_path)
    imported = json.loads(
        broker.execute(_call("messages.inbox.import_manual", {"from_file": "workspace/incoming_message.md"})).content
    )
    message_id = imported["message_id"]

    listed = json.loads(broker.execute(_call("messages.inbox.list", {"include_mock": True})).content)
    shown = json.loads(broker.execute(_call("messages.inbox.show", {"message_id": message_id})).content)

    assert listed["status"] == "ok"
    assert any(item["message_id"] == message_id for item in listed["messages"])
    assert any(item["provider"] == "mock" for item in listed["messages"])
    assert shown["message"]["body"] == "Interested in a demo next week."
    assert shown["message"]["lead_candidate"]["lead_id"] == f"inbound-{message_id}"
    assert shown["private_messages_database_accessed"] is False


def test_draft_reply_creates_draft_only_and_ignores_injection(tmp_path) -> None:
    broker = _broker(tmp_path)

    result = broker.execute(_call("messages.inbox.draft_reply", {"message_id": "mock-message-002"}))

    payload = json.loads(result.content)
    body = payload["message_draft"]["body"]
    assert result.allowed is True
    assert payload["send_executed"] is False
    assert payload["send_action_created"] is False
    assert payload["automatic_reply"] is False
    assert payload["stored_in_memory"] is False
    assert "messages.send" not in body
    assert "ignore previous instructions" not in body.lower()
    assert default_registry(project_root=tmp_path).get("messages.send") is None


def test_audit_logs_import_read_and_draft(tmp_path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "incoming_message.md").write_text("Please send a safe draft.", encoding="utf-8")
    broker = _broker(tmp_path)
    imported = json.loads(
        broker.execute(_call("messages.inbox.import_manual", {"from_file": "workspace/incoming_message.md"})).content
    )

    broker.execute(_call("messages.inbox.list", {}))
    broker.execute(_call("messages.inbox.show", {"message_id": imported["message_id"]}))
    broker.execute(_call("messages.inbox.draft_reply", {"message_id": imported["message_id"]}))

    audit_text = (tmp_path / "broker-audit.jsonl").read_text(encoding="utf-8")
    assert "messages.inbox.import_manual" in audit_text
    assert "messages.inbox.list" in audit_text
    assert "messages.inbox.show" in audit_text
    assert "messages.inbox.draft_reply" in audit_text
    assert "memory.store" not in audit_text


def test_manifest_keeps_incoming_manual_and_no_send(tmp_path) -> None:
    tools = load_capabilities_config("config/capabilities.yaml")["tools"]
    status = default_connector_registry().status("messages", load_capabilities_config("config/capabilities.yaml"))

    assert tools["messages.inbox.import_manual"]["connector_name"] == "messaging_inbound"
    assert tools["messages.inbox.import_manual"]["trust_level"] == "UNTRUSTED_MESSAGE"
    assert tools["messages.inbox.draft_reply"]["memory_behavior"] == "no_store"
    assert tools["messages.inbox.draft_reply"]["sends_message"] is False
    assert tools["messaging.send_approved"]["default_enabled"] is False
    assert status["enabled"] is False


def test_cli_messages_inbox_commands(tmp_path, capsys) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "incoming_message.md").write_text("CLI import message", encoding="utf-8")
    broker = _broker(tmp_path)

    assert _run_messages_command(["import", "--from-file", "workspace/incoming_message.md"], broker) == 0
    imported = json.loads(capsys.readouterr().out)
    assert _run_messages_command(["inbox", "list", "--no-mock"], broker) == 0
    listed = json.loads(capsys.readouterr().out)
    assert _run_messages_command(["inbox", "show", imported["message_id"]], broker) == 0
    shown = json.loads(capsys.readouterr().out)
    assert _run_messages_command(["inbox", "draft-reply", imported["message_id"]], broker) == 0
    drafted = json.loads(capsys.readouterr().out)

    assert listed["count"] == 1
    assert shown["message"]["trust_level"] == "UNTRUSTED_MESSAGE"
    assert drafted["send_executed"] is False
