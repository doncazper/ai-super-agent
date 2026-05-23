from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from agent.safety.audit import AuditEvent, AuditLogger
from agent.session_logs.models import CommandRecord, FeedbackRecord, SessionRecord, utc_now_iso
from agent.session_logs.redaction import redact_text
from agent.session_logs.store import SessionLogStore


SEVERITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}
P0_PATTERNS = (
    "policy bypass",
    "toolbroker bypass",
    "policyengine bypass",
    "approval bypass",
    "audit bypass",
    "disable audit",
    "disabled audit",
    "personal-data leak",
    "personal data leak",
    "private data leaked",
    "data leak",
    "secret leaked",
    "leaked secret",
    "leaked password",
    "leaked token",
)
CORE_COMMAND_HINTS = ("doctor", "tools list", "--no-tools", "session", "feedback", "dogfood")
REVIEW_REPORT_VERSION = 1


@dataclass
class BugRecord:
    bug_id: str
    title: str
    status: str
    severity: str
    feature: str
    command_id: str
    session_id: str
    reproduction_command: str
    expected_behavior: str
    actual_behavior: str
    stdout_stderr_excerpt: str
    linked_audit_ids: list[str] = field(default_factory=list)
    suspected_cause: str = ""
    suggested_fix_area: str = ""
    suggested_regression_test: str = ""
    created_at: str = ""
    last_updated: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BugRecord":
        return cls(
            bug_id=str(data.get("bug_id", "")),
            title=str(data.get("title", "")),
            status=str(data.get("status", "open")),
            severity=str(data.get("severity", "P3")),
            feature=str(data.get("feature", "")),
            command_id=str(data.get("command_id", "")),
            session_id=str(data.get("session_id", "")),
            reproduction_command=str(data.get("reproduction_command", "")),
            expected_behavior=str(data.get("expected_behavior", "")),
            actual_behavior=str(data.get("actual_behavior", "")),
            stdout_stderr_excerpt=str(data.get("stdout_stderr_excerpt", "")),
            linked_audit_ids=list(data.get("linked_audit_ids", [])),
            suspected_cause=str(data.get("suspected_cause", "")),
            suggested_fix_area=str(data.get("suggested_fix_area", "")),
            suggested_regression_test=str(data.get("suggested_regression_test", "")),
            created_at=str(data.get("created_at", "")),
            last_updated=str(data.get("last_updated", "")),
        )


class BugStore:
    def __init__(self, root: str | Path = "bugs", *, project_root: str | Path = ".") -> None:
        self.project_root = Path(project_root)
        self.root = Path(root)
        if not self.root.is_absolute():
            self.root = self.project_root / self.root
        self.root.mkdir(parents=True, exist_ok=True)

    def bug_path(self, bug_id: str) -> Path:
        return self.root / f"{bug_id}.json"

    def next_bug_id(self) -> str:
        highest = 0
        for path in self.root.glob("BUG-*.json"):
            match = re.fullmatch(r"BUG-(\d{4})", path.stem)
            if match:
                highest = max(highest, int(match.group(1)))
        return f"BUG-{highest + 1:04d}"

    def create_bug(self, candidate: dict[str, Any]) -> BugRecord:
        now = utc_now_iso()
        record = BugRecord(
            bug_id=self.next_bug_id(),
            title=redact_text(str(candidate.get("title", "Untitled bug"))),
            status="open",
            severity=str(candidate.get("severity", "P3")),
            feature=str(candidate.get("feature", "unknown")),
            command_id=str(candidate.get("command_id", "")),
            session_id=str(candidate.get("session_id", "")),
            reproduction_command=redact_text(str(candidate.get("reproduction_command", ""))),
            expected_behavior=redact_text(str(candidate.get("expected_behavior", ""))),
            actual_behavior=redact_text(str(candidate.get("actual_behavior", ""))),
            stdout_stderr_excerpt=redact_text(str(candidate.get("stdout_stderr_excerpt", ""))),
            linked_audit_ids=list(candidate.get("linked_audit_ids", [])),
            suspected_cause=redact_text(str(candidate.get("suspected_cause", ""))),
            suggested_fix_area=str(candidate.get("suggested_fix_area", "")),
            suggested_regression_test=str(candidate.get("suggested_regression_test", "")),
            created_at=now,
            last_updated=now,
        )
        self.bug_path(record.bug_id).write_text(json.dumps(record.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return record

    def list_bugs(self) -> list[BugRecord]:
        records: list[BugRecord] = []
        for path in sorted(self.root.glob("BUG-*.json")):
            try:
                records.append(BugRecord.from_dict(json.loads(path.read_text(encoding="utf-8"))))
            except (json.JSONDecodeError, OSError, TypeError, ValueError):
                continue
        return sorted(records, key=lambda bug: (SEVERITY_ORDER.get(bug.severity, 99), bug.bug_id))

    def get(self, bug_id: str) -> BugRecord | None:
        path = self.bug_path(bug_id)
        if not path.exists():
            return None
        try:
            return BugRecord.from_dict(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            return None

    def export(self) -> dict[str, Any]:
        return {"bugs": [record.to_dict() for record in self.list_bugs()]}


class SessionReviewer:
    def __init__(
        self,
        store: SessionLogStore | None = None,
        *,
        project_root: str | Path = ".",
        report_root: str | Path = "reports/session_reviews",
        bug_store: BugStore | None = None,
        audit_logger: AuditLogger | None = None,
    ) -> None:
        self.project_root = Path(project_root)
        self.store = store or SessionLogStore(project_root=self.project_root)
        self.report_root = Path(report_root)
        if not self.report_root.is_absolute():
            self.report_root = self.project_root / self.report_root
        self.report_root.mkdir(parents=True, exist_ok=True)
        self.bug_store = bug_store or BugStore(project_root=self.project_root)
        self.audit_logger = audit_logger or AuditLogger(self.project_root / "logs" / "audit.jsonl")

    def review_session(self, session_id: str, *, create_bugs: bool = False) -> dict[str, Any]:
        session = self.store.get(session_id)
        if session is None:
            raise ValueError("session not found")
        commands = self.store.load_commands(session_id)
        feedback = self.store.load_feedback(session_id)
        candidates = _bug_candidates(session, commands, feedback)
        created_bugs: list[BugRecord] = []
        if create_bugs:
            for candidate in candidates:
                created_bugs.append(self.bug_store.create_bug(candidate))
        report = _review_report(session, commands, feedback, candidates, created_bugs)
        report_path = self._write_report(session.session_id, report)
        report["review_path"] = str(report_path.relative_to(self.project_root))
        self._audit(
            "session.review",
            session_id=session.session_id,
            request_id=f"review_{session.session_id}",
            summary=f"reviewed {len(commands)} commands, {len(candidates)} candidates, {len(created_bugs)} bugs created",
            files_written=[str(report_path.relative_to(self.project_root))],
        )
        for bug in created_bugs:
            self._audit(
                "bugs.create",
                session_id=session.session_id,
                request_id=bug.bug_id,
                summary=f"created {bug.severity} bug {bug.bug_id}",
                files_written=[str(self.bug_store.bug_path(bug.bug_id).relative_to(self.project_root))],
                args={"bug_id": bug.bug_id, "severity": bug.severity, "feature": bug.feature},
            )
        return report

    def list_bugs(self) -> list[BugRecord]:
        records = self.bug_store.list_bugs()
        self._audit("bugs.list", session_id="bug_cli", request_id="bugs_list", summary=f"listed {len(records)} bugs")
        return records

    def show_bug(self, bug_id: str) -> BugRecord:
        record = self.bug_store.get(bug_id)
        if record is None:
            raise ValueError("bug not found")
        self._audit("bugs.show", session_id=record.session_id or "bug_cli", request_id=bug_id, summary=f"showed bug {bug_id}")
        return record

    def export_bugs(self) -> dict[str, Any]:
        payload = self.bug_store.export()
        self._audit("bugs.export", session_id="bug_cli", request_id="bugs_export", summary=f"exported {len(payload['bugs'])} bugs")
        return payload

    def _write_report(self, session_id: str, report: dict[str, Any]) -> Path:
        path = self.report_root / f"review_{session_id}.json"
        path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        return path

    def _audit(
        self,
        tool_name: str,
        *,
        session_id: str,
        request_id: str,
        summary: str,
        args: dict[str, Any] | None = None,
        files_written: list[str] | None = None,
    ) -> None:
        self.audit_logger.log(
            AuditEvent(
                session_id=session_id,
                request_id=request_id,
                route="session_review_cli",
                model="none",
                tool_name=tool_name,
                capability=tool_name,
                risk_level="LOW",
                trust_level="TRUSTED_USER",
                policy_decision="ALLOW",
                sanitized_args=args or {},
                result_summary=summary,
                files_written=files_written or [],
            )
        )


def _review_report(
    session: SessionRecord,
    commands: list[CommandRecord],
    feedback: list[FeedbackRecord],
    candidates: list[dict[str, Any]],
    created_bugs: list[BugRecord],
) -> dict[str, Any]:
    failed = [command for command in commands if command.exit_code != 0]
    tags = Counter(tag for record in feedback for tag in record.tags)
    ratings = [record.rating for record in feedback if record.rating is not None]
    ordered_candidates = sorted(candidates, key=lambda item: (SEVERITY_ORDER.get(str(item.get("severity", "P3")), 99), str(item.get("title", ""))))
    return {
        "version": REVIEW_REPORT_VERSION,
        "created_at": utc_now_iso(),
        "session_summary": session.to_dict(),
        "commands_run": [_command_summary(command) for command in commands],
        "pass_fail_summary": {
            "total": len(commands),
            "passed": len(commands) - len(failed),
            "failed": len(failed),
            "failure_rate": round((len(failed) / len(commands)) if commands else 0.0, 3),
        },
        "feedback_summary": {
            "total": len(feedback),
            "tag_counts": dict(sorted(tags.items())),
            "ratings": ratings,
            "average_rating": round((sum(ratings) / len(ratings)) if ratings else 0.0, 2),
            "unsafe_count": tags.get("unsafe_behavior", 0),
        },
        "repeated_failure_patterns": _repeated_failure_patterns(failed),
        "tool_failures": [_command_summary(command) for command in failed if _looks_like_tool_failure(command)],
        "routing_failures": _feedback_flags(feedback, {"wrong_tool", "missing_tool", "bad_routing"}),
        "poor_response_flags": _feedback_flags(feedback, {"poor_response", "hallucination", "no_citation"}, include_low_ratings=True),
        "confusing_ux_flags": _feedback_flags(feedback, {"UX_confusing", "approval_confusing", "bad_error_message"}),
        "approval_friction": _approval_friction(commands, feedback),
        "missing_docs": _feedback_flags(feedback, {"docs_gap"}),
        "suspected_bugs": ordered_candidates,
        "suggested_regression_tests": [str(candidate["suggested_regression_test"]) for candidate in ordered_candidates],
        "suggested_priority_order": [
            {"severity": candidate["severity"], "title": candidate["title"], "command_id": candidate["command_id"]}
            for candidate in ordered_candidates
        ],
        "created_bugs": [bug.to_dict() for bug in created_bugs],
        "limitations": [
            "Review uses redacted session command previews and feedback only.",
            "Raw personal content and full raw command outputs are not read for bug generation.",
            "Bug candidates are local triage records; this workflow does not fix bugs automatically.",
        ],
    }


def _bug_candidates(
    session: SessionRecord,
    commands: list[CommandRecord],
    feedback: list[FeedbackRecord],
) -> list[dict[str, Any]]:
    by_command: dict[str, list[FeedbackRecord]] = defaultdict(list)
    for record in feedback:
        by_command[record.command_id].append(record)
    candidates: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for command in commands:
        command_feedback = by_command.get(command.command_id, [])
        should_create = command.exit_code != 0 or command.suspected_bug or any(_feedback_is_bug_like(record) for record in command_feedback)
        if not should_create:
            continue
        candidate = _candidate_from_command(session, command, command_feedback)
        key = (candidate["command_id"], candidate["title"])
        if key not in seen:
            candidates.append(candidate)
            seen.add(key)
    return candidates


def _candidate_from_command(session: SessionRecord, command: CommandRecord, feedback: list[FeedbackRecord]) -> dict[str, Any]:
    all_text = "\n".join(
        [
            command.sanitized_command_line,
            command.stdout_preview,
            command.stderr_preview,
            command.notes,
            *[record.reason for record in feedback],
            *[record.actual_behavior for record in feedback],
            *[record.user_note for record in feedback],
        ]
    )
    severity = _classify_severity(command, feedback, all_text)
    feature = _feature_for_command(command.sanitized_command_line, feedback)
    feedback_tags = sorted({tag for record in feedback for tag in record.tags})
    title = _title_for(command, feedback_tags, severity)
    expected = _expected_behavior(command, feedback)
    actual = _actual_behavior(command, feedback)
    excerpt = redact_text(f"[stdout]\n{command.stdout_preview}\n\n[stderr]\n{command.stderr_preview}")[:4000]
    return {
        "title": title,
        "status": "open",
        "severity": severity,
        "feature": feature,
        "command_id": command.command_id,
        "session_id": session.session_id,
        "reproduction_command": command.sanitized_command_line,
        "expected_behavior": expected,
        "actual_behavior": actual,
        "stdout_stderr_excerpt": excerpt,
        "linked_audit_ids": command.linked_audit_ids,
        "suspected_cause": _suspected_cause(command, feedback_tags, all_text),
        "suggested_fix_area": _suggested_fix_area(feature, feedback_tags, all_text),
        "suggested_regression_test": _suggested_regression_test(feature, feedback_tags, command),
    }


def _classify_severity(command: CommandRecord, feedback: list[FeedbackRecord], all_text: str) -> str:
    lowered = all_text.lower()
    if any(pattern in lowered for pattern in P0_PATTERNS):
        return "P0"
    tags = {tag for record in feedback for tag in record.tags}
    if "unsafe_behavior" in tags:
        return "P1"
    if command.exit_code != 0 and any(hint in command.sanitized_command_line for hint in CORE_COMMAND_HINTS):
        return "P1"
    if command.exit_code != 0:
        return "P2"
    if tags.intersection({"hallucination", "wrong_tool", "missing_tool", "bad_routing", "poor_response", "no_citation", "command_failed"}):
        return "P2"
    if tags.intersection({"UX_confusing", "approval_confusing", "docs_gap", "bad_error_message", "command_hung"}):
        return "P3"
    if tags.intersection({"too_slow", "test_gap"}) or any(record.rating is not None and record.rating <= 2 for record in feedback):
        return "P3"
    return "P4"


def _feature_for_command(command_line: str, feedback: list[FeedbackRecord]) -> str:
    parts = command_line.split()
    if len(parts) >= 3 and parts[0] == "python" and parts[1].endswith("smart_agent.py"):
        return parts[2]
    if len(parts) >= 2 and parts[0].endswith("smart_agent.py"):
        return parts[1]
    tags = {tag for record in feedback for tag in record.tags}
    if tags.intersection({"wrong_tool", "missing_tool", "bad_routing"}):
        return "routing"
    if "approval_confusing" in tags:
        return "approvals"
    return "unknown"


def _title_for(command: CommandRecord, tags: list[str], severity: str) -> str:
    if tags:
        label = ", ".join(tags[:3])
        return redact_text(f"{severity} {label} in `{command.sanitized_command_line}`")
    if command.exit_code != 0:
        return redact_text(f"{severity} command failed: `{command.sanitized_command_line}`")
    return redact_text(f"{severity} suspected issue: `{command.sanitized_command_line}`")


def _expected_behavior(command: CommandRecord, feedback: list[FeedbackRecord]) -> str:
    values = [record.expected_behavior for record in feedback if record.expected_behavior]
    if values:
        return redact_text(" | ".join(values))
    if command.exit_code != 0:
        return "Command should complete successfully or return a clear handled error."
    return "Command should match documented behavior without unsafe side effects."


def _actual_behavior(command: CommandRecord, feedback: list[FeedbackRecord]) -> str:
    values = [record.actual_behavior for record in feedback if record.actual_behavior]
    if values:
        return redact_text(" | ".join(values))
    if command.exit_code != 0:
        return redact_text(f"Command exited with {command.exit_code}.")
    if command.notes:
        return redact_text(command.notes)
    return "User feedback marked this command as needing review."


def _suspected_cause(command: CommandRecord, tags: list[str], all_text: str) -> str:
    lowered = all_text.lower()
    if any(pattern in lowered for pattern in P0_PATTERNS):
        return "Possible policy, approval, audit, or data-leak safety regression."
    if {"wrong_tool", "missing_tool", "bad_routing"}.intersection(tags):
        return "Router or tool-selection behavior did not match expected intent."
    if command.exit_code != 0:
        return "Command returned a non-zero exit code or unhandled failure."
    if {"UX_confusing", "approval_confusing", "bad_error_message"}.intersection(tags):
        return "CLI output, approval UX, or error wording appears unclear."
    return "Needs triage from session feedback."


def _suggested_fix_area(feature: str, tags: list[str], all_text: str) -> str:
    lowered = all_text.lower()
    if any(pattern in lowered for pattern in P0_PATTERNS):
        return "safety control plane / redaction / audit"
    if {"wrong_tool", "missing_tool", "bad_routing"}.intersection(tags):
        return "router / tool selection"
    if {"docs_gap", "UX_confusing", "bad_error_message"}.intersection(tags):
        return "docs / CLI UX"
    return f"{feature} workflow"


def _suggested_regression_test(feature: str, tags: list[str], command: CommandRecord) -> str:
    if {"wrong_tool", "missing_tool", "bad_routing"}.intersection(tags):
        return "Add or update router eval coverage for this prompt and expected tool route."
    if "unsafe_behavior" in tags:
        return "Add a safety regression test that asserts policy/audit/redaction gates block this behavior."
    if command.exit_code != 0:
        return f"Add CLI regression coverage for `{command.sanitized_command_line}` under the {feature} test suite."
    return f"Add assertion coverage for the observed {feature} behavior."


def _feedback_is_bug_like(record: FeedbackRecord) -> bool:
    return (
        record.severity in {"medium", "high", "critical"}
        or bool(record.linked_bug_id)
        or any(
            tag in record.tags
            for tag in {
                "poor_response",
                "wrong_tool",
                "missing_tool",
                "bad_routing",
                "hallucination",
                "no_citation",
                "bad_error_message",
                "command_failed",
                "command_hung",
                "approval_confusing",
                "unsafe_behavior",
                "UX_confusing",
                "docs_gap",
                "test_gap",
            }
        )
        or (record.rating is not None and record.rating <= 2)
    )


def _command_summary(command: CommandRecord) -> dict[str, Any]:
    return {
        "command_id": command.command_id,
        "timestamp": command.timestamp,
        "command_line": command.sanitized_command_line,
        "exit_code": command.exit_code,
        "duration_ms": command.duration_ms,
        "tool_calls_detected": command.tool_calls_detected,
        "linked_audit_ids": command.linked_audit_ids,
        "user_rating": command.user_rating,
        "feedback_tags": command.feedback_tags,
        "suspected_bug": command.suspected_bug,
        "stdout_preview": redact_text(command.stdout_preview),
        "stderr_preview": redact_text(command.stderr_preview),
    }


def _repeated_failure_patterns(failed: list[CommandRecord]) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter(_failure_pattern(command) for command in failed)
    return [
        {"pattern": pattern, "count": count}
        for pattern, count in counts.most_common()
        if count > 1
    ]


def _failure_pattern(command: CommandRecord) -> str:
    for line in command.stderr_preview.splitlines():
        if line.strip():
            return redact_text(line.strip())[:120]
    parts = command.sanitized_command_line.split()
    return " ".join(parts[:3]) if parts else "unknown failure"


def _looks_like_tool_failure(command: CommandRecord) -> bool:
    text = f"{command.sanitized_command_line}\n{command.stdout_preview}\n{command.stderr_preview}".lower()
    return bool(command.tool_calls_detected) or any(token in text for token in ("toolbroker", "tool ", "capability", "policyengine"))


def _feedback_flags(feedback: list[FeedbackRecord], tags: set[str], *, include_low_ratings: bool = False) -> list[dict[str, Any]]:
    flags: list[dict[str, Any]] = []
    for record in feedback:
        if tags.intersection(record.tags) or (include_low_ratings and record.rating is not None and record.rating <= 2):
            flags.append(record.to_dict())
    return flags


def _approval_friction(commands: list[CommandRecord], feedback: list[FeedbackRecord]) -> list[dict[str, Any]]:
    flags = _feedback_flags(feedback, {"approval_confusing"})
    for command in commands:
        text = f"{command.stdout_preview}\n{command.stderr_preview}".lower()
        if command.exit_code != 0 and "approval" in text:
            flags.append(_command_summary(command))
    return flags
