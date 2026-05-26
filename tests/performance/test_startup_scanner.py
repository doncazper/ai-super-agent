from __future__ import annotations

import subprocess
from pathlib import Path

from agent.performance.startup_scanner import scan_startup
from agent.tools.registry import default_registry


def _fake_runner(argv: list[str], cwd: Path, timeout_seconds: int) -> subprocess.CompletedProcess[str]:
    assert timeout_seconds == 3
    assert cwd.exists()
    return subprocess.CompletedProcess(argv, 0, stdout="{}", stderr="")


def test_startup_scan_uses_bounded_subprocess_runner(tmp_path) -> None:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "agent").write_text("#!/bin/sh\n", encoding="utf-8")
    payload = scan_startup(tmp_path, timeout_seconds=3, max_commands=2, max_imports=1, runner=_fake_runner, write_report=False)
    assert payload["report_type"] == "startup"
    assert len(payload["command_results"]) == 2
    assert len(payload["import_results"]) == 1
    assert all(item["status"] == "ok" for item in payload["command_results"])
    assert "No LM Studio chat" in " ".join(payload["limitations"])


def test_startup_scan_skips_missing_commands(tmp_path) -> None:
    payload = scan_startup(tmp_path, timeout_seconds=3, max_commands=1, max_imports=0, runner=_fake_runner, write_report=False)
    assert payload["command_results"][0]["status"] == "skipped"
    assert payload["command_results"][0]["reason"] == "command not found"


def test_startup_scan_handles_timeout(tmp_path) -> None:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "agent").write_text("#!/bin/sh\n", encoding="utf-8")

    def timeout_runner(argv: list[str], cwd: Path, timeout_seconds: int) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(argv, timeout_seconds)

    payload = scan_startup(tmp_path, timeout_seconds=3, max_commands=1, max_imports=0, runner=timeout_runner, write_report=False)
    assert payload["command_results"][0]["status"] == "timeout"


def test_startup_scan_tool_registered(tmp_path) -> None:
    registry = default_registry(project_root=tmp_path)
    tool = registry.get("perf.scan_startup")
    assert tool is not None
