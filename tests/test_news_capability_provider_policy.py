from __future__ import annotations

import copy
from pathlib import Path

import pytest

from agent.config.loader import load_capabilities_config
from agent.config.schema import CapabilityConfigError, validate_capabilities_config
from agent.news import NewsConfig, select_news_provider
from agent.safety.policy import PolicyDecision, PolicyEngine, RiskLevel
from agent.safety.validation import validate_startup_policy


ROOT = Path(__file__).resolve().parents[1]

NEWS_CAPABILITIES = {
    "news.providers.status",
    "news.search",
    "news.top",
    "news.feed.fetch",
    "news.sitemap.fetch",
    "news.gdelt.search",
    "news.gdelt.timeline",
    "news.mediacloud.search",
    "news.newsapi.search",
    "news.article.fetch",
    "news.article.extract",
    "news.brief",
    "news.timeline",
    "news.compare",
    "news.multilingual",
    "news.cache.status",
    "news.cache.clear",
    "news.dogfood",
}


def _news_manifest_entries() -> dict[str, dict[str, object]]:
    tools = load_capabilities_config(ROOT / "config" / "capabilities.yaml")["tools"]
    return {name: tools[name] for name in NEWS_CAPABILITIES}


def test_news_capability_manifest_validates() -> None:
    validate_startup_policy(ROOT / "config" / "capabilities.yaml")

    entries = _news_manifest_entries()
    assert set(entries) == NEWS_CAPABILITIES
    for capability_id, entry in entries.items():
        assert entry["capability_name"] == capability_id
        assert entry["tool_name"] == capability_id
        assert entry["connector_name"] == "news"
        assert entry["status"] == "planned"
        assert "provider" in entry
        assert "rate_limit" in entry
        assert "memory_behavior" in entry
        assert "audit_fields" in entry
        assert "docs_reference" in entry


def test_unknown_news_capability_denied() -> None:
    policy = PolicyEngine.from_config(load_capabilities_config(ROOT / "config" / "capabilities.yaml"))

    result = policy.evaluate("news.unknown")

    assert result.decision == PolicyDecision.DENY
    assert result.reason == "unknown capability"


def test_planned_news_capabilities_are_disabled_before_runtime_implementation() -> None:
    policy = PolicyEngine.from_config(load_capabilities_config(ROOT / "config" / "capabilities.yaml"))

    for capability_id in NEWS_CAPABILITIES:
        result = policy.evaluate(capability_id)
        assert result.decision == PolicyDecision.DENY
        assert result.reason == "capability disabled"


def test_news_v1_has_no_critical_actions() -> None:
    for entry in _news_manifest_entries().values():
        assert entry["risk_level"] != RiskLevel.CRITICAL.value
        assert entry["approval_required"] is False


def test_missing_news_risk_or_trust_is_rejected() -> None:
    config = load_capabilities_config(ROOT / "config" / "capabilities.yaml")

    missing_risk = {"tools": {"news.search": copy.deepcopy(config["tools"]["news.search"])}}
    del missing_risk["tools"]["news.search"]["risk_level"]
    with pytest.raises(CapabilityConfigError, match="missing risk_level"):
        validate_capabilities_config(missing_risk)

    missing_trust = {"tools": {"news.search": copy.deepcopy(config["tools"]["news.search"])}}
    del missing_trust["tools"]["news.search"]["trust_level"]
    with pytest.raises(CapabilityConfigError, match="missing trust_level"):
        validate_capabilities_config(missing_trust)


def test_news_config_defaults_are_safe() -> None:
    config = NewsConfig.from_env({})

    assert config.enabled is True
    assert config.default_provider == "auto"
    assert config.cost_mode == "free_first"
    assert config.allow_paid_apis is False
    assert config.store_history is False
    assert config.cache_enabled is True
    assert config.cache_ttl_seconds == 3600
    assert config.article_cache_ttl_seconds == 86400
    assert config.max_sources == 8
    assert config.max_fetched_articles == 5
    assert config.freshness_default == "recent"
    assert config.gdelt_enabled is True
    assert config.mediacloud_enabled is False
    assert config.newsapi_enabled is False
    assert config.require_source_grounding is True


def test_news_provider_policy_chooses_free_first() -> None:
    decision = select_news_provider(config=NewsConfig.from_env({}), purpose="search")

    assert decision.status == "selected"
    assert decision.selected_provider == "cache"
    assert decision.cache_used is True
    assert decision.paid_api_used is False
    assert decision.trust_level == "UNTRUSTED_WEB"
    assert decision.memory_behavior == "no_store_history_or_article_bodies"


def test_paid_news_providers_disabled_by_default() -> None:
    decision = select_news_provider(
        config=NewsConfig.from_env({"NEWS_NEWSAPI_ENABLED": "true"}),
        requested_provider="newsapi",
        purpose="search",
    )

    assert decision.status == "unavailable"
    assert decision.selected_provider is None
    assert decision.reason == "newsapi skipped because NEWS_ALLOW_PAID_APIS=false"
    assert decision.paid_api_used is False


def test_news_search_history_disabled_by_default() -> None:
    config = NewsConfig.from_env({})
    decision = select_news_provider(config=config, purpose="search")

    assert config.store_history is False
    assert decision.config["store_history"] is False
    assert "article_bodies" in decision.memory_behavior


def test_news_command_registry_planned_entries_remain_conservative() -> None:
    registry = (ROOT / "docs" / "COMMAND_REGISTRY.md").read_text(encoding="utf-8")

    for command_id in [f"CMD-NEWS-{index:03d}" for index in range(1, 12)]:
        assert f"| {command_id} |" in registry
    assert "not implemented; planned command" in registry
    assert "planned provider decision audit; no provider calls" in registry
    assert "no news history or article bodies by default" in registry
