from __future__ import annotations

import subprocess
import sys
import json
from pathlib import Path

import pytest

from agent.core.tool_broker import ToolBroker
from agent.safety.actions import ActionCenter, ActionCenterStore
from agent.safety.approvals import ApprovalStore
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry
from agent.workflows.self_improvement import SelfImprovementManager
from agent.workflows.self_improvement_backlog import self_improvement_backlog
from agent.workflows.self_improvement_loop import (
    execute_self_improvement_commit,
    implement_approved_proposal,
    run_self_improvement_tests,
    show_self_improvement_diff,
)
from agent.tools.errors import ToolError


def init_repo(path: Path) -> None:
    path.mkdir()
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    (path / "README.md").write_text("# Test\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-m", "initial"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )


def make_manager(project: Path) -> SelfImprovementManager:
    return SelfImprovementManager(project, python_executable=sys.executable)


def test_propose_does_not_edit_files(tmp_path) -> None:
    project = tmp_path / "repo"
    init_repo(project)
    before = sorted(path.relative_to(project).as_posix() for path in project.rglob("*") if path.is_file())
    manager = make_manager(project)

    proposal = manager.propose(
        title="Add helper",
        why="Improve clarity",
        files_expected_to_change=["agent/example.py"],
        risk_level="LOW",
        tests=["pytest"],
        rollback_plan="Revert branch",
    )
    after = sorted(path.relative_to(project).as_posix() for path in project.rglob("*") if path.is_file())

    assert proposal["title"] == "Add helper"
    assert before == after


def test_implement_creates_branch(tmp_path) -> None:
    project = tmp_path / "repo"
    init_repo(project)
    manager = make_manager(project)

    result = manager.implement(
        approved_feature="Add note",
        branch_name="codex/add-note",
        file_writes={"notes.txt": "hello\n"},
    )

    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=project,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert result["branch"] == "codex/add-note"
    assert branch == "codex/add-note"
    assert (project / "notes.txt").read_text(encoding="utf-8") == "hello\n"


def test_policy_reduction_blocked(tmp_path) -> None:
    project = tmp_path / "repo"
    init_repo(project)
    manager = make_manager(project)

    with pytest.raises(ToolError, match="protected safety file"):
        manager.implement(
            approved_feature="Weaken policy",
            branch_name="codex/bad-policy",
            file_writes={"config/capabilities.yaml": "tools: {}\n"},
        )


def test_audit_disabling_blocked(tmp_path) -> None:
    project = tmp_path / "repo"
    init_repo(project)
    manager = make_manager(project)

    with pytest.raises(ToolError, match="protected safety file"):
        manager.implement(
            approved_feature="Disable audit",
            branch_name="codex/bad-audit",
            file_writes={"agent/safety/audit.py": "# disable audit\n"},
        )


def test_tests_are_run(tmp_path) -> None:
    project = tmp_path / "repo"
    init_repo(project)
    tests_dir = project / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_ok.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    manager = make_manager(project)

    result = manager.run_tests()

    assert result["returncode"] == 0
    assert "1 passed" in result["stdout"]


def test_diff_shown(tmp_path) -> None:
    project = tmp_path / "repo"
    init_repo(project)
    (project / "README.md").write_text("# Changed\n", encoding="utf-8")
    manager = make_manager(project)

    result = manager.show_diff()

    assert result["returncode"] == 0
    assert "-# Test" in result["stdout"]
    assert "+# Changed" in result["stdout"]


def test_commit_requires_approval(tmp_path) -> None:
    project = tmp_path / "repo"
    init_repo(project)
    (project / "README.md").write_text("# Changed\n", encoding="utf-8")
    manager = make_manager(project)

    result = manager.commit("change readme")

    assert result["committed"] is False
    assert result["approval_result"] == "denied"


def test_loop_implement_requires_approved_proposal(tmp_path) -> None:
    project = tmp_path / "repo"
    init_repo(project)
    path = write_approved_proposals(
        project,
        [{"proposal_id": "p1", "approved": False, "file_writes": {"notes.txt": "hello\n"}}],
    )
    broker = make_loop_broker(project, tmp_path / "audit.jsonl")
    center = make_loop_center(project)

    with pytest.raises(ToolError, match="not approved"):
        implement_approved_proposal(broker, center, proposal_id="p1", project_root=project, proposals_path=path)


def test_loop_implement_creates_branch_and_commit_action(tmp_path) -> None:
    project = tmp_path / "repo"
    init_repo(project)
    tests_dir = project / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_ok.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    path = write_approved_proposals(
        project,
        [
            {
                "proposal_id": "p1",
                "approved": True,
                "branch_name": "codex/p1",
                "file_writes": {"notes.txt": "hello\n"},
                "tests": ["tests/test_ok.py"],
                "commit_message": "Add notes",
            }
        ],
    )
    broker = make_loop_broker(project, tmp_path / "audit.jsonl")
    center = make_loop_center(project)

    result = implement_approved_proposal(broker, center, proposal_id="p1", project_root=project, proposals_path=path)

    branch = subprocess.run(["git", "branch", "--show-current"], cwd=project, capture_output=True, text=True, check=True).stdout.strip()
    assert result["status"] == "ok"
    assert branch == "codex/p1"
    assert (project / "notes.txt").read_text(encoding="utf-8") == "hello\n"
    assert result["commit_action"]["action_type"] == "self_improvement.commit"
    assert center.get_action(result["commit_action"]["action_id"]).status.value == "pending"


def test_loop_policy_weakening_blocked(tmp_path) -> None:
    project = tmp_path / "repo"
    init_repo(project)
    path = write_approved_proposals(
        project,
        [
            {
                "proposal_id": "p1",
                "approved": True,
                "file_writes": {"README.md": "approval_required: false\n"},
            }
        ],
    )
    broker = make_loop_broker(project, tmp_path / "audit.jsonl")

    with pytest.raises(ToolError, match="weaken safety"):
        implement_approved_proposal(broker, make_loop_center(project), proposal_id="p1", project_root=project, proposals_path=path)


def test_loop_audit_disabling_blocked(tmp_path) -> None:
    project = tmp_path / "repo"
    init_repo(project)
    path = write_approved_proposals(
        project,
        [{"proposal_id": "p1", "approved": True, "file_writes": {"README.md": "disable audit logging\n"}}],
    )
    broker = make_loop_broker(project, tmp_path / "audit.jsonl")

    with pytest.raises(ToolError, match="weaken safety"):
        implement_approved_proposal(broker, make_loop_center(project), proposal_id="p1", project_root=project, proposals_path=path)


def test_loop_package_install_blocked(tmp_path) -> None:
    project = tmp_path / "repo"
    init_repo(project)
    path = write_approved_proposals(
        project,
        [{"proposal_id": "p1", "approved": True, "packages": ["example"], "file_writes": {"README.md": "# ok\n"}}],
    )
    broker = make_loop_broker(project, tmp_path / "audit.jsonl")

    with pytest.raises(ToolError, match="package installation is blocked"):
        implement_approved_proposal(broker, make_loop_center(project), proposal_id="p1", project_root=project, proposals_path=path)


def test_loop_tests_run_and_diff_shown(tmp_path) -> None:
    project = tmp_path / "repo"
    init_repo(project)
    tests_dir = project / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_ok.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    (project / "README.md").write_text("# Changed\n", encoding="utf-8")
    broker = make_loop_broker(project, tmp_path / "audit.jsonl")

    tests = run_self_improvement_tests(broker, test_path="tests/test_ok.py")
    diff = show_self_improvement_diff(broker)

    assert tests["content"]["returncode"] == 0
    assert "1 passed" in tests["content"]["stdout"]
    assert "-# Test" in diff["content"]["stdout"]
    assert "+# Changed" in diff["content"]["stdout"]


def test_loop_commit_action_requires_approval_and_denial_prevents_commit(tmp_path) -> None:
    project = tmp_path / "repo"
    init_repo(project)
    broker = make_loop_broker(project, tmp_path / "audit.jsonl")
    center = make_loop_center(project)
    record = center.create_action("self_improvement.commit", {"message": "Change"}, source_workflow="test")

    result = execute_self_improvement_commit(broker, center, action_id=record.action_id)

    assert result["committed"] is False
    assert "approved" in result["error"].lower()
    assert center.get_action(record.action_id).status.value == "pending"


def test_loop_audit_logs_implementation_steps(tmp_path) -> None:
    project = tmp_path / "repo"
    init_repo(project)
    tests_dir = project / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_ok.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    path = write_approved_proposals(
        project,
        [
            {
                "proposal_id": "p1",
                "approved": True,
                "branch_name": "codex/p1",
                "file_writes": {"notes.txt": "hello\n"},
                "tests": ["tests/test_ok.py"],
            }
        ],
    )
    audit_path = tmp_path / "audit.jsonl"
    broker = make_loop_broker(project, audit_path)
    center = make_loop_center(project)

    implement_approved_proposal(broker, center, proposal_id="p1", project_root=project, proposals_path=path)

    events = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
    tool_names = [event["tool_name"] for event in events]
    assert "self_improvement.branch" in tool_names
    assert "filesystem.write" in tool_names
    assert "code.run_tests" in tool_names
    assert "git.diff" in tool_names


def backlog_capabilities() -> dict[str, Capability]:
    return {
        "filesystem.read": Capability("filesystem.read", RiskLevel.LOW),
    }


def make_backlog_broker(project: Path, audit_path: Path) -> ToolBroker:
    return ToolBroker(
        default_registry(project_root=project),
        PolicyEngine(backlog_capabilities()),
        AuditLogger(audit_path),
        session_id="test-session",
        model="test-model",
        route="test",
    )


def loop_capabilities() -> dict[str, Capability]:
    return {
        "filesystem.write": Capability("filesystem.write", RiskLevel.LOW),
        "code.run_tests": Capability("code.run_tests", RiskLevel.LOW),
        "git.diff": Capability("git.diff", RiskLevel.LOW),
        "git.commit": Capability(
            "git.commit",
            RiskLevel.HIGH,
            default_enabled=True,
            approval_required=True,
        ),
    }


def make_loop_broker(project: Path, audit_path: Path) -> ToolBroker:
    return ToolBroker(
        default_registry(project_root=project, python_executable=sys.executable),
        PolicyEngine(loop_capabilities()),
        AuditLogger(audit_path),
        session_id="test-session",
        model="test-model",
        route="test",
    )


def make_loop_center(project: Path) -> ActionCenter:
    return ActionCenter(
        store=ActionCenterStore(project / "data" / "actions.json"),
        approval_store=ApprovalStore(project / "data" / "approvals.json"),
        audit_logger=AuditLogger(project / "logs" / "actions_audit.jsonl"),
        session_id="test-session",
        model="test-model",
        route="test_actions",
    )


def write_approved_proposals(project: Path, proposals: list[dict[str, object]]) -> Path:
    path = project / "data" / "self_improvement" / "approved_proposals.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"proposals": proposals}, indent=2), encoding="utf-8")
    return path


def seed_tracking_project(project: Path) -> None:
    (project / "docs").mkdir(parents=True)
    (project / "tests").mkdir()
    (project / "config").mkdir()
    (project / "agent" / "workflows").mkdir(parents=True)
    files = {
        "SPEC.md": "Safety-first local agent.\n",
        "AGENTS.md": "Do not weaken policy. Do not disable audit logs.\n",
        "README.md": "Agent dashboard planned. Source-grounded web research exists.\n",
        "CHANGELOG.md": "## Unreleased\n",
        "docs/PROJECT_STATE.md": "Current task: email triage complete. Next queue: release gate, agent dashboard.\n",
        "docs/FEATURE_REGISTRY.md": "| Agent dashboard | planned |\n| Email draft-only | complete |\n",
        "docs/FEATURE_MATURITY.md": "Features needing live validation: LM Studio, Weather.\n",
        "docs/FEATURE_ROADMAP.md": "18. Self-improvement backlog generator.\n20. Feature review + release gate.\n",
        "docs/COMPLETION_REPORT.md": "Last tests: 348 passed. Audit-log tampering remains a risk to verify.\n",
        "docs/RISK_REGISTER.md": "Self-improvement weakening safety mitigated by policy protections.\n",
        "docs/THREAT_MODEL.md": "ToolBroker bypass, audit-log tampering, prompt injection.\n",
        "docs/TEST_PLAN.md": "Run unit, integration, policy, approval, audit-log tests.\n",
        "docs/RELEASE_CHECKLIST.md": "All tests pass. Audit logs verified.\n",
        "config/capabilities.yaml": "tools:\n  filesystem.read:\n    risk_level: LOW\n",
        "tests/test_policy.py": "def test_policy(): assert True\n",
        "tests/test_tool_broker.py": "def test_broker(): assert True\n",
        "tests/test_workflows.py": "def test_workflows(): assert True\n",
        "tests/test_personal_modules.py": "def test_personal(): assert True\n",
        "tests/test_self_improvement.py": "def test_self_improvement(): assert True\n",
        "tests/test_feature_maturity_docs.py": "def test_docs(): assert True\n",
        "agent/workflows/self_improvement.py": "PROTECTED_FILES = {'config/capabilities.yaml'}\n",
    }
    for relative_path, content in files.items():
        path = project / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def test_backlog_propose_does_not_edit_files(tmp_path) -> None:
    project = tmp_path / "repo"
    project.mkdir()
    seed_tracking_project(project)
    before = {path.relative_to(project).as_posix(): path.read_text(encoding="utf-8") for path in project.rglob("*") if path.is_file()}
    broker = make_backlog_broker(project, tmp_path / "audit.jsonl")

    payload = self_improvement_backlog(broker, mode="propose")

    after = {path.relative_to(project).as_posix(): path.read_text(encoding="utf-8") for path in project.rglob("*") if path.is_file()}
    assert before == after
    assert payload["status"] == "ok"
    assert payload["proposal"]["title"]


def test_backlog_reads_only_approved_project_files(tmp_path) -> None:
    project = tmp_path / "repo"
    project.mkdir()
    seed_tracking_project(project)
    broker = make_backlog_broker(project, tmp_path / "audit.jsonl")

    payload = self_improvement_backlog(broker)

    inspected = [Path(path) for path in payload["files_inspected"]]
    assert inspected
    assert all(project in path.parents for path in inspected)
    assert all(".." not in path.relative_to(project).parts for path in inspected)
    assert not any(path.name == ".env" for path in inspected)


def test_backlog_policy_weakening_suggestions_flagged_blocked(tmp_path) -> None:
    project = tmp_path / "repo"
    project.mkdir()
    seed_tracking_project(project)
    broker = make_backlog_broker(project, tmp_path / "audit.jsonl")

    payload = self_improvement_backlog(broker)

    blocked = payload["blocked_suggestions"]
    assert blocked
    assert all(item["blocked"] is True for item in blocked)
    assert any("weaken" in item["reason"].casefold() or "policy" in item["reason"].casefold() for item in blocked)


def test_backlog_ranked_improvements_produced(tmp_path) -> None:
    project = tmp_path / "repo"
    project.mkdir()
    seed_tracking_project(project)
    broker = make_backlog_broker(project, tmp_path / "audit.jsonl")

    payload = self_improvement_backlog(broker)

    ranks = [item["rank"] for item in payload["improvements"]]
    assert ranks == sorted(ranks)
    assert payload["improvements"][0]["title"] == "Run a post-workflow release gate and checkpoint"
    for item in payload["improvements"]:
        assert item["why"]
        assert item["risk_level"] in {level.value for level in RiskLevel}
        assert item["expected_files"]
        assert item["tests_needed"]
        assert item["rollback_plan"]
        assert item["approval_requirements"]


def test_backlog_audit_logs_file_reads(tmp_path) -> None:
    project = tmp_path / "repo"
    project.mkdir()
    seed_tracking_project(project)
    audit_path = tmp_path / "audit.jsonl"
    broker = make_backlog_broker(project, audit_path)

    self_improvement_backlog(broker)

    events = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
    assert events
    assert all(event["tool_name"] == "filesystem.read" for event in events)
    assert any(event["files_read"] for event in events)


def test_backlog_dry_run_executes_no_file_reads(tmp_path) -> None:
    project = tmp_path / "repo"
    project.mkdir()
    seed_tracking_project(project)
    audit_path = tmp_path / "audit.jsonl"
    broker = make_backlog_broker(project, audit_path)

    payload = self_improvement_backlog(broker, dry_run=True)

    assert payload["status"] == "dry_run"
    assert payload["files_inspected"] == []
    assert payload["steps"]
    assert all(step["dry_run"] is True for step in payload["steps"])
    events = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
    assert events
    assert all(event["dry_run"] is True for event in events)
    assert all(event["files_read"] == [] for event in events)
