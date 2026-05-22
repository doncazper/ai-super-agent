from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from agent.tools.errors import ToolError


def make_test_tools(project_root: str | Path, python_executable: str | None = None) -> dict[str, Any]:
    root = Path(project_root).resolve()
    python = python_executable or sys.executable

    def run_tests(test_path: str = "tests", timeout_seconds: int = 60) -> dict[str, Any]:
        relative = Path(test_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ToolError("test_path must be a relative project path")
        target = (root / relative).resolve()
        if root not in target.parents and target != root:
            raise ToolError("test_path is outside project root")
        completed = subprocess.run(
            [python, "-m", "pytest", str(relative)],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        return {
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "_audit": {"commands_run": [f"{python} -m pytest {relative}"]},
        }

    return {"code.run_tests": run_tests}


TEST_RUNNER_SCHEMAS = {
    "code.run_tests": {
        "type": "function",
        "function": {
            "name": "code.run_tests",
            "description": "Run pytest inside the project repository with a timeout.",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_path": {"type": "string"},
                    "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 300},
                },
                "additionalProperties": False,
            },
        },
    }
}
