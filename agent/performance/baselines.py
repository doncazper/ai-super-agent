from __future__ import annotations

import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

from .models import PerformanceMetric, utc_now_iso
from .reports import PerformanceReportStore


BASELINES_DIR = Path("reports/performance/baselines")


def _safe_git(args: list[str], root: Path) -> str:
    try:
        completed = subprocess.run(["git", *args], cwd=str(root), text=True, capture_output=True, timeout=3, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    if completed.returncode != 0:
        return "unknown"
    return (completed.stdout or "").strip() or "unknown"


def _baseline_dir(project_root: Path) -> Path:
    return project_root / BASELINES_DIR


def _baseline_path(project_root: Path, baseline_id: str) -> Path:
    safe_id = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in baseline_id)
    return _baseline_dir(project_root) / f"{safe_id}.json"


def _latest_source_report(store: PerformanceReportStore) -> dict[str, Any]:
    for path in store.list_reports():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if payload.get("report_type") in {"recommendations", "baseline", "regressions"}:
            continue
        if payload.get("report_type") == "test_profile":
            profile_path = store.report_path(str(payload.get("report_id", "")), suffix=".profile.json")
            if profile_path.exists():
                try:
                    profile_payload = json.loads(profile_path.read_text(encoding="utf-8"))
                    if isinstance(profile_payload, dict):
                        payload.update(profile_payload)
                except json.JSONDecodeError:
                    pass
        payload["report_path"] = str(path)
        return store.redact_payload(payload)
    return store.read_latest_report()


def _duration_map(report: dict[str, Any]) -> dict[str, float]:
    timings: dict[str, float] = {}
    for item in report.get("benchmark_results", []) if isinstance(report.get("benchmark_results"), list) else []:
        if not isinstance(item, dict):
            continue
        key = str(item.get("command_id") or item.get("command") or item.get("benchmark_id"))
        value = item.get("median_duration_ms", item.get("duration_ms"))
        if key and isinstance(value, (int, float)):
            timings[key] = float(value)
    return timings


def _test_duration_map(report: dict[str, Any]) -> dict[str, float]:
    timings: dict[str, float] = {}
    for item in report.get("durations", []) if isinstance(report.get("durations"), list) else []:
        if not isinstance(item, dict):
            continue
        key = str(item.get("nodeid") or item.get("module_path"))
        seconds = item.get("seconds")
        if key and isinstance(seconds, (int, float)):
            timings[key] = round(float(seconds) * 1000, 3)
    return timings


def _startup_metrics(report: dict[str, Any]) -> dict[str, float]:
    metrics: dict[str, float] = {}
    scan_result = report.get("scan_result")
    if isinstance(scan_result, dict):
        for item in scan_result.get("metrics", []) if isinstance(scan_result.get("metrics"), list) else []:
            if isinstance(item, dict) and isinstance(item.get("value"), (int, float)):
                metrics[str(item.get("name"))] = float(item["value"])
    return metrics


def _finding_count(report: dict[str, Any]) -> int:
    findings = report.get("findings")
    if isinstance(findings, list):
        return len(findings)
    scan_result = report.get("scan_result")
    if isinstance(scan_result, dict) and isinstance(scan_result.get("findings"), list):
        return len(scan_result["findings"])
    return 0


def _baseline_payload(root: Path, source_report: dict[str, Any], notes: str = "") -> dict[str, Any]:
    created_at = utc_now_iso()
    baseline_id = f"baseline_{created_at.replace(':', '').replace('-', '')}"
    return {
        "baseline_id": baseline_id,
        "created_at": created_at,
        "source_report_id": source_report.get("report_id", ""),
        "source_report_type": source_report.get("report_type", ""),
        "branch": _safe_git(["branch", "--show-current"], root),
        "commit": _safe_git(["rev-parse", "--short", "HEAD"], root),
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "notes": notes,
        "command_timings": _duration_map(source_report),
        "startup_timings": _startup_metrics(source_report),
        "test_durations": _test_duration_map(source_report),
        "finding_count": _finding_count(source_report),
        "redacted": True,
    }


def create_baseline(project_root: str | Path = ".", *, notes: str = "") -> dict[str, Any]:
    root = Path(project_root).resolve()
    store = PerformanceReportStore(root)
    source_report = _latest_source_report(store)
    if source_report.get("status") == "no_report":
        return {**source_report, "baseline_created": False}
    payload = _baseline_payload(root, source_report, notes=notes)
    baseline_dir = _baseline_dir(root)
    baseline_dir.mkdir(parents=True, exist_ok=True)
    path = _baseline_path(root, str(payload["baseline_id"]))
    redacted = store.redact_payload(payload)
    path.write_text(json.dumps(redacted, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {**redacted, "status": "ok", "baseline_created": True, "baseline_path": str(path)}


def _latest_baseline_path(root: Path) -> Path | None:
    baseline_dir = _baseline_dir(root)
    if not baseline_dir.exists():
        return None
    paths = sorted(baseline_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
    return paths[0] if paths else None


def read_baseline(project_root: str | Path = ".", *, baseline_id: str | None = None) -> dict[str, Any]:
    root = Path(project_root).resolve()
    store = PerformanceReportStore(root)
    path = _baseline_path(root, baseline_id) if baseline_id else _latest_baseline_path(root)
    if path is None or not path.exists():
        return {
            "status": "no_baseline",
            "message": "No performance baseline found. Run `python smart_agent.py perf baseline create` first.",
            "baselines_dir": str(_baseline_dir(root)),
        }
    return store.redact_payload(json.loads(path.read_text(encoding="utf-8")) | {"status": "ok", "baseline_path": str(path)})


def _compare_metric_maps(baseline: dict[str, float], current: dict[str, float], *, tolerance: float, category: str) -> list[dict[str, Any]]:
    regressions: list[dict[str, Any]] = []
    for key, baseline_value in baseline.items():
        current_value = current.get(key)
        if current_value is None or baseline_value <= 0:
            continue
        ratio = (current_value - baseline_value) / baseline_value
        if ratio > tolerance:
            regressions.append(
                {
                    "category": category,
                    "key": key,
                    "baseline_ms": round(baseline_value, 3),
                    "current_ms": round(current_value, 3),
                    "delta_ms": round(current_value - baseline_value, 3),
                    "delta_percent": round(ratio * 100, 2),
                    "severity": "P1" if ratio >= 1.0 else "P2" if ratio >= 0.5 else "P3",
                }
            )
    return regressions


def compare_baseline(project_root: str | Path = ".", *, baseline_id: str | None = None, tolerance: float = 0.2) -> dict[str, Any]:
    if tolerance < 0 or tolerance > 10:
        raise ValueError("tolerance must be between 0 and 10")
    root = Path(project_root).resolve()
    store = PerformanceReportStore(root)
    baseline = read_baseline(root, baseline_id=baseline_id)
    if baseline.get("status") == "no_baseline":
        return {**baseline, "regressions": []}
    current = _latest_source_report(store)
    if current.get("status") == "no_report":
        return {**current, "regressions": [], "baseline_id": baseline.get("baseline_id")}
    regressions = []
    regressions.extend(_compare_metric_maps(baseline.get("command_timings", {}), _duration_map(current), tolerance=tolerance, category="command_timing"))
    regressions.extend(_compare_metric_maps(baseline.get("test_durations", {}), _test_duration_map(current), tolerance=tolerance, category="test_duration"))
    regressions.extend(_compare_metric_maps(baseline.get("startup_timings", {}), _startup_metrics(current), tolerance=tolerance, category="startup_timing"))
    baseline_findings = int(baseline.get("finding_count") or 0)
    current_findings = _finding_count(current)
    if current_findings > baseline_findings:
        regressions.append(
            {
                "category": "finding_count",
                "key": "findings",
                "baseline_count": baseline_findings,
                "current_count": current_findings,
                "delta_count": current_findings - baseline_findings,
                "severity": "P3",
            }
        )
    regressions.sort(key=lambda item: (item.get("severity", "P4"), -float(item.get("delta_percent", 0) or 0)))
    generated_at = utc_now_iso()
    payload = {
        "status": "ok",
        "report_type": "regressions",
        "generated_at": generated_at,
        "baseline_id": baseline.get("baseline_id"),
        "source_report_id": current.get("report_id"),
        "source_report_type": current.get("report_type"),
        "tolerance": tolerance,
        "regression_count": len(regressions),
        "regressions": regressions,
        "redacted": True,
    }
    report_id = f"regressions_{generated_at.replace(':', '').replace('-', '')}"
    path = store.report_path(report_id)
    store.ensure_dir()
    path.write_text(json.dumps(store.redact_payload(payload | {"report_id": report_id}), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    payload["report_id"] = report_id
    payload["report_path"] = str(path)
    return store.redact_payload(payload)


def regression_status(project_root: str | Path = ".", *, tolerance: float = 0.2) -> dict[str, Any]:
    return compare_baseline(project_root, tolerance=tolerance)
