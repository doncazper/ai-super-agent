from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_bug_0001_setup_command_exits_cleanly_without_lmstudio_model() -> None:
    env = os.environ.copy()
    env.pop("LMSTUDIO_MODEL", None)

    result = subprocess.run(
        [sys.executable, "smart_agent.py", "setup"],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )

    assert result.returncode == 0
    assert "Set LMSTUDIO_MODEL" in result.stdout
    assert "secret" not in result.stdout.lower()
    assert result.stderr == ""
