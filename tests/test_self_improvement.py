from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from agent.workflows.self_improvement import SelfImprovementManager
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
