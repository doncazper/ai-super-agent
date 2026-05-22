from __future__ import annotations

import json

import pytest

from agent.config.runtime import RuntimeConfig
from agent.tools.web.fetch import WebResponse
from agent.tools.registry import default_registry
from agent.ui import cli_commands
from agent.ui.smoke import SmokeCheck, SmokeOptions, run_smoke, smoke_exit_code


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
        return {"choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": "RCS is carrier messaging; iMessage is Apple messaging."}}]}


class StaticSearchProvider:
    name = "static"

    def is_configured(self) -> bool:
        return True

    def search(self, query, max_results, locale=None, safe_search=True):
        return [
            {
                "title": "Example",
                "url": "https://example.com/",
                "snippet": "Example Domain",
                "source": "example.com",
                "trust_level": "UNTRUSTED_WEB",
            }
        ][:max_results]


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


def test_smoke_requires_selection(tmp_path) -> None:
    checks = run_smoke(SmokeOptions(), runtime=runtime(tmp_path))

    assert smoke_exit_code(checks) == 1
    assert checks[-1].name == "smoke_selection"


def test_lmstudio_smoke_uses_no_tools_and_time_tool_with_fake_client(tmp_path) -> None:
    checks = run_smoke(
        SmokeOptions(lmstudio=True),
        runtime=runtime(tmp_path),
        registry=default_registry(project_root=tmp_path, memory_path=tmp_path / "memory.sqlite3"),
        client_factory=FakeLMStudioClient,
    )

    by_name = {check.name: check for check in checks}
    assert by_name["lmstudio_no_tools"].status == "ok"
    assert by_name["lmstudio_no_tool_response"].status == "ok"
    assert by_name["lmstudio_debug_events"].status == "ok"
    assert by_name["lmstudio_time_tool_path"].status == "ok"


def test_lmstudio_smoke_skips_when_model_missing(tmp_path) -> None:
    checks = run_smoke(SmokeOptions(lmstudio=True), runtime=runtime(tmp_path, model=""))

    assert any(check.name == "live_lmstudio_config" and check.status == "skip" for check in checks)
    assert smoke_exit_code(checks) == 0


def test_web_smoke_with_mocked_provider_and_fetcher(tmp_path) -> None:
    registry = default_registry(
        project_root=tmp_path,
        memory_path=tmp_path / "memory.sqlite3",
        web_search_provider=StaticSearchProvider(),
        web_fetcher=fake_fetcher,
    )

    checks = run_smoke(SmokeOptions(web=True), runtime=runtime(tmp_path), registry=registry)

    by_name = {check.name: check for check in checks}
    assert by_name["web_search"].status == "ok"
    assert by_name["web_fetch_url"].status == "ok"
    assert by_name["research_workflow"].status in {"ok", "skip"}


def test_personal_smoke_is_dry_run_and_does_not_read_data(tmp_path) -> None:
    checks = run_smoke(
        SmokeOptions(calendar=True, contacts=True),
        runtime=runtime(tmp_path),
        registry=default_registry(project_root=tmp_path, memory_path=tmp_path / "memory.sqlite3"),
    )

    by_name = {check.name: check for check in checks}
    assert by_name["calendar_mode"].detail == "dry-run only; no personal data read"
    assert by_name["contacts_mode"].detail == "dry-run only; no personal data read"
    assert by_name["calendar.read_date_range_dry_run"].status == "ok"
    assert by_name["contacts.search_dry_run"].status == "ok"


def test_smoke_command_dispatches_with_mocks(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli_commands, "run_smoke", lambda options: [SmokeCheck("mock", "ok", "done")])

    assert cli_commands.dispatch_cli(["smoke", "--all-safe"]) == 0
    assert "[ok] mock: done" in capsys.readouterr().out
