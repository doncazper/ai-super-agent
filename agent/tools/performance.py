from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.performance.benchmark_runner import run_safe_benchmarks
from agent.performance.baselines import compare_baseline, create_baseline, regression_status
from agent.performance.dashboard import build_dashboard, next_fix, performance_status, trends
from agent.performance.patch_planner import create_patch_plan
from agent.performance.recommendations import suggest_fixes
from agent.performance.reports import PerformanceReportStore
from agent.performance.static_scanner import scan_static
from agent.performance.startup_scanner import scan_startup
from agent.performance.test_profiler import read_latest_test_profile, run_test_profile


PERFORMANCE_SCAN_SCHEMA = {
    "type": "function",
    "function": {
        "name": "perf.scan",
        "description": "Run the default safe local performance scan. v1 runs the static scanner only.",
        "parameters": {
            "type": "object",
            "properties": {
                "max_files": {"type": "integer", "minimum": 1, "maximum": 10000},
            },
            "additionalProperties": False,
        },
    },
}

PERFORMANCE_STATIC_SCAN_SCHEMA = {
    "type": "function",
    "function": {
        "name": "perf.scan_static",
        "description": "Run a safe static bottleneck scan without executing scanned code.",
        "parameters": {
            "type": "object",
            "properties": {
                "max_files": {"type": "integer", "minimum": 1, "maximum": 10000},
            },
            "additionalProperties": False,
        },
    },
}

PERFORMANCE_STARTUP_SCAN_SCHEMA = {
    "type": "function",
    "function": {
        "name": "perf.scan_startup",
        "description": "Measure safe startup/import timings with bounded subprocesses and no provider/model calls.",
        "parameters": {
            "type": "object",
            "properties": {
                "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 60},
                "max_commands": {"type": "integer", "minimum": 0, "maximum": 20},
                "max_imports": {"type": "integer", "minimum": 0, "maximum": 20},
            },
            "additionalProperties": False,
        },
    },
}

PERFORMANCE_BENCHMARK_SCHEMA = {
    "type": "function",
    "function": {
        "name": "perf.benchmark",
        "description": "Benchmark only SAFE/LOW read-only command registry commands with bounded subprocesses.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "group": {"type": "string"},
                "iterations": {"type": "integer", "minimum": 1, "maximum": 10},
                "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 60},
                "max_commands": {"type": "integer", "minimum": 1, "maximum": 20},
            },
            "additionalProperties": False,
        },
    },
}

PERFORMANCE_TEST_PROFILE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "perf.tests_profile",
        "description": "Run pytest --durations for safe local test targets and store redacted timing reports.",
        "parameters": {
            "type": "object",
            "properties": {
                "target": {"type": "string"},
                "durations": {"type": "integer", "minimum": 1, "maximum": 100},
                "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 900},
                "full_suite": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
    },
}

PERFORMANCE_TEST_REPORT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "perf.tests_report",
        "description": "Read the latest redacted pytest duration profile report without running tests.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
}

PERFORMANCE_SUGGEST_FIXES_SCHEMA = {
    "type": "function",
    "function": {
        "name": "perf.suggest_fixes",
        "description": "Generate advisory optimization recommendations from the latest redacted performance report without applying patches.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
}

PERFORMANCE_BASELINE_CREATE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "perf.baseline_create",
        "description": "Create a redacted local performance baseline from the latest safe performance report.",
        "parameters": {
            "type": "object",
            "properties": {"notes": {"type": "string"}},
            "additionalProperties": False,
        },
    },
}

PERFORMANCE_BASELINE_COMPARE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "perf.baseline_compare",
        "description": "Compare the latest safe performance report with a redacted local baseline.",
        "parameters": {
            "type": "object",
            "properties": {
                "baseline_id": {"type": "string"},
                "tolerance": {"type": "number", "minimum": 0, "maximum": 10},
            },
            "additionalProperties": False,
        },
    },
}

PERFORMANCE_REGRESSIONS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "perf.regressions",
        "description": "Show local performance regression status from the latest baseline comparison.",
        "parameters": {
            "type": "object",
            "properties": {"tolerance": {"type": "number", "minimum": 0, "maximum": 10}},
            "additionalProperties": False,
        },
    },
}

PERFORMANCE_PATCH_PLAN_SCHEMA = {
    "type": "function",
    "function": {
        "name": "perf.patch_plan",
        "description": "Create safe optimization patch plans from recommendation reports without applying patches.",
        "parameters": {
            "type": "object",
            "properties": {"recommendation_id": {"type": "string"}},
            "additionalProperties": False,
        },
    },
}

PERFORMANCE_DASHBOARD_SCHEMA = {
    "type": "function",
    "function": {
        "name": "perf.dashboard",
        "description": "Read performance dashboard summaries from redacted local reports without running scans or fixes.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}

PERFORMANCE_STATUS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "perf.status",
        "description": "Read compact performance status from redacted local reports without running scans or fixes.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}

PERFORMANCE_NEXT_FIX_SCHEMA = {
    "type": "function",
    "function": {
        "name": "perf.next_fix",
        "description": "Show the next safe performance action from local reports without executing it.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}

PERFORMANCE_TRENDS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "perf.trends",
        "description": "Read performance trend/regression summaries from local reports without running benchmarks.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}


PERFORMANCE_REPORT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "perf.report",
        "description": "Read the latest redacted local performance report without running scans or benchmarks.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
}

PERFORMANCE_FINDINGS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "perf.findings",
        "description": "Read findings from the latest redacted local performance report without running scans or benchmarks.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
}

PERFORMANCE_SCHEMAS = {
    "perf.scan": PERFORMANCE_SCAN_SCHEMA,
    "perf.scan_static": PERFORMANCE_STATIC_SCAN_SCHEMA,
    "perf.scan_startup": PERFORMANCE_STARTUP_SCAN_SCHEMA,
    "perf.benchmark": PERFORMANCE_BENCHMARK_SCHEMA,
    "perf.tests_profile": PERFORMANCE_TEST_PROFILE_SCHEMA,
    "perf.tests_report": PERFORMANCE_TEST_REPORT_SCHEMA,
    "perf.suggest_fixes": PERFORMANCE_SUGGEST_FIXES_SCHEMA,
    "perf.baseline_create": PERFORMANCE_BASELINE_CREATE_SCHEMA,
    "perf.baseline_compare": PERFORMANCE_BASELINE_COMPARE_SCHEMA,
    "perf.regressions": PERFORMANCE_REGRESSIONS_SCHEMA,
    "perf.patch_plan": PERFORMANCE_PATCH_PLAN_SCHEMA,
    "perf.dashboard": PERFORMANCE_DASHBOARD_SCHEMA,
    "perf.status": PERFORMANCE_STATUS_SCHEMA,
    "perf.next_fix": PERFORMANCE_NEXT_FIX_SCHEMA,
    "perf.trends": PERFORMANCE_TRENDS_SCHEMA,
    "perf.report": PERFORMANCE_REPORT_SCHEMA,
    "perf.findings": PERFORMANCE_FINDINGS_SCHEMA,
}


def make_performance_tools(project_root: str | Path = ".") -> dict[str, Any]:
    store = PerformanceReportStore(project_root)
    return {
        "perf.scan": lambda max_files=5000: scan_static(project_root, max_files=int(max_files or 5000)),
        "perf.scan_static": lambda max_files=5000: scan_static(project_root, max_files=int(max_files or 5000)),
        "perf.scan_startup": lambda timeout_seconds=10, max_commands=5, max_imports=5: scan_startup(
            project_root,
            timeout_seconds=int(timeout_seconds or 10),
            max_commands=int(max_commands or 5),
            max_imports=int(max_imports or 5),
        ),
        "perf.benchmark": lambda command=None, group=None, iterations=3, timeout_seconds=10, max_commands=5: run_safe_benchmarks(
            project_root,
            command=command,
            group=group,
            iterations=int(iterations or 3),
            timeout_seconds=int(timeout_seconds or 10),
            max_commands=int(max_commands or 5),
        ),
        "perf.tests_profile": lambda target="tests/performance", durations=25, timeout_seconds=120, full_suite=False: run_test_profile(
            project_root,
            target=target or "tests/performance",
            durations=int(durations or 25),
            timeout_seconds=int(timeout_seconds or 120),
            full_suite=bool(full_suite),
        ),
        "perf.tests_report": lambda: read_latest_test_profile(project_root),
        "perf.suggest_fixes": lambda: suggest_fixes(project_root),
        "perf.baseline_create": lambda notes="": create_baseline(project_root, notes=notes or ""),
        "perf.baseline_compare": lambda baseline_id=None, tolerance=0.2: compare_baseline(
            project_root,
            baseline_id=baseline_id or None,
            tolerance=float(tolerance if tolerance is not None else 0.2),
        ),
        "perf.regressions": lambda tolerance=0.2: regression_status(project_root, tolerance=float(tolerance if tolerance is not None else 0.2)),
        "perf.patch_plan": lambda recommendation_id=None: create_patch_plan(project_root, recommendation_id=recommendation_id or None),
        "perf.dashboard": lambda: build_dashboard(project_root),
        "perf.status": lambda: performance_status(project_root),
        "perf.next_fix": lambda: next_fix(project_root),
        "perf.trends": lambda: trends(project_root),
        "perf.report": lambda: store.read_latest_report(),
        "perf.findings": lambda: store.read_latest_findings(),
    }
