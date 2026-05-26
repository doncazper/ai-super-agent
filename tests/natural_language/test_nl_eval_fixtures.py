from __future__ import annotations

from agent.config.runtime import RuntimeConfig
from agent.ui.command_registry import get_command
from agent.ui.evals import EvalOptions, load_eval_cases, run_eval


def _runtime(tmp_path) -> RuntimeConfig:
    return RuntimeConfig(
        lmstudio_model="fake-model",
        audit_log_path=str(tmp_path / "audit.jsonl"),
        capabilities_path="config/capabilities.yaml",
    )


def _options(tmp_path, **kwargs) -> EvalOptions:
    return EvalOptions(
        report_path=tmp_path / "docs" / "EVAL_REPORT.md",
        results_path=tmp_path / "logs" / "eval_results.json",
        reports_dir=tmp_path / "reports" / "evals",
        **kwargs,
    )


def test_nl_eval_fixtures_load() -> None:
    cases = [case for case in load_eval_cases() if case.category == "natural_language"]
    assert len(cases) >= 15
    categories = {tag for case in cases for tag in case.tags}
    for expected in {
        "weather",
        "web",
        "news",
        "reddit",
        "help",
        "doctor",
        "memory",
        "workspace",
        "prompt_tracker",
        "session",
        "ambiguous",
        "personal_data",
        "send",
        "unsupported",
        "legacy",
    }:
        assert expected in categories


def test_nl_eval_safe_cases_pass(tmp_path) -> None:
    report = run_eval(_options(tmp_path, natural_language=True), runtime=_runtime(tmp_path))
    checks = {check["name"]: check for check in report["checks"]}
    assert report["status"] == "ok"
    assert checks["nl.weather.current_phoenix"]["status"] == "pass"
    assert checks["nl.help.commands_memory"]["status"] == "pass"
    assert checks["nl.session.bug_review"]["status"] == "pass"


def test_nl_eval_risky_cases_do_not_execute(tmp_path) -> None:
    report = run_eval(_options(tmp_path, natural_language=True), runtime=_runtime(tmp_path))
    checks = {check["name"]: check for check in report["checks"]}
    for case_id in ("nl.personal.email_read", "nl.send.email"):
        details = checks[case_id]["details"]
        assert checks[case_id]["status"] == "pass"
        assert details["safe_to_execute"] is False
        assert details["approval_required"] is True
        assert details["audit_preview"]["tools_called"] == []
        assert details["audit_preview"]["commands_executed"] == []


def test_nl_eval_ambiguous_cases_clarify(tmp_path) -> None:
    report = run_eval(_options(tmp_path, natural_language=True), runtime=_runtime(tmp_path))
    checks = {check["name"]: check for check in report["checks"]}
    assert checks["nl.ambiguous.fix"]["details"]["clarification_required"] is True
    assert checks["nl.doctor.ambiguous"]["details"]["clarification_required"] is True


def test_nl_eval_unsupported_cases_report_help(tmp_path) -> None:
    report = run_eval(_options(tmp_path, natural_language=True), runtime=_runtime(tmp_path))
    checks = {check["name"]: check for check in report["checks"]}
    for case_id in ("nl.unsupported.frobnicate", "nl.news.unsupported"):
        details = checks[case_id]["details"]
        assert checks[case_id]["status"] == "pass"
        assert details["safe_to_execute"] is False
        assert "deterministic intent or exact command" in details["missing_requirements"]


def test_nl_eval_command_registry_entries_exist() -> None:
    assert get_command("CMD-EVAL-017") is not None
    assert get_command("CMD-EVAL-018") is not None
