from __future__ import annotations

import hashlib
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

from agent.qa.disposable_workspace import init_disposable_workspace
from agent.qa.errors import CommandQAUnsafeError
from agent.qa.logging import CommandRunRecord, write_run_report
from agent.qa.models import QAPlanCommand, utc_now_iso
from agent.qa.qa_plan import generate_qa_plan
from agent.qa.redaction import redact_text


PLACEHOLDER_MARKERS = ("<", ">", "[", "]", "...")
SHELL_CONTROL_MARKERS = (";", "&&", "||", "|", "`", "$(", "\n")


def _repo_python(project_root: Path) -> str:
    venv_python = project_root / ".venv/bin/python"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def _run_id(seed: str) -> str:
    return "qa_run_" + hashlib.sha256(f"{seed}:{time.time_ns()}".encode("utf-8")).hexdigest()[:12]


def _safe_env(project_root: Path, *, sandbox_path: str = "") -> dict[str, str]:
    allowed_prefixes = ("PATH", "HOME", "LANG", "LC_", "TERM", "PYTHONPATH")
    env = {key: value for key, value in os.environ.items() if key in allowed_prefixes or key.startswith("LC_")}
    env["PYTHONUNBUFFERED"] = "1"
    env["AI_AGENT_QA_SANDBOX"] = "1"
    if sandbox_path:
        env["AI_AGENT_QA_WORKSPACE"] = sandbox_path
    env["PYTHONPATH"] = str(project_root)
    return env


def validate_runner_command(command: QAPlanCommand, *, sandbox: bool = False) -> None:
    if not command.safe_to_auto_run:
        if not (sandbox and command.qa_tier == 3 and command.requires_disposable_workspace):
            raise CommandQAUnsafeError(f"{command.command_id} is not safe to auto-run: {command.skip_reason}")
    if command.qa_tier not in {0, 1, 3}:
        raise CommandQAUnsafeError(f"{command.command_id} tier {command.qa_tier} is not enabled for the safe runner")
    if command.qa_tier == 3 and not sandbox:
        raise CommandQAUnsafeError(f"{command.command_id} tier 3 requires --sandbox")
    if any(marker in command.example for marker in PLACEHOLDER_MARKERS):
        raise CommandQAUnsafeError(f"{command.command_id} example contains placeholders and needs manual arguments")
    if any(marker in command.example for marker in SHELL_CONTROL_MARKERS):
        raise CommandQAUnsafeError(f"{command.command_id} example contains shell control syntax")
    if any(word in command.command.lower() for word in (" send", " commit", " restore")):
        raise CommandQAUnsafeError(f"{command.command_id} has write/send/delete semantics")
    if command.qa_tier == 3 and any(word in command.command.lower() for word in (" delete", " clear")):
        raise CommandQAUnsafeError(f"{command.command_id} destructive commands remain dry-run/manual only")
    if command.qa_tier in {0, 1} and any(word in command.command.lower() for word in (" delete", " update", " create", " patch", " write", " clear")):
        raise CommandQAUnsafeError(f"{command.command_id} has write/delete semantics")


def _record_for_skip(run_id: str, command: QAPlanCommand, reason: str) -> CommandRunRecord:
    now = utc_now_iso()
    return CommandRunRecord(
        run_id=run_id,
        command_id=command.command_id,
        command_string=redact_text(command.example or command.command, max_chars=500),
        qa_tier=command.qa_tier,
        risk_level=command.risk_level,
        start_time=now,
        duration_ms=0,
        exit_code=None,
        redacted_stdout_excerpt="",
        redacted_stderr_excerpt="",
        full_log_path="",
        status="skipped",
        failure_type="manual_arguments_required" if "placeholder" in reason else "blocked_by_policy",
        severity="P3",
        suspected_area=command.group,
        linked_bug_id="",
        regression_test_path="",
        feature_id="",
        maturity_impact="none",
        audit_ids=[],
        notes=redact_text(reason, max_chars=500),
    )


def run_safe_commands(
    *,
    project_root: str | Path = ".",
    tier: int = 1,
    group: str | None = None,
    safe_only: bool = True,
    timeout_seconds: int = 10,
    limit: int = 10,
    sandbox: bool = False,
) -> dict[str, object]:
    root = Path(project_root).resolve()
    if tier not in {0, 1, 3}:
        raise CommandQAUnsafeError("The safe runner currently supports only Tier 0, Tier 1, and sandboxed Tier 3.")
    if tier == 3 and not sandbox:
        raise CommandQAUnsafeError("Tier 3 command QA requires --sandbox.")
    run_id = _run_id(f"tier{tier}:{group or 'all'}")
    plan = generate_qa_plan(project_root=root, tier=tier, group=group, safe_only=safe_only if tier != 3 else False)
    selected = plan.commands[: max(0, limit)]
    records: list[CommandRunRecord] = []
    repo_python = _repo_python(root)
    sandbox_path = ""
    if sandbox:
        workspace = init_disposable_workspace(project_root=root)
        sandbox_path = workspace.workspace_path

    if tier == 0 and not selected:
        selected = [
            QAPlanCommand(
                command_id="CMD-COMMANDS-005",
                command="python smart_agent.py commands validate",
                group="Command QA",
                qa_tier=0,
                risk_level="SAFE",
                status="active",
                safe_to_auto_run=True,
                skip_reason="",
                requires_approval=False,
                requires_provider_setup=False,
                requires_disposable_workspace=False,
                docs_link="docs/COMMAND_QA_RUNBOOK.md",
                example="python smart_agent.py commands validate",
            )
        ]

    for command in selected:
        started = utc_now_iso()
        start = time.monotonic()
        try:
            validate_runner_command(command, sandbox=sandbox)
        except CommandQAUnsafeError as exc:
            records.append(_record_for_skip(run_id, command, str(exc)))
            continue
        argv = shlex.split(command.example)
        if argv[:2] == ["python", "smart_agent.py"]:
            argv = [repo_python, "smart_agent.py", *argv[2:]]
        elif argv and argv[0] == "python":
            argv[0] = repo_python
        try:
            result = subprocess.run(
                argv,
                cwd=root,
                env=_safe_env(root, sandbox_path=sandbox_path),
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
            duration_ms = int((time.monotonic() - start) * 1000)
            stdout = redact_text(result.stdout, max_chars=2000)
            stderr = redact_text(result.stderr, max_chars=2000)
            status = "passed" if result.returncode == 0 else "failed"
            failure_type = "" if status == "passed" else "nonzero_exit"
            severity = "" if status == "passed" else "P2"
            full_log_path = Path("reports/qa") / f"{run_id}_{command.command_id}.log"
            log_path = root / full_log_path
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(
                f"$ {' '.join(shlex.quote(part) for part in argv)}\n\n[stdout]\n{stdout}\n\n[stderr]\n{stderr}\n",
                encoding="utf-8",
            )
            records.append(
                CommandRunRecord(
                    run_id=run_id,
                    command_id=command.command_id,
                    command_string=redact_text(command.example, max_chars=500),
                    qa_tier=command.qa_tier,
                    risk_level=command.risk_level,
                    start_time=started,
                    duration_ms=duration_ms,
                    exit_code=result.returncode,
                    redacted_stdout_excerpt=stdout[:500],
                    redacted_stderr_excerpt=stderr[:500],
                    full_log_path=full_log_path.as_posix(),
                    status=status,
                    failure_type=failure_type,
                    severity=severity,
                    suspected_area=command.group,
                    linked_bug_id="",
                    regression_test_path="",
                    feature_id="",
                    maturity_impact="none" if status == "passed" else "needs_review",
                    audit_ids=[],
                    notes="",
                )
            )
        except subprocess.TimeoutExpired as exc:
            duration_ms = int((time.monotonic() - start) * 1000)
            records.append(
                CommandRunRecord(
                    run_id=run_id,
                    command_id=command.command_id,
                    command_string=redact_text(command.example, max_chars=500),
                    qa_tier=command.qa_tier,
                    risk_level=command.risk_level,
                    start_time=started,
                    duration_ms=duration_ms,
                    exit_code=None,
                    redacted_stdout_excerpt=redact_text(exc.stdout or "", max_chars=500),
                    redacted_stderr_excerpt=redact_text(exc.stderr or "", max_chars=500),
                    full_log_path="",
                    status="failed",
                    failure_type="timeout",
                    severity="P2",
                    suspected_area=command.group,
                    linked_bug_id="",
                    regression_test_path="",
                    feature_id="",
                    maturity_impact="needs_review",
                    audit_ids=[],
                    notes=f"Timed out after {timeout_seconds}s",
                )
            )
    latest = write_run_report(records, run_id=run_id, project_root=root, notes=plan.notes, sandbox_path=sandbox_path)
    return {"run_id": run_id, "records": [record.to_dict() for record in records], "report": latest, "sandbox_path": sandbox_path}
