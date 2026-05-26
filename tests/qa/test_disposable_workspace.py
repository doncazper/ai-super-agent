from pathlib import Path
import subprocess

import pytest

from agent.qa import runner
from agent.qa.disposable_workspace import (
    DisposableWorkspaceError,
    clean_disposable_workspace,
    init_disposable_workspace,
    require_workspace_path_inside,
    sandbox_status,
)
from agent.qa.models import QAPlan, QAPlanCommand, utc_now_iso
from agent.qa.runner import run_safe_commands
from agent.ui import cli_commands


def test_workspace_init_status_and_clean(tmp_path: Path) -> None:
    initialized = init_disposable_workspace(project_root=tmp_path)
    assert initialized.exists is True
    assert initialized.status == "ready"
    assert initialized.workspace_path == "reports/qa/workspaces/current"
    assert (tmp_path / initialized.workspace_path / "manifest.json").exists()
    assert (tmp_path / initialized.workspace_path / "files/notes.txt").exists()

    status = sandbox_status(project_root=tmp_path)
    assert status.fixture_count >= 5

    cleaned = clean_disposable_workspace(project_root=tmp_path)
    assert cleaned.exists is False


def test_workspace_path_traversal_blocked(tmp_path: Path) -> None:
    with pytest.raises(DisposableWorkspaceError):
        init_disposable_workspace(project_root=tmp_path, workspace_path="../outside")
    init_disposable_workspace(project_root=tmp_path)
    with pytest.raises(DisposableWorkspaceError):
        require_workspace_path_inside(tmp_path, "../../real-file.txt")


def test_cleanup_bounded_to_workspace(tmp_path: Path) -> None:
    outside = tmp_path / "important.txt"
    outside.write_text("do not delete\n", encoding="utf-8")
    init_disposable_workspace(project_root=tmp_path)
    clean_disposable_workspace(project_root=tmp_path)
    assert outside.exists()


def test_tier_three_requires_sandbox_flag(tmp_path: Path) -> None:
    with pytest.raises(Exception):
        run_safe_commands(project_root=tmp_path, tier=3)


def test_cli_sandbox_init_status_clean(tmp_path: Path, capsys) -> None:
    assert cli_commands.dispatch_cli(["qa", "sandbox", "init"], project_root=tmp_path) == 0
    initialized = capsys.readouterr().out
    assert "reports/qa/workspaces/current" in initialized
    assert cli_commands.dispatch_cli(["qa", "sandbox", "status"], project_root=tmp_path) == 0
    status = capsys.readouterr().out
    assert '"status": "ready"' in status
    assert cli_commands.dispatch_cli(["qa", "sandbox", "clean"], project_root=tmp_path) == 0
    cleaned = capsys.readouterr().out
    assert '"exists": false' in cleaned


def test_tier_three_sandbox_sets_workspace_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    command = QAPlanCommand(
        command_id="CMD-TEST-WRITE",
        command="python smart_agent.py workspace write",
        group="Workspace files",
        qa_tier=3,
        risk_level="MEDIUM",
        status="active",
        safe_to_auto_run=False,
        skip_reason="requires_disposable_workspace_or_manual_review",
        requires_approval=False,
        requires_provider_setup=False,
        requires_disposable_workspace=True,
        docs_link="docs/qa/DISPOSABLE_WORKSPACE.md",
        example="python smart_agent.py setup",
    )
    plan = QAPlan(
        plan_id="qa_plan_tier3",
        generated_at=utc_now_iso(),
        command_count=1,
        safe_count=0,
        skipped_count=0,
        blocked_count=0,
        commands_by_tier={"3": 1},
        commands_by_group={"Workspace files": 1},
        recommended_first_batch=[],
        setup_required=[],
        risks=[],
        notes=[],
        commands=[command],
    )

    def fake_generate_qa_plan(**kwargs):
        return plan

    def fake_run(*args, **kwargs):
        assert kwargs["env"]["AI_AGENT_QA_WORKSPACE"] == "reports/qa/workspaces/current"
        return subprocess.CompletedProcess(args=args[0], returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(runner, "generate_qa_plan", fake_generate_qa_plan)
    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    result = run_safe_commands(project_root=tmp_path, tier=3, sandbox=True, limit=1)
    assert result["sandbox_path"] == "reports/qa/workspaces/current"
    assert result["records"][0]["status"] == "passed"
