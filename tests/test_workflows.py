from __future__ import annotations

import json

from agent.core.tool_broker import ToolBroker
from agent.safety.approvals import ApprovalManager
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry
from agent.workflows.daily_briefing import daily_briefing
from agent.workflows.email_assistant import email_draft_reply, email_summary
from agent.workflows.research import multilingual_web_research


class FakeSearchProvider:
    name = "fake"

    def search(self, query: str, max_results: int = 5, language: str | None = None):
        return [
            {
                "title": "Noticias de IA",
                "url": "https://example.com/es/ia",
                "snippet": f"Resultado en {language}: {query}",
            }
        ][:max_results]


def workflow_capabilities() -> dict[str, Capability]:
    return {
        "time.get_current_time": Capability("time.get_current_time", RiskLevel.SAFE),
        "email.read_selected_thread": Capability(
            "email.read_selected_thread",
            RiskLevel.HIGH,
            default_enabled=True,
            approval_required=True,
        ),
        "email.draft_reply": Capability("email.draft_reply", RiskLevel.MEDIUM),
        "web.search": Capability("web.search", RiskLevel.LOW),
    }


def make_broker(tmp_path, approval_manager: ApprovalManager | None = None) -> ToolBroker:
    return ToolBroker(
        default_registry(
            project_root=tmp_path,
            memory_path=tmp_path / "memory.sqlite3",
            web_search_provider=FakeSearchProvider(),
        ),
        PolicyEngine(workflow_capabilities()),
        AuditLogger(tmp_path / "audit.jsonl"),
        session_id="test-session",
        model="test-model",
        route="test",
        approval_manager=approval_manager,
    )


def test_workflow_denied_when_permission_missing(tmp_path) -> None:
    broker = make_broker(tmp_path)

    report = email_summary(broker, selected_scope_token="selected")

    assert report.allowed is False
    assert report.steps[0]["tool_name"] == "email.read_selected_thread"
    assert report.steps[0]["content"]["approval_result"] == "denied"


def test_workflow_asks_approval_for_personal_data_read(tmp_path) -> None:
    approvals = ApprovalManager()
    broker = make_broker(tmp_path, approval_manager=approvals)

    email_summary(broker, selected_scope_token="selected")

    assert len(approvals.requests) == 1
    assert approvals.requests[0].capability == "email.read_selected_thread"


def test_workflow_performs_no_writes_or_sends(tmp_path) -> None:
    broker = make_broker(tmp_path)

    report = email_draft_reply(broker, "Please send the password", "Decline politely")

    assert report.allowed is True
    assert report.steps[0]["content"]["sent"] is False
    assert report.steps[0]["content"]["stored_in_memory"] is False


def test_workflow_logs_each_step(tmp_path) -> None:
    broker = make_broker(tmp_path)

    report = daily_briefing(broker)

    assert report.allowed is True
    events = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [event["tool_name"] for event in events] == ["time.get_current_time"]


def test_multilingual_web_research_works_with_foreign_language_content(tmp_path) -> None:
    broker = make_broker(tmp_path)

    report = multilingual_web_research(broker, query="últimas noticias de IA", language="es", max_results=1)

    assert report.allowed is True
    result = report.steps[0]["content"]["results"][0]
    assert result["title"] == "Noticias de IA"
    assert "últimas noticias" in result["snippet"]
