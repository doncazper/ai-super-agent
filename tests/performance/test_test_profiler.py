from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from agent.performance.test_profiler import parse_pytest_durations, read_latest_test_profile, run_test_profile
from agent.tools.registry import default_registry


PYTEST_OUTPUT = """
============================= slowest 3 durations =============================
1.20s setup    tests/example/test_slow.py::test_expensive_fixture
0.50s call     tests/example/test_slow.py::test_expensive_fixture
0.25s call     tests/example/test_other.py::test_other
"""


def _fake_runner(argv: list[str], cwd: Path, timeout_seconds: int) -> subprocess.CompletedProcess[str]:
    assert cwd.exists()
    assert timeout_seconds == 5
    assert "--durations=3" in argv
    return subprocess.CompletedProcess(argv, 0, stdout=PYTEST_OUTPUT, stderr="RAW_STDERR")


def test_parse_pytest_durations_fixture_output() -> None:
    rows = parse_pytest_durations(PYTEST_OUTPUT)
    assert len(rows) == 3
    assert rows[0].seconds == 1.2
    assert rows[0].phase == "setup"
    assert rows[0].module_path == "tests/example/test_slow.py"


def test_test_profile_runs_safe_target_and_stores_redacted_metadata(tmp_path) -> None:
    target = tmp_path / "tests" / "performance"
    target.mkdir(parents=True)
    (target / "test_fixture.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    payload = run_test_profile(
        tmp_path,
        target="tests/performance",
        durations=3,
        timeout_seconds=5,
        runner=_fake_runner,
    )
    assert payload["report_type"] == "test_profile"
    assert payload["durations"][0]["nodeid"].endswith("test_expensive_fixture")
    assert payload["slow_modules"][0]["module_path"] == "tests/example/test_slow.py"
    assert Path(payload["profile_report_path"]).exists()
    serialized = json.dumps(payload)
    assert "RAW_STDERR" not in serialized
    latest = read_latest_test_profile(tmp_path)
    assert latest["report_type"] == "test_profile"


def test_test_profile_requires_explicit_full_suite(tmp_path) -> None:
    (tmp_path / "tests").mkdir()
    with pytest.raises(ValueError, match="full-suite"):
        run_test_profile(tmp_path, target="tests", runner=_fake_runner, write_report=False)


def test_test_profile_rejects_outside_target(tmp_path) -> None:
    outside = tmp_path.parent
    with pytest.raises(ValueError, match="inside"):
        run_test_profile(tmp_path, target=str(outside), runner=_fake_runner, write_report=False)


def test_test_profile_report_no_report_state(tmp_path) -> None:
    payload = read_latest_test_profile(tmp_path)
    assert payload["status"] == "no_report"


def test_test_profile_tools_registered(tmp_path) -> None:
    registry = default_registry(project_root=tmp_path)
    assert registry.get("perf.tests_profile") is not None
    assert registry.get("perf.tests_report") is not None
