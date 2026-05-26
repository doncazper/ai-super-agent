from __future__ import annotations

import json
from pathlib import Path

from agent.brain.benchmark import BrainBenchmarkOptions, run_benchmark
from agent.brain.evals import BrainEvalOptions, run_brain_evals
from agent.brain.health import BrainHealthOptions, collect_health
from agent.ui import cli_commands


def test_health_report_with_mock_provider() -> None:
    report = collect_health(BrainHealthOptions(provider_id="mock"))

    assert report["status"] == "unknown_provider"
    assert report["no_model_generation"] is True
    assert report["no_tool_execution"] is True
    assert report["personal_data_used"] is False


def test_benchmark_with_mock_provider(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    report = run_benchmark(BrainBenchmarkOptions(safe=True))

    assert report["status"] == "ok"
    assert report["personal_data_used"] is False
    assert report["high_risk_tools_used"] is False
    assert report["results"][0]["provider"] == "mock"
    assert report["results"][0]["status"] == "pass"
    assert Path(str(report["report_path"])).exists()


def test_eval_report_generated(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    report = run_brain_evals(BrainEvalOptions(safe=True))

    assert report["status"] == "ok"
    assert report["summary"]["pass"] >= 3
    assert report["personal_data_used"] is False
    assert Path(str(report["report_path"])).exists()


def test_unavailable_provider_skipped(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    report = run_benchmark(BrainBenchmarkOptions(provider_id="mlx", safe=True, live=False))

    assert report["results"][0]["status"] == "skip"
    assert report["results"][0]["reason"] == "unknown_provider"


def test_no_tools_eval_checks_no_tools(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    report = run_brain_evals(BrainEvalOptions(safe=True))
    no_tool = next(result for result in report["results"] if result["case_id"] == "no_tool_chat")

    assert no_tool["status"] == "pass"


def test_tool_call_eval_uses_mock_safe_tool(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    report = run_brain_evals(BrainEvalOptions(safe=True))
    tool_case = next(result for result in report["results"] if result["case_id"] == "safe_tool_call")

    assert tool_case["status"] == "pass"
    assert tool_case["safe_tool_only"] is True


def test_brain_benchmark_eval_report_cli(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    assert cli_commands.dispatch_cli(["brain", "benchmark", "--safe"]) == 0
    benchmark = json.loads(capsys.readouterr().out)
    assert benchmark["report_type"] == "brain_benchmark"

    assert cli_commands.dispatch_cli(["brain", "eval", "--safe"]) == 0
    eval_report = json.loads(capsys.readouterr().out)
    assert eval_report["report_type"] == "brain_eval"

    assert cli_commands.dispatch_cli(["brain", "report"]) == 0
    last = json.loads(capsys.readouterr().out)
    assert last["report_type"] in {"brain_benchmark", "brain_eval"}
