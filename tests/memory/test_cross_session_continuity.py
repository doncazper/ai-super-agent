from __future__ import annotations

import json

from agent.core.tool_broker import ToolBroker
from agent.memory.persistent_memory import PersistentMemoryStore
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry
from agent.ui.command_registry import list_commands


def _capabilities() -> dict[str, Capability]:
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
        "memory.delete": Capability("memory.delete", RiskLevel.LOW),
        "memory.context": Capability("memory.context", RiskLevel.LOW),
        "memory.continuity_status": Capability("memory.continuity_status", RiskLevel.LOW),
        "memory.continuity_build_summary": Capability("memory.continuity_build_summary", RiskLevel.LOW),
        "memory.continuity_clear": Capability("memory.continuity_clear", RiskLevel.LOW),
        "memory.context_preview": Capability("memory.context_preview", RiskLevel.LOW),
    }


def _broker(tmp_path) -> ToolBroker:
    return ToolBroker(
        default_registry(project_root=tmp_path, memory_path=tmp_path / "memory.sqlite3"),
        PolicyEngine(_capabilities()),
        AuditLogger(tmp_path / "audit.jsonl"),
        session_id="test-session",
        model="test-model",
        route="test",
    )


def _call(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    return {
        "id": f"call_{tool_name}",
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments)},
    }


def _payload(result) -> dict[str, object]:
    return json.loads(result.content)


def test_safe_project_fact_retrieved_for_continuity(tmp_path) -> None:
    broker = _broker(tmp_path)
    broker.execute(_call("memory.store", {"content": "Project uses pytest for regressions.", "category": "project_fact"}))

    result = broker.execute(_call("memory.continuity_build_summary", {"query": "pytest"}))

    payload = _payload(result)
    assert payload["memory_written"] is False
    assert payload["personal_data_included"] is False
    assert "pytest" in payload["summary"]
    assert payload["injected_memory_ids"]


def test_secret_memory_rejected_and_redacted_in_continuity_summary(tmp_path) -> None:
    broker = _broker(tmp_path)
    rejected = broker.execute(
        _call("memory.store", {"content": "api_key=sk-supersecretvalue123456", "category": "project_fact"})
    )
    assert rejected.allowed is False

    PersistentMemoryStore(tmp_path / "memory.sqlite3").add(
        content="Rotate api_key=sk-supersecretvalue123456 after tests.",
        category="project_fact",
    )

    result = broker.execute(_call("memory.continuity_build_summary", {"query": "Rotate"}))
    payload = _payload(result)
    assert "sk-supersecretvalue123456" not in payload["summary"]
    assert "[REDACTED]" in payload["summary"]


def test_personal_memory_requires_approval_and_is_excluded_from_preview(tmp_path) -> None:
    broker = _broker(tmp_path)
    denied = broker.execute(
        _call(
            "memory.store",
            {
                "content": "Personal appointment detail",
                "category": "personal_data_reference",
                "source_trust": "LOCAL_PRIVATE_DATA",
            },
        )
    )
    assert denied.allowed is False
    PersistentMemoryStore(tmp_path / "memory.sqlite3").add(
        content="Personal appointment detail",
        category="personal_data_reference",
        source_trust="LOCAL_PRIVATE_DATA",
    )

    preview = broker.execute(_call("memory.context_preview", {"query": "Personal"}))

    payload = _payload(preview)
    assert payload["personal_data_included"] is False
    assert payload["context_preview"] == ""
    assert payload["injected_memory_ids"] == []


def test_context_preview_redacts_pii_and_does_not_inject(tmp_path) -> None:
    broker = _broker(tmp_path)
    broker.execute(
        _call(
            "memory.store",
            {
                "content": "Workflow owner can be reached at owner@example.com or 415-555-1212.",
                "category": "workflow_lesson",
            },
        )
    )

    preview = broker.execute(_call("memory.context_preview", {"query": "Workflow owner", "max_chars": 300}))

    payload = _payload(preview)
    assert payload["injection_performed"] is False
    assert payload["memory_written"] is False
    assert "owner@example.com" not in payload["context_preview"]
    assert "415-555-1212" not in payload["context_preview"]
    assert "[REDACTED_EMAIL]" in payload["context_preview"]
    assert "[REDACTED_PHONE]" in payload["context_preview"]


def test_token_limit_enforced_for_context_preview(tmp_path) -> None:
    broker = _broker(tmp_path)
    broker.execute(
        _call(
            "memory.store",
            {
                "content": "Project fact one is short.",
                "category": "project_fact",
            },
        )
    )
    broker.execute(
        _call(
            "memory.store",
            {
                "content": "Project fact two is intentionally too long for the tiny budget.",
                "category": "project_fact",
            },
        )
    )

    result = broker.execute(_call("memory.context_preview", {"query": "Project fact", "max_chars": 40}))

    payload = _payload(result)
    assert payload["character_budget"] == 40
    assert payload["truncated"] is True
    assert len(payload["context_preview"]) <= 40


def test_deletion_removes_item_from_search(tmp_path) -> None:
    broker = _broker(tmp_path)
    stored = broker.execute(_call("memory.store", {"content": "Delete continuity test fact.", "category": "project_fact"}))
    record_id = _payload(stored)["record"]["id"]

    broker.execute(_call("memory.delete", {"record_id": record_id}))
    result = broker.execute(_call("memory.search", {"query": "Delete continuity"}))

    assert _payload(result)["results"] == []


def test_continuity_clear_is_noop_and_does_not_delete_memory(tmp_path) -> None:
    broker = _broker(tmp_path)
    broker.execute(_call("memory.store", {"content": "Keep this project fact.", "category": "project_fact"}))

    clear = broker.execute(_call("memory.continuity_clear", {}))
    search = broker.execute(_call("memory.search", {"query": "Keep this"}))

    assert _payload(clear)["memory_written"] is False
    assert _payload(clear)["cleared"] is False
    assert len(_payload(search)["results"]) == 1


def test_command_registry_includes_continuity_commands() -> None:
    commands = {record.command_id: record for record in list_commands()}

    for command_id in ["CMD-MEMORY-008", "CMD-MEMORY-009", "CMD-MEMORY-010", "CMD-MEMORY-011"]:
        record = commands[command_id]
        assert record.status == "active"
        assert record.example
        assert record.risk_level in {"SAFE", "LOW"}
        assert "memory" in record.toolbroker_path
