from __future__ import annotations

import json
from pathlib import Path

from agent.config.loader import load_capabilities_config
from agent.config.runtime import RuntimeConfig
from agent.core.tool_broker import ToolBroker
from agent.memory.persistent_memory import PersistentMemoryStore
from agent.safety.audit import AuditLogger
from agent.safety.policy import PolicyEngine
from agent.tools.registry import default_registry
from agent.ui.privacy_center import (
    CONFIRM_DELETE_MEMORY,
    privacy_audit_summary,
    privacy_delete_memory,
    privacy_export,
    privacy_inventory,
    privacy_permissions,
    privacy_status,
)
from smart_agent import _run_privacy_command


REPO_ROOT = Path(__file__).resolve().parents[1]
CAPABILITIES_PATH = REPO_ROOT / "config" / "capabilities.yaml"


def _runtime(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        audit_log_path=str(tmp_path / "logs" / "audit.jsonl"),
        capabilities_path=str(CAPABILITIES_PATH),
    )


def _broker(tmp_path: Path) -> ToolBroker:
    audit = AuditLogger(tmp_path / "logs" / "audit.jsonl")
    return ToolBroker(
        default_registry(project_root=tmp_path, memory_path=tmp_path / "data" / "memory.sqlite3"),
        PolicyEngine.from_config(load_capabilities_config(CAPABILITIES_PATH)),
        audit,
        session_id="privacy-test",
        model="test-model",
        route="privacy-test",
    )


def _events(tmp_path: Path) -> list[dict[str, object]]:
    path = tmp_path / "logs" / "audit.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_privacy_status_works_and_audits(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    runtime = _runtime(tmp_path)

    report = privacy_status(project_root=tmp_path, runtime=runtime, audit_logger=AuditLogger(runtime.audit_log_path))

    assert report["status"] == "ok"
    assert report["personal_connector_reads_performed"] is False
    assert "disabled" in report["connectors"]
    assert report["connectors"]["personal_connector_reads_disabled_by_default"] is True
    assert report["connectors"]["personal_data_capabilities_requiring_approval"] is True
    assert _events(tmp_path)[-1]["tool_name"] == "privacy.status"


def test_privacy_inventory_shows_disabled_connectors_and_memory_counts_without_contents(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    PersistentMemoryStore(tmp_path / "data" / "memory.sqlite3").add(
        content="Project fact: privacy inventory counts memory.",
        category="project_fact",
        scope="default",
    )

    report = privacy_inventory(project_root=tmp_path, runtime=_runtime(tmp_path), audit_logger=AuditLogger(tmp_path / "logs" / "audit.jsonl"))

    disabled_names = {item["name"] for item in report["disabled_connectors"]}
    assert {"calendar", "contacts", "email", "messages"}.issubset(disabled_names)
    assert report["memory"]["total_records"] == 1
    assert report["memory"]["contents_returned"] is False
    assert "Project fact" not in json.dumps(report)


def test_privacy_export_redacts_secret_previews(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    PersistentMemoryStore(tmp_path / "data" / "memory.sqlite3").add(
        content="api_key=not-a-real-secret-value",
        category="project_fact",
        scope="default",
    )

    report = privacy_export(project_root=tmp_path, runtime=_runtime(tmp_path), audit_logger=AuditLogger(tmp_path / "logs" / "audit.jsonl"))
    rendered = json.dumps(report)

    assert report["status"] == "ok"
    assert "[REDACTED]" in rendered
    assert "sk-supersecret" not in rendered


def test_privacy_delete_memory_requires_confirmation(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    store = PersistentMemoryStore(tmp_path / "data" / "memory.sqlite3")
    store.add(content="Project fact: keep until confirmed.", category="project_fact", scope="default")
    broker = _broker(tmp_path)

    denied = privacy_delete_memory(broker, confirm="", audit_logger=AuditLogger(tmp_path / "logs" / "audit.jsonl"))

    assert denied["status"] == "error"
    assert PersistentMemoryStore(tmp_path / "data" / "memory.sqlite3").export(scope="default")
    events = _events(tmp_path)
    assert events[-1]["tool_name"] == "privacy.delete_memory"
    assert events[-1]["policy_decision"] == "DENY"


def test_privacy_delete_memory_confirmed_uses_toolbroker(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    PersistentMemoryStore(tmp_path / "data" / "memory.sqlite3").add(
        content="Project fact: delete through broker.",
        category="project_fact",
        scope="default",
    )
    broker = _broker(tmp_path)

    result = privacy_delete_memory(
        broker,
        confirm=CONFIRM_DELETE_MEMORY,
        audit_logger=AuditLogger(tmp_path / "logs" / "audit.jsonl"),
    )

    assert result["status"] == "ok"
    assert result["toolbroker_path"] == "memory.clear"
    assert result["memory_result"]["deleted_count"] == 1
    assert not PersistentMemoryStore(tmp_path / "data" / "memory.sqlite3").export(scope="default")
    assert [event["tool_name"] for event in _events(tmp_path)][-2:] == ["privacy.delete_memory", "memory.clear"]


def test_privacy_audit_summary_and_permissions_do_not_read_personal_connectors(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    runtime = _runtime(tmp_path)
    privacy_status(project_root=tmp_path, runtime=runtime, audit_logger=AuditLogger(runtime.audit_log_path))

    summary = privacy_audit_summary(runtime=runtime, audit_logger=AuditLogger(runtime.audit_log_path))
    permissions = privacy_permissions(runtime=runtime, audit_logger=AuditLogger(runtime.audit_log_path))

    assert summary["status"] == "ok"
    assert summary["raw_args_returned"] is False
    assert permissions["personal_connector_reads_performed"] is False
    assert any(item["default_enabled"] is False for item in permissions["personal_data_capabilities"])


def test_privacy_cli_status_and_delete_confirmation(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    PersistentMemoryStore(tmp_path / "data" / "memory.sqlite3").add(
        content="Project fact: CLI privacy.",
        category="project_fact",
        scope="default",
    )
    broker = _broker(tmp_path)
    runtime = _runtime(tmp_path)

    status_code = _run_privacy_command(["status"], broker, runtime=runtime, audit_logger=AuditLogger(runtime.audit_log_path))
    status_payload = json.loads(capsys.readouterr().out)
    denied_code = _run_privacy_command(["delete-memory"], broker, runtime=runtime, audit_logger=AuditLogger(runtime.audit_log_path))
    denied_payload = json.loads(capsys.readouterr().out)

    assert status_code == 0
    assert status_payload["status"] == "ok"
    assert denied_code == 2
    assert "confirmation required" in denied_payload["error"]
