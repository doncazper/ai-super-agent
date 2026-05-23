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


def _safe_call_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", value).strip("_")[:80] or "path"


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")[:60] or "self-improvement"
