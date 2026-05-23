from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from agent.promptops.models import AutopilotResult, PromptOpsConfig, RunnerResult
from agent.promptops.report import write_promptops_report
from agent.promptops.safety import autopilot_decision, redact_secrets
from agent.promptops.workbench import mark_active, next_work, show_next
from agent.ui.prompts import list_prompt_records, next_prompt, show_prompt


def run_next(*, project_root: str | Path = ".", config: PromptOpsConfig | None = None) -> RunnerResult:
    cfg = config or PromptOpsConfig.from_env()
    next_result = next_work(project_root=project_root)
    if next_result.prompt_id is None:
        return RunnerResult(status="empty", prompt_id=None, runner_enabled=cfg.runner_enabled, error=next_result.error)
    if not cfg.runner_enabled:
        report_path = write_promptops_report(
            {
                "status": "runner_disabled",
                "prompt_id": next_result.prompt_id,
                "runner_enabled": False,
                "message": "CODEX_RUNNER_ENABLED is false; prompt was not executed.",
            },
            project_root=project_root,
        )
        return RunnerResult(
            status="runner_disabled",
            prompt_id=next_result.prompt_id,
            runner_enabled=False,
            report_path=report_path,
            error="CODEX_RUNNER_ENABLED=false; use work copy-next or enable runner explicitly.",
        )
    prompt = show_next(project_root=project_root)
    content = prompt.get("content")
    if not content:
        return RunnerResult(status="error", prompt_id=next_result.prompt_id, runner_enabled=True, error="prompt body missing")
    mark_active(next_result.prompt_id, project_root=project_root)
    command = [
        cfg.runner_command,
        "--model",
        cfg.runner_model,
        "--reasoning",
        cfg.runner_reasoning,
        "--sandbox",
        cfg.runner_sandbox,
        "--approval-policy",
        cfg.runner_approval_policy,
    ]
    try:
        completed = subprocess.run(command, input=content, capture_output=True, text=True, timeout=3600, cwd=project_root)
    except (FileNotFoundError, subprocess.SubprocessError) as exc:
        report_path = write_promptops_report(
            {"status": "runner_error", "prompt_id": next_result.prompt_id, "error": str(exc)},
            project_root=project_root,
        )
        return RunnerResult(status="runner_error", prompt_id=next_result.prompt_id, runner_enabled=True, report_path=report_path, error=str(exc))
    changed_files = _git_changed_files(project_root)
    report_path = write_promptops_report(
        {
            "status": "ran",
            "prompt_id": next_result.prompt_id,
            "exit_code": completed.returncode,
            "stdout": redact_secrets(completed.stdout),
            "stderr": redact_secrets(completed.stderr),
            "changed_files": changed_files,
        },
        project_root=project_root,
    )
    return RunnerResult(
        status="ran",
        prompt_id=next_result.prompt_id,
        runner_enabled=True,
        exit_code=completed.returncode,
        stdout=redact_secrets(completed.stdout),
        stderr=redact_secrets(completed.stderr),
        changed_files=changed_files,
        report_path=report_path,
    )


def autopilot(*, project_root: str | Path = ".", max_prompts: int | None = None, safe_only: bool = True, config: PromptOpsConfig | None = None) -> AutopilotResult:
    cfg = config or PromptOpsConfig.from_env()
    limit = max_prompts if max_prompts is not None else cfg.autopilot_max_prompts
    attempted: list[str] = []
    stopped_reason = "max prompts reached"
    for _ in range(max(0, limit)):
        record = next_prompt(project_root)
        if record is None:
            gated = _first_gated_queued_prompt(project_root)
            stopped_reason = f"approval gate is blocking prompt {gated}" if gated else "no runnable queued prompt"
            break
        payload = show_prompt(record.prompt_id, project_root) or {}
        metadata = _metadata_from_content(payload.get("content", ""))
        decision = autopilot_decision(record, metadata)
        if safe_only and not decision.allowed:
            stopped_reason = decision.reason
            break
        result = run_next(project_root=project_root, config=cfg)
        attempted.append(record.prompt_id)
        if result.status != "ran" or result.exit_code not in {0, None}:
            stopped_reason = result.error or result.status
            break
        stopped_reason = "runner completed prompt; PromptOps v1 does not auto-mark completion"
        break
    report_path = write_promptops_report(
        {"status": "autopilot", "attempted_prompt_ids": attempted, "stopped_reason": stopped_reason},
        project_root=project_root,
    )
    return AutopilotResult(status="stopped", attempted_prompt_ids=attempted, stopped_reason=stopped_reason, report_path=report_path)


def _metadata_from_content(content: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in content.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key in {"risk_level", "category", "approval_gate"}:
            fields[key] = value.strip()
    return fields


def _first_gated_queued_prompt(project_root: str | Path) -> str | None:
    for record in list_prompt_records(project_root):
        if record.status == "queued" and str(record.approval_gate).strip().lower() in {"true", "yes", "approval required", "blocked"}:
            return record.prompt_id
    return None


def _git_changed_files(project_root: str | Path) -> list[str]:
    try:
        completed = subprocess.run(["git", "status", "--short"], cwd=project_root, capture_output=True, text=True, timeout=10, check=False)
    except (FileNotFoundError, subprocess.SubprocessError):
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]
