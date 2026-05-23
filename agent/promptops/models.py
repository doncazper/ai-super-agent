from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


SAFE_AUTOPILOT_RISKS = {"SAFE", "LOW", "MEDIUM"}
FORBIDDEN_AUTOPILOT_RISKS = {"HIGH", "CRITICAL", "FORBIDDEN"}
ALLOWED_AUTOPILOT_CATEGORIES = {
    "docs",
    "tests",
    "diagnostics",
    "evals",
    "prompt_tracking",
    "feature_maturity",
    "low_risk_refactor",
}
FORBIDDEN_AUTOPILOT_CATEGORIES = {
    "personal_data",
    "message_send",
    "email_send",
    "calendar_write",
    "contact_write",
    "policy_relaxation",
    "external_script",
    "package_install",
    "persistence",
}


@dataclass(frozen=True)
class PromptOpsConfig:
    runner_enabled: bool = False
    runner_command: str = "codex"
    runner_model: str = "gpt-5.5"
    runner_reasoning: str = "high"
    runner_sandbox: str = "workspace-write"
    runner_approval_policy: str = "on-request"
    autopilot_max_prompts: int = 3
    autopilot_safe_only: bool = True
    stop_on_approval_gate: bool = True
    stop_on_test_failure: bool = True

    @classmethod
    def from_env(cls) -> "PromptOpsConfig":
        return cls(
            runner_enabled=_env_bool("CODEX_RUNNER_ENABLED", False),
            runner_command=os.getenv("CODEX_RUNNER_COMMAND", "codex"),
            runner_model=os.getenv("CODEX_RUNNER_MODEL", "gpt-5.5"),
            runner_reasoning=os.getenv("CODEX_RUNNER_REASONING", "high"),
            runner_sandbox=os.getenv("CODEX_RUNNER_SANDBOX", "workspace-write"),
            runner_approval_policy=os.getenv("CODEX_RUNNER_APPROVAL_POLICY", "on-request"),
            autopilot_max_prompts=_env_int("PROMPTOPS_AUTOPILOT_MAX_PROMPTS", 3),
            autopilot_safe_only=_env_bool("PROMPTOPS_AUTOPILOT_SAFE_ONLY", True),
            stop_on_approval_gate=_env_bool("PROMPTOPS_STOP_ON_APPROVAL_GATE", True),
            stop_on_test_failure=_env_bool("PROMPTOPS_STOP_ON_TEST_FAILURE", True),
        )


@dataclass(frozen=True)
class WorkbenchImportResult:
    status: str
    mode: str
    pack_id: str | None
    prompt_ids: list[str]
    prompt_paths: list[str]
    pack_path: str | None = None
    next_prompt_id: str | None = None
    ledger_updated: bool = False
    queue_updated: bool = False
    audit_updated: bool = False
    project_state_updated: bool = False
    trust_level: str = "UNTRUSTED_DOCUMENT"
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "mode": self.mode,
            "pack_id": self.pack_id,
            "prompt_ids": self.prompt_ids,
            "prompt_paths": self.prompt_paths,
            "pack_path": self.pack_path,
            "next_prompt_id": self.next_prompt_id,
            "ledger_updated": self.ledger_updated,
            "queue_updated": self.queue_updated,
            "audit_updated": self.audit_updated,
            "project_state_updated": self.project_state_updated,
            "trust_level": self.trust_level,
            "error": self.error,
        }


@dataclass(frozen=True)
class WorkbenchNextResult:
    status: str
    prompt_id: str | None
    title: str | None
    category: str | None
    risk_level: str | None
    approval_gate: str | None
    prerequisites: str | None
    path: str | None
    command: str | None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "prompt_id": self.prompt_id,
            "title": self.title,
            "category": self.category,
            "risk_level": self.risk_level,
            "approval_gate": self.approval_gate,
            "prerequisites": self.prerequisites,
            "path": self.path,
            "command": self.command,
            "error": self.error,
        }


@dataclass(frozen=True)
class RunnerResult:
    status: str
    prompt_id: str | None
    runner_enabled: bool
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    changed_files: list[str] = field(default_factory=list)
    report_path: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "prompt_id": self.prompt_id,
            "runner_enabled": self.runner_enabled,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "changed_files": self.changed_files,
            "report_path": self.report_path,
            "error": self.error,
        }


@dataclass(frozen=True)
class AutopilotResult:
    status: str
    attempted_prompt_ids: list[str]
    stopped_reason: str
    report_path: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "attempted_prompt_ids": self.attempted_prompt_ids,
            "stopped_reason": self.stopped_reason,
            "report_path": self.report_path,
        }


def project_path(project_root: str | Path, *parts: str) -> Path:
    return Path(project_root).resolve().joinpath(*parts)


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default

