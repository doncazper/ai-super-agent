from __future__ import annotations

import json

from agent.core.tool_broker import ToolBroker
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry
from agent.web_acquisition.official_apis import OfficialApiRegistry
from agent.web_acquisition.official_apis.github import GitHubOfficialApiProvider
from agent.web_acquisition.official_apis.reddit import RedditOfficialApiProvider
from agent.web_acquisition.official_apis.registry import default_official_api_registry


def call(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    return {
        "id": f"call_{tool_name}",
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments)},
    }


def official_api_capabilities() -> dict[str, Capability]:
    return {
        "web.official_apis": Capability("web.official_apis", RiskLevel.SAFE),
        "web.official_api.status": Capability("web.official_api.status", RiskLevel.SAFE),
        "web.official_api.search": Capability(
            "web.official_api.search",
            RiskLevel.LOW,
            metadata={"requires_web_access": True},
        ),
    }


def broker(tmp_path, registry: OfficialApiRegistry | None = None) -> ToolBroker:
    return ToolBroker(
        default_registry(project_root=tmp_path, official_api_registry=registry),
        PolicyEngine(official_api_capabilities()),
        AuditLogger(tmp_path / "audit.jsonl"),
        session_id="test-session",
        model="test-model",
        route="test",
    )


def test_registry_loads_default_providers() -> None:
    registry = default_official_api_registry()

    assert registry.provider_names() == ["arxiv", "github", "reddit", "wikipedia"]
    payload = registry.list_providers()
    assert {provider["provider_name"] for provider in payload} == {"github", "wikipedia", "arxiv", "reddit"}


def test_provider_matching_prefers_official_api_for_known_domains() -> None:
    registry = default_official_api_registry()

    assert registry.match_provider_for_url("https://github.com/openai/openai-python").provider_name == "github"
    assert registry.match_provider_for_url("https://en.wikipedia.org/wiki/Safety").provider_name == "wikipedia"
    assert registry.match_provider_for_url("https://arxiv.org/abs/2401.00001").provider_name == "arxiv"
    assert registry.match_provider_for_url("https://example.com") is None


def test_missing_credentials_return_setup_hint_for_reddit(monkeypatch) -> None:
    monkeypatch.delenv("REDDIT_CLIENT_SECRET", raising=False)
    registry = OfficialApiRegistry([RedditOfficialApiProvider()])

    response = registry.search("reddit", "test", 3, brokered_execution=True).to_dict()

    assert response["status"] == "setup_required"
    assert response["errors"][0]["code"] == "setup_required"
    assert "OAuth" in response["errors"][0]["message"] or "REDDIT_CLIENT_ID" in response["errors"][0]["message"]
    assert response["query_history_persisted"] is False


def test_public_provider_mock_results_normalize_to_search_result(tmp_path) -> None:
    registry = OfficialApiRegistry(
        [
            GitHubOfficialApiProvider(
                mock_results=[
                    {
                        "full_name": "openai/example",
                        "html_url": "https://github.com/openai/example",
                        "description": "A mock public repository.",
                        "language": "Python",
                    }
                ]
            )
        ]
    )
    tool_broker = broker(tmp_path, registry)

    result = tool_broker.execute(call("web.official_api.search", {"provider": "github", "query": "openai", "max_results": 1}))
    payload = json.loads(result.content)

    assert result.allowed is True
    assert payload["status"] == "ok"
    assert payload["live_call_performed"] is False
    assert payload["query_history_persisted"] is False
    assert payload["results"][0]["title"] == "openai/example"
    assert payload["results"][0]["provider"] == "github"
    assert payload["results"][0]["trust_level"] == "UNTRUSTED_WEB"
    assert payload["results"][0]["reliability_signals"]["official_api"] is True


def test_rate_limit_enforced_by_toolbroker(tmp_path) -> None:
    registry = OfficialApiRegistry([GitHubOfficialApiProvider(mock_results=[{"title": "One", "url": "https://github.com/a/b"}])])
    policy = PolicyEngine(
        {
            "web.official_api.search": Capability(
                "web.official_api.search",
                RiskLevel.LOW,
                metadata={"requires_web_access": True, "rate_limit": {"requests_per_minute": 1}},
            )
        }
    )
    tool_broker = ToolBroker(
        default_registry(project_root=tmp_path, official_api_registry=registry),
        policy,
        AuditLogger(tmp_path / "audit.jsonl"),
        session_id="test-session",
        model="test-model",
        route="test",
    )

    first = tool_broker.execute(call("web.official_api.search", {"provider": "github", "query": "one"}))
    second = tool_broker.execute(call("web.official_api.search", {"provider": "github", "query": "two"}))

    assert first.allowed is True
    assert second.allowed is False
    assert "rate limit" in second.content.lower()


def test_secrets_redacted_in_status_and_audit(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("REDDIT_ENABLED", "true")
    monkeypatch.setenv("REDDIT_CLIENT_ID", "client-id")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "super-secret-reddit-value")
    monkeypatch.setenv("REDDIT_USER_AGENT", "ai-super-agent-test")
    monkeypatch.setenv("REDDIT_REFRESH_TOKEN", "refresh-secret-token")
    tool_broker = broker(tmp_path, default_official_api_registry())

    result = tool_broker.execute(call("web.official_api.status", {"provider": "reddit"}))
    payload = json.loads(result.content)
    audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")

    assert result.allowed is True
    assert payload["provider"]["configured"] is True
    assert "super-secret-reddit-value" not in json.dumps(payload)
    assert "refresh-secret-token" not in json.dumps(payload)
    assert "super-secret-reddit-value" not in audit_text
    assert "refresh-secret-token" not in audit_text


def test_reddit_web_scraping_is_not_used_as_api_substitute(tmp_path) -> None:
    tool_broker = broker(tmp_path, default_official_api_registry())

    result = tool_broker.execute(call("web.official_api.status", {"provider": "reddit"}))
    payload = json.loads(result.content)

    assert result.allowed is True
    assert payload["provider"]["web_scraping_fallback"] is False
    assert payload["provider"]["personal_data_access"] is False
    assert "web scraping is not used" in payload["provider"]["setup_hint"]


def test_provider_call_audits_provider_domain_and_redacts_query(tmp_path) -> None:
    registry = OfficialApiRegistry([GitHubOfficialApiProvider(mock_results=[{"title": "One", "url": "https://github.com/a/b"}])])
    tool_broker = broker(tmp_path, registry)

    tool_broker.execute(call("web.official_api.search", {"provider": "github", "query": "private token query"}))

    audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
    assert "private token query" not in audit_text
    assert "[WEB_SEARCH_QUERY_REDACTED]" in audit_text
    assert "github.com" in audit_text


def test_command_registry_includes_official_api_commands() -> None:
    from agent.ui.command_registry import list_commands

    commands = {record.command for record in list_commands()}
    assert "python smart_agent.py web official-apis" in commands
    assert "python smart_agent.py web api-status <provider>" in commands
    assert "python smart_agent.py web api-search <provider> \"<query>\"" in commands
