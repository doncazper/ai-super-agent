from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from agent.core.tool_broker import ToolBroker
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry


def capabilities() -> dict[str, Capability]:
    return {
        "git.status": Capability("git.status", RiskLevel.LOW),
        "git.diff": Capability("git.diff", RiskLevel.LOW),
        "git.commit": Capability("git.commit", RiskLevel.HIGH, approval_required=True),
        "code.run_tests": Capability("code.run_tests", RiskLevel.LOW),
    }


def make_broker(project_root: Path, audit_path: Path) -> ToolBroker:
    return ToolBroker(
        default_registry(project_root=project_root, python_executable=sys.executable),
        PolicyEngine(capabilities()),
        AuditLogger(audit_path),
        session_id="test-session",
        model="test-model",
        route="test",
    )


def call(tool_name: str, arguments: dict[str, object] | None = None) -> dict[str, object]:
    return {
        "id": f"call_{tool_name}",
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments or {})},
    }


def init_repo(path: Path) -> None:
    path.mkdir()
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)


def test_git_status_allowed_and_audited(tmp_path) -> None:
    project = tmp_path / "repo"
    init_repo(project)
    audit_path = tmp_path / "audit.jsonl"
    broker = make_broker(project, audit_path)

    result = broker.execute(call("git.status"))

    assert result.allowed is True
    payload = json.loads(result.content)
    assert payload["returncode"] == 0
    event = json.loads(audit_path.read_text(encoding="utf-8").splitlines()[0])
    assert event["commands_run"] == ["git status --short"]


def test_git_commit_requires_approval(tmp_path) -> None:
    project = tmp_path / "repo"
    init_repo(project)
    broker = make_broker(project, tmp_path / "audit.jsonl")

    result = broker.execute(call("git.commit", {"message": "test commit"}))

    assert result.allowed is False
    assert json.loads(result.content)["approval_result"] == "denied"


def test_pytest_command_allowed_with_timeout(tmp_path) -> None:
    project = tmp_path / "repo"
    test_dir = project / "tests"
    test_dir.mkdir(parents=True)
    (test_dir / "test_sample.py").write_text("def test_sample():\n    assert True\n", encoding="utf-8")
    audit_path = tmp_path / "audit.jsonl"
    broker = make_broker(project, audit_path)

    result = broker.execute(call("code.run_tests", {"test_path": "tests", "timeout_seconds": 30}))

    assert result.allowed is True
    payload = json.loads(result.content)
    assert payload["returncode"] == 0
    assert "1 passed" in payload["stdout"]
    event = json.loads(audit_path.read_text(encoding="utf-8").splitlines()[0])
    assert "pytest tests" in event["commands_run"][0]
