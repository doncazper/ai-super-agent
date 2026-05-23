from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

from agent.core.tool_broker import ToolBroker
from agent.safety.actions import ActionCenter, ActionRecord, ActionStatus
from agent.safety.approvals import ApprovalManager, ApprovalResult
from agent.safety.audit import AuditEvent, new_request_id
from agent.safety.policy import PolicyDecision, RiskLevel
from agent.safety.trust import TrustLevel
from agent.tools.errors import ToolError
from agent.workflows.self_improvement import FORBIDDEN_CONTENT_PATTERNS, PROTECTED_FILES


DEFAULT_APPROVED_PROPOSALS_PATH = Path("data/self_improvement/approved_proposals.json")
SELF_IMPROVEMENT_COMMIT_ACTION = "self_improvement.commit"
PERSISTENCE_PATH_TOKENS = (
    "LaunchAgents",
    "LaunchDaemons",
    "crontab",
    ".plist",
    ".service",
    "authorized_keys",
)
OVERNIGHT_PLAN_SOURCE_FILES = (
    "docs/FEATURE_MATURITY.md",
    "docs/PROJECT_STATE.md",
    "docs/FEATURE_REGISTRY.md",
    "docs/FEATURE_ROADMAP.md",
)
OVERNIGHT_FORBIDDEN_WORK = (
    "personal-data connector implementation",
    "email or text sending",
    "calendar/contact writes",
    "policy weakening",
    "approval bypass",
    "audit disabling",
    "package installs",
    "external scripts",
    "full disk access",
    "background persistence",
    "commits without approval",
    "unplanned network access",
)


def implement_approved_proposal(
    broker: ToolBroker,
    center: ActionCenter,
    *,
    proposal_id: str,
    project_root: str | Path = ".",
    proposals_path: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    proposal = load_approved_proposal(proposal_id, root=root, proposals_path=proposals_path)
    branch_name = str(proposal.get("branch_name") or f"codex/{_slug(proposal_id)}")
    _validate_branch_name(branch_name)
    _block_package_install(proposal)
    file_writes = _proposal_file_writes(proposal)
    if not file_writes:
        raise ToolError("approved proposal does not include file_writes")

    branch_result = _checkout_branch(root, branch_name, broker=broker)
    write_steps = []
    for relative_path, content in file_writes.items():
        _validate_self_improvement_write(relative_path, content)
        write_steps.append(
            _execute_tool(
                broker,
                f"self_improve_write_{_safe_call_id(relative_path)}",
                "filesystem.write",
                {"path": relative_path, "content": content, "overwrite": True},
            )
        )
    tests = [str(item) for item in proposal.get("tests", []) if str(item).strip()] or ["tests/test_self_improvement.py"]
    test_steps = [
        _execute_tool(
            broker,
            f"self_improve_test_{index}",
            "code.run_tests",
            {"test_path": test_path, "timeout_seconds": 120},
        )
        for index, test_path in enumerate(tests, start=1)
    ]
    diff = _execute_tool(broker, "self_improve_diff", "git.diff", {"max_chars": 50_000})
    commit_message = str(proposal.get("commit_message") or proposal.get("title") or proposal_id)
    commit_action = center.create_action(
        SELF_IMPROVEMENT_COMMIT_ACTION,
        {"message": commit_message},
        source_workflow="self_improvement.implement",
    )
    return {
        "status": _implementation_status(write_steps, test_steps),
        "workflow": "self_improvement_implement",
        "proposal_id": proposal_id,
        "branch": branch_name,
        "branch_result": branch_result,
        "files_written": [step.get("content", {}).get("path") for step in write_steps if isinstance(step.get("content"), dict)],
        "write_steps": write_steps,
        "test_steps": test_steps,
        "diff": diff,
        "commit_action": commit_action.to_dict(),
        "blocked": False,
        "safety_rules": {
            "policy_weakening_blocked": True,
            "audit_disabling_blocked": True,
            "personal_data_access_not_granted": True,
            "persistence_creation_blocked": True,
            "package_install_blocked_without_approval": True,
            "commit_requires_action_center": True,
        },
    }


def run_self_improvement_tests(broker: ToolBroker, *, test_path: str = "tests", timeout_seconds: int = 120) -> dict[str, Any]:
    return _execute_tool(broker, "self_improve_run_tests", "code.run_tests", {"test_path": test_path, "timeout_seconds": timeout_seconds})


def show_self_improvement_diff(broker: ToolBroker, *, max_chars: int = 50_000) -> dict[str, Any]:
    return _execute_tool(broker, "self_improve_show_diff", "git.diff", {"max_chars": max_chars})


def build_overnight_plan(broker: ToolBroker, *, max_items: int = 8) -> dict[str, Any]:
    """Build a safe overnight candidate list from project tracking docs.

    The result is a plan only. It does not create branches, edit files, run tests,
    execute prompts, create schedules, or commit changes.
    """
    reads: list[dict[str, Any]] = []
    source_text: dict[str, str] = {}
    for path in OVERNIGHT_PLAN_SOURCE_FILES:
        step = _execute_tool(
            broker,
            f"overnight_plan_read_{_safe_call_id(path)}",
            "filesystem.read",
            {"path": path, "max_bytes": 200_000},
        )
        reads.append(step)
        if step.get("allowed") and isinstance(step.get("content"), dict):
            source_text[path] = str(step["content"].get("content", ""))

    candidates = _overnight_candidates_from_sources(source_text)
    safe_candidates = [candidate for candidate in candidates if _is_safe_overnight_candidate(candidate)]
    safe_candidates = sorted(safe_candidates, key=lambda item: int(item["rank"]))[: max(1, max_items)]
    for index, candidate in enumerate(safe_candidates, start=1):
        candidate["rank"] = index

    return {
        "status": "ok" if safe_candidates else "no_candidates",
        "workflow": "self_improvement_overnight_plan",
        "safe_mode": True,
        "plan_only": True,
        "source_files": list(source_text),
        "read_steps": reads,
        "candidates": safe_candidates,
        "excluded_work": [
            {"title": item, "reason": "forbidden by overnight safe-mode constraints"}
            for item in OVERNIGHT_FORBIDDEN_WORK
        ],
        "stop_conditions": [
            "approval required",
            "personal data needed",
            "package install needed",
            "policy change needed",
            "tests failing after one safe fix attempt",
            "unclear requirements",
        ],
        "sandbox": {
            "recommended": "workspace-write",
            "full_access": False,
            "approval_bypass": False,
        },
    }


def create_self_improvement_commit_action(
    broker: ToolBroker,
    center: ActionCenter,
    *,
    message: str,
    test_path: str = "tests/test_self_improvement.py",
    timeout_seconds: int = 120,
    max_diff_chars: int = 50_000,
) -> dict[str, Any]:
    if not message.strip():
        raise ToolError("commit message is required")
    tests = run_self_improvement_tests(broker, test_path=test_path, timeout_seconds=timeout_seconds)
    diff = show_self_improvement_diff(broker, max_chars=max_diff_chars)
    tests_ok = bool(tests.get("allowed") and tests.get("content", {}).get("returncode") == 0)
    diff_text = str(diff.get("content", {}).get("stdout", "") if isinstance(diff.get("content"), dict) else "")
    if not tests_ok:
        return {
            "status": "tests_failed",
            "workflow": "self_improvement_create_commit_action",
            "action_created": False,
            "test_step": tests,
            "diff": diff,
            "error": "self-improvement tests must pass before creating a commit action",
        }
    if not diff.get("allowed"):
        return {
            "status": "error",
            "workflow": "self_improvement_create_commit_action",
            "action_created": False,
            "test_step": tests,
            "diff": diff,
            "error": "self-improvement diff could not be generated through ToolBroker",
        }
    if not diff_text.strip():
        return {
            "status": "no_changes",
            "workflow": "self_improvement_create_commit_action",
            "action_created": False,
            "test_step": tests,
            "diff": diff,
            "error": "no unstaged git diff found for self-improvement commit review",
        }
    commit_action = center.create_action(
        SELF_IMPROVEMENT_COMMIT_ACTION,
        {"message": message.strip()},
        source_workflow="self_improvement.create_action_for_commit",
    )
    commit_action.preview["test_result"] = {
        "test_path": test_path,
        "returncode": tests.get("content", {}).get("returncode"),
        "passed": True,
    }
    commit_action.preview["diff_summary"] = _diff_summary(diff_text)
    center.store.update(commit_action)
    return {
        "status": "ok",
        "workflow": "self_improvement_create_commit_action",
        "action_created": True,
        "test_step": tests,
        "diff": diff,
        "commit_action": commit_action.to_dict(),
        "commit_executed": False,
    }


def execute_self_improvement_commit(broker: ToolBroker, center: ActionCenter, *, action_id: str) -> dict[str, Any]:
    record = center.get_action(action_id)
    if record is None:
        return {"status": "error", "committed": False, "error": "action not found", "action_id": action_id}
    if record.action_type != SELF_IMPROVEMENT_COMMIT_ACTION:
        center.record_failure(action_id, "self-improvement commit action type mismatch")
        return {
            "status": "error",
            "committed": False,
            "error": f"action type mismatch: expected {SELF_IMPROVEMENT_COMMIT_ACTION}, got {record.action_type}",
            "action_id": action_id,
            "action_status": record.status.value,
        }
    if record.status is not ActionStatus.APPROVED:
        center.record_failure(action_id, "self-improvement commit blocked because approval is missing")
        return {
            "status": "error",
            "committed": False,
            "error": "action must be approved in Action Center before commit",
            "action_id": action_id,
            "action_status": record.status.value,
        }
    result = _execute_approved_action(broker, center, record)
    payload = result["tool_result"]
    committed = bool(result["executed"] and payload.get("returncode") == 0)
    return {**result, "committed": committed}


def load_approved_proposal(
    proposal_id: str,
    *,
    root: Path,
    proposals_path: str | Path | None = None,
) -> dict[str, Any]:
    path = Path(proposals_path or DEFAULT_APPROVED_PROPOSALS_PATH)
    if not path.is_absolute():
        path = root / path
    if not path.exists():
        raise ToolError(f"approved proposal store not found at {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ToolError("approved proposal store is not valid JSON") from exc
    proposals = raw.get("proposals") if isinstance(raw, dict) else raw
    if not isinstance(proposals, list):
        raise ToolError("approved proposal store must contain a proposals list")
    for item in proposals:
        if isinstance(item, dict) and str(item.get("proposal_id")) == proposal_id:
            if item.get("approved") is not True:
                raise ToolError("proposal exists but is not approved")
            return item
    raise ToolError("approved proposal not found")


def _execute_approved_action(broker: ToolBroker, center: ActionCenter, record: ActionRecord) -> dict[str, Any]:
    tool_call = {
        "id": f"action_{record.action_id}",
        "type": "function",
        "function": {"name": record.tool_name, "arguments": json.dumps(record.sanitized_args)},
    }
    previous_manager = broker.approval_manager

    def decision_provider(request):
        if request.capability == record.capability and record.status is ActionStatus.APPROVED:
            return ApprovalResult.APPROVED
        return ApprovalResult.DENIED

    broker.approval_manager = ApprovalManager(decision_provider=decision_provider, store=center.approval_store)
    broker.approval_manager.configure_audit(broker.audit_logger, session_id=broker.session_id, model=broker.model, route=broker.route)
    try:
        result = broker.execute(tool_call)
    finally:
        broker.approval_manager = previous_manager
    payload = json.loads(result.content)
    if result.allowed:
        center.consume_approval_once(record.action_id)
    else:
        center.record_failure(record.action_id, "self-improvement commit ToolBroker execution failed or was denied")
    refreshed = center.get_action(record.action_id)
    return {
        "status": "ok" if result.allowed else "error",
        "executed": result.allowed,
        "action_id": record.action_id,
        "action_status": refreshed.status.value if refreshed else "unknown",
        "tool_name": record.tool_name,
        "tool_result": payload,
        "debug": result.debug or {},
    }


def _execute_tool(broker: ToolBroker, call_id: str, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    result = broker.execute({"id": call_id, "type": "function", "function": {"name": tool_name, "arguments": json.dumps(arguments)}})
    try:
        content = json.loads(result.content)
    except json.JSONDecodeError:
        content = {"raw": result.content}
    return {"tool_name": result.tool_name, "tool_call_id": result.tool_call_id, "allowed": result.allowed, "content": content, "debug": result.debug}


def _checkout_branch(root: Path, branch_name: str, *, broker: ToolBroker) -> dict[str, Any]:
    completed = subprocess.run(["git", "checkout", "-B", branch_name], cwd=root, capture_output=True, text=True, timeout=30, check=False)
    broker.audit_logger.log(
        AuditEvent(
            session_id=broker.session_id,
            request_id=new_request_id(),
            route=broker.route,
            model=broker.model,
            tool_name="self_improvement.branch",
            capability="git.branch",
            risk_level=RiskLevel.LOW.value,
            trust_level=TrustLevel.LOCAL_PRIVATE_DATA.value,
            policy_decision=PolicyDecision.ALLOW.value,
            sanitized_args={"branch_name": branch_name},
            result_summary="Created or switched to self-improvement branch.",
            commands_run=[f"git checkout -B {branch_name}"],
        )
    )
    return {"returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def _proposal_file_writes(proposal: dict[str, Any]) -> dict[str, str]:
    file_writes = proposal.get("file_writes")
    if not isinstance(file_writes, dict):
        return {}
    return {str(path): str(content) for path, content in file_writes.items()}


def _block_package_install(proposal: dict[str, Any]) -> None:
    if proposal.get("packages") or proposal.get("install_commands"):
        raise ToolError("package installation is blocked without a separate approval gate")


def _validate_self_improvement_write(relative_path: str, content: str) -> None:
    path = Path(relative_path)
    normalized = path.as_posix()
    if path.is_absolute() or ".." in path.parts:
        raise ToolError("self-improvement writes must stay inside the project")
    if normalized in PROTECTED_FILES:
        raise ToolError("protected safety file cannot be modified by self-improvement")
    if any(token in normalized for token in PERSISTENCE_PATH_TOKENS):
        raise ToolError("self-improvement may not create persistence")
    for pattern in FORBIDDEN_CONTENT_PATTERNS:
        if pattern.search(content):
            raise ToolError("self-improvement content appears to weaken safety")


def _validate_branch_name(branch_name: str) -> None:
    if not branch_name.startswith("codex/"):
        raise ToolError("self-improvement branches must use codex/ prefix")
    if not re.match(r"^[A-Za-z0-9._/-]+$", branch_name) or ".." in branch_name:
        raise ToolError("invalid branch name")


def _implementation_status(write_steps: list[dict[str, Any]], test_steps: list[dict[str, Any]]) -> str:
    if any(not step["allowed"] for step in write_steps + test_steps):
        return "error"
    if any(step.get("content", {}).get("returncode", 0) != 0 for step in test_steps):
        return "tests_failed"
    return "ok"


def _diff_summary(diff_text: str) -> dict[str, Any]:
    added = sum(1 for line in diff_text.splitlines() if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in diff_text.splitlines() if line.startswith("-") and not line.startswith("---"))
    files = []
    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            parts = line.split()
            if len(parts) >= 4:
                files.append(parts[3][2:] if parts[3].startswith("b/") else parts[3])
    return {
        "files_changed": files,
        "files_changed_count": len(files),
        "lines_added": added,
        "lines_removed": removed,
        "truncated": len(diff_text) >= 50_000,
    }


def _overnight_candidates_from_sources(source_text: dict[str, str]) -> list[dict[str, Any]]:
    combined = "\n".join(source_text.values()).casefold()
    candidates: list[dict[str, Any]] = [
        {
            "rank": 1,
            "title": "Refresh tracking docs and maturity evidence",
            "category": "docs",
            "risk_level": RiskLevel.LOW.value,
            "why": "Tracking docs are the safest overnight work and prevent future prompt drift.",
            "expected_work": [
                "check PROJECT_STATE/FEATURE_MATURITY/FEATURE_REGISTRY consistency",
                "clarify known limitations and next-work notes",
            ],
            "tests_needed": ["docs validation", "command registry validation"],
            "source_signal": "feature registry, project state, and maturity tracking",
        },
        {
            "rank": 2,
            "title": "Add or tighten low-risk regression tests",
            "category": "tests",
            "risk_level": RiskLevel.LOW.value,
            "why": "Additional denial, docs-validation, and formatting tests improve safety without touching providers.",
            "expected_work": ["add mocks/fixtures", "cover existing error messages", "avoid live-network tests"],
            "tests_needed": ["targeted pytest", "full pytest if time allows"],
            "source_signal": "test plan and release checklist",
        },
        {
            "rank": 3,
            "title": "Harden diagnostics and safe error messages",
            "category": "hardening",
            "risk_level": RiskLevel.LOW.value,
            "why": "Doctor/eval/reporting polish is useful and does not require private connectors or new capabilities.",
            "expected_work": ["improve structured errors", "redact secret-like values", "add setup hints"],
            "tests_needed": ["doctor/eval/command tests"],
            "source_signal": "diagnostics and release-gate docs",
        },
        {
            "rank": 4,
            "title": "Improve safe eval fixtures and scorecard reporting",
            "category": "evals",
            "risk_level": RiskLevel.LOW.value,
            "why": "Safe evals can catch regressions without live services or private connectors.",
            "expected_work": ["add fixture prompts", "improve skipped/failure reasons", "refresh report templates"],
            "tests_needed": ["eval tests"],
            "source_signal": "golden eval and model-router quality docs",
        },
        {
            "rank": 5,
            "title": "Polish README/setup and command examples",
            "category": "docs",
            "risk_level": RiskLevel.LOW.value,
            "why": "Setup clarity improves local startup without changing policy or connectors.",
            "expected_work": ["verify examples", "add troubleshooting notes", "link registry/runbooks"],
            "tests_needed": ["docs validation"],
            "source_signal": "README and command registry",
        },
        {
            "rank": 6,
            "title": "Add mocks and fixtures for existing safe workflows",
            "category": "tests",
            "risk_level": RiskLevel.LOW.value,
            "why": "Better fixture coverage improves reliability without live web or personal data.",
            "expected_work": ["add deterministic fixtures", "avoid provider calls", "document fixture purpose"],
            "tests_needed": ["targeted workflow tests"],
            "source_signal": "test plan",
        },
        {
            "rank": 7,
            "title": "Refactor low-risk helper code without behavior changes",
            "category": "low_risk_refactor",
            "risk_level": RiskLevel.LOW.value,
            "why": "Small readability/type-hint changes can reduce maintenance risk when tests already cover behavior.",
            "expected_work": ["type hints", "deduplicate formatting helpers", "keep diffs small"],
            "tests_needed": ["targeted tests for touched modules"],
            "source_signal": "feature maturity limitations",
        },
    ]
    if "features needing live validation" in combined:
        candidates.append(
            {
                "rank": 8,
                "title": "Document live-validation gaps without running live services",
                "category": "docs",
                "risk_level": RiskLevel.LOW.value,
                "why": "Live validation can be prepared as checklists while avoiding unattended network or personal-data access.",
                "expected_work": ["clarify live smoke prerequisites", "mark personal-data evals skipped by default"],
                "tests_needed": ["docs validation"],
                "source_signal": "features needing live validation",
            }
        )
    return candidates


def _is_safe_overnight_candidate(candidate: dict[str, Any]) -> bool:
    risk = str(candidate.get("risk_level", "")).upper()
    if risk in {"HIGH", "CRITICAL", "FORBIDDEN"}:
        return False
    text = " ".join(
        str(candidate.get(key, ""))
        for key in ("title", "category", "why", "source_signal")
    ).casefold()
    forbidden_tokens = (
        "personal-data",
        "personal data",
        "email send",
        "text send",
        "message send",
        "calendar write",
        "contact write",
        "full disk",
        "package install",
        "external script",
        "background",
        "persistence",
        "approval bypass",
        "policy weakening",
        "audit disabling",
    )
    return not any(token in text for token in forbidden_tokens)


def _safe_call_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", value).strip("_")[:80] or "path"


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")[:60] or "self-improvement"
