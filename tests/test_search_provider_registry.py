from __future__ import annotations

import json
from dataclasses import dataclass

from agent.core.tool_broker import ToolBroker
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry
from agent.web_acquisition.search import (
    SearchCostClass,
    SearchProvider,
    SearchProviderRegistry,
    SearchProviderSetupError,
    normalize_search_response,
)


@dataclass(frozen=True)
class FixtureSearchProvider(SearchProvider):
    provider_name: str = "fixture"
    cost_class: SearchCostClass = SearchCostClass.FREE
    requires_api_key: bool = False
    supports_news: bool = True
    supports_images: bool = False
    supports_time_filter: bool = True
    configured: bool = True
    enabled: bool = True

    def is_configured(self) -> bool:
        return self.configured

    def is_enabled(self) -> bool:
        return self.enabled

    def setup_hint(self) -> str:
        return "fixture provider is available"

    def search(self, query: str, max_results: int, locale: str | None = None, safe_search: bool = True, freshness: str | None = None):
        return [
            {
                "title": "Example",
                "url": "https://example.com/result",
                "snippet": f"{query}:{locale}:{safe_search}:{freshness}",
                "source": "example.com",
            }
        ][:max_results]


def call(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    return {
        "id": f"call_{tool_name}",
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments)},
    }


def test_provider_registry_loads_default_metadata(monkeypatch) -> None:
    monkeypatch.setenv("SEARXNG_BASE_URL", "https://search.example")
    registry = SearchProviderRegistry()
    registry.register(FixtureSearchProvider())

    assert registry.provider_names() == ["fixture"]
    assert registry.list_providers()[0]["provider_name"] == "fixture"


def test_unknown_provider_denied_structurally() -> None:
    registry = SearchProviderRegistry([FixtureSearchProvider()])

    response = registry.search("unknown", "query", 1, brokered_execution=True).to_dict()

    assert response["status"] == "error"
    assert response["errors"][0]["code"] == "unknown_provider"
    assert response["query_history_persisted"] is False


def test_missing_provider_returns_setup_hint() -> None:
    registry = SearchProviderRegistry([FixtureSearchProvider(configured=False, enabled=False)])

    response = registry.search("fixture", "query", 1, brokered_execution=True).to_dict()

    assert response["status"] == "setup_required"
    assert response["errors"][0]["code"] == "setup_required"
    assert "fixture provider" in response["errors"][0]["message"]


def test_registry_search_requires_toolbroker_context() -> None:
    registry = SearchProviderRegistry([FixtureSearchProvider()])

    response = registry.search("fixture", "query", 1).to_dict()

    assert response["status"] == "denied"
    assert "ToolBroker" in response["errors"][0]["message"]


def test_normalized_result_and_response_schema() -> None:
    response = normalize_search_response(
        query="private sensitive query",
        provider="fixture",
        results=[{"title": "Example", "url": "https://example.com", "snippet": "Snippet"}],
    ).to_dict()

    result = response["results"][0]
    assert response["query_hash"]
    assert response["redacted_query"] == "[WEB_SEARCH_QUERY_REDACTED]"
    assert response["query_history_persisted"] is False
    assert response["errors"] == []
    assert result["provider"] == "fixture"
    assert result["rank"] == 1
    assert result["trust_level"] == "UNTRUSTED_WEB"
    assert result["reliability_signals"] == {}


def test_provider_error_normalized() -> None:
    registry = SearchProviderRegistry([FixtureSearchProvider(configured=False)])

    response = registry.search("fixture", "query", 1, brokered_execution=True).to_dict()

    assert response["errors"] == [{"code": "setup_required", "message": "fixture provider is available"}]


def test_sensitive_query_redacted_in_broker_audit_and_no_history(tmp_path) -> None:
    broker = ToolBroker(
        default_registry(project_root=tmp_path),
        PolicyEngine(
            {
                "web.search": Capability("web.search", RiskLevel.LOW, metadata={"requires_web_access": True}),
                "web.search_providers": Capability("web.search_providers", RiskLevel.SAFE),
            }
        ),
        AuditLogger(tmp_path / "audit.jsonl"),
        session_id="test-session",
        model="test-model",
        route="test",
    )

    result = broker.execute(call("web.search", {"query": "private sensitive search", "provider": "searxng"}))

    payload = json.loads(result.content)
    assert payload["query_history_persisted"] is False
    assert payload["redacted_query"] == "[WEB_SEARCH_QUERY_REDACTED]"
    audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
    assert "private sensitive search" not in audit_text
    assert "[WEB_SEARCH_QUERY_REDACTED]" in audit_text


def test_command_registry_includes_search_providers_command() -> None:
    from agent.ui.command_registry import list_commands

    commands = {record.command for record in list_commands()}
    assert "python smart_agent.py web search-providers" in commands
    assert "python smart_agent.py web searxng doctor" in commands
    assert "python smart_agent.py web serpapi doctor" in commands
    assert "python smart_agent.py web brave doctor" in commands
