from __future__ import annotations

import json
from pathlib import Path

from agent.core.tool_broker import ToolBroker
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry


def m3_capabilities() -> dict[str, Capability]:
    return {
        "filesystem.list": Capability("filesystem.list", RiskLevel.LOW),
        "filesystem.read": Capability("filesystem.read", RiskLevel.LOW),
        "filesystem.write": Capability("filesystem.write", RiskLevel.LOW),
        "filesystem.patch": Capability("filesystem.patch", RiskLevel.LOW),
        "filesystem.delete": Capability(
            "filesystem.delete",
            RiskLevel.HIGH,
            default_enabled=True,
            approval_required=True,
        ),
        "git.status": Capability("git.status", RiskLevel.LOW),
        "git.diff": Capability("git.diff", RiskLevel.LOW),
        "git.branch": Capability("git.branch", RiskLevel.LOW),
        "git.commit": Capability(
            "git.commit",
            RiskLevel.HIGH,
            default_enabled=True,
            approval_required=True,
        ),
        "code.run_tests": Capability("code.run_tests", RiskLevel.LOW),
    }


def make_broker(project_root: Path, audit_path: Path) -> ToolBroker:
    return ToolBroker(
        default_registry(project_root=project_root),
        PolicyEngine(m3_capabilities()),
        AuditLogger(audit_path),
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


def test_path_traversal_blocked(tmp_path) -> None:
    project = tmp_path / "repo"
    project.mkdir()
    broker = make_broker(project, tmp_path / "audit.jsonl")

    result = broker.execute(call("filesystem.read", {"path": "../secret.txt"}))

    assert result.allowed is False
    assert json.loads(result.content)["error"] == "path traversal is blocked"


def test_denied_env_path_blocked(tmp_path) -> None:
    project = tmp_path / "repo"
    project.mkdir()
    (project / ".env").write_text("TOKEN=secret", encoding="utf-8")
    broker = make_broker(project, tmp_path / "audit.jsonl")

    result = broker.execute(call("filesystem.read", {"path": ".env"}))

    assert result.allowed is False
    assert json.loads(result.content)["error"] == "access to denied filename is blocked"


def test_write_inside_workspace_allowed_and_audited(tmp_path) -> None:
    project = tmp_path / "repo"
    project.mkdir()
    audit_path = tmp_path / "audit.jsonl"
    broker = make_broker(project, audit_path)

    result = broker.execute(
        call("filesystem.write", {"path": "workspace/note.txt", "content": "hello"})
    )

    assert result.allowed is True
    written = project / "workspace" / "note.txt"
    assert written.read_text(encoding="utf-8") == "hello"
    event = json.loads(audit_path.read_text(encoding="utf-8").splitlines()[0])
    assert event["files_written"] == [str(written)]


def test_write_outside_workspace_denied(tmp_path) -> None:
    project = tmp_path / "repo"
    project.mkdir()
    outside = tmp_path / "outside.txt"
    broker = make_broker(project, tmp_path / "audit.jsonl")

    result = broker.execute(
        call("filesystem.write", {"path": str(outside), "content": "nope"})
    )

    assert result.allowed is False
    assert json.loads(result.content)["error"] == "path is outside approved roots"
    assert not outside.exists()


def test_delete_requires_approval(tmp_path) -> None:
    project = tmp_path / "repo"
    project.mkdir()
    target = project / "workspace" / "delete-me.txt"
    target.parent.mkdir()
    target.write_text("keep", encoding="utf-8")
    broker = make_broker(project, tmp_path / "audit.jsonl")

    result = broker.execute(call("filesystem.delete", {"path": "workspace/delete-me.txt"}))

    assert result.allowed is False
    assert target.exists()
    assert json.loads(result.content)["approval_result"] == "denied"


def test_patch_backs_up_before_overwrite(tmp_path) -> None:
    project = tmp_path / "repo"
    project.mkdir()
    target = project / "workspace" / "patch.txt"
    target.parent.mkdir()
    target.write_text("before", encoding="utf-8")
    broker = make_broker(project, tmp_path / "audit.jsonl")

    result = broker.execute(
        call(
            "filesystem.patch",
            {"path": "workspace/patch.txt", "old_text": "before", "new_text": "after"},
        )
    )

    assert result.allowed is True
    payload = json.loads(result.content)
    assert Path(payload["backup_path"]).exists()
    assert target.read_text(encoding="utf-8") == "after"
