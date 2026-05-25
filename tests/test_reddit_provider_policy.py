from __future__ import annotations

from pathlib import Path

from agent.config.loader import load_capabilities_config
from agent.config.schema import validate_capabilities_config
from agent.forums.reddit.policy import (
    REDDIT_FORBIDDEN_WRITE_CAPABILITIES,
    REDDIT_READ_CAPABILITIES,
    is_reddit_capability_allowed,
    load_reddit_policy_config,
    reddit_compliance_status,
)


ROOT = Path(__file__).resolve().parents[1]


def test_reddit_disabled_by_default() -> None:
    config = load_reddit_policy_config({})
    status = reddit_compliance_status({})

    assert config.enabled is False
    assert config.configured is False
    assert status["status"] == "disabled"
    assert status["enabled"] is False
    assert "disabled" in status["setup_hint"].lower()


def test_missing_oauth_config_returns_setup_hint() -> None:
    env = {"REDDIT_ENABLED": "true"}

    status = reddit_compliance_status(env)

    assert status["status"] == "requires_setup"
    assert status["oauth_required"] is True
    assert status["unauthenticated_mode_allowed"] is False
    assert "REDDIT_CLIENT_ID" in status["missing_oauth_env"]
    assert "REDDIT_CLIENT_SECRET" in status["missing_oauth_env"]
    assert "REDDIT_USER_AGENT" in status["missing_oauth_env"]
    assert "REDDIT_REFRESH_TOKEN or REDDIT_ACCESS_TOKEN" in status["missing_oauth_env"]
    assert "Unauthenticated Reddit access" in status["setup_hint"]


def test_no_unauthenticated_mode_even_with_partial_oauth() -> None:
    env = {
        "REDDIT_ENABLED": "true",
        "REDDIT_CLIENT_ID": "client-id",
        "REDDIT_CLIENT_SECRET": "secret",
        "REDDIT_USER_AGENT": "ai-super-agent-test",
    }

    config = load_reddit_policy_config(env)

    assert config.configured is False
    assert config.token_configured is False
    assert config.unauthenticated_mode_allowed is False
    assert is_reddit_capability_allowed("reddit.search_posts", config) is False


def test_forbidden_write_capabilities_absent_or_denied() -> None:
    config = load_reddit_policy_config(
        {
            "REDDIT_ENABLED": "true",
            "REDDIT_CLIENT_ID": "client-id",
            "REDDIT_CLIENT_SECRET": "secret",
            "REDDIT_USER_AGENT": "ai-super-agent-test",
            "REDDIT_REFRESH_TOKEN": "token",
        }
    )

    for capability in REDDIT_FORBIDDEN_WRITE_CAPABILITIES:
        assert is_reddit_capability_allowed(capability, config) is False
    assert is_reddit_capability_allowed("reddit.unknown", config) is False
    assert is_reddit_capability_allowed("reddit.search_posts", config) is True


def test_retention_defaults_and_author_metadata_minimized() -> None:
    config = load_reddit_policy_config({})

    assert config.cache_enabled is True
    assert config.cache_ttl_seconds == 86400
    assert config.delete_user_content_after_seconds == 172800
    assert config.max_requests_per_minute == 60
    assert config.store_author_metadata is False


def test_use_for_training_is_hard_false() -> None:
    config = load_reddit_policy_config({"REDDIT_USE_FOR_TRAINING": "true"})
    status = reddit_compliance_status({"REDDIT_USE_FOR_TRAINING": "true"})

    assert config.use_for_training is False
    assert config.use_for_training_env_requested is True
    assert status["model_training_allowed"] is False
    assert status["use_for_training"] is False


def test_reddit_web_fallback_is_policy_denied_even_if_env_requests_it() -> None:
    config = load_reddit_policy_config({"REDDIT_ALLOW_WEB_FALLBACK": "true"})

    assert config.web_fallback_env_requested is True
    assert config.allow_web_fallback is False


def test_reddit_capability_manifest_validates_and_defaults_disabled() -> None:
    capabilities = load_capabilities_config(ROOT / "config/capabilities.yaml")

    validate_capabilities_config(capabilities)
    tools = capabilities["tools"]
    for capability in REDDIT_READ_CAPABILITIES:
        entry = tools[capability]
        assert entry["connector_name"] == "reddit"
        if capability == "reddit.thread_export":
            assert entry["trust_level"] == "UNTRUSTED_DOCUMENT"
        else:
            assert entry["trust_level"] == "UNTRUSTED_WEB"
        if capability in {
            "reddit.status",
            "reddit.auth_check",
            "reddit.search_posts",
            "reddit.search_subreddit",
            "reddit.fetch_subreddit_info",
            "reddit.fetch_post",
            "reddit.fetch_comments",
            "reddit.fetch_thread",
            "reddit.explain_result",
            "reddit.thread_export",
            "reddit.summarize_thread",
            "reddit.summarize_search",
            "reddit.consensus",
            "reddit.pros_cons",
            "reddit.complaints",
            "reddit.buying_advice",
            "reddit.cache_status",
            "reddit.cache_clear",
            "reddit.retention_status",
            "reddit.retention_sweep",
            "reddit.privacy_report",
        }:
            assert entry["default_enabled"] is True
        else:
            assert entry["default_enabled"] is False
        if capability == "reddit.thread_export":
            assert entry["stores_data"] is True
            assert entry["memory_behavior"] == "workspace_write"
        else:
            assert entry["stores_data"] is False
            assert entry["memory_behavior"] in {"no_store", "cache_only"}
    for capability in REDDIT_FORBIDDEN_WRITE_CAPABILITIES:
        assert capability not in tools
