from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_performance_scanner_policy_docs_exist() -> None:
    required = [
        "docs/performance/PERFORMANCE_SCANNER_TRACK.md",
        "docs/performance/PERFORMANCE_BOTTLENECK_POLICY.md",
        "docs/performance/PERFORMANCE_FINDING_SCHEMA.md",
        "docs/performance/PERFORMANCE_OPTIMIZATION_POLICY.md",
        "docs/performance/PERFORMANCE_BASELINE_STRATEGY.md",
        "docs/decisions/performance_bottleneck_scanner.md",
    ]
    for relative in required:
        assert (ROOT / relative).exists(), relative


def test_performance_policy_preserves_safety_boundaries() -> None:
    text = (ROOT / "docs/performance/PERFORMANCE_SCANNER_TRACK.md").read_text(encoding="utf-8")
    policy = (ROOT / "docs/performance/PERFORMANCE_BOTTLENECK_POLICY.md").read_text(encoding="utf-8")
    optimization = (ROOT / "docs/performance/PERFORMANCE_OPTIMIZATION_POLICY.md").read_text(encoding="utf-8")
    combined = "\n".join([text, policy, optimization])
    for phrase in [
        "ToolBroker",
        "PolicyEngine",
        "ApprovalManager",
        "AuditLogger",
        "No live provider calls by default",
        "No paid APIs",
        "No personal-data access",
        "must not execute scanned code",
    ]:
        assert phrase in combined


def test_performance_track_lists_planned_commands_and_categories() -> None:
    track = (ROOT / "docs/performance/PERFORMANCE_SCANNER_TRACK.md").read_text(encoding="utf-8")
    policy = (ROOT / "docs/performance/PERFORMANCE_BOTTLENECK_POLICY.md").read_text(encoding="utf-8")
    for command in [
        "python smart_agent.py perf scan",
        "python smart_agent.py perf benchmark --safe",
        "python smart_agent.py perf report --last",
        "python smart_agent.py perf baseline compare",
    ]:
        assert command in track
    for category in [
        "Startup/import overhead",
        "Command registry loading",
        "ToolBroker overhead",
        "Missing timeouts",
        "Slow tests",
    ]:
        assert category in policy
