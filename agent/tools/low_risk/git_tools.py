from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

from agent.tools.errors import ToolError


BRANCH_RE = re.compile(r"^[A-Za-z0-9._/-]+$")


def _run_git(project_root: Path, args: list[str], timeout: int = 20) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", *args],
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "_audit": {"commands_run": ["git " + " ".join(args)]},
    }


def make_git_tools(project_root: str | Path) -> dict[str, Any]:
    root = Path(project_root).resolve()

    def status() -> dict[str, Any]:
        return _run_git(root, ["status", "--short"])

    def diff(path: str | None = None, staged: bool = False, max_chars: int = 20000) -> dict[str, Any]:
        args = ["diff"]
        if staged:
            args.append("--staged")
        if path:
            if ".." in Path(path).parts or Path(path).is_absolute():
                raise ToolError("git diff path must be a relative project path")
            args.extend(["--", path])
        result = _run_git(root, args)
        result["stdout"] = result["stdout"][:max_chars]
        return result

    def branch(branch_name: str) -> dict[str, Any]:
        if not branch_name or not BRANCH_RE.match(branch_name) or ".." in branch_name:
            raise ToolError("invalid branch name")
        return _run_git(root, ["branch", branch_name])

    def commit(message: str) -> dict[str, Any]:
        if not message.strip():
            raise ToolError("commit message is required")
        return _run_git(root, ["commit", "-m", message], timeout=60)

    return {
        "git.status": status,
        "git.diff": diff,
        "git.branch": branch,
        "git.commit": commit,
    }


GIT_SCHEMAS = {
    "git.status": {
        "type": "function",
        "function": {
            "name": "git.status",
            "description": "Show short git status for the project repository.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    "git.diff": {
        "type": "function",
        "function": {
            "name": "git.diff",
            "description": "Show git diff for the project repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "staged": {"type": "boolean"},
                    "max_chars": {"type": "integer", "minimum": 1, "maximum": 100000},
                },
                "additionalProperties": False,
            },
        },
    },
    "git.branch": {
        "type": "function",
        "function": {
            "name": "git.branch",
            "description": "Create a git branch without switching to it.",
            "parameters": {
                "type": "object",
                "properties": {"branch_name": {"type": "string"}},
                "required": ["branch_name"],
                "additionalProperties": False,
            },
        },
    },
    "git.commit": {
        "type": "function",
        "function": {
            "name": "git.commit",
            "description": "Create a git commit. Requires approval.",
            "parameters": {
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
                "additionalProperties": False,
            },
        },
    },
}
