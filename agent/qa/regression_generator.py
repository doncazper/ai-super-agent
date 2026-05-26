from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from agent.qa.bug_generator import create_bugs_from_run
from agent.qa.redaction import redact_text


def _regressions_dir(project_root: str | Path = ".") -> Path:
    path = Path(project_root) / "tests/regressions"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _safe_py_literal(value: str) -> str:
    return repr(redact_text(value, max_chars=1000))


def load_bug(project_root: str | Path, bug_id: str) -> dict[str, Any]:
    path = Path(project_root) / "bugs" / f"{bug_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Bug report not found: {bug_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def create_regression_from_bug(project_root: str | Path = ".", *, bug_id: str) -> dict[str, Any]:
    bug = load_bug(project_root, bug_id)
    slug = re.sub(r"[^a-z0-9_]+", "_", bug_id.lower())
    path = _regressions_dir(project_root) / f"test_{slug}_qa_command.py"
    content = f'''from __future__ import annotations

import pytest


BUG_ID = {_safe_py_literal(str(bug.get("bug_id", bug_id)))}
COMMAND_ID = {_safe_py_literal(str(bug.get("command_id", "")))}
REPRODUCTION_COMMAND = {_safe_py_literal(str(bug.get("reproduction_command", "")))}
EXPECTED_BEHAVIOR = {_safe_py_literal(str(bug.get("expected_behavior", "")))}
ACTUAL_BEHAVIOR = {_safe_py_literal(str(bug.get("actual_behavior", "")))}


@pytest.mark.skip(reason="Generated QA regression scaffold; review and convert to a concrete fixture-backed assertion.")
def test_{{slug}}_qa_regression_scaffold() -> None:
    assert BUG_ID
    assert COMMAND_ID
    assert "[REDACTED" in ACTUAL_BEHAVIOR or ACTUAL_BEHAVIOR
'''
    content = content.replace("{slug}", slug)
    path.write_text(content, encoding="utf-8")
    bug["suggested_regression_test"] = path.relative_to(Path(project_root)).as_posix()
    bug_path = Path(project_root) / "bugs" / f"{bug_id}.json"
    bug_path.write_text(json.dumps(bug, indent=2, sort_keys=True), encoding="utf-8")
    return {"status": "ok", "bug_id": bug_id, "regression_test_path": path.relative_to(Path(project_root)).as_posix()}


def create_regressions_from_run(project_root: str | Path = ".", *, run_id: str | None = None) -> dict[str, Any]:
    created_bugs = create_bugs_from_run(project_root, run_id=run_id)
    regressions = [create_regression_from_bug(project_root, bug_id=item["bug_id"]) for item in created_bugs["bugs"]]
    return {"status": "ok", "created_bugs": created_bugs["bugs"], "regressions": regressions}

