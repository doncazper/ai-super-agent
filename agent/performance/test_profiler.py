from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Any

from .models import PerformanceBenchmarkResult, PerformanceReport, utc_now_iso
from .reports import PerformanceReportStore


SAFE_DEFAULT_TARGET = "tests/performance"
BROAD_TARGETS = {"", ".", "./", "tests", "tests/"}
DURATION_RE = re.compile(r"^\s*(?P<seconds>\d+(?:\.\d+)?)s\s+(?P<phase>\w+)\s+(?P<nodeid>.+?)\s*$")

PytestRunner = Callable[[list[str], Path, int], subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class TestDuration:
    seconds: float
    phase: str
    nodeid: str

    @property
    def module_path(self) -> str:
        return self.nodeid.split("::", 1)[0]

    def to_dict(self) -> dict[str, object]:
        return {
            "seconds": self.seconds,
            "phase": self.phase,
            "nodeid": self.nodeid,
            "module_path": self.module_path,
        }


def _run_pytest(argv: list[str], cwd: Path, timeout_seconds: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=str(cwd), text=True, capture_output=True, timeout=timeout_seconds, check=False)


def parse_pytest_durations(output: str) -> list[TestDuration]:
    durations: list[TestDuration] = []
    for line in output.splitlines():
        match = DURATION_RE.match(line)
        if not match:
            continue
        durations.append(
            TestDuration(
                seconds=float(match.group("seconds")),
                phase=match.group("phase"),
                nodeid=match.group("nodeid").strip(),
            )
        )
    return durations


def _safe_target(project_root: Path, target: str, *, full_suite: bool) -> Path:
    target_text = (target or SAFE_DEFAULT_TARGET).strip()
    if target_text in BROAD_TARGETS and not full_suite:
        raise ValueError("full-suite profiling requires explicit --full-suite")
    candidate = (project_root / target_text).resolve()
    try:
        candidate.relative_to(project_root)
    except ValueError as exc:
        raise ValueError("test profile target must stay inside the repository") from exc
    if any(part in {".venv", ".git", "logs", "reports", "media_outputs", ".qa_workspace"} for part in candidate.parts):
        raise ValueError("test profile target cannot point at generated, cache, log, report, or disposable workspace paths")
    if not candidate.exists():
        raise ValueError(f"test profile target does not exist: {target_text}")
    return candidate


def summarize_modules(durations: list[TestDuration]) -> list[dict[str, object]]:
    totals: dict[str, float] = {}
    counts: dict[str, int] = {}
    for item in durations:
        totals[item.module_path] = totals.get(item.module_path, 0.0) + item.seconds
        counts[item.module_path] = counts.get(item.module_path, 0) + 1
    return [
        {"module_path": module, "total_seconds": round(total, 3), "duration_entries": counts[module]}
        for module, total in sorted(totals.items(), key=lambda pair: pair[1], reverse=True)
    ]


def recommendation_summary(durations: list[TestDuration]) -> list[str]:
    if not durations:
        return ["No pytest duration rows were parsed; run with a target that emits --durations output."]
    recommendations = [
        "Review the slowest setup durations first; fixture caching or narrower fixture scope may help.",
        "Review repeated call-phase hotspots for expensive local IO, broad imports, or repeated registry/config construction.",
    ]
    if any(item.phase == "setup" for item in durations[:10]):
        recommendations.append("Several top entries are setup-phase durations; prefer session/module fixtures only when isolation remains correct.")
    if any(item.seconds >= 1.0 for item in durations):
        recommendations.append("At least one duration is >=1s; consider adding a focused regression benchmark before optimizing.")
    return recommendations


def _report_extra_path(store: PerformanceReportStore, report_id: str) -> Path:
    return store.report_path(report_id, suffix=".profile.json")


def run_test_profile(
    project_root: str | Path = ".",
    *,
    target: str = SAFE_DEFAULT_TARGET,
    durations: int = 25,
    timeout_seconds: int = 120,
    full_suite: bool = False,
    runner: PytestRunner = _run_pytest,
    write_report: bool = True,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    if durations < 1 or durations > 100:
        raise ValueError("durations must be between 1 and 100")
    if timeout_seconds < 1 or timeout_seconds > 900:
        raise ValueError("timeout_seconds must be between 1 and 900")
    target_path = _safe_target(root, target, full_suite=full_suite)
    display_target = str(target_path.relative_to(root))
    argv = [sys.executable, "-m", "pytest", display_target, f"--durations={durations}", "-q"]

    started = time.perf_counter()
    try:
        completed = runner(argv, root, timeout_seconds)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        status = "ok" if completed.returncode == 0 else "failed"
        returncode: int | None = completed.returncode
    except subprocess.TimeoutExpired:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
        stdout = ""
        stderr = ""
        status = "timeout"
        returncode = None

    parsed = parse_pytest_durations("\n".join([stdout, stderr]))
    generated_at = utc_now_iso()
    report_id = f"test_profile_{generated_at.replace(':', '').replace('-', '')}"
    benchmark_results = [
        PerformanceBenchmarkResult(
            benchmark_id=f"pytest_{index + 1}",
            command_id="pytest.duration",
            command=item.nodeid,
            status="observed",
            duration_ms=round(item.seconds * 1000, 3),
            iterations=1,
            min_duration_ms=round(item.seconds * 1000, 3),
            median_duration_ms=round(item.seconds * 1000, 3),
            max_duration_ms=round(item.seconds * 1000, 3),
            returncode=returncode,
        )
        for index, item in enumerate(parsed)
    ]
    report = PerformanceReport(
        report_id=report_id,
        report_type="test_profile",
        generated_at=generated_at,
        status=status,
        summary=f"Profiled pytest target {display_target} with --durations={durations}.",
        benchmark_results=benchmark_results,
        limitations=[
            "Pytest profiling is local and approximate.",
            "This profiler never deletes, skips, xfails, or edits tests to improve results.",
            "Full-suite profiling requires explicit --full-suite.",
            "Raw pytest stdout/stderr is not stored; only duration rows and byte counts are retained.",
        ],
    )
    payload = report.to_dict()
    payload["target"] = display_target
    payload["durations_requested"] = durations
    payload["timeout_seconds"] = timeout_seconds
    payload["full_suite"] = full_suite
    payload["elapsed_ms"] = elapsed_ms
    payload["returncode"] = returncode
    payload["stdout_bytes"] = len(stdout)
    payload["stderr_bytes"] = len(stderr)
    payload["durations"] = [item.to_dict() for item in parsed]
    payload["slow_modules"] = summarize_modules(parsed)
    payload["optimization_recommendations"] = recommendation_summary(parsed)
    if write_report:
        store = PerformanceReportStore(root)
        payload["report_path"] = str(store.write_report(report))
        payload["markdown_path"] = str(store.write_markdown(report))
        extra_path = _report_extra_path(store, report_id)
        store.ensure_dir()
        extra_path.write_text(json.dumps(store.redact_payload(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        payload["profile_report_path"] = str(extra_path)
    return PerformanceReportStore(root).redact_payload(payload)


def read_latest_test_profile(project_root: str | Path = ".") -> dict[str, Any]:
    store = PerformanceReportStore(project_root)
    for path in store.list_reports():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if payload.get("report_type") == "test_profile":
            profile_path = _report_extra_path(store, str(payload.get("report_id", "")))
            redacted = store.redact_payload(payload)
            if isinstance(redacted, dict):
                redacted["report_path"] = str(path)
                redacted["profile_report_path"] = str(profile_path) if profile_path.exists() else ""
            return redacted
    return {
        "status": "no_report",
        "message": "No test-suite performance profile found. Run `python smart_agent.py perf tests --durations 25` first.",
        "reports_dir": str(store.reports_dir),
    }
