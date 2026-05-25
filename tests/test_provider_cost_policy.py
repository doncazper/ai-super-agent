from __future__ import annotations

import json

from agent.connectors.cost_policy import (
    ProviderCandidate,
    ProviderCostConfig,
    ProviderCostMode,
    ProviderDecisionStatus,
    audit_provider_decision,
    select_provider,
    weather_provider_candidates,
    web_provider_candidates,
)
from agent.safety.audit import AuditLogger


def test_free_first_selects_no_key_provider_first() -> None:
    decision = select_provider(
        "weather",
        [
            ProviderCandidate("weatherapi", "weather", True, "Set WEATHER_API_KEY.", paid_api=True),
            ProviderCandidate("open_meteo", "weather", True, "Open-Meteo is available.", no_key_required=True),
        ],
        config=ProviderCostConfig(),
    )

    assert decision.status == ProviderDecisionStatus.SELECTED
    assert decision.selected_provider == "open_meteo"
    assert "no-key" in decision.reason


def test_paid_provider_skipped_when_paid_apis_disabled() -> None:
    decision = select_provider(
        "web",
        [ProviderCandidate("serpapi", "web", True, "Set SERPAPI_API_KEY.", paid_api=True, quota_limited=True)],
        config=ProviderCostConfig(allow_paid_apis=False, max_paid_api_calls_per_day=0),
    )

    assert decision.status == ProviderDecisionStatus.UNAVAILABLE
    assert decision.selected_provider is None
    assert decision.skipped_providers[0]["reason"] == "serpapi skipped because ALLOW_PAID_APIS=false"


def test_serpapi_selected_only_when_allowed_and_configured() -> None:
    denied = select_provider(
        "web",
        web_provider_candidates({"SERPAPI_API_KEY": "secret-serpapi-key"}),
        config=ProviderCostConfig(allow_paid_apis=False, max_paid_api_calls_per_day=0),
    )
    allowed = select_provider(
        "web",
        web_provider_candidates({"SERPAPI_API_KEY": "secret-serpapi-key"}),
        config=ProviderCostConfig(allow_paid_apis=True, max_paid_api_calls_per_day=10),
    )

    assert denied.selected_provider is None
    assert allowed.status == ProviderDecisionStatus.SELECTED
    assert allowed.selected_provider == "serpapi"


def test_weatherapi_selected_only_when_allowed_or_explicitly_requested() -> None:
    candidates = weather_provider_candidates({"WEATHER_API_KEY": "secret-weather-key"})
    default_decision = select_provider("weather", candidates, config=ProviderCostConfig())
    allowed_default = select_provider(
        "weather",
        candidates,
        config=ProviderCostConfig(allow_paid_apis=True, max_paid_api_calls_per_day=5, weather_default_provider="weatherapi"),
    )
    explicit_decision = select_provider(
        "weather",
        candidates,
        config=ProviderCostConfig(),
        explicit_provider="weatherapi",
    )

    assert default_decision.selected_provider == "open_meteo"
    assert allowed_default.selected_provider == "weatherapi"
    assert explicit_decision.selected_provider == "weatherapi"
    assert explicit_decision.reason == "explicit provider selected"


def test_provider_decision_is_audited(tmp_path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    decision = select_provider(
        "weather",
        weather_provider_candidates({}),
        config=ProviderCostConfig(),
    )

    audit_provider_decision(AuditLogger(audit_path), decision, request_id="provider-test")

    event = json.loads(audit_path.read_text(encoding="utf-8").splitlines()[0])
    assert event["tool_name"] == "provider.select"
    assert event["capability"] == "weather.provider_select"
    assert event["sanitized_args"]["cost_mode"] == "free_first"
    assert event["result_summary"].startswith("free_first selected open_meteo")


def test_search_policy_config_defaults_from_env() -> None:
    config = ProviderCostConfig.from_env({})

    assert config.cost_mode.value == "free_first"
    assert config.allow_paid_apis is False
    assert config.max_paid_api_calls_per_day == 0
    assert config.search_default_provider == "auto"
    assert config.search_allowed_providers == (
        "cache",
        "url",
        "feed",
        "sitemap",
        "official_api",
        "searxng",
        "brave",
        "serpapi",
    )
    assert config.search_store_history is False
    assert config.search_cache_enabled is True
    assert config.search_cache_ttl_seconds == 86400


def test_manual_mode_respects_explicit_search_provider() -> None:
    decision = select_provider(
        "web",
        [
            ProviderCandidate("url", "web", True, "Provide a URL.", no_key_required=True, user_provided=True),
            ProviderCandidate("searxng", "web", True, "Set SEARXNG_BASE_URL.", local=True, user_provided=True),
        ],
        config=ProviderCostConfig(cost_mode=ProviderCostMode.MANUAL),
        explicit_provider="searxng",
    )

    assert decision.status == ProviderDecisionStatus.SELECTED
    assert decision.selected_provider == "searxng"
    assert decision.reason == "explicit provider selected"


def test_paid_search_provider_blocked_when_not_allowed_even_if_explicit() -> None:
    decision = select_provider(
        "web",
        web_provider_candidates({"SERPAPI_API_KEY": "secret-serpapi-key"}),
        config=ProviderCostConfig(allow_paid_apis=False, max_paid_api_calls_per_day=0),
        explicit_provider="serpapi",
    )

    assert decision.status == ProviderDecisionStatus.UNAVAILABLE
    assert decision.selected_provider is None
    assert decision.reason == "serpapi requires ALLOW_PAID_APIS=true"


def test_paid_search_provider_requires_daily_cap_even_if_explicit() -> None:
    decision = select_provider(
        "web",
        web_provider_candidates({"SERPAPI_API_KEY": "secret-serpapi-key"}),
        config=ProviderCostConfig(allow_paid_apis=True, max_paid_api_calls_per_day=0),
        explicit_provider="serpapi",
    )

    assert decision.status == ProviderDecisionStatus.UNAVAILABLE
    assert decision.selected_provider is None
    assert decision.reason == "serpapi requires MAX_PAID_API_CALLS_PER_DAY>0"


def test_provider_decision_payload_includes_required_summary_fields() -> None:
    decision = select_provider(
        "web",
        [
            ProviderCandidate("cache", "web", False, "No cache hit.", local=True, cached=True, no_key_required=True),
            ProviderCandidate("url", "web", True, "Provide a URL.", no_key_required=True, user_provided=True),
        ],
        config=ProviderCostConfig(),
    )
    payload = decision.to_dict()

    assert payload["selected_provider"] == "url"
    assert payload["paid_api_used"] is False
    assert payload["cache_used"] is False
    assert payload["cost_mode"] == "free_first"
    assert "cache" in payload["skip_reasons"]
    assert payload["audit_summary"].startswith("provider_decision domain=web selected=url")


def test_secrets_redacted_from_decision_payload_and_audit(tmp_path) -> None:
    decision = select_provider(
        "web",
        [
            ProviderCandidate(
                "brave",
                "web",
                True,
                "Configured.",
                quota_limited=True,
                metadata={"api_key": "fake-provider-key-for-redaction-test"},
            )
        ],
        config=ProviderCostConfig(allow_paid_apis=True, max_paid_api_calls_per_day=1),
    )
    payload = json.dumps(decision.to_dict())

    audit_provider_decision(AuditLogger(tmp_path / "audit.jsonl"), decision, request_id="redact-test")
    audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")

    assert "fake-provider-key-for-redaction-test" not in payload
    assert "fake-provider-key-for-redaction-test" not in audit_text


def test_missing_provider_returns_clear_setup_hint() -> None:
    decision = select_provider(
        "web",
        web_provider_candidates({}),
        config=ProviderCostConfig(search_default_provider="serpapi"),
    )

    assert decision.status == ProviderDecisionStatus.UNAVAILABLE
    assert decision.selected_provider is None
    assert "SERPAPI_API_KEY" in decision.setup_hint
    assert "not configured" in decision.reason
