from __future__ import annotations

import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .models import (
    PerformanceMetric,
    PerformanceReport,
    PerformanceScanConfig,
    PerformanceScanResult,
    utc_now_iso,
)
from .reports import PerformanceReportStore


@dataclass(frozen=True)
class StartupCommand:
    command_id: str
    argv: tuple[str, ...]
    description: str


Runner = Callable[[list[str], Path, int], subprocess.CompletedProcess[str]]


def default_startup_commands(project_root: str | Path = ".") -> list[StartupCommand]:
    root = Path(project_root)
    scripts_agent = root / "scripts" / "agent"
    python = sys.executable
    commands = [
        StartupCommand("scripts_agent_help", (str(scripts_agent), "--help"), "Repo launcher help."),
        StartupCommand("doctor", (python, "smart_agent.py", "doctor"), "Config/status doctor."),
        StartupCommand("commands_list", (python, "smart_agent.py", "commands", "list"), "Command registry listing."),
        StartupCommand("runtime_status", (python, "smart_agent.py", "runtime", "status"), "Runtime status metadata."),
        StartupCommand("brain_providers", (python, "smart_agent.py", "brain", "providers"), "Brain provider metadata."),
    ]
    return commands


def default_import_modules() -> list[str]:
    return [
        "smart_agent",
        "agent.ui.cli_commands",
        "agent.tools.registry",
        "agent.core.tool_broker",
        "agent.performance.static_scanner",
    ]


def _run_subprocess(argv: list[str], cwd: Path, timeout_seconds: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=str(cwd), text=True, capture_output=True, timeout=timeout_seconds, check=False)


def _measure_command(command: StartupCommand, root: Path, timeout_seconds: int, runner: Runner) -> dict[str, object]:
    executable = Path(command.argv[0])
    if ("/" in command.argv[0] or command.argv[0].startswith(".")) and not executable.exists():
        return {
            "command_id": command.command_id,
            "argv": list(command.argv),
            "description": command.description,
            "status": "skipped",
            "reason": "command not found",
            "duration_ms": None,
        }
    started = time.perf_counter()
    try:
        completed = runner(list(command.argv), root, timeout_seconds)
        duration_ms = round((time.perf_counter() - started) * 1000, 3)
        return {
            "command_id": command.command_id,
            "argv": list(command.argv),
            "description": command.description,
            "status": "ok" if completed.returncode == 0 else "nonzero",
            "returncode": completed.returncode,
            "duration_ms": duration_ms,
            "stdout_bytes": len(completed.stdout or ""),
            "stderr_bytes": len(completed.stderr or ""),
        }
    except subprocess.TimeoutExpired:
        duration_ms = round((time.perf_counter() - started) * 1000, 3)
        return {
            "command_id": command.command_id,
            "argv": list(command.argv),
            "description": command.description,
            "status": "timeout",
            "duration_ms": duration_ms,
            "timeout_seconds": timeout_seconds,
        }
    except OSError as exc:
        return {
            "command_id": command.command_id,
            "argv": list(command.argv),
            "description": command.description,
            "status": "skipped",
            "reason": str(exc),
            "duration_ms": None,
        }


def _measure_import(module_name: str, root: Path, timeout_seconds: int, runner: Runner) -> dict[str, object]:
    code = (
        "import importlib, json, time; "
        "start=time.perf_counter(); "
        f"importlib.import_module({module_name!r}); "
        "print(json.dumps({'duration_ms': round((time.perf_counter()-start)*1000, 3)}))"
    )
    command = StartupCommand(f"import_{module_name}", (sys.executable, "-c", code), f"Import {module_name}.")
    result = _measure_command(command, root, timeout_seconds, runner)
    if result.get("status") == "ok" and result.get("stdout_bytes", 0):
        return result
    return result


def scan_startup(
    project_root: str | Path = ".",
    *,
    timeout_seconds: int = 10,
    max_commands: int = 5,
    max_imports: int = 5,
    runner: Runner = _run_subprocess,
    write_report: bool = True,
) -> dict[str, object]:
    root = Path(project_root).resolve()
    scan_id = f"startup_{utc_now_iso().replace(':', '').replace('-', '')}"
    commands = default_startup_commands(root)[:max_commands]
    imports = default_import_modules()[:max_imports]
    started_at = utc_now_iso()
    command_results = [_measure_command(command, root, timeout_seconds, runner) for command in commands]
    import_results = [_measure_import(module, root, timeout_seconds, runner) for module in imports]
    completed_at = utc_now_iso()
    durations = [item.get("duration_ms") for item in command_results + import_results if isinstance(item.get("duration_ms"), (int, float))]
    metrics = [
        PerformanceMetric(name="startup_measurements", value=float(len(durations)), unit="count"),
    ]
    if durations:
        metrics.append(PerformanceMetric(name="max_duration_ms", value=float(max(durations)), unit="ms"))
    config = PerformanceScanConfig(
        scan_id=scan_id,
        scan_type="startup",
        project_root=str(root),
        timeout_seconds=timeout_seconds,
        max_files=0,
        live_providers_allowed=False,
        paid_apis_allowed=False,
        personal_data_allowed=False,
    )
    result = PerformanceScanResult(
        scan_id=scan_id,
        status="ok",
        started_at=started_at,
        completed_at=completed_at,
        config=config,
        metrics=metrics,
        findings=[],
        warnings=[str(item) for item in command_results + import_results if item.get("status") in {"timeout", "nonzero", "skipped"}],
    )
    report = PerformanceReport(
        report_id=scan_id,
        report_type="startup",
        generated_at=completed_at,
        status="ok",
        summary=f"Startup scan measured {len(command_results)} commands and {len(import_results)} imports.",
        scan_result=result,
        findings=[],
        recommendations=[],
        limitations=[
            "Startup timings are local and approximate.",
            "No LM Studio chat, live provider, personal-data, or model-loading command is used.",
            "Missing commands are skipped, not treated as failures.",
        ],
    )
    payload = report.to_dict()
    payload["command_results"] = command_results
    payload["import_results"] = import_results
    if write_report:
        store = PerformanceReportStore(root)
        payload["report_path"] = str(store.write_report(report))
        payload["markdown_path"] = str(store.write_markdown(report))
    return PerformanceReportStore(root).redact_payload(payload)
