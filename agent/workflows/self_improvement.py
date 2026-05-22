from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent.safety.approvals import ApprovalManager, ApprovalRequest, ApprovalResult
from agent.safety.policy import RiskLevel
from agent.tools.errors import ToolError
from agent.tools.low_risk.workspace_files import WorkspaceGuard


PROTECTED_FILES = {
    "config/capabilities.yaml",
    "agent/safety/audit.py",
    "agent/safety/policy.py",
    "agent/safety/approvals.py",
}

FORBIDDEN_CONTENT_PATTERNS = (
    re.compile(r"disable[_ -]?audit", re.IGNORECASE),
    re.compile(r"approval_required\s*:\s*false", re.IGNORECASE),
    re.compile(r"risk_level\s*:\s*(SAFE|LOW)", re.IGNORECASE),
    re.compile(r"default_enabled\s*:\s*true", re.IGNORECASE),
)


@dataclass(frozen=True)
class FeatureProposal:
    title: str
    why: str
    files_expected_to_change: list[str]
    risk_level: str
    tests: list[str]
    rollback_plan: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "why": self.why,
            "files_expected_to_change": self.files_expected_to_change,
            "risk_level": self.risk_level,
            "tests": self.tests,
            "rollback_plan": self.rollback_plan,
        }


class SelfImprovementManager:
    def __init__(
        self,
        project_root: str | Path,
        *,
        python_executable: str,
        approval_manager: ApprovalManager | None = None,
    ) -> None:
        self.project_root = Path(project_root).resolve()
        self.python_executable = python_executable
        self.approval_manager = approval_manager or ApprovalManager()
        self.guard = WorkspaceGuard.for_project(self.project_root)

    def propose(
        self,
        *,
        title: str,
        why: str,
        files_expected_to_change: list[str],
        risk_level: str,
        tests: list[str],
        rollback_plan: str,
    ) -> dict[str, Any]:
        return FeatureProposal(
            title=title,
            why=why,
            files_expected_to_change=files_expected_to_change,
            risk_level=risk_level,
            tests=tests,
            rollback_plan=rollback_plan,
        ).to_dict()

    def implement(
        self,
        *,
        approved_feature: str,
        branch_name: str,
        file_writes: dict[str, str],
    ) -> dict[str, Any]:
        if not approved_feature.strip():
            raise ToolError("approved_feature is required")
        self._validate_branch_name(branch_name)
        self._run(["git", "checkout", "-B", branch_name], timeout=30)
        written: list[str] = []
        for relative_path, content in file_writes.items():
            self._validate_write(relative_path, content)
            target = self.guard.resolve(relative_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            written.append(str(target))
        return {"branch": branch_name, "files_written": written}

    def run_tests(self, test_path: str = "tests", timeout_seconds: int = 120) -> dict[str, Any]:
        return self._run([self.python_executable, "-m", "pytest", test_path], timeout=timeout_seconds)

    def show_diff(self) -> dict[str, Any]:
        return self._run(["git", "diff"], timeout=30)

    def commit(self, message: str) -> dict[str, Any]:
        approval = self.approval_manager.request_approval(
            ApprovalRequest(
                capability="self_improvement.commit",
                tool_name="improve.commit",
                risk_level=RiskLevel.HIGH,
                summary=f"Commit self-improvement changes with message: {message}",
                per_action=False,
            )
        )
        if approval is not ApprovalResult.APPROVED:
            return {"committed": False, "approval_result": approval.value}
        result = self._run(["git", "commit", "-m", message], timeout=60)
        return {"committed": result["returncode"] == 0, "approval_result": approval.value, **result}

    def _validate_write(self, relative_path: str, content: str) -> None:
        path = Path(relative_path)
        normalized = path.as_posix()
        if path.is_absolute() or ".." in path.parts:
            raise ToolError("self-improvement writes must stay inside the project")
        if normalized in PROTECTED_FILES:
            raise ToolError("protected safety file cannot be modified by self-improvement")
        for pattern in FORBIDDEN_CONTENT_PATTERNS:
            if pattern.search(content):
                raise ToolError("self-improvement content appears to weaken safety")

    def _validate_branch_name(self, branch_name: str) -> None:
        if not branch_name.startswith("codex/"):
            raise ToolError("self-improvement branches must use codex/ prefix")
        if not re.match(r"^[A-Za-z0-9._/-]+$", branch_name) or ".." in branch_name:
            raise ToolError("invalid branch name")

    def _run(self, command: list[str], timeout: int) -> dict[str, Any]:
        completed = subprocess.run(
            command,
            cwd=self.project_root,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }


def proposal_json(proposal: dict[str, Any]) -> str:
    return json.dumps(proposal, indent=2, sort_keys=True)
