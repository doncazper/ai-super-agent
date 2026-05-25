from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from agent.dogfood.planner import dogfood_next
from agent.safety.redaction import SecretRedactor
from agent.session_logs.redaction import redact_text
from agent.session_logs.review import BugRecord, BugStore, SEVERITY_ORDER
from agent.session_logs.store import SessionLogStore


def build_quality_dashboard(*, project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    sessions = _sessions_section(root)
    bugs = _bugs_section(root)
    features = _features_section(root)
    evals = _evals_section(root)
    dashboard = {
        "status": _overall_status(bugs, evals),
        "read_only": True,
        "accesses_personal_data": False,
        "last_session": sessions["last_session"],
        "last_session_result": sessions["last_session_result"],
        "recent_feedback": sessions["recent_feedback"],
        "last_full_test_result": _last_full_test_result(root),
        "open_bugs_by_severity": bugs["open_by_severity"],
        "next_recommended_bug": bugs["next_recommended_bug"],
        "regressions": {
            "bugs_lacking_regression_tests": bugs["bugs_lacking_regression_tests"],
            "count": len(bugs["bugs_lacking_regression_tests"]),
        },
        "features": features,
        "evals": evals,
        "next_recommended_dogfood_suite": _dogfood_next_read_only(root),
        "release_gate_status": _release_gate_status(root),
        "safety_notes": [
            "Quality dashboard is read-only and does not execute tools or connectors.",
            "Session excerpts and feedback are redacted before display.",
            "Personal-data sessions must remain redacted; raw personal content is not displayed.",
        ],
    }
    return SecretRedactor().redact(dashboard)


def quality_status(*, project_root: str | Path = ".") -> dict[str, Any]:
    report = build_quality_dashboard(project_root=project_root)
    return {
        "status": report["status"],
        "read_only": report["read_only"],
        "last_session_result": report["last_session_result"],
        "last_full_test_result": report["last_full_test_result"],
        "open_bugs_by_severity": report["open_bugs_by_severity"],
        "next_recommended_dogfood_suite": report["next_recommended_dogfood_suite"],
        "release_gate_status": report["release_gate_status"],
    }


def quality_sessions(*, project_root: str | Path = ".") -> dict[str, Any]:
    return _sessions_section(Path(project_root))


def quality_bugs(*, project_root: str | Path = ".") -> dict[str, Any]:
    return _bugs_section(Path(project_root))


def quality_regressions(*, project_root: str | Path = ".") -> dict[str, Any]:
    bugs = _bugs_section(Path(project_root))
    return {
        "read_only": True,
        "bugs_lacking_regression_tests": bugs["bugs_lacking_regression_tests"],
        "count": len(bugs["bugs_lacking_regression_tests"]),
    }


def quality_features(*, project_root: str | Path = ".") -> dict[str, Any]:
    return _features_section(Path(project_root))


def quality_next(*, project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    bugs = _bugs_section(root)
    next_bug = bugs["next_recommended_bug"]
    if next_bug:
        return {
            "priority": "bug",
            "reason": "Open P0/P1 bugs take priority over dogfood polish and feature maturity work.",
            "bug": next_bug,
            "dogfood": _dogfood_next_read_only(root),
        }
    return {
        "priority": "dogfood",
        "reason": "No open P0/P1 bug is available; continue daily/weekly dogfood validation.",
        "bug": None,
        "dogfood": _dogfood_next_read_only(root),
    }


def format_quality_dashboard(report: dict[str, Any]) -> str:
    lines = [
        "Product Quality Dashboard v1",
        f"Status: {report.get('status')}",
        f"Read-only: {report.get('read_only')} | Personal data accessed: {report.get('accesses_personal_data')}",
        "",
        "Last Session",
        f"- {report.get('last_session_result', {}).get('summary', 'No session found')}",
        "",
        "Tests",
        f"- {report.get('last_full_test_result', {}).get('summary', 'unknown')}",
        "",
        "Open Bugs",
        f"- By severity: {report.get('open_bugs_by_severity')}",
    ]
    next_bug = report.get("next_recommended_bug")
    lines.append(f"- Next bug: {next_bug.get('bug_id')} {next_bug.get('title')}" if next_bug else "- Next bug: (none)")
    lines.extend(["", "Recent Feedback"])
    feedback = report.get("recent_feedback", [])
    lines.extend(
        f"- {item.get('session_id')} {item.get('command_id')} tags={item.get('tags')} rating={item.get('rating')} {item.get('note')}".rstrip()
        for item in feedback[:5]
    )
    if not feedback:
        lines.append("- (none)")
    features = report.get("features", {})
    lines.extend(
        [
            "",
            "Features",
            f"- Lacking live validation: {', '.join(item.get('feature', '') for item in features.get('lacking_live_validation', [])[:8]) or '(none)'}",
            f"- Lacking regression tests: {', '.join(item.get('feature', '') for item in features.get('lacking_regression_tests', [])[:8]) or '(none)'}",
            f"- Most mature: {', '.join(item.get('feature', '') for item in features.get('most_mature', [])[:5]) or '(none)'}",
            f"- Least mature: {', '.join(item.get('feature', '') for item in features.get('least_mature', [])[:5]) or '(none)'}",
            "",
            "Next Dogfood",
            f"- {report.get('next_recommended_dogfood_suite', {}).get('reason', '')}",
            "",
            "Release Gate",
            f"- {report.get('release_gate_status', {}).get('summary', 'unknown')}",
        ]
    )
    return "\n".join(lines)


def format_quality_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True)


def _sessions_section(root: Path) -> dict[str, Any]:
    if not (root / "reports" / "sessions").exists():
        return {
            "read_only": True,
            "session_count": 0,
            "last_session": None,
            "last_session_result": {"status": "missing", "summary": "No dogfood session found."},
            "recent_feedback": [],
        }
    store = SessionLogStore(project_root=root)
    sessions = store.list_sessions()
    last = store.last_session()
    return {
        "read_only": True,
        "session_count": len(sessions),
        "last_session": _session_summary(last),
        "last_session_result": _session_result(last),
        "recent_feedback": _recent_feedback(root, limit=10),
    }


def _session_summary(session: Any | None) -> dict[str, Any] | None:
    if session is None:
        return None
    return {
        "session_id": session.session_id,
        "name": redact_text(session.name),
        "status": session.status,
        "started_at": session.started_at,
        "ended_at": session.ended_at,
        "command_count": session.command_count,
        "failure_count": session.failure_count,
        "bug_count": session.bug_count,
        "feedback_count": session.feedback_count,
        "redaction_status": session.redaction_status,
    }


def _session_result(session: Any | None) -> dict[str, Any]:
    if session is None:
        return {"status": "missing", "summary": "No dogfood session found."}
    status = "fail" if session.failure_count else "pass"
    if session.status == "active":
        status = "active"
    return {
        "status": status,
        "summary": (
            f"{session.session_id}: {session.command_count} commands, "
            f"{session.failure_count} failures, {session.feedback_count} feedback records"
        ),
    }


def _recent_feedback(root: Path, *, limit: int) -> list[dict[str, Any]]:
    if not (root / "reports" / "sessions").exists():
        return []
    store = SessionLogStore(project_root=root)
    items: list[dict[str, Any]] = []
    for session in store.list_sessions()[:10]:
        for record in store.load_feedback(session.session_id):
            note = record.user_note or record.reason or record.actual_behavior
            items.append(
                {
                    "feedback_id": record.feedback_id,
                    "session_id": record.session_id,
                    "command_id": record.command_id,
                    "timestamp": record.timestamp,
                    "rating": record.rating,
                    "tags": record.tags,
                    "severity": record.severity,
                    "note": redact_text(note),
                }
            )
    return sorted(items, key=lambda item: item["timestamp"], reverse=True)[:limit]


def _bugs_section(root: Path) -> dict[str, Any]:
    if not (root / "bugs").exists():
        return {
            "read_only": True,
            "total": 0,
            "open_total": 0,
            "open_by_severity": {severity: 0 for severity in ("P0", "P1", "P2", "P3", "P4")},
            "open_bugs": [],
            "bugs_lacking_regression_tests": [],
            "next_recommended_bug": None,
        }
    records = BugStore(project_root=root).list_bugs()
    open_records = [bug for bug in records if bug.status not in {"fixed", "wontfix"}]
    by_severity = Counter(bug.severity for bug in open_records)
    lacking = [bug for bug in open_records if not bug.linked_tests and not bug.regression_test_path]
    return {
        "read_only": True,
        "total": len(records),
        "open_total": len(open_records),
        "open_by_severity": {severity: by_severity.get(severity, 0) for severity in ("P0", "P1", "P2", "P3", "P4")},
        "open_bugs": [_bug_summary(bug) for bug in open_records],
        "bugs_lacking_regression_tests": [_bug_summary(bug) for bug in lacking],
        "next_recommended_bug": _bug_summary(_next_bug(open_records)),
    }


def _bug_summary(bug: BugRecord | None) -> dict[str, Any] | None:
    if bug is None:
        return None
    return {
        "bug_id": bug.bug_id,
        "title": redact_text(bug.title),
        "status": bug.status,
        "severity": bug.severity,
        "feature": bug.feature,
        "session_id": bug.session_id,
        "command_id": bug.command_id,
        "has_regression_test": bool(bug.linked_tests or bug.regression_test_path),
        "regression_test_path": bug.regression_test_path,
    }


def _next_bug(open_records: list[BugRecord]) -> BugRecord | None:
    if not open_records:
        return None
    priority = sorted(open_records, key=lambda bug: (SEVERITY_ORDER.get(bug.severity, 99), bug.created_at or bug.bug_id))
    return priority[0]


def _features_section(root: Path) -> dict[str, Any]:
    features = _parse_maturity(root / "docs" / "FEATURE_MATURITY.md")
    poor_features = _features_with_poor_feedback(root)
    lacking_live = [
        feature
        for feature in features
        if _needs_live_validation(feature)
    ]
    lacking_regressions = [
        feature
        for feature in features
        if "regression" not in (feature.get("test_coverage", "") + " " + feature.get("next_work_needed", "")).lower()
    ][:25]
    return {
        "read_only": True,
        "features_with_poor_dogfood_results": poor_features,
        "lacking_live_validation": lacking_live[:25],
        "lacking_regression_tests": lacking_regressions,
        "most_mature": sorted(features, key=lambda item: (-int(item.get("maturity_value", 0)), -int(item.get("readiness_score", 0))))[:10],
        "least_mature": sorted(features, key=lambda item: (int(item.get("maturity_value", 0)), int(item.get("readiness_score", 0))))[:10],
    }


def _parse_maturity(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ") or line.startswith("| Feature ") or line.startswith("|---"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 14:
            continue
        maturity_match = re.match(r"(\d+)", parts[2])
        score_match = re.match(r"(\d+)", parts[3])
        if not maturity_match:
            continue
        rows.append(
            {
                "feature": parts[0],
                "category": parts[1],
                "maturity_level": parts[2],
                "maturity_value": int(maturity_match.group(1)),
                "readiness_score": int(score_match.group(1)) if score_match else 0,
                "test_coverage": parts[7],
                "live_validation_status": parts[10],
                "known_limitations": parts[12],
                "next_work_needed": parts[13],
            }
        )
    return rows


def _needs_live_validation(feature: dict[str, Any]) -> bool:
    text = " ".join(
        [
            feature.get("maturity_level", ""),
            feature.get("live_validation_status", ""),
            feature.get("known_limitations", ""),
            feature.get("next_work_needed", ""),
        ]
    ).lower()
    return "live" in text and any(marker in text for marker in ("need", "pending", "optional", "not live", "not validated", "smoke"))


def _features_with_poor_feedback(root: Path) -> list[dict[str, Any]]:
    if not (root / "reports" / "sessions").exists():
        return []
    store = SessionLogStore(project_root=root)
    counts: Counter[str] = Counter()
    for session in store.list_sessions()[:20]:
        commands = {command.command_id: command.sanitized_command_line or command.command_line for command in store.load_commands(session.session_id)}
        for feedback in store.load_feedback(session.session_id):
            if feedback.rating is not None and feedback.rating >= 4 and not {"poor_response", "command_failed", "unsafe_behavior"} & set(feedback.tags):
                continue
            feature = _feature_from_command(commands.get(feedback.command_id, ""))
            counts[feature] += 1
    return [{"feature": feature, "poor_feedback_count": count} for feature, count in counts.most_common()]


def _feature_from_command(command_line: str) -> str:
    parts = command_line.split()
    if "smart_agent.py" in parts:
        index = parts.index("smart_agent.py")
        if len(parts) > index + 1:
            return parts[index + 1]
    if parts:
        return parts[0]
    return "unknown"


def _evals_section(root: Path) -> dict[str, Any]:
    latest = _latest_json_file([root / "logs" / "eval_results.json", *(root / "reports" / "evals").glob("eval-*.json")])
    if latest is None:
        return {"status": "missing", "summary": "No eval report found.", "latest_report": None}
    data = _read_json(latest)
    checks = data.get("checks", []) if isinstance(data, dict) else []
    counts = Counter(str(check.get("status", "unknown")) for check in checks if isinstance(check, dict))
    return {
        "status": "ok" if counts.get("fail", 0) == 0 else "fail",
        "latest_report": _relative(root, latest),
        "summary": f"{counts.get('pass', 0)} passed, {counts.get('fail', 0)} failed, {counts.get('skipped', 0)} skipped",
        "counts": dict(counts),
    }


def _last_full_test_result(root: Path) -> dict[str, Any]:
    text = (root / "docs" / "PROJECT_STATE.md").read_text(encoding="utf-8") if (root / "docs" / "PROJECT_STATE.md").exists() else ""
    section_match = re.search(r"## Last Test Result\n\n(?P<section>.*?)(?:\n## |\Z)", text, flags=re.S)
    search_text = section_match.group("section") if section_match else text
    matches = re.findall(r"Full suite: ([^\n]+)", search_text)
    summary = matches[-1].strip() if matches else "Full suite result not found."
    return {"summary": redact_text(summary), "source": "docs/PROJECT_STATE.md"}


def _release_gate_status(root: Path) -> dict[str, Any]:
    checklist = root / "docs" / "RELEASE_CHECKLIST.md"
    completion = root / "docs" / "COMPLETION_REPORT.md"
    checklist_text = checklist.read_text(encoding="utf-8") if checklist.exists() else ""
    completion_text = completion.read_text(encoding="utf-8") if completion.exists() else ""
    unchecked = len(re.findall(r"- \[ \]", checklist_text))
    failed = "fail" in completion_text.lower() and "0 failed" not in completion_text.lower()
    status = "pass" if unchecked == 0 and not failed else "warn"
    return {
        "status": status,
        "unchecked_items": unchecked,
        "summary": "release checklist complete" if status == "pass" else "release gate needs review",
        "sources": ["docs/RELEASE_CHECKLIST.md", "docs/COMPLETION_REPORT.md"],
    }


def _dogfood_next_read_only(root: Path) -> dict[str, Any]:
    if not (root / "reports" / "sessions").exists():
        return {
            "next_type": "start_daily_session",
            "suite": "all_safe",
            "reason": "No session logs were found; start with the safe baseline dogfood session.",
            "commands": [
                'python smart_agent.py session start --name "daily-dogfood"',
                "python smart_agent.py dogfood run all_safe --session",
            ],
            "maturity_notes": ["Session log directory not found; quality dashboard did not create it."],
        }
    return dogfood_next(project_root=root)


def _overall_status(bugs: dict[str, Any], evals: dict[str, Any]) -> str:
    if bugs["open_by_severity"].get("P0", 0) or evals.get("status") == "fail":
        return "fail"
    if bugs["open_by_severity"].get("P1", 0):
        return "warn"
    return "ok"


def _latest_json_file(paths: list[Path]) -> Path | None:
    existing = [path for path in paths if path.exists() and path.is_file()]
    return max(existing, key=lambda path: path.stat().st_mtime) if existing else None


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _relative(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
