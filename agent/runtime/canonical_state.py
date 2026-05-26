from __future__ import annotations

import re
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .models import now_iso
from .state import redact_runtime_value


CANONICAL_RUNTIME_STATE_SCHEMA_VERSION = "1.0"

SOURCE_OF_TRUTH_HIERARCHY: tuple[tuple[int, str, str], ...] = (
    (1, "SPEC.md", "Highest-level mission, non-goals, architecture, safety model, and acceptance criteria."),
    (2, "docs/SDLC.md", "Process rules, mini-SDLC, and release-gate expectations."),
    (3, "AGENTS.md", "Permanent repository operating rules for Codex and agent work."),
    (4, "config/capabilities.yaml", "Runtime capability, risk, approval, and default-enable truth."),
    (5, "actual code/tests", "Implementation truth and regression evidence."),
    (6, "canonical runtime state JSON/model", "Machine-readable current execution and reconciliation state."),
    (7, "COMMAND_REGISTRY", "CLI command truth, including status, risk, approval, examples, and tests."),
    (8, "FEATURE_REGISTRY / FEATURE_MATURITY", "Feature existence, status, and readiness truth."),
    (9, "PROMPT_LEDGER / PROMPT_QUEUE / PROMPT_AUDIT", "Prompt history, next work, and prompt reconciliation truth."),
    (10, "PROJECT_STATE / COMPLETION_REPORT / CHANGELOG", "Durable resume summary, validation evidence, and human-readable history."),
    (11, "summary dashboards", "Navigation and summary views only; not primary truth."),
)


@dataclass(frozen=True)
class DirtyWorktreeSummary:
    is_dirty: bool = False
    modified: int = 0
    added: int = 0
    deleted: int = 0
    renamed: int = 0
    untracked: int = 0
    other: int = 0
    total_entries: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CanonicalRuntimeState:
    schema_version: str = CANONICAL_RUNTIME_STATE_SCHEMA_VERSION
    generated_at: str = field(default_factory=now_iso)
    branch: str = "unknown"
    last_commit: str = "unknown"
    dirty_worktree_summary: DirtyWorktreeSummary = field(default_factory=DirtyWorktreeSummary)
    active_prompt_id: str = "none"
    active_prompt_pack: str = "none"
    active_job_id: str = "none"
    active_workflow_id: str = "none"
    active_session_id: str = "none"
    active_action_id: str = "none"
    current_phase: str = "unknown"
    current_status: str = "unknown"
    next_prompt_id: str = "unknown"
    last_completed_prompt_id: str = "unknown"
    blocked_reason: str = ""
    resume_instruction: str = ""
    last_test_result: str = "unknown"
    last_policy_check: str = "unknown"
    last_capability_check: str = "unknown"
    last_command_registry_check: str = "unknown"
    last_prompt_audit: str = "unknown"
    safety_summary: dict[str, Any] = field(default_factory=dict)
    tracker_summary: dict[str, Any] = field(default_factory=dict)
    evidence_links: tuple[str, ...] = ()
    updated_by: str = "canonical_runtime_state"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["dirty_worktree_summary"] = self.dirty_worktree_summary.to_dict()
        data["evidence_links"] = list(self.evidence_links)
        return redact_runtime_value(data)


def source_of_truth_hierarchy() -> list[dict[str, Any]]:
    return [
        {"rank": rank, "source": source, "meaning": meaning}
        for rank, source, meaning in SOURCE_OF_TRUTH_HIERARCHY
    ]


def build_canonical_runtime_state(project_root: str | Path = ".") -> CanonicalRuntimeState:
    root = Path(project_root)
    project_state = _read_text(root / "docs/PROJECT_STATE.md")
    completion_report = _read_text(root / "docs/COMPLETION_REPORT.md")
    prompt_queue = _read_text(root / "docs/PROMPT_QUEUE.md")
    prompt_audit = _read_text(root / "docs/PROMPT_AUDIT.md")
    git_status = _git(root, ["status", "--short"])
    active_prompt_id = _active_prompt_id(root) or _extract_field(project_state, "active_prompt_id") or "none"
    next_prompt_id = _extract_field(project_state, "next_prompt_id") or _extract_field(prompt_queue, "next_prompt_id") or "unknown"
    return CanonicalRuntimeState(
        branch=_git(root, ["branch", "--show-current"]) or "unknown",
        last_commit=_git(root, ["log", "-1", "--pretty=%h %s"]) or "unknown",
        dirty_worktree_summary=_summarize_git_status(git_status),
        active_prompt_id=active_prompt_id,
        active_prompt_pack=_infer_prompt_pack(root, active_prompt_id) or _extract_field(project_state, "active_prompt_pack") or "none",
        active_job_id=_extract_field(project_state, "active_job_id") or "none",
        active_workflow_id=_extract_field(project_state, "active_workflow_id") or "none",
        active_session_id=_extract_field(project_state, "active_session_id") or "none",
        active_action_id=_extract_field(project_state, "active_action_id") or "none",
        current_phase=_extract_field(project_state, "current_phase") or "unknown",
        current_status=_extract_field(project_state, "current_status") or _infer_status_from_active(active_prompt_id),
        next_prompt_id=next_prompt_id,
        last_completed_prompt_id=_latest_completed_prompt_id(root, completion_report),
        blocked_reason=_extract_field(project_state, "blocked_reason") or "",
        resume_instruction=_extract_field(project_state, "resume_instruction") or "",
        last_test_result=_latest_line(completion_report, ("test", "pytest", "passed", "failed")) or "unknown",
        last_policy_check=_latest_line(completion_report, ("policy", "startup policy")) or "unknown",
        last_capability_check=_latest_line(completion_report, ("capability", "manifest")) or "unknown",
        last_command_registry_check=_latest_line(completion_report, ("command registry", "commands validate")) or "unknown",
        last_prompt_audit=_latest_line(prompt_audit, ("audit", "prompt")) or "unknown",
        safety_summary=_safety_summary(),
        tracker_summary=_tracker_summary(root, project_state, prompt_queue, prompt_audit),
        evidence_links=_evidence_links(root),
    )


def build_reconcile_preview(project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    state = build_canonical_runtime_state(root)
    project_state = _read_text(root / "docs/PROJECT_STATE.md")
    conflicts: list[dict[str, str]] = []
    active_file_prompt = _active_prompt_id(root)
    project_active_prompt = _extract_field(project_state, "active_prompt_id")
    if active_file_prompt and project_active_prompt and active_file_prompt != project_active_prompt:
        conflicts.append(
            {
                "field": "active_prompt_id",
                "canonical_value": active_file_prompt,
                "conflicting_value": project_active_prompt,
                "preferred_source": "prompts/active/*.md and prompt evidence",
                "recommendation": "Update PROJECT_STATE to match the single active prompt file or clear stale active prompt metadata.",
            }
        )
    if len(_prompt_ids_in_dir(root / "prompts/active")) > 1:
        conflicts.append(
            {
                "field": "active_prompt_id",
                "canonical_value": active_file_prompt or "multiple",
                "conflicting_value": "multiple active prompt files",
                "preferred_source": "prompt tracker invariant",
                "recommendation": "Keep at most one active prompt; mark stale active prompts completed, blocked, or needs_review with evidence.",
            }
        )
    return {
        "status": "ok" if not conflicts else "needs_reconciliation",
        "conflicts": conflicts,
        "canonical_state": state.to_dict(),
        "source_of_truth_hierarchy": source_of_truth_hierarchy(),
        "side_effects": "none; read-only metadata preview",
    }


def _git(root: Path, args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _extract_field(text: str, field_name: str) -> str:
    patterns = [
        rf"(?im)^\s*[-*]?\s*{re.escape(field_name)}\s*[:=]\s*`?([^`\n]+)`?\s*$",
        rf"(?im)^\s*[-*]?\s*{re.escape(field_name.replace('_', ' '))}\s*[:=]\s*`?([^`\n]+)`?\s*$",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            value = match.group(1).strip()
            return "" if value.lower() in {"", "n/a", "none"} else value
    return ""


def _summarize_git_status(status_text: str) -> DirtyWorktreeSummary:
    counts = {"modified": 0, "added": 0, "deleted": 0, "renamed": 0, "untracked": 0, "other": 0}
    entries = [line for line in status_text.splitlines() if line.strip()]
    for line in entries:
        code = line[:2]
        if code == "??":
            counts["untracked"] += 1
        elif "R" in code:
            counts["renamed"] += 1
        elif "D" in code:
            counts["deleted"] += 1
        elif "A" in code:
            counts["added"] += 1
        elif "M" in code:
            counts["modified"] += 1
        else:
            counts["other"] += 1
    return DirtyWorktreeSummary(is_dirty=bool(entries), total_entries=len(entries), **counts)


def _prompt_ids_in_dir(directory: Path) -> list[str]:
    if not directory.exists():
        return []
    return sorted(path.stem for path in directory.glob("*.md") if path.is_file())


def _active_prompt_id(root: Path) -> str:
    active_ids = _prompt_ids_in_dir(root / "prompts/active")
    return active_ids[0] if len(active_ids) == 1 else ""


def _infer_prompt_pack(root: Path, prompt_id: str) -> str:
    if not prompt_id or prompt_id == "none":
        return "none"
    prompt_text = _read_text(root / "prompts/active" / f"{prompt_id}.md")
    match = re.search(r"(?im)^\s*(?:pack_id|prompt_pack|pack)\s*:\s*`?([^`\n]+)`?", prompt_text)
    return match.group(1).strip() if match else "unknown"


def _infer_status_from_active(active_prompt_id: str) -> str:
    return "in_progress" if active_prompt_id and active_prompt_id != "none" else "idle"


def _latest_completed_prompt_id(root: Path, completion_report: str) -> str:
    match = re.search(r"(?im)^\s*[-*]?\s*prompt_id\s*:\s*`?([^`\n]+)`?\s*$", completion_report)
    if match:
        return match.group(1).strip()
    completed_ids = _prompt_ids_in_dir(root / "prompts/completed")
    return completed_ids[-1] if completed_ids else "unknown"


def _latest_line(text: str, needles: tuple[str, ...]) -> str:
    lowered = tuple(needle.lower() for needle in needles)
    for line in reversed([line.strip() for line in text.splitlines() if line.strip()]):
        if any(needle in line.lower() for needle in lowered):
            return line[:240]
    return ""


def _safety_summary() -> dict[str, Any]:
    return {
        "toolbroker_only_execution_preserved": True,
        "policy_engine_final_authority_preserved": True,
        "approval_manager_required_for_high_critical": True,
        "audit_logger_required": True,
        "personal_data_tools_enabled_by_default": False,
        "canonical_state_executes_tools": False,
        "canonical_state_calls_providers": False,
        "canonical_state_persists_sensitive_values": False,
    }


def _tracker_summary(root: Path, project_state: str, prompt_queue: str, prompt_audit: str) -> dict[str, Any]:
    return {
        "active_prompt_files": len(_prompt_ids_in_dir(root / "prompts/active")),
        "queued_prompt_files": len(_prompt_ids_in_dir(root / "prompts/queued")),
        "completed_prompt_files": len(_prompt_ids_in_dir(root / "prompts/completed")),
        "project_state_mentions_in_progress": "in_progress" in project_state.lower(),
        "prompt_queue_has_next_prompt": "next_prompt_id" in prompt_queue,
        "prompt_audit_present": bool(prompt_audit.strip()),
    }


def _evidence_links(root: Path) -> tuple[str, ...]:
    candidates = (
        "SPEC.md",
        "docs/SDLC.md",
        "AGENTS.md",
        "config/capabilities.yaml",
        "docs/COMMAND_REGISTRY.md",
        "docs/FEATURE_REGISTRY.md",
        "docs/FEATURE_MATURITY.md",
        "docs/PROMPT_LEDGER.md",
        "docs/PROMPT_QUEUE.md",
        "docs/PROMPT_AUDIT.md",
        "docs/PROJECT_STATE.md",
        "docs/COMPLETION_REPORT.md",
        "CHANGELOG.md",
    )
    return tuple(path for path in candidates if (root / path).exists())
