from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Mapping

from agent.config.loader import load_capabilities_config
from agent.connectors.base import ConnectorConfiguration, ConnectorDefinition
from agent.connectors.errors import UnknownConnectorError
from agent.connectors.status import build_connector_status
from agent.tools.weather.provider import weather_provider_status


CONNECTOR_NAMES = ("weather", "web", "browser", "calendar", "contacts", "email", "messages", "tasks")


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
            ),
            ConnectorDefinition(
                name="tasks",
                capability_prefixes=("tasks.",),
                configuration_probe=_tasks_configuration,
                setup_docs="Tasks connector is disabled by default; TASKS_CONNECTOR=mock is for tests only.",
                personal_data=True,
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
    provider = _env(env, "WEB_SEARCH_PROVIDER") or ("brave" if _env(env, "BRAVE_SEARCH_API_KEY") else "disabled")
    configured = provider == "brave" and bool(_env(env, "BRAVE_SEARCH_API_KEY"))
    hint = "Set WEB_SEARCH_PROVIDER=brave and BRAVE_SEARCH_API_KEY, or leave disabled."
    if provider not in {"disabled", "brave"}:
        hint = "Configured web search provider is not supported by this build."
    return ConnectorConfiguration(configured=configured, provider_name=provider, setup_hint=hint)


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
    return ConnectorConfiguration(
        configured=False if provider == "disabled" else True,
        provider_name=provider,
        setup_hint="Messages live connector is intentionally unavailable until a safe permissioned path exists.",
    )


def _tasks_configuration(env: Mapping[str, str]) -> ConnectorConfiguration:
    provider = _env(env, "TASKS_CONNECTOR") or "disabled"
    configured = provider == "mock"
    hint = "Tasks connector is disabled by default; TASKS_CONNECTOR=mock is for tests only."
    if provider not in {"disabled", "mock"}:
        hint = "Configured tasks connector is not supported by this build."
    return ConnectorConfiguration(configured=configured, provider_name=provider, setup_hint=hint)


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


def _env(env: Mapping[str, str], key: str, default: str = "") -> str:
    return env.get(key, default) or default
