from __future__ import annotations

import json
from pathlib import Path

from agent.core.tool_broker import ToolBroker
from agent.memory.persistent_memory import PersistentMemoryStore
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry


def memory_capabilities() -> dict[str, Capability]:
    return {
        "memory.store": Capability("memory.store", RiskLevel.LOW, stores_data=True),
        "memory.store_personal": Capability(
            "memory.store_personal",
            RiskLevel.HIGH,
            default_enabled=True,
            approval_required=True,
            stores_data=True,
        ),
        "memory.search": Capability("memory.search", RiskLevel.LOW),
        "memory.export": Capability("memory.export", RiskLevel.LOW),
        "memory.delete": Capability("memory.delete", RiskLevel.LOW),
    }


def make_broker(tmp_path) -> ToolBroker:
    return ToolBroker(
        default_registry(project_root=tmp_path, memory_path=tmp_path / "memory.sqlite3"),
        PolicyEngine(memory_capabilities()),
        AuditLogger(tmp_path / "audit.jsonl"),
        session_id="test-session",
        model="test-model",
        route="test",
    )


def call(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    return {
        "id": f"call_{tool_name}",
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments)},
    }


def test_preference_memory_stored(tmp_path) -> None:
    broker = make_broker(tmp_path)

    result = broker.execute(
        call(
            "memory.store",
            {"content": "User prefers concise answers.", "category": "user_preference"},
        )
    )

    assert result.allowed is True
    payload = json.loads(result.content)
    assert payload["stored"] is True
    assert payload["record"]["category"] == "user_preference"


def test_secret_memory_rejected_and_audit_redacts_content(tmp_path) -> None:
    broker = make_broker(tmp_path)

    result = broker.execute(
        call(
            "memory.store",
            {"content": "api_key=sk-supersecretvalue123456", "category": "project_fact"},
        )
    )

    assert result.allowed is False
    assert json.loads(result.content)["error"] == "memory content contains a secret and was not stored"
    raw_log = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
    assert "sk-supersecretvalue123456" not in raw_log
    event = json.loads(raw_log.splitlines()[0])
    assert event["sanitized_args"]["content"] == "[MEMORY_CONTENT_REDACTED]"


def test_email_body_not_stored_by_default(tmp_path) -> None:
    broker = make_broker(tmp_path)

    result = broker.execute(
        call(
            "memory.store",
            {
                "content": "Email body: private dinner plans",
                "category": "project_fact",
                "source_trust": "UNTRUSTED_EMAIL",
            },
        )
    )

    assert result.allowed is False
    assert json.loads(result.content)["error"] == "personal data memory requires approval"
    assert PersistentMemoryStore(tmp_path / "memory.sqlite3").export(scope="default") == []


def test_personal_data_requires_approval(tmp_path) -> None:
    broker = make_broker(tmp_path)

    result = broker.execute(
        call(
            "memory.store_personal",
            {
                "content": "Selected contact phone number",
                "category": "personal_data_reference",
            },
        )
    )

    assert result.allowed is False
    assert json.loads(result.content)["approval_result"] == "denied"
    assert PersistentMemoryStore(tmp_path / "memory.sqlite3").export(scope="default") == []


def test_memory_search_respects_scope(tmp_path) -> None:
    broker = make_broker(tmp_path)
    broker.execute(
        call(
            "memory.store",
            {"content": "Project uses LM Studio.", "category": "project_fact", "scope": "agent"},
        )
    )
    broker.execute(
        call(
            "memory.store",
            {"content": "Project uses another runtime.", "category": "project_fact", "scope": "other"},
        )
    )

    result = broker.execute(call("memory.search", {"query": "Project uses", "scope": "agent"}))

    payload = json.loads(result.content)
    assert len(payload["results"]) == 1
    assert payload["results"][0]["scope"] == "agent"


def test_memory_delete_removes_record(tmp_path) -> None:
    broker = make_broker(tmp_path)
    stored = broker.execute(
        call(
            "memory.store",
            {"content": "Delete this workflow lesson.", "category": "workflow_lesson"},
        )
    )
    record_id = json.loads(stored.content)["record"]["id"]

    delete_result = broker.execute(call("memory.delete", {"record_id": record_id}))
    search_result = broker.execute(call("memory.search", {"query": "Delete this"}))

    assert json.loads(delete_result.content)["deleted"] is True
    assert json.loads(search_result.content)["results"] == []


def test_audit_logs_memory_operations(tmp_path) -> None:
    broker = make_broker(tmp_path)

    broker.execute(
        call(
            "memory.store",
            {"content": "Remember this project fact.", "category": "project_fact"},
        )
    )
    broker.execute(call("memory.search", {"query": "project fact"}))

    events = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [event["tool_name"] for event in events] == ["memory.store", "memory.search"]
    assert events[0]["sanitized_args"]["content"] == "[MEMORY_CONTENT_REDACTED]"
