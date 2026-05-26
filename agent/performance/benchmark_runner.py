from __future__ import annotations

import shlex
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from agent.ui.command_registry import CommandRecord, get_command, list_commands

from .models import PerformanceBenchmarkResult, PerformanceReport, utc_now_iso
from .reports import PerformanceReportStore


SAFE_RISKS = {"SAFE", "LOW"}
UNSAFE_SIDE_EFFECT_TERMS = (
    "write",
    "delete",
    "send",
    "draft",
    "post",
    "comment",
    "vote",
    "network",
    "provider call",
    "model call",
    "report write",
    "session output",
    "feedback metadata",
    "approval",
    "exec",
    "run",
    "patch",
    "commit",
    "push",
)
UNSAFE_TEXT_TERMS = (
    "personal",
    "gmail",
    "telegram",
    "reddit api",
    "live provider",
    "paid",
    "browser automation",
    "background",
    "critical",
    "high",
)


BenchmarkRunner = Callable[[list[str], Path, int], subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class BenchmarkCandidate:
    command_id: str
    command: str
    argv: tuple[str, ...]
    group: str


def _run_subprocess(argv: list[str], cwd: Path, timeout_seconds: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=str(cwd), text=True, capture_output=True, timeout=timeout_seconds, check=False)


def _contains_placeholder(command: str) -> bool:
    return "<" in command or ">" in command or "..." in command


def _unsafe_reason(record: CommandRecord) -> str | None:
    if record.status != "active":
        return f"command status is {record.status}"
    if record.risk_level not in SAFE_RISKS:
        return f"risk level {record.risk_level} is not benchmark-safe"
    if record.requires_approval.lower() != "no":
        return "approval is required"
    if _contains_placeholder(record.command):
        return "command contains placeholders"
    side_effects = record.side_effects.lower()
    unsafe_side_effect = next((term for term in UNSAFE_SIDE_EFFECT_TERMS if term in side_effects), None)
    if unsafe_side_effect:
        return f"side effects mention {unsafe_side_effect}"
    combined = " ".join(
        [
            record.command,
            record.group,
            record.description,
            record.trust_level,
            record.requires_connector,
            record.requires_provider,
            record.notes,
        ]
    ).lower()
    unsafe_term = next((term for term in UNSAFE_TEXT_TERMS if term in combined), None)
    if unsafe_term:
        return f"metadata mentions {unsafe_term}"
    return None


def is_benchmark_safe(record: CommandRecord) -> tuple[bool, str]:
    reason = _unsafe_reason(record)
    if reason:
        return False, reason
    return True, "benchmark-safe command metadata"


def _record_to_candidate(record: CommandRecord) -> BenchmarkCandidate:
    argv = shlex.split(record.command)
    if argv and argv[0] == "python":
        argv = [sys.executable, *argv[1:]]
    return BenchmarkCandidate(command_id=record.command_id, command=record.command, argv=tuple(argv), group=record.group)


def find_benchmark_candidate(command: str) -> BenchmarkCandidate:
    matches = [record for record in list_commands(status="active") if record.command == command]
    if not matches:
        matches = [record for record in list_commands(status="active") if record.example == command]
    if not matches:
        record = get_command(command)
        if record is not None:
            matches = [record]
    if not matches:
        raise ValueError("benchmark command must match an active command registry command, example, or command_id")
    record = matches[0]
    allowed, reason = is_benchmark_safe(record)
    if not allowed:
        raise ValueError(f"benchmark denied for {record.command_id}: {reason}")
    return _record_to_candidate(record)


def default_safe_candidates(*, group: str | None = None, max_commands: int = 5) -> tuple[list[BenchmarkCandidate], list[str]]:
    candidates: list[BenchmarkCandidate] = []
    skipped: list[str] = []
    group_filter = (group or "").strip().lower()
    for record in list_commands(status="active"):
        if group_filter and group_filter not in record.group.lower():
            continue
        allowed, reason = is_benchmark_safe(record)
        if allowed:
            candidates.append(_record_to_candidate(record))
        else:
            skipped.append(f"{record.command_id}: {reason}")
        if len(candidates) >= max_commands:
            break
    return candidates, skipped


def _measure_candidate(
    candidate: BenchmarkCandidate,
    root: Path,
    *,
    iterations: int,
    timeout_seconds: int,
    runner: BenchmarkRunner,
) -> PerformanceBenchmarkResult:
    durations: list[float] = []
    stdout_bytes = 0
    stderr_bytes = 0
    returncode: int | None = None
    warnings: list[str] = []
    for _ in range(iterations):
        started = time.perf_counter()
        try:
            completed = runner(list(candidate.argv), root, timeout_seconds)
            duration_ms = round((time.perf_counter() - started) * 1000, 3)
            durations.append(duration_ms)
            returncode = completed.returncode
            stdout_bytes += len(completed.stdout or "")
            stderr_bytes += len(completed.stderr or "")
            if completed.returncode != 0:
                warnings.append(f"nonzero return code {completed.returncode}")
                break
        except subprocess.TimeoutExpired:
            duration_ms = round((time.perf_counter() - started) * 1000, 3)
            durations.append(duration_ms)
            warnings.append(f"timeout after {timeout_seconds}s")
            returncode = None
            break
        except OSError as exc:
            warnings.append(str(exc))
            break
    if durations:
        min_duration = round(min(durations), 3)
        median_duration = round(statistics.median(durations), 3)
        max_duration = round(max(durations), 3)
    else:
        min_duration = median_duration = max_duration = 0.0
    status = "ok" if not warnings and returncode == 0 else "warning"
    return PerformanceBenchmarkResult(
        benchmark_id=f"{candidate.command_id}_{utc_now_iso().replace(':', '').replace('-', '')}",
        command_id=candidate.command_id,
        command=candidate.command,
        status=status,
        duration_ms=median_duration,
        iterations=len(durations),
        min_duration_ms=min_duration,
        median_duration_ms=median_duration,
        max_duration_ms=max_duration,
        returncode=returncode,
        stdout_bytes=stdout_bytes,
        stderr_bytes=stderr_bytes,
        warnings=warnings,
    )


def run_safe_benchmarks(
    project_root: str | Path = ".",
    *,
    command: str | None = None,
    group: str | None = None,
    iterations: int = 3,
    timeout_seconds: int = 10,
    max_commands: int = 5,
    runner: BenchmarkRunner = _run_subprocess,
    write_report: bool = True,
) -> dict[str, object]:
    root = Path(project_root).resolve()
    if iterations < 1 or iterations > 10:
        raise ValueError("iterations must be between 1 and 10")
    if timeout_seconds < 1 or timeout_seconds > 60:
        raise ValueError("timeout_seconds must be between 1 and 60")
    if max_commands < 1 or max_commands > 20:
        raise ValueError("max_commands must be between 1 and 20")

    skipped: list[str] = []
    if command:
        candidates = [find_benchmark_candidate(command)]
    else:
        candidates, skipped = default_safe_candidates(group=group, max_commands=max_commands)
    if not candidates:
        raise ValueError("no benchmark-safe commands matched the requested scope")

    generated_at = utc_now_iso()
    report_id = f"benchmark_{generated_at.replace(':', '').replace('-', '')}"
    results = [
        _measure_candidate(candidate, root, iterations=iterations, timeout_seconds=timeout_seconds, runner=runner)
        for candidate in candidates
    ]
    report = PerformanceReport(
        report_id=report_id,
        report_type="benchmark",
        generated_at=utc_now_iso(),
        status="ok",
        summary=f"Benchmarked {len(results)} safe command(s) with {iterations} requested iteration(s).",
        benchmark_results=results,
        findings=[],
        recommendations=[],
        limitations=[
            "Benchmarks only active SAFE/LOW read-only command registry entries by default.",
            "HIGH, CRITICAL, personal-data, mutating, live-provider, paid-provider, placeholder, and approval-required commands are denied.",
            "Output content is not stored; only byte counts, timing metadata, and return codes are recorded.",
        ],
    )
    payload = report.to_dict()
    payload["skipped_count"] = len(skipped)
    payload["skipped_examples"] = skipped[:25]
    if write_report:
        store = PerformanceReportStore(root)
        payload["report_path"] = str(store.write_report(report))
        payload["markdown_path"] = str(store.write_markdown(report))
    return PerformanceReportStore(root).redact_payload(payload)
