from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Mapping

from agent.config.loader import load_capabilities_config
from agent.connectors.base import ConnectorConfiguration, ConnectorDefinition
from agent.connectors.errors import UnknownConnectorError
from agent.connectors.secret_doctor import provider_status
from agent.connectors.status import build_connector_status
from agent.messaging.macos_probe import last_probe_result
from agent.tools.weather.provider import weather_provider_status


CONNECTOR_NAMES = (
    "weather",
    "web",
    "browser",
    "calendar",
    "contacts",
    "email",
    "messages",
    "tasks",
    "searxng",
    "brave",
    "serpapi",
    "weatherapi",
    "gmail",
    "telegram",
    "reddit",
    "v2ex",
    "apple_business",
)


class ConnectorRegistry:
    def __init__(self, definitions: Iterable[ConnectorDefinition]) -> None:
        self._definitions = {definition.name: definition for definition in definitions}

    def names(self) -> list[str]:
        return list(self._definitions)

    def get(self, name: str) -> ConnectorDefinition | None:
        return self._definitions.get(name)

    def status(
        self,
        name: str,
        config: Mapping[str, Any] | None = None,
        *,
        audit_path: str | Path = "logs/audit.jsonl",
        environ: Mapping[str, str] | None = None,
        include_health: bool = False,
    ) -> dict[str, Any]:
        definition = self.get(name)
        if definition is None:
            raise UnknownConnectorError(name)
        return build_connector_status(
            definition,
            config or load_capabilities_config(),
            audit_path=audit_path,
            environ=environ or os.environ,
            include_health=include_health,
        ).to_dict()

    def list_statuses(
        self,
        config: Mapping[str, Any] | None = None,
        *,
        audit_path: str | Path = "logs/audit.jsonl",
        environ: Mapping[str, str] | None = None,
        include_health: bool = False,
    ) -> list[dict[str, Any]]:
        config_data = config or load_capabilities_config()
        return [
            self.status(
                name,
                config_data,
                audit_path=audit_path,
                environ=environ,
                include_health=include_health,
            )
            for name in self.names()
        ]


def default_connector_registry() -> ConnectorRegistry:
    return ConnectorRegistry(
        [
            ConnectorDefinition(
                name="weather",
                capability_prefixes=("weather.",),
                configuration_probe=_weather_configuration,
                cache_probe=_weather_cache_state,
                setup_docs="Open-Meteo is the default no-key provider. Set WEATHER_PROVIDER=disabled to disable weather.",
            ),
            ConnectorDefinition(
                name="web",
                capability_prefixes=("web.",),
                configuration_probe=_web_configuration,
                setup_docs="Set WEB_SEARCH_PROVIDER=brave and BRAVE_SEARCH_API_KEY, or leave disabled.",
            ),
            ConnectorDefinition(
                name="browser",
                capability_prefixes=("browser.",),
                configuration_probe=_browser_configuration,
                setup_docs=(
                    "URL-based browser clipping is available with explicit URLs. "
                    "Native selected-tab integration is not enabled."
                ),
                personal_data=True,
            ),
            ConnectorDefinition(
                name="calendar",
                capability_prefixes=("calendar.",),
                configuration_probe=_calendar_configuration,
                setup_docs="Set CALENDAR_CONNECTOR=applescript only after approving read-only calendar setup.",
                personal_data=True,
            ),
            ConnectorDefinition(
                name="contacts",
                capability_prefixes=("contacts.",),
                configuration_probe=_contacts_configuration,
                setup_docs="Set CONTACTS_CONNECTOR=applescript only after approving read-only contacts setup.",
                personal_data=True,
            ),
            ConnectorDefinition(
                name="email",
                capability_prefixes=("email.",),
                configuration_probe=_email_configuration,
                setup_docs=(
                    "Set EMAIL_CONNECTOR=imap with IMAP_HOST, IMAP_USERNAME, and IMAP_PASSWORD "
                    "via environment or external secret setup."
                ),
                personal_data=True,
            ),
            ConnectorDefinition(
                name="messages",
                capability_prefixes=("messages.",),
                configuration_probe=_messages_configuration,
                setup_docs="Messages live connector is intentionally unavailable until a safe permissioned path exists.",
                personal_data=True,
                excluded_capabilities=(
                    "messages.probe",
                    "messages.draft_from_lead",
                    "messages.open_handoff_instructions",
                    "messages.inbox.import_manual",
                    "messages.inbox.list",
                    "messages.inbox.show",
                    "messages.inbox.draft_reply",
                    "messages.macos.status",
                    "messages.macos.allowed_recipients.manage",
                ),
            ),
            ConnectorDefinition(
                name="tasks",
                capability_prefixes=("tasks.",),
                configuration_probe=_tasks_configuration,
                setup_docs="Tasks connector is disabled by default; TASKS_CONNECTOR=mock is for tests only.",
                personal_data=True,
            ),
            ConnectorDefinition(
                name="searxng",
                capability_prefixes=("web.",),
                configuration_probe=_searxng_configuration,
                setup_docs="Set SEARXNG_BASE_URL and SEARXNG_ENABLED=true for a self-hosted SearXNG instance.",
            ),
            ConnectorDefinition(
                name="brave",
                capability_prefixes=("web.",),
                configuration_probe=_brave_configuration,
                setup_docs=(
                    "Set BRAVE_SEARCH_API_KEY, BRAVE_SEARCH_ENABLED=true, "
                    "ALLOW_PAID_APIS=true, and MAX_PAID_API_CALLS_PER_DAY>0 before use."
                ),
            ),
            ConnectorDefinition(
                name="serpapi",
                capability_prefixes=("web.",),
                configuration_probe=_serpapi_configuration,
                setup_docs=(
                    "Set SERPAPI_API_KEY, SERPAPI_ENABLED=true, ALLOW_PAID_APIS=true, "
                    "and MAX_PAID_API_CALLS_PER_DAY>0 before use."
                ),
            ),
            ConnectorDefinition(
                name="weatherapi",
                capability_prefixes=("weather.",),
                configuration_probe=_weatherapi_configuration,
                setup_docs="Set WEATHERAPI_API_KEY or WEATHER_API_KEY, then explicitly select WeatherAPI or allow paid APIs.",
            ),
            ConnectorDefinition(
                name="gmail",
                capability_prefixes=("email.",),
                configuration_probe=_gmail_configuration,
                setup_docs="Set Gmail OAuth env vars for config checks only; this connector does not read inboxes.",
                personal_data=True,
            ),
            ConnectorDefinition(
                name="telegram",
                capability_prefixes=("messages.",),
                configuration_probe=_telegram_configuration,
                setup_docs="Set Telegram bot env vars for config checks only; this connector does not send messages.",
                personal_data=True,
                excluded_capabilities=(
                    "messages.probe",
                    "messages.draft_from_lead",
                    "messages.open_handoff_instructions",
                    "messages.inbox.import_manual",
                    "messages.inbox.list",
                    "messages.inbox.show",
                    "messages.inbox.draft_reply",
                    "messages.macos.status",
                    "messages.macos.allowed_recipients.manage",
                ),
            ),
            ConnectorDefinition(
                name="reddit",
                capability_prefixes=("reddit.",),
                configuration_probe=_reddit_configuration,
                setup_docs=(
                    "Set REDDIT_ENABLED=true with Reddit OAuth env vars and a specific REDDIT_USER_AGENT. "
                    "Status/doctor commands fetch no posts or comments; web scraping fallback is forbidden."
                ),
            ),
            ConnectorDefinition(
                name="v2ex",
                capability_prefixes=("v2ex.",),
                configuration_probe=_v2ex_configuration,
                cache_probe=_v2ex_cache_state,
                setup_docs=(
                    "Set V2EX_ENABLED=true for documented read-only V2EX API access. "
                    "V2EX_TOKEN is optional and redacted; member/profile/notification/write endpoints are absent."
                ),
            ),
            ConnectorDefinition(
                name="apple_business",
                capability_prefixes=("apple_business.",),
                configuration_probe=_apple_business_configuration,
                setup_docs=(
                    "Apple Messages for Business live provider is disabled by default. "
                    "Use `apple-business mock-inbound` for local tests only."
                ),
                personal_data=True,
                excluded_capabilities=(
                    "apple_business.doctor",
                    "apple_business.status",
                    "apple_business.inbound.receive",
                    "apple_business.message.draft_response",
                    "apple_business.conversation.status",
                ),
            ),
        ]
    )


def _weather_configuration(env: Mapping[str, str]) -> ConnectorConfiguration:
    status = weather_provider_status()
    return ConnectorConfiguration(
        configured=bool(status["configured"]),
        provider_name=str(status["provider"]),
        setup_hint="Open-Meteo is the default no-key provider. Set WEATHER_PROVIDER=disabled to disable weather.",
        metadata={"provider_status": status},
    )


def _web_configuration(env: Mapping[str, str]) -> ConnectorConfiguration:
    provider = _env(env, "WEB_SEARCH_PROVIDER") or "disabled"
    configured = provider in {"searxng", "brave", "serpapi"}
    hint = "Configure a search provider explicitly, such as BRAVE_SEARCH_API_KEY plus BRAVE_SEARCH_ENABLED=true, or leave web search disabled."
    if provider == "brave":
        hint = "Brave also requires BRAVE_SEARCH_API_KEY, BRAVE_SEARCH_ENABLED=true, and paid/quota policy opt-in."
    elif provider == "searxng":
        hint = "SearXNG requires SEARXNG_BASE_URL and SEARXNG_ENABLED=true."
    elif provider == "serpapi":
        hint = "SerpAPI requires SERPAPI_API_KEY, SERPAPI_ENABLED=true, and paid/quota policy opt-in."
    elif provider not in {"disabled", "auto"}:
        configured = False
        hint = "Configured web search provider is not supported by this build."
    return ConnectorConfiguration(configured=configured and provider != "disabled", provider_name=provider, setup_hint=hint)


def _browser_configuration(env: Mapping[str, str]) -> ConnectorConfiguration:
    provider = _env(env, "BROWSER_CONNECTOR") or "url_workflow"
    if provider == "url_workflow":
        return ConnectorConfiguration(
            configured=True,
            provider_name=provider,
            setup_hint=(
                "Use explicit URL commands. Native selected-tab reading is unavailable by default; "
                "browser history, cookies, sessions, passwords, and profile databases are not accessed."
            ),
        )
    return ConnectorConfiguration(
        configured=False,
        provider_name=provider,
        setup_hint="Configured browser connector is unsupported; use url_workflow explicit URL commands.",
    )


def _calendar_configuration(env: Mapping[str, str]) -> ConnectorConfiguration:
    provider = _env(env, "CALENDAR_CONNECTOR") or "disabled"
    return ConnectorConfiguration(
        configured=provider != "disabled",
        provider_name=provider,
        setup_hint="Set CALENDAR_CONNECTOR=applescript only after approving read-only calendar setup.",
    )


def _contacts_configuration(env: Mapping[str, str]) -> ConnectorConfiguration:
    provider = _env(env, "CONTACTS_CONNECTOR") or "disabled"
    return ConnectorConfiguration(
        configured=provider != "disabled",
        provider_name=provider,
        setup_hint="Set CONTACTS_CONNECTOR=applescript only after approving read-only contacts setup.",
    )


def _email_configuration(env: Mapping[str, str]) -> ConnectorConfiguration:
    provider = _env(env, "EMAIL_CONNECTOR") or "disabled"
    configured = provider == "imap" and all(_env(env, key) for key in ("IMAP_HOST", "IMAP_USERNAME", "IMAP_PASSWORD"))
    return ConnectorConfiguration(
        configured=configured,
        provider_name=provider,
        setup_hint=(
            "Set EMAIL_CONNECTOR=imap with IMAP_HOST, IMAP_USERNAME, and IMAP_PASSWORD "
            "via environment or external secret setup."
        ),
    )


def _messages_configuration(env: Mapping[str, str]) -> ConnectorConfiguration:
    provider = _env(env, "MESSAGES_CONNECTOR") or "disabled"
    last_probe = last_probe_result()
    return ConnectorConfiguration(
        configured=False if provider == "disabled" else True,
        provider_name=provider,
        setup_hint="Messages live connector is intentionally unavailable until a safe permissioned path exists.",
        metadata={
            "macos_probe": last_probe or {"status": "not_run"},
            "send_capability_known": False,
            "private_messages_db_accessed": False,
            "full_disk_access_required": False,
        },
    )


def _tasks_configuration(env: Mapping[str, str]) -> ConnectorConfiguration:
    provider = _env(env, "TASKS_CONNECTOR") or "disabled"
    configured = provider == "mock"
    hint = "Tasks connector is disabled by default; TASKS_CONNECTOR=mock is for tests only."
    if provider not in {"disabled", "mock"}:
        hint = "Configured tasks connector is not supported by this build."
    return ConnectorConfiguration(configured=configured, provider_name=provider, setup_hint=hint)


def _serpapi_configuration(env: Mapping[str, str]) -> ConnectorConfiguration:
    enabled = _env(env, "SERPAPI_ENABLED", "false").strip().casefold() in {"1", "true", "yes", "on"}
    key_present = bool(_env(env, "SERPAPI_API_KEY"))
    allow_paid = _env(env, "ALLOW_PAID_APIS", "false").strip().casefold() in {"1", "true", "yes", "on"}
    try:
        max_paid_calls = int(_env(env, "MAX_PAID_API_CALLS_PER_DAY", "0") or "0")
    except ValueError:
        max_paid_calls = 0
    configured = key_present and enabled
    if not key_present:
        hint = "Set SERPAPI_API_KEY and SERPAPI_ENABLED=true."
    elif not enabled:
        hint = "Set SERPAPI_ENABLED=true after confirming quota and cost-policy settings."
    elif not allow_paid or max_paid_calls <= 0:
        hint = "Set ALLOW_PAID_APIS=true and MAX_PAID_API_CALLS_PER_DAY>0 before using SerpAPI."
    else:
        hint = "SerpAPI is configured and allowed by paid/quota policy."
    return ConnectorConfiguration(
        configured=configured,
        provider_name="serpapi",
        setup_hint=hint,
        metadata={
            "enabled_by_config": enabled,
            "api_key_configured": key_present,
            "requires_api_key": True,
            "paid_or_quota_limited": True,
            "allow_paid_apis": allow_paid,
            "max_paid_api_calls_per_day": max_paid_calls,
            "disabled_by_cost_policy": not allow_paid or max_paid_calls <= 0,
            "timeout_seconds": _env(env, "SERPAPI_TIMEOUT_SECONDS", "10"),
            "max_results": _env(env, "SERPAPI_MAX_RESULTS", "10"),
            "captcha_bypass_supported": False,
        },
    )


def _searxng_configuration(env: Mapping[str, str]) -> ConnectorConfiguration:
    from urllib.parse import urlparse

    base_url = _env(env, "SEARXNG_BASE_URL").strip()
    parsed = urlparse(base_url)
    base_url_valid = parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    enabled = _env(env, "SEARXNG_ENABLED", "false").strip().casefold() in {"1", "true", "yes", "on"}
    configured = base_url_valid and enabled
    if not base_url:
        hint = "Set SEARXNG_BASE_URL to your self-hosted SearXNG instance and SEARXNG_ENABLED=true."
    elif not base_url_valid:
        hint = "SEARXNG_BASE_URL must be a valid http(s) URL for a self-hosted SearXNG instance."
    elif not enabled:
        hint = "Set SEARXNG_ENABLED=true after confirming the configured instance allows JSON output."
    else:
        hint = "SearXNG is configured; JSON output must be enabled on the instance."
    return ConnectorConfiguration(
        configured=configured,
        provider_name="searxng",
        setup_hint=hint,
        metadata={
            "enabled_by_config": enabled,
            "base_url_configured": bool(base_url),
            "base_url_host": (parsed.hostname or "") if base_url_valid else "",
            "requires_api_key": False,
            "json_output_required": True,
            "default_public_instance_used": False,
        },
    )


def _brave_configuration(env: Mapping[str, str]) -> ConnectorConfiguration:
    enabled = _env(env, "BRAVE_SEARCH_ENABLED", "false").strip().casefold() in {"1", "true", "yes", "on"}
    key_present = bool(_env(env, "BRAVE_SEARCH_API_KEY"))
    allow_paid = _env(env, "ALLOW_PAID_APIS", "false").strip().casefold() in {"1", "true", "yes", "on"}
    try:
        max_paid_calls = int(_env(env, "MAX_PAID_API_CALLS_PER_DAY", "0") or "0")
    except ValueError:
        max_paid_calls = 0
    configured = key_present and enabled
    if not key_present:
        hint = "Set BRAVE_SEARCH_API_KEY and BRAVE_SEARCH_ENABLED=true."
    elif not enabled:
        hint = "Set BRAVE_SEARCH_ENABLED=true after confirming quota and cost-policy settings."
    elif not allow_paid or max_paid_calls <= 0:
        hint = "Set ALLOW_PAID_APIS=true and MAX_PAID_API_CALLS_PER_DAY>0 before using Brave."
    else:
        hint = "Brave Search is configured and allowed by paid/quota policy."
    return ConnectorConfiguration(
        configured=configured,
        provider_name="brave",
        setup_hint=hint,
        metadata={
            "enabled_by_config": enabled,
            "api_key_configured": key_present,
            "requires_api_key": True,
            "paid_or_quota_limited": True,
            "allow_paid_apis": allow_paid,
            "max_paid_api_calls_per_day": max_paid_calls,
            "disabled_by_cost_policy": not allow_paid or max_paid_calls <= 0,
            "safe_search": _env(env, "BRAVE_SEARCH_SAFE_SEARCH", "true"),
            "timeout_seconds": _env(env, "BRAVE_SEARCH_TIMEOUT_SECONDS", "10"),
            "max_results": _env(env, "BRAVE_SEARCH_MAX_RESULTS", "10"),
        },
    )


def _weatherapi_configuration(env: Mapping[str, str]) -> ConnectorConfiguration:
    return _secret_configuration(provider_status("weatherapi", environ=env))


def _gmail_configuration(env: Mapping[str, str]) -> ConnectorConfiguration:
    return _secret_configuration(provider_status("gmail", environ=env))


def _telegram_configuration(env: Mapping[str, str]) -> ConnectorConfiguration:
    return _secret_configuration(provider_status("telegram", environ=env))


def _reddit_configuration(env: Mapping[str, str]) -> ConnectorConfiguration:
    return _secret_configuration(provider_status("reddit", environ=env))


def _v2ex_configuration(env: Mapping[str, str]) -> ConnectorConfiguration:
    from agent.forums.v2ex.client import load_v2ex_config, v2ex_setup_hint

    config = load_v2ex_config(env)
    return ConnectorConfiguration(
        configured=config.enabled,
        provider_name="v2ex",
        setup_hint=v2ex_setup_hint(config),
        metadata={
            "enabled_by_config": config.enabled,
            "token_configured": config.token_configured,
            "requires_api_key": False,
            "optional_token_supported": True,
            "timeout_seconds": config.timeout_seconds,
            "max_requests_per_hour": config.max_requests_per_hour,
            "cache_enabled": config.cache_enabled,
            "cache_ttl_seconds": config.cache_ttl_seconds,
            "read_only": True,
            "write_capabilities_enabled": False,
            "member_profile_access_enabled": False,
            "notification_access_enabled": False,
        },
    )


def _apple_business_configuration(env: Mapping[str, str]) -> ConnectorConfiguration:
    provider = _env(env, "APPLE_BUSINESS_PROVIDER") or "disabled"
    enabled = (_env(env, "APPLE_BUSINESS_ENABLED") or "false").casefold() in {"1", "true", "yes", "on"}
    account_id_present = bool(_env(env, "APPLE_BUSINESS_ACCOUNT_ID"))
    configured = enabled and provider != "disabled" and account_id_present
    return ConnectorConfiguration(
        configured=configured,
        provider_name=provider,
        setup_hint=(
            "Configure an Apple Messages for Business provider/account only after provider review; "
            "live sends remain CRITICAL and disabled by default."
        ),
        metadata={
            "enabled_by_config": enabled,
            "account_id_configured": account_id_present,
            "webhook_url_configured": bool(_env(env, "APPLE_BUSINESS_WEBHOOK_URL")),
            "send_endpoint_configured": bool(_env(env, "APPLE_BUSINESS_SEND_ENDPOINT")),
            "send_enabled": False,
            "mock_provider_available": True,
        },
    )


def _secret_configuration(status: Any) -> ConnectorConfiguration:
    payload = status.to_dict()
    return ConnectorConfiguration(
        configured=bool(payload["configured"]),
        provider_name=str(payload["name"]),
        setup_hint=str(payload["setup_hint"]),
        metadata={
            "allowed": payload["allowed"],
            "default": payload["default"],
            "paid_or_quota_limited": payload["paid_or_quota_limited"],
            "disabled_by_cost_policy": payload["disabled_by_cost_policy"],
            "present_env": payload["present_env"],
            "missing_env": payload["missing_env"],
            "provider_status": payload,
        },
    )


def _weather_cache_state(env: Mapping[str, str]) -> str | dict[str, Any]:
    path = Path(_env(env, "WEATHER_CACHE_PATH", "data/weather_cache.json"))
    if not path.exists():
        return {"configured": True, "path": str(path), "entries": 0}
    try:
        import json

        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"configured": True, "path": str(path), "state": "unreadable"}
    entries = len(payload) if isinstance(payload, Mapping) else 0
    return {"configured": True, "path": str(path), "entries": entries}


def _v2ex_cache_state(env: Mapping[str, str]) -> str | dict[str, Any]:
    from agent.forums.v2ex.cache import V2EXCache
    from agent.forums.v2ex.client import load_v2ex_config

    config = load_v2ex_config(env)
    return V2EXCache(ttl_seconds=config.cache_ttl_seconds, enabled=config.cache_enabled).status()


def _env(env: Mapping[str, str], key: str, default: str = "") -> str:
    return env.get(key, default) or default
