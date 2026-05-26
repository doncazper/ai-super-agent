from __future__ import annotations

import json
import subprocess

from agent.qa.surface_lanes import SURFACE_LANES, dry_run_surface_lanes, list_surface_lanes, surface_matrix


def test_surface_lanes_cover_required_surfaces() -> None:
    surfaces = {lane.surface for lane in SURFACE_LANES}

    for required in {
        "CLI core",
        "Command registry",
        "PromptOps",
        "Runtime/canonical state",
        "Agent Gateway / Runtime Kernel",
        "Action Center/approvals",
        "ToolBroker/policy/audit",
        "Web/research",
        "Reddit/forums",
        "Weather",
        "News planned/stubbed",
        "Brain providers",
        "Native skills",
        "Secrets",
        "QA sandbox",
        "Media planned/stubbed",
        "Platform/app bridge",
        "Channels/Telegram/mobile",
        "Memory",
        "Backup/restore",
    }:
        assert required in surfaces


def test_surface_lanes_are_safe_by_default() -> None:
    report = list_surface_lanes()

    assert report["status"] == "ok"
    assert report["personal_data_excluded_by_default"] is True
    assert report["high_critical_excluded_by_default"] is True
    for lane in report["lanes"]:
        assert lane["default_dry_run"] is True
        assert lane["excludes_personal_data"] is True
        assert lane["excludes_high_critical"] is True
        assert lane["owner_docs"]
        assert lane["expected_commands"]
        assert lane["expected_tests"]


def test_surface_dry_run_executes_no_commands() -> None:
    report = dry_run_surface_lanes()

    assert report["status"] == "dry_run"
    assert report["executed_commands"] == []
    assert report["would_run_count"] > 0
    assert "Dry-run only" in report["notes"][0]


def test_surface_matrix_is_json_serializable() -> None:
    matrix = surface_matrix()

    assert matrix["status"] == "ok"
    assert matrix["rows"]
    json.dumps(matrix)


def test_surface_cli_commands_work() -> None:
    for args in (
        ["./.venv/bin/python", "smart_agent.py", "qa", "surfaces"],
        ["./.venv/bin/python", "smart_agent.py", "qa", "surfaces", "run", "--dry-run"],
        ["./.venv/bin/python", "smart_agent.py", "qa", "surfaces", "matrix"],
    ):
        completed = subprocess.run(args, capture_output=True, text=True, check=False)
        assert completed.returncode == 0, completed.stderr
        assert json.loads(completed.stdout)["status"] in {"ok", "dry_run"}

