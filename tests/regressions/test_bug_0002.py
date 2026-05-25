from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

BUG_ID = 'BUG-0002'
BUG_TITLE = 'P2 command_failed in `python smart_agent.py setup`'
REPRODUCTION_COMMAND = 'python smart_agent.py setup'
EXPECTED_BEHAVIOR = 'Command should match documented behavior without unsafe side effects.'
ACTUAL_BEHAVIOR = 'Release gate synthetic regression seed: Synthetic QA issue with fake token <REDACTED_SECRET>; should be redacted\nRelease gate synthetic QA bug: Synthetic release-gate bug with fake token <REDACTED_SECRET> should be redacted'
SUGGESTED_REGRESSION = 'Add assertion coverage for the observed setup behavior.'
REPO_ROOT = Path(__file__).resolve().parents[2]

# Reproduction command:
#   python smart_agent.py setup
# Expected behavior:
#   Command should match documented behavior without unsafe side effects.
# Observed behavior:
#   Release gate synthetic regression seed: Synthetic QA issue with fake token <REDACTED_SECRET>; should be redacted
#   Release gate synthetic QA bug: Synthetic release-gate bug with fake token <REDACTED_SECRET> should be redacted

@pytest.mark.integration
def test_bug_0002_regression_scaffold() -> None:
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
    assert "<REDACTED_SECRET>" not in result.stdout
    assert result.stderr == ""
