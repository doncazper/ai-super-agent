from __future__ import annotations

import json

import pytest

from agent.config.runtime import RuntimeConfig
from agent.tools.registry import default_registry
from agent.tools.web.fetch import WebResponse
from agent.ui import cli_commands
from agent.ui.evals import EvalOptions, eval_exit_code, list_evals, load_eval_cases, read_eval_report, run_eval


pytestmark = pytest.mark.unit


class FakeLMStudioClient:
    def __init__(self, config) -> None:
        self.config = config
        self.calls = 0

    def chat(self, messages, *, tools=None):
        self.calls += 1
        if tools:
            has_tool_result = any(message.get("role") == "tool" for message in messages)
            if not has_tool_result:
                return {
                    "choices": [
                        {
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [
                                    {
                                        "id": "call_time",
                                        "type": "function",
                                        "function": {"name": "time.get_current_time", "arguments": "{}"},
                                    }
                                ],
                            },
                        }
                    ]
                }
            return {"choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": "It is now."}}]}
        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"role": "assistant", "content": "RCS is carrier messaging; iMessage is Apple messaging."},
                }
            ]
        }


class StaticSearchProvider:
    name = "static"

    def is_configured(self) -> bool:
        return True

    def search(self, query, max_results, locale=None, safe_search=True):
        return [
            {
                "title": "Example Domain",
                "url": "https://example.com/",
                "snippet": "Example Domain is a safe test page.",
                "source": "example.com",
                "trust_level": "UNTRUSTED_WEB",
            }
        ][:max_results]


class BrokenSearchProvider(StaticSearchProvider):
    name = "broken"

    def search(self, query, max_results, locale=None, safe_search=True):
        raise RuntimeError("provider exploded")


class StaticWeatherProvider:
    name = "static-weather"

    def is_configured(self) -> bool:
        return True

    def current_weather(self, location: str, units: str, locale: str | None = None):
        return {
            "status": "ok",
            "provider": self.name,
            "location": location,
            "units": units,
            "trust_level": "UNTRUSTED_WEB",
            "retrieved_at": "2026-05-22T12:00:00Z",
            "current": {"temperature": 80, "temperature_unit": "F", "condition": "clear"},
        }

    def forecast(self, location: str, days: int, units: str, locale: str | None = None, include_hourly: bool = False):
        return {
            "status": "ok",
            "provider": self.name,
            "location": location,
            "units": units,
            "trust_level": "UNTRUSTED_WEB",
            "retrieved_at": "2026-05-22T12:00:00Z",
            "forecast": [{"date": "2026-05-22", "temperature_max": 90, "temperature_min": 70}],
        }

    def alerts(self, location: str, locale: str | None = None):
        return {"status": "ok", "provider": self.name, "alerts": []}


def fake_fetcher(url: str, timeout_seconds: int) -> WebResponse:
    return WebResponse(
        url=url,
        status_code=200,
        headers={"content-type": "text/html"},
        text="<html><title>Example</title><body><p>Example Domain</p></body></html>",
    )


def runtime(tmp_path, *, model: str = "fake-model") -> RuntimeConfig:
    return RuntimeConfig(
        lmstudio_model=model,
        audit_log_path=str(tmp_path / "audit.jsonl"),
        capabilities_path="config/capabilities.yaml",
    )


def registry(tmp_path, *, search_provider=None, weather_provider=None):
    return default_registry(
        project_root=tmp_path,
        memory_path=tmp_path / "memory.sqlite3",
        web_search_provider=search_provider or StaticSearchProvider(),
        web_fetcher=fake_fetcher,
        weather_provider=weather_provider or StaticWeatherProvider(),
    )


def options(tmp_path, **kwargs) -> EvalOptions:
    return EvalOptions(
        report_path=tmp_path / "docs" / "EVAL_REPORT.md",
        results_path=tmp_path / "logs" / "eval_results.json",
        reports_dir=tmp_path / "reports" / "evals",
        **kwargs,
    )


def test_eval_list_works() -> None:
    listed = list_evals()

    names = {item["name"] for item in listed["evals"]}
    assert listed["status"] == "ok"
    assert listed["case_count"] > 0
    assert "lmstudio.no_tool_chat" in names
    assert "routing.intent_cases" in names
    assert "calendar.read" in names


def test_golden_eval_cases_load_from_data_files() -> None:
    cases = load_eval_cases()

    by_id = {case.case_id: case for case in cases}
    assert "routing.weather_current_phoenix" in by_id
    assert "policy.unknown_denied" in by_id
    assert "prompt_injection.web_ignore_instructions" in by_id


def test_safe_evals_run_with_mocks(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEB_ACCESS_ENABLED", "true")
    monkeypatch.setenv("WEATHER_CACHE_PATH", str(tmp_path / "weather_cache.json"))

    report = run_eval(
        options(tmp_path, safe=True),
        runtime=runtime(tmp_path),
        registry=registry(tmp_path),
        client_factory=FakeLMStudioClient,
    )

    by_name = {check["name"]: check for check in report["checks"]}
    assert report["status"] == "ok"
    assert report["quality_score"] == 100.0
    assert by_name["routing.weather_current_phoenix"]["status"] == "pass"
    assert by_name["policy.unknown_denied"]["status"] == "pass"
    assert by_name["tools.unknown_tool_denied"]["status"] == "pass"
    assert by_name["prompt_injection.web_ignore_instructions"]["status"] == "pass"
    assert by_name["workflows.file_write_preflight"]["status"] == "pass"
    assert by_name["lmstudio.no_tool_chat"]["status"] == "pass"
    assert by_name["tool.time_direct"]["status"] == "pass"
    assert by_name["weather.current"]["status"] == "pass"
    assert by_name["web.fetch_url"]["status"] == "pass"
    assert by_name["workspace.read_write"]["status"] == "pass"
    assert by_name["memory.add_search_delete"]["status"] == "pass"
    assert by_name["dry_run.preflight"]["status"] == "pass"
    assert by_name["connectors.doctor"]["status"] == "pass"


def test_personal_evals_skipped_by_default(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEB_ACCESS_ENABLED", "true")

    report = run_eval(
        options(tmp_path, safe=True),
        runtime=runtime(tmp_path),
        registry=registry(tmp_path),
        client_factory=FakeLMStudioClient,
    )

    personal = [check for check in report["checks"] if check["personal_data"]]
    assert personal
    assert all(check["status"] == "skipped" for check in personal)


def test_eval_report_produced(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEB_ACCESS_ENABLED", "true")
    eval_options = options(tmp_path, workspace=True)

    report = run_eval(eval_options, runtime=runtime(tmp_path), registry=registry(tmp_path), client_factory=FakeLMStudioClient)

    markdown = read_eval_report(eval_options.report_path)
    assert report["report_path"] == str(eval_options.report_path)
    assert (tmp_path / "docs" / "EVAL_REPORT.md").exists()
    assert (tmp_path / "logs" / "eval_results.json").exists()
    assert list((tmp_path / "reports" / "evals").glob("eval-*.json"))
    assert "## Scorecards" in markdown
    assert "workspace.read_write" in markdown


def test_policy_eval_catches_denial_behavior(tmp_path) -> None:
    report = run_eval(options(tmp_path, policy=True), runtime=runtime(tmp_path), registry=registry(tmp_path), client_factory=FakeLMStudioClient)

    by_name = {check["name"]: check for check in report["checks"]}
    assert by_name["policy.unknown_denied"]["status"] == "pass"
    assert by_name["policy.calendar_read_disabled_or_approval"]["status"] == "pass"
    assert by_name["policy.email_send_per_action"]["status"] == "pass"


def test_prompt_injection_evals_pass(tmp_path) -> None:
    report = run_eval(
        options(tmp_path, safe=False, workflows=True),
        runtime=runtime(tmp_path),
        registry=registry(tmp_path),
        client_factory=FakeLMStudioClient,
    )

    by_name = {check["name"]: check for check in report["checks"]}
    assert by_name["workflows.file_write_preflight"]["status"] == "pass"

    report = run_eval(
        options(tmp_path, safe=True),
        runtime=runtime(tmp_path),
        registry=registry(tmp_path),
        client_factory=FakeLMStudioClient,
    )
    by_name = {check["name"]: check for check in report["checks"]}
    assert by_name["prompt_injection.web_ignore_instructions"]["status"] == "pass"


def test_eval_failures_are_reported_without_crashing(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEB_ACCESS_ENABLED", "true")

    report = run_eval(
        options(tmp_path, web=True),
        runtime=runtime(tmp_path),
        registry=registry(tmp_path, search_provider=BrokenSearchProvider()),
        client_factory=FakeLMStudioClient,
    )

    by_name = {check["name"]: check for check in report["checks"]}
    assert by_name["web.search"]["status"] == "fail"
    assert eval_exit_code(report) == 1


def test_evals_do_not_bypass_toolbroker_and_audit_calls(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEB_ACCESS_ENABLED", "true")

    run_eval(
        options(tmp_path, workspace=True, memory=True),
        runtime=runtime(tmp_path),
        registry=registry(tmp_path),
        client_factory=FakeLMStudioClient,
    )

    events = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    tool_names = [event["tool_name"] for event in events]
    assert "filesystem.write" in tool_names
    assert "filesystem.read" in tool_names
    assert "memory.store" in tool_names
    assert "memory.search" in tool_names
    assert "memory.delete" in tool_names


def test_evals_do_not_access_personal_data_unless_explicitly_enabled(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEB_ACCESS_ENABLED", "true")

    report = run_eval(
        options(tmp_path, safe=True),
        runtime=runtime(tmp_path),
        registry=registry(tmp_path),
        client_factory=FakeLMStudioClient,
    )

    events = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert all(
        not str(event["tool_name"]).startswith(("calendar.", "contacts.", "email.", "messages."))
        for event in events
    )
    assert report["personal_data_evals"] == "skipped_by_default"


def test_eval_command_dispatches_with_mocks(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli_commands, "run_eval", lambda options: {"status": "ok", "run_id": "test", "selected_categories": ["safe"], "summary": {"pass": 1, "fail": 0, "skipped": 0}, "checks": [], "report_path": "docs/EVAL_REPORT.md"})

    assert cli_commands.dispatch_cli(["eval", "run", "--safe"]) == 0
    assert "Eval run: test" in capsys.readouterr().out


def test_eval_command_accepts_golden_category_flags(monkeypatch, capsys) -> None:
    captured = {}

    def fake_run(options):
        captured["options"] = options
        return {"status": "ok", "run_id": "golden", "selected_categories": ["routing"], "summary": {"pass": 1, "fail": 0, "skipped": 0}, "checks": [], "report_path": "docs/EVAL_REPORT.md"}

    monkeypatch.setattr(cli_commands, "run_eval", fake_run)

    assert cli_commands.dispatch_cli(["eval", "run", "--routing", "--policy", "--tools", "--workflows", "--prompt-injection", "--lmstudio-live"]) == 0
    assert captured["options"].routing is True
    assert captured["options"].policy is True
    assert captured["options"].tools is True
    assert captured["options"].workflows is True
    assert captured["options"].prompt_injection is True
    assert captured["options"].lmstudio_live is True
    assert "Eval run: golden" in capsys.readouterr().out
