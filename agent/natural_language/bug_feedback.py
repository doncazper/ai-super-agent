from __future__ import annotations

import json
import shlex
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from agent.session_logs.models import CommandRecord, FeedbackRecord, utc_now_iso
from agent.session_logs.redaction import redact_text
from agent.session_logs.review import BugRecord, BugStore
from agent.session_logs.store import SessionLogStore


NL_FEEDBACK_TAGS = {
    "misunderstood_intent",
    "wrong_command_suggested",
    "should_have_clarified",
    "should_have_denied",
    "should_have_required_approval",
    "executed_when_should_not",
    "failed_to_find_command",
    "poor_natural_language_answer",
}


@dataclass(frozen=True)
class NaturalLanguageRegressionResult:
    bug_id: str
    status: str
    fixture_path: str
    case_id: str
    redaction_status: str = "redacted"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def create_nl_bug_record(
    *,
    project_root: str | Path,
    feedback: FeedbackRecord,
    expected_intent: str,
) -> BugRecord:
    root = Path(project_root)
    store = SessionLogStore(project_root=root)
    command = _find_command(store, feedback.session_id, feedback.command_id)
    bug_store = BugStore(project_root=root)
    bug_id = bug_store.next_bug_id()
    now = utc_now_iso()
    tags = ", ".join(feedback.tags)
    title = f"Natural-language command misunderstanding: {expected_intent or 'needs review'}"
    expected = feedback.expected_behavior or f"Expected natural-language intent: {expected_intent}\nExpected safe behavior: no silent execution."
    actual = feedback.actual_behavior or feedback.reason or feedback.user_note or "User reported natural-language misunderstanding."
    record = BugRecord(
        bug_id=bug_id,
        title=redact_text(title),
        status="open",
        severity=_severity_for_feedback(feedback),
        feature="natural_language",
        command_id=feedback.command_id,
        session_id=feedback.session_id,
        reproduction_command=redact_text(command.sanitized_command_line if command else ""),
        expected_behavior=redact_text(expected),
        actual_behavior=redact_text(actual),
        stdout_stderr_excerpt=redact_text(_command_excerpt(command)),
        linked_audit_ids=list(command.linked_audit_ids if command else []),
        suspected_cause=redact_text(f"NL feedback tags: {tags}"),
        suggested_fix_area="agent.natural_language parser/router/preflight or command intent index",
        suggested_regression_test="Add a sanitized natural-language eval case with expected intent and safety outcome.",
        created_at=now,
        last_updated=now,
    )
    return bug_store.save(record)


def create_nl_regression_fixture(
    bug_id: str,
    *,
    project_root: str | Path = ".",
    fixture_path: str | Path = "eval_cases/natural_language/regressions.json",
) -> NaturalLanguageRegressionResult:
    root = Path(project_root)
    bug = BugStore(project_root=root).get(bug_id)
    if bug is None:
        raise ValueError("bug not found")
    if bug.feature != "natural_language":
        raise ValueError("bug is not a natural-language bug")

    path = Path(fixture_path)
    if not path.is_absolute():
        path = root / path
    _ensure_inside(root, path)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = _load_fixture_payload(path)
    case = _case_from_bug(bug)
    cases = payload.setdefault("cases", [])
    if not isinstance(cases, list):
        raise ValueError("natural-language regression fixture must contain a cases list")
    cases[:] = [item for item in cases if not isinstance(item, dict) or item.get("id") != case["id"]]
    cases.append(case)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    bug.regression_test_path = path.relative_to(root).as_posix()
    if bug.regression_test_path not in bug.linked_tests:
        bug.linked_tests.append(bug.regression_test_path)
    bug.status = "regression_added"
    BugStore(project_root=root).save(bug)

    return NaturalLanguageRegressionResult(
        bug_id=bug.bug_id,
        status="created",
        fixture_path=bug.regression_test_path,
        case_id=str(case["id"]),
    )


def list_nl_regressions(
    *,
    project_root: str | Path = ".",
    fixture_path: str | Path = "eval_cases/natural_language/regressions.json",
) -> dict[str, Any]:
    root = Path(project_root)
    path = Path(fixture_path)
    if not path.is_absolute():
        path = root / path
    if not path.exists():
        return {"status": "ok", "fixture_path": path.relative_to(root).as_posix(), "count": 0, "cases": []}
    payload = _load_fixture_payload(path)
    cases = [case for case in payload.get("cases", []) if isinstance(case, dict)]
    return {
        "status": "ok",
        "fixture_path": path.relative_to(root).as_posix(),
        "count": len(cases),
        "cases": cases,
    }


def _find_command(store: SessionLogStore, session_id: str, command_id: str) -> CommandRecord | None:
    for command in store.load_commands(session_id):
        if command.command_id == command_id:
            return command
    return None


def _command_excerpt(command: CommandRecord | None) -> str:
    if command is None:
        return ""
    return "\n".join(value for value in (command.stdout_preview, command.stderr_preview) if value)


def _severity_for_feedback(feedback: FeedbackRecord) -> str:
    if "executed_when_should_not" in feedback.tags:
        return "P1"
    if feedback.severity in {"high", "critical"}:
        return "P2"
    return "P3"


def _case_from_bug(bug: BugRecord) -> dict[str, Any]:
    input_text = _extract_nl_input(bug.reproduction_command)
    expected_intent = _extract_expected_value(bug.expected_behavior, "Expected natural-language intent") or "needs_review"
    expected_safety = _extract_expected_value(bug.expected_behavior, "Expected safety outcome") or _infer_safety_outcome(bug)
    return {
        "id": f"nl.regression.{bug.bug_id.lower()}",
        "category": "natural_language",
        "title": redact_text(bug.title),
        "input_text": input_text,
        "expected_intent": expected_intent,
        "expected_safety_outcome": expected_safety,
        "expected_command_group": "",
        "should_execute": False,
        "should_clarify": "should_have_clarified" in bug.suspected_cause,
        "should_require_approval": "should_have_required_approval" in bug.suspected_cause,
        "should_deny": "should_have_denied" in bug.suspected_cause or "executed_when_should_not" in bug.suspected_cause,
        "risk_level": "LOW",
        "personal_data": False,
        "live": False,
        "tags": ["natural_language", "regression", bug.bug_id],
        "notes": redact_text(f"Generated from {bug.bug_id}. Review before promoting from skipped/fixture evidence."),
    }


def _extract_nl_input(command_line: str) -> str:
    redacted = redact_text(command_line)
    try:
        parts = shlex.split(redacted)
    except ValueError:
        return redacted[:400]
    if "smart_agent.py" in [Path(part).name for part in parts]:
        script_index = next(index for index, part in enumerate(parts) if Path(part).name == "smart_agent.py")
        args = parts[script_index + 1 :]
    else:
        args = parts
    if not args:
        return redacted[:400]
    if args[0] == "ask":
        return redact_text(" ".join(arg for arg in args[1:] if arg != "--no-tools"))[:400]
    if args[0] == "nl":
        remaining = args[1:]
        if remaining and remaining[0] == "--no-tools":
            remaining = remaining[1:]
        if remaining and remaining[0] in {"preflight", "explain", "suggest"}:
            remaining = remaining[1:]
        return redact_text(" ".join(remaining))[:400]
    return redacted[:400]


def _extract_expected_value(text: str, label: str) -> str:
    prefix = f"{label}:"
    for line in text.splitlines():
        if line.startswith(prefix):
            return redact_text(line.removeprefix(prefix).strip())[:120]
    return ""


def _infer_safety_outcome(bug: BugRecord) -> str:
    text = f"{bug.expected_behavior}\n{bug.actual_behavior}\n{bug.suspected_cause}".lower()
    if "deny" in text or "executed_when_should_not" in text:
        return "deny"
    if "approval" in text:
        return "requires_approval"
    if "clarif" in text:
        return "clarify"
    return "needs_review"


def _load_fixture_payload(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"category": "natural_language", "cases": []}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("natural-language regression fixture must be a JSON object")
    payload.setdefault("category", "natural_language")
    payload.setdefault("cases", [])
    return payload


def _ensure_inside(root: Path, path: Path) -> None:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError("fixture path must stay inside the project root") from exc
