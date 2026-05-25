from __future__ import annotations

import json
from pathlib import Path

from agent.session_logs.models import CommandRecord, FeedbackRecord, SessionRecord, utc_now_iso
from agent.session_logs.review import BugStore
from agent.session_logs.store import SessionLogStore
from agent.ui import cli_commands
from agent.ui.product_quality import build_quality_dashboard, quality_next


ROOT = Path(__file__).resolve().parents[1]


def test_quality_status_works(capsys) -> None:
    assert cli_commands.dispatch_cli(["quality", "status"], project_root=ROOT) == 0
    output = capsys.readouterr().out
    assert "Product Quality Dashboard v1" in output
    assert "Read-only: True" in output


def test_open_bugs_counted_and_p0_prioritized(tmp_path: Path) -> None:
    _write_quality_docs(tmp_path)
    store = BugStore(project_root=tmp_path)
    store.create_bug({"title": "P2 docs issue", "severity": "P2", "feature": "docs"})
    store.create_bug({"title": "P0 policy bypass", "severity": "P0", "feature": "safety"})
    report = build_quality_dashboard(project_root=tmp_path)

    assert report["open_bugs_by_severity"]["P0"] == 1
    assert report["open_bugs_by_severity"]["P2"] == 1
    assert report["next_recommended_bug"]["severity"] == "P0"
    assert quality_next(project_root=tmp_path)["priority"] == "bug"


def test_features_lacking_live_validation_listed(tmp_path: Path) -> None:
    _write_quality_docs(tmp_path)
    report = build_quality_dashboard(project_root=tmp_path)

    names = {item["feature"] for item in report["features"]["lacking_live_validation"]}
    assert "Calendar read-only" in names
    assert report["features"]["most_mature"][0]["feature"] == "ToolBroker / PolicyEngine / AuditLogger"
    assert report["features"]["least_mature"][0]["feature"] == "Native Skills Program foundation"


def test_last_session_and_feedback_are_redacted(tmp_path: Path) -> None:
    _write_quality_docs(tmp_path)
    session = _write_session_with_feedback(tmp_path)

    report = build_quality_dashboard(project_root=tmp_path)

    assert report["last_session"]["session_id"] == session.session_id
    assert report["last_session_result"]["status"] == "fail"
    feedback = report["recent_feedback"][0]
    assert "sk-secret-value" not in feedback["note"]
    assert "[REDACTED]" in feedback["note"]


def test_regressions_lists_bugs_without_linked_tests(tmp_path: Path) -> None:
    _write_quality_docs(tmp_path)
    store = BugStore(project_root=tmp_path)
    missing = store.create_bug({"title": "missing regression", "severity": "P1", "feature": "weather"})
    linked = store.create_bug({"title": "has regression", "severity": "P1", "feature": "web"})
    linked.linked_tests.append("tests/regressions/test_bug_0002.py")
    store.save(linked)

    report = build_quality_dashboard(project_root=tmp_path)

    ids = {bug["bug_id"] for bug in report["regressions"]["bugs_lacking_regression_tests"]}
    assert missing.bug_id in ids
    assert linked.bug_id not in ids


def test_quality_dashboard_is_read_only_when_no_artifact_dirs(tmp_path: Path) -> None:
    _write_quality_docs(tmp_path)
    before = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))
    report = build_quality_dashboard(project_root=tmp_path)
    after = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))

    assert report["read_only"] is True
    assert before == after


def test_quality_subcommands_return_json(capsys) -> None:
    for command in ("sessions", "bugs", "regressions", "features", "next"):
        assert cli_commands.dispatch_cli(["quality", command], project_root=ROOT) == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload


def _write_quality_docs(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir(parents=True)
    (docs / "PROJECT_STATE.md").write_text("## Last Test Result\nFull suite: 656 passed in 21.58s.\n", encoding="utf-8")
    (docs / "RELEASE_CHECKLIST.md").write_text("- [x] Tests pass\n", encoding="utf-8")
    (docs / "COMPLETION_REPORT.md").write_text("Release gate passed. 0 failed.\n", encoding="utf-8")
    (docs / "FEATURE_MATURITY.md").write_text(
        """# Feature Maturity

| Feature | Category | Maturity Level | Readiness Score | Prompt / Iteration Count | Design Completeness | Implementation Completeness | Test Coverage | Policy/Audit Status | Security Hardening Status | Live Validation Status | UX/Docs Status | Known Limitations | Next Work Needed |
|---|---|---:|---:|---:|---|---|---|---|---|---|---|---|---|
| ToolBroker / PolicyEngine / AuditLogger | Safety control plane | 8 Mature Pattern | 95 | 10 | Complete | Complete | Broad regression tests | Complete | Hardened | Local validation complete | Complete | none | Keep as pattern |
| Calendar read-only | Personal connector | 5 Hardened | 78 | 6 | Complete | Complete | Approval tests | Complete | Hardened | Needs explicit live local smoke with user approval | Docs exist | Not live-validated | Run live smoke |
| Native Skills Program foundation | Native skills governance | 2 Scaffolded | 48 | 1 | Complete | Docs only | Docs validation | No runtime | Supply chain risks documented | Not applicable | Docs exist | foundation only | Build vetter |
""",
        encoding="utf-8",
    )
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "eval_results.json").write_text(
        json.dumps({"checks": [{"status": "pass"}, {"status": "skipped"}]}),
        encoding="utf-8",
    )


def _write_session_with_feedback(tmp_path: Path) -> SessionRecord:
    store = SessionLogStore(tmp_path / "reports" / "sessions", project_root=tmp_path)
    session = SessionRecord.start(
        name="quality-test",
        git_commit="abc123",
        branch="test",
        model="none",
        base_url="http://localhost",
        config_summary={},
    )
    store.start(session)
    command = CommandRecord(
        command_id="cmd_quality",
        timestamp=utc_now_iso(),
        command_line="python smart_agent.py doctor",
        sanitized_command_line="python smart_agent.py doctor",
        exit_code=1,
        duration_ms=5,
        stdout_preview="",
        stderr_preview="boom",
    )
    store.append_command(session.session_id, command)
    feedback = FeedbackRecord(
        feedback_id="fb_quality",
        session_id=session.session_id,
        command_id=command.command_id,
        timestamp=utc_now_iso(),
        rating=1,
        tags=["command_failed"],
        severity="medium",
        user_note="failed with API_KEY=sk-secret-value",
    )
    store.append_feedback(feedback)
    store.end_active()
    return store.get(session.session_id) or session
