from __future__ import annotations

import json
from pathlib import Path

from agent.config.loader import load_capabilities_config
from agent.core.tool_broker import ToolBroker
from agent.safety.approvals import ApprovalManager
from agent.safety.audit import AuditLogger
from agent.safety.policy import PolicyEngine
from agent.tools.backup.backup_tools import BackupManager
from agent.tools.registry import default_registry
from agent.ui.cli_commands import dispatch_cli


def call(tool_name: str, args: dict[str, object] | None = None) -> dict[str, object]:
    return {
        "id": f"call_{tool_name.replace('.', '_')}",
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(args or {})},
    }


def seed_project(project: Path, *, capabilities_text: str | None = None) -> None:
    (project / "config").mkdir(parents=True, exist_ok=True)
    (project / "docs").mkdir(parents=True, exist_ok=True)
    (project / "README.md").write_text("Project README\n", encoding="utf-8")
    (project / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
    (project / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (project / "SPEC.md").write_text("# Spec\n", encoding="utf-8")
    (project / "SDLC.md").write_text("# SDLC\n", encoding="utf-8")
    capabilities = capabilities_text or Path("config/capabilities.yaml").read_text(encoding="utf-8")
    (project / "config" / "capabilities.yaml").write_text(capabilities, encoding="utf-8")
    (project / "config" / "settings.yaml").write_text("api_key: not-a-real-secret-value\n", encoding="utf-8")
    (project / ".env.example").write_text("TOKEN=not-a-real-example-token\n", encoding="utf-8")
    (project / ".env").write_text("TOKEN=not-a-real-production-token\n", encoding="utf-8")
    (project / "docs" / "PROJECT_STATE.md").write_text("status: test\n", encoding="utf-8")


def make_broker(project: Path, audit_path: Path, *, auto_approve: set[str] | None = None) -> ToolBroker:
    return ToolBroker(
        default_registry(project_root=project, memory_path=project / "data" / "memory.sqlite3"),
        PolicyEngine.from_config(load_capabilities_config()),
        AuditLogger(audit_path),
        session_id="test-session",
        model="test-model",
        route="test",
        approval_manager=ApprovalManager(auto_approve=auto_approve),
    )


def payload(result) -> dict[str, object]:
    return json.loads(result.content)


def test_backup_create_writes_manifest_and_redacts_secrets(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    seed_project(project)
    broker = make_broker(project, tmp_path / "audit.jsonl")

    result = broker.execute(call("backup.create", {"backup_dir": str(tmp_path / "backups")}))
    data = payload(result)

    assert result.allowed is True
    assert data["status"] == "ok"
    archive = Path(str(data["path"]))
    manifest = json.loads((archive / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["backup_id"] == data["backup_id"]
    assert manifest["personal_connectors_read"] is False
    rendered_archive = "\n".join(path.read_text(encoding="utf-8") for path in archive.rglob("*") if path.is_file())
    assert "not-a-real-secret-value" not in rendered_archive
    assert "not-a-real-production-token" not in rendered_archive
    assert "[REDACTED]" in rendered_archive


def test_unredacted_backup_is_rejected(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    seed_project(project)
    broker = make_broker(project, tmp_path / "audit.jsonl")

    result = broker.execute(call("backup.create", {"backup_dir": str(tmp_path / "backups"), "redacted": False}))
    data = payload(result)

    assert result.allowed is False
    assert "unredacted backups are not supported" in data["error"]


def test_backup_inspect_and_verify_work(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    seed_project(project)
    broker = make_broker(project, tmp_path / "audit.jsonl")
    created = payload(broker.execute(call("backup.create", {"backup_dir": str(tmp_path / "backups")})))

    inspected = payload(broker.execute(call("backup.inspect", {"backup_id": created["backup_id"], "backup_dir": str(tmp_path / "backups")})))
    verified = payload(broker.execute(call("backup.verify", {"backup_id": created["backup_id"], "backup_dir": str(tmp_path / "backups")})))

    assert inspected["status"] == "ok"
    assert inspected["restore_preview"]
    assert verified["valid"] is True


def test_backup_verify_detects_tampering(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    seed_project(project)
    broker = make_broker(project, tmp_path / "audit.jsonl")
    created = payload(broker.execute(call("backup.create", {"backup_dir": str(tmp_path / "backups")})))
    archive = Path(str(created["path"]))
    target = next((archive / "files").rglob("README.md"))
    target.write_text("tampered\n", encoding="utf-8")

    verified = payload(broker.execute(call("backup.verify", {"backup_id": created["backup_id"], "backup_dir": str(tmp_path / "backups")})))

    assert verified["status"] == "error"
    assert verified["valid"] is False
    assert any("hash mismatch" in problem for problem in verified["problems"])


def test_restore_requires_approval(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    seed_project(project)
    broker = make_broker(project, tmp_path / "audit.jsonl")
    created = payload(broker.execute(call("backup.create", {"backup_dir": str(tmp_path / "backups")})))

    result = broker.execute(call("backup.restore", {"backup_id": created["backup_id"], "backup_dir": str(tmp_path / "backups")}))
    data = payload(result)

    assert result.allowed is False
    assert data["error"] == "approval required"
    assert data["approval_result"] == "denied"


def test_restore_rejects_policy_weakening_manifest(tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    current_capabilities = Path("config/capabilities.yaml").read_text(encoding="utf-8")
    marker = "  calendar.read_date_range:\n"
    start = current_capabilities.index(marker)
    end = current_capabilities.index("\n  calendar.find_availability:", start)
    bad_block = current_capabilities[start:end].replace("    default_enabled: false\n", "    default_enabled: true\n")
    bad_capabilities = current_capabilities[:start] + bad_block + current_capabilities[end:]
    seed_project(source, capabilities_text=bad_capabilities)
    seed_project(target)
    created = BackupManager(source).create(backup_dir=str(tmp_path / "backups"))
    broker = make_broker(target, tmp_path / "audit.jsonl", auto_approve={"backup.restore"})

    result = broker.execute(call("backup.restore", {"backup_id": created["backup_id"], "backup_dir": str(tmp_path / "backups")}))
    data = payload(result)

    assert result.allowed is False
    assert "restore blocked" in data["error"]
    assert "policy" in data["error"]


def test_backup_restore_actions_are_audited(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    seed_project(project)
    audit_path = tmp_path / "audit.jsonl"
    broker = make_broker(project, audit_path)
    created = payload(broker.execute(call("backup.create", {"backup_dir": str(tmp_path / "backups")})))
    broker.execute(call("backup.restore", {"backup_id": created["backup_id"], "backup_dir": str(tmp_path / "backups")}))

    events = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
    assert any(event["tool_name"] == "backup.create" and event["policy_decision"] == "ALLOW" for event in events)
    assert any(event["tool_name"] == "backup.restore" and event["policy_decision"] == "DENY" for event in events)


def test_backup_cli_dispatch_uses_toolbroker(tmp_path: Path, monkeypatch, capsys) -> None:
    seed_project(tmp_path)
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))
    monkeypatch.chdir(tmp_path)

    assert dispatch_cli(["backup", "create", "--backup-dir", str(tmp_path / "backups")], project_root=tmp_path) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "ok"
    assert any(json.loads(line)["tool_name"] == "backup.create" for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines())
