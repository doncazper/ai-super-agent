from __future__ import annotations

import subprocess
from pathlib import Path

from .scanner import SecretLeakScanner


class GitPreflight:
    def __init__(self, project_root: str | Path = ".") -> None:
        self.project_root = Path(project_root).resolve()

    def run(self, *, staged: bool = False) -> dict[str, object]:
        scan = SecretLeakScanner(self.project_root).scan(staged=staged)
        status = self._git(["status", "--short"])
        staged_files = self._git(["diff", "--staged", "--name-only"]).splitlines()
        return {
            "status": "fail" if scan["status"] == "fail" else "ok",
            "scope": "staged" if staged else "tracked",
            "secret_scan": scan,
            "git_status_short": status.splitlines(),
            "staged_files": staged_files,
            "safe_to_commit": scan["status"] != "fail",
            "values_redacted": True,
        }

    def _git(self, args: list[str]) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
        )
        return completed.stdout if completed.returncode == 0 else ""
