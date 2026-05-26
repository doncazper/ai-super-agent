from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from agent.qa.analyzer import rank_failures
from agent.qa.api_models import QAActionEnvelope, QAApiEnvelope, QABugSummary, QACommandCoverage, QAFailureSummary
from agent.qa.bug_generator import create_bugs_from_run
from agent.qa.errors import CommandQAUnsafeError
from agent.qa.logging import read_last_report
from agent.qa.models import utc_now_iso
from agent.qa.progressive import next_batch
from agent.qa.qa_plan import generate_qa_plan
from agent.qa.redaction import redact_text
from agent.qa.regression_generator import create_regression_from_bug, create_regressions_from_run
from agent.qa.runner import run_safe_commands
from agent.qa.self_heal import plan_self_heal
from agent.ui.command_registry import COMMANDS


PERSONAL_DATA_HINTS = ("personal", "calendar", "contact", "email", "message", "sms", "lead", "gmail")
HIGH_RISK_LEVELS = {"HIGH", "CRITICAL", "FORBIDDEN"}


def _redact_value(value: Any) -> Any:
    if isinstance(value, str):
        return redact_text(value, max_chars=2000)
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _redact_value(item) for key, item in value.items()}
    return value


class QAService:
    """Backend service boundary for Command QA data and safe actions."""

    def __init__(self, project_root: str | Path = ".") -> None:
        self.project_root = Path(project_root)

    def _reports_dir(self) -> Path:
        return self.project_root / "reports/qa"

    def _load_qa_records(self) -> list[dict[str, Any]]:
        reports = self._reports_dir()
        records: list[dict[str, Any]] = []
        if not reports.exists():
            return records
        for path in sorted(reports.glob("qa_run_*.jsonl")):
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    records.append(_redact_value(json.loads(line)))
        return records

    def _load_bugs(self) -> list[dict[str, Any]]:
        bugs_dir = self.project_root / "bugs"
        if not bugs_dir.exists():
            return []
        bugs: list[dict[str, Any]] = []
        for path in sorted(bugs_dir.glob("BUG-*.json")):
            try:
                bugs.append(_redact_value(json.loads(path.read_text(encoding="utf-8"))))
            except json.JSONDecodeError:
                continue
        return bugs

    def _open_bugs(self) -> list[dict[str, Any]]:
        return [bug for bug in self._load_bugs() if bug.get("status", "open") == "open"]

    def _envelope(self, data: dict[str, Any], *, status: str = "ok", warnings: list[str] | None = None) -> dict[str, Any]:
        return QAApiEnvelope(
            status=status,
            generated_at=utc_now_iso(),
            read_only=True,
            data=_redact_value(data),
            warnings=warnings or [],
        ).to_dict()

    def _action_envelope(
        self,
        action: str,
        data: dict[str, Any],
        *,
        status: str = "ok",
        safe_only: bool = True,
        warnings: list[str] | None = None,
    ) -> dict[str, Any]:
        return QAActionEnvelope(
            status=status,
            generated_at=utc_now_iso(),
            action=action,
            safe_only=safe_only,
            data=_redact_value(data),
            warnings=warnings or [],
        ).to_dict()

    def get_qa_status(self) -> dict[str, Any]:
        records = self._load_qa_records()
        return self._envelope(
            {
                "report_count": len(list(self._reports_dir().glob("qa_run_*.jsonl"))) if self._reports_dir().exists() else 0,
                "record_count": len(records),
                "bug_count": len(self._load_bugs()),
                "command_count": len(COMMANDS),
                "boundary": "service",
                "note": "Read-only status does not execute commands.",
            }
        )

    def get_latest_run_summary(self) -> dict[str, Any]:
        latest = read_last_report(self.project_root)
        return self._envelope({"latest_run": latest})

    def get_command_coverage(self) -> dict[str, Any]:
        records = self._load_qa_records()
        tested_command_ids = {str(record.get("command_id")) for record in records if record.get("command_id")}
        active_commands = [command for command in COMMANDS if command.status == "active"]
        untested = [command for command in active_commands if command.command_id not in tested_command_ids]
        missing_examples = [command.command_id for command in active_commands if not command.example or "<" in command.example]
        missing_tests = [
            command.command_id
            for command in active_commands
            if "pending" in command.test_coverage.lower() or command.test_coverage.lower() in {"n/a", "none"}
        ]
        coverage = QACommandCoverage(
            total=len(COMMANDS),
            active=len(active_commands),
            tested_by_qa_reports=len(tested_command_ids),
            untested_active=len(untested),
            missing_examples=missing_examples[:50],
            missing_tests=missing_tests[:50],
        )
        return self._envelope(coverage.to_dict())

    def get_failures_by_severity(self) -> dict[str, Any]:
        ranked = rank_failures(self._load_qa_records())
        summary = QAFailureSummary(
            by_severity=dict(Counter(str(record.get("severity", "P4")) for record in ranked)),
            failures=ranked[:25],
        )
        return self._envelope(summary.to_dict())

    def get_failures_by_feature(self) -> dict[str, Any]:
        ranked = rank_failures(self._load_qa_records())
        counts = Counter(str(record.get("feature_id") or record.get("suspected_area") or "unknown") for record in ranked)
        return self._envelope({"by_feature": dict(counts), "failures": ranked[:25]})

    def get_open_bugs(self) -> dict[str, Any]:
        open_bugs = sorted(self._open_bugs(), key=lambda bug: (str(bug.get("severity", "P4")), str(bug.get("bug_id", ""))))[:25]
        return self._envelope(QABugSummary(open_count=len(open_bugs), bugs=open_bugs).to_dict())

    def get_regression_coverage(self) -> dict[str, Any]:
        bugs = self._open_bugs()
        with_regression = [bug for bug in bugs if str(bug.get("suggested_regression_test", "")).startswith("tests/")]
        return self._envelope(
            {
                "open_bug_count": len(bugs),
                "open_bugs_with_regression": len(with_regression),
                "open_bugs_missing_regression": max(0, len(bugs) - len(with_regression)),
            }
        )

    def get_next_safe_batch(self, *, limit: int = 10) -> dict[str, Any]:
        return self._envelope(next_batch(self.project_root, limit=limit))

    def get_next_safe_fix(self) -> dict[str, Any]:
        return self._envelope({"candidate": next_safe_fix_candidate(self._open_bugs())})

    def get_maturity_impact(self) -> dict[str, Any]:
        records = self._load_qa_records()
        failed = sum(1 for record in records if record.get("status") in {"failed", "blocked"})
        tested = {str(record.get("command_id")) for record in records if record.get("command_id")}
        return self._envelope(
            {
                "conservative": True,
                "can_increase_maturity": failed == 0 and bool(tested),
                "reason": "Maturity may increase only after reviewed passing QA evidence; mock/local QA is not live validation.",
                "failed_or_blocked_records": failed,
                "tested_command_count": len(tested),
            }
        )

    def create_plan(
        self,
        *,
        tier: int | None = None,
        group: str | None = None,
        safe_only: bool = True,
        include_non_active: bool = False,
    ) -> dict[str, Any]:
        plan = generate_qa_plan(
            project_root=self.project_root,
            tier=tier,
            group=group,
            safe_only=safe_only,
            include_non_active=include_non_active,
        )
        return self._action_envelope("create_plan", plan.to_dict(), safe_only=safe_only)

    def run_safe_batch(
        self,
        *,
        tier: int = 1,
        group: str | None = None,
        limit: int = 10,
        timeout_seconds: int = 10,
        sandbox: bool = False,
    ) -> dict[str, Any]:
        if tier not in {0, 1, 3}:
            raise CommandQAUnsafeError("QA service action runner supports only Tier 0, Tier 1, and sandboxed Tier 3.")
        if tier == 3 and not sandbox:
            raise CommandQAUnsafeError("Tier 3 command QA requires the disposable sandbox.")
        plan = generate_qa_plan(project_root=self.project_root, tier=tier, group=group, safe_only=tier != 3)
        unsafe = [command for command in plan.commands if self._is_forbidden_for_action(command.to_dict())]
        if unsafe:
            raise CommandQAUnsafeError(f"QA service blocked unsafe command from batch: {unsafe[0].command_id}")
        result = run_safe_commands(
            project_root=self.project_root,
            tier=tier,
            group=group,
            safe_only=True,
            timeout_seconds=timeout_seconds,
            limit=limit,
            sandbox=sandbox,
        )
        return self._action_envelope("run_safe_batch", result, safe_only=True)

    def create_bug_from_run(self, *, run_id: str | None = None, report_id: str | None = None) -> dict[str, Any]:
        return self._action_envelope(
            "create_bug_from_run",
            create_bugs_from_run(self.project_root, run_id=run_id, report_id=report_id),
            safe_only=True,
        )

    def create_regression_from_bug(self, *, bug_id: str) -> dict[str, Any]:
        return self._action_envelope("create_regression_from_bug", create_regression_from_bug(self.project_root, bug_id=bug_id))

    def create_regression_from_run(self, *, run_id: str) -> dict[str, Any]:
        return self._action_envelope("create_regression_from_run", create_regressions_from_run(self.project_root, run_id=run_id))

    def create_self_heal_plan(self, *, bug_id: str | None = None) -> dict[str, Any]:
        return self._action_envelope("create_self_heal_plan", plan_self_heal(self.project_root, bug_id=bug_id), safe_only=True)

    def _is_forbidden_for_action(self, command: dict[str, Any]) -> bool:
        risk = str(command.get("risk_level", "")).upper()
        if risk in HIGH_RISK_LEVELS:
            return True
        text = " ".join(str(command.get(key, "")) for key in ("command", "group", "skip_reason")).lower()
        return any(hint in text for hint in PERSONAL_DATA_HINTS)


def next_safe_fix_candidate(open_bugs: list[dict[str, Any]]) -> dict[str, Any]:
    severity_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}
    candidates = [
        bug
        for bug in open_bugs
        if bug.get("severity") in {"P2", "P3", "P4"}
        and str(bug.get("suggested_regression_test", "")).startswith("tests/")
    ]
    if not candidates:
        return {"status": "none", "reason": "No open P2/P3/P4 bug with linked regression test found."}
    selected = sorted(candidates, key=lambda bug: (severity_order.get(str(bug.get("severity", "P4")), 4), bug.get("bug_id", "")))[0]
    return {
        "status": "candidate",
        "bug_id": selected.get("bug_id", ""),
        "severity": selected.get("severity", ""),
        "reason": "Open low/medium-risk bug with regression evidence.",
    }
