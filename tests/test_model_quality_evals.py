from __future__ import annotations

from pathlib import Path

import pytest

from agent.config.runtime import RuntimeConfig
from agent.core.router import Router
from agent.ui import cli_commands
from agent.ui.model_quality import (
    list_models,
    load_quality_cases,
    read_prompt_quality_report,
    run_model_benchmark,
    run_prompt_eval,
    run_router_eval,
)


pytestmark = pytest.mark.unit


def runtime(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        lmstudio_model="",
        audit_log_path=str(tmp_path / "audit.jsonl"),
        capabilities_path="config/capabilities.yaml",
    )


def test_router_eval_works(tmp_path) -> None:
    report = run_router_eval(
        runtime=runtime(tmp_path),
        report_path=tmp_path / "docs" / "PROMPT_QUALITY_REPORT.md",
        results_path=tmp_path / "logs" / "quality.json",
        reports_dir=tmp_path / "reports",
    )

    by_name = {check["name"]: check for check in report["checks"]}
    assert report["status"] == "ok"
    assert by_name["quality.weather_routing"]["status"] == "pass"
    assert by_name["quality.web_current_info_routing"]["actual_tools"] == ["web.fetch_url", "web.search"]


def test_prompt_eval_works_and_handles_injection(tmp_path) -> None:
    report = run_prompt_eval(
        runtime=runtime(tmp_path),
        report_path=tmp_path / "docs" / "PROMPT_QUALITY_REPORT.md",
        results_path=tmp_path / "logs" / "quality.json",
        reports_dir=tmp_path / "reports",
    )

    by_name = {check["name"]: check for check in report["checks"]}
    assert report["status"] == "ok"
    assert by_name["quality.prompt_system_tool_restraint"]["status"] == "pass"
    assert by_name["quality.prompt_injection_wrapper"]["status"] == "pass"
    assert "disable audit logs" not in by_name["quality.prompt_injection_wrapper"]["prompt_excerpt"].splitlines()[0].lower()


def test_no_tool_cases_attach_no_tools(tmp_path) -> None:
    report = run_model_benchmark(
        safe=True,
        runtime=runtime(tmp_path),
        report_path=tmp_path / "docs" / "PROMPT_QUALITY_REPORT.md",
        results_path=tmp_path / "logs" / "quality.json",
        reports_dir=tmp_path / "reports",
    )

    by_name = {check["name"]: check for check in report["checks"]}
    assert by_name["quality.normal_chat_no_tools"]["status"] == "pass"
    assert by_name["quality.normal_chat_no_tools"]["actual_tools"] == []


def test_personal_data_request_does_not_auto_execute() -> None:
    route = Router().route("Read my latest email and summarize it")

    assert route.name == "chat.personal_data_approval_required"
    assert route.use_tools is False
    assert route.tool_names == set()
    assert route.metadata["approval_required"] is True


def test_model_benchmark_policy_gates_personal_data(tmp_path) -> None:
    report = run_model_benchmark(
        safe=True,
        runtime=runtime(tmp_path),
        report_path=tmp_path / "docs" / "PROMPT_QUALITY_REPORT.md",
        results_path=tmp_path / "logs" / "quality.json",
        reports_dir=tmp_path / "reports",
    )

    by_name = {check["name"]: check for check in report["checks"]}
    assert by_name["quality.personal_data_no_auto_execute"]["actual_use_tools"] is False
    assert by_name["quality.personal_data_no_auto_execute.policy"]["actual_policy_decision"] == "DENY"
    assert by_name["quality.send_request_no_auto_execute.policy"]["actual_policy_decision"] == "DENY"
    assert report["personal_data_accessed"] is False


def test_report_generated(tmp_path) -> None:
    report_path = tmp_path / "docs" / "PROMPT_QUALITY_REPORT.md"
    results_path = tmp_path / "logs" / "quality.json"
    report = run_model_benchmark(
        safe=True,
        runtime=runtime(tmp_path),
        report_path=report_path,
        results_path=results_path,
        reports_dir=tmp_path / "reports",
    )

    assert report["report_path"] == str(report_path)
    assert report_path.exists()
    assert results_path.exists()
    assert list((tmp_path / "reports").glob("model-quality-*.json"))
    assert "Model Router and Prompt Quality Report" in read_prompt_quality_report(report_path)


def test_models_list_does_not_send_prompts(tmp_path) -> None:
    listed = list_models(runtime=runtime(tmp_path))

    assert listed["status"] == "ok"
    assert listed["prompt_sent"] is False
    assert listed["live_requested"] is False


def test_quality_cases_load() -> None:
    cases = load_quality_cases()
    by_id = {case.case_id: case for case in cases}

    assert "quality.file_document_url_routing" in by_id
    assert "quality.live_no_tool_answer_quality" in by_id


def test_model_router_prompt_cli_dispatch(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        cli_commands,
        "run_model_benchmark",
        lambda **kwargs: {"status": "ok", "run_id": "bench", "suite": "model_benchmark", "summary": {"pass": 1, "fail": 0, "skipped": 0}, "quality_score": 100, "checks": [], "report_path": "docs/PROMPT_QUALITY_REPORT.md"},
    )
    monkeypatch.setattr(
        cli_commands,
        "run_router_eval",
        lambda: {"status": "ok", "run_id": "router", "suite": "router_eval", "summary": {"pass": 1, "fail": 0, "skipped": 0}, "quality_score": 100, "checks": [], "report_path": "docs/PROMPT_QUALITY_REPORT.md"},
    )
    monkeypatch.setattr(
        cli_commands,
        "run_prompt_eval",
        lambda: {"status": "ok", "run_id": "prompt", "suite": "prompt_eval", "summary": {"pass": 1, "fail": 0, "skipped": 0}, "quality_score": 100, "checks": [], "report_path": "docs/PROMPT_QUALITY_REPORT.md"},
    )

    assert cli_commands.dispatch_cli(["models", "benchmark", "--safe"]) == 0
    assert "Run: bench" in capsys.readouterr().out
    assert cli_commands.dispatch_cli(["router", "eval"]) == 0
    assert "Run: router" in capsys.readouterr().out
    assert cli_commands.dispatch_cli(["prompts", "eval"]) == 0
    assert "Run: prompt" in capsys.readouterr().out
