from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

from smart_agent import _python_version_error_message


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_python_version_guard_message_includes_setup_commands() -> None:
    message = _python_version_error_message((3, 9, 6), "/usr/bin/python3")

    assert "requires Python 3.11 or newer" in message
    assert "Detected Python: 3.9.6" in message
    assert "python3.12 -m venv .venv" in message
    assert "python -m pip install -e '.[dev]'" in message
    assert "LMSTUDIO_BASE_URL" in message
    assert "LMSTUDIO_MODEL" in message
    assert "curl http://localhost:1234/v1/models" in message
    assert "./scripts/agent doctor" in message


def test_local_agent_wrapper_exists_and_is_executable() -> None:
    wrapper = REPO_ROOT / "scripts" / "agent"

    assert wrapper.exists()
    assert wrapper.stat().st_mode & stat.S_IXUSR
    text = wrapper.read_text(encoding="utf-8")
    assert ".venv/bin/python" in text
    assert "python3.12" in text
    assert "No supported interpreter was found." in text
    assert "LMSTUDIO_MODEL" in text


def test_local_agent_wrapper_runs_setup_without_lmstudio_model() -> None:
    env = os.environ.copy()
    env.pop("LMSTUDIO_MODEL", None)

    result = subprocess.run(
        [str(REPO_ROOT / "scripts" / "agent"), "setup"],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )

    assert result.returncode == 0
    assert "Set LMSTUDIO_MODEL" in result.stdout
    assert result.stderr == ""
