from __future__ import annotations

from typing import Any, Callable

from agent.web_acquisition.official_apis import OfficialApiRegistry, default_official_api_registry
from agent.web_acquisition.official_apis.errors import OfficialApiNotFoundError, normalize_official_api_error
from agent.web_acquisition.official_apis.registry import registry_status_payload


WEB_OFFICIAL_APIS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.official_apis",
        "description": "List official API provider framework metadata without provider calls.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}
WEB_OFFICIAL_API_STATUS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.official_api.status",
        "description": "Inspect one official API provider setup/status without provider calls.",
        "parameters": {
            "type": "object",
            "properties": {"provider": {"type": "string"}},
            "required": ["provider"],
            "additionalProperties": False,
        },
    },
}
WEB_OFFICIAL_API_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.official_api.search",
        "description": "Search one configured official API provider through ToolBroker.",
        "parameters": {
            "type": "object",
            "properties": {
                "provider": {"type": "string"},
                "query": {"type": "string"},
                "max_results": {"type": "integer", "minimum": 1, "maximum": 50},
                "locale": {"type": "string"},
                "safe_search": {"type": "boolean"},
            },
            "required": ["provider", "query"],
            "additionalProperties": False,
        },
    },
}

WEB_OFFICIAL_API_SCHEMAS = {
    "web.official_apis": WEB_OFFICIAL_APIS_SCHEMA,
    "web.official_api.status": WEB_OFFICIAL_API_STATUS_SCHEMA,
    "web.official_api.search": WEB_OFFICIAL_API_SEARCH_SCHEMA,
}


def make_official_api_tools(
    *, registry: OfficialApiRegistry | None = None
) -> dict[str, Callable[..., dict[str, Any]]]:
    active_registry = registry or default_official_api_registry()

    def official_apis() -> dict[str, Any]:
        return registry_status_payload(active_registry)

    def api_status(provider: str) -> dict[str, Any]:
        try:
            payload = {
                "status": "ok",
                "provider": active_registry.provider_status(provider),
                "live_call_performed": False,
                "_audit": {
                    "network_domains": [],
                    "result_summary": f"Official API provider status inspected for {provider}.",
                },
            }
        except OfficialApiNotFoundError as exc:
            payload = {
                "status": "error",
                "provider": provider,
                "errors": [normalize_official_api_error(exc)],
                "live_call_performed": False,
                "_audit": {
                    "network_domains": [],
                    "result_summary": f"Unknown official API provider status requested: {provider}.",
                },
            }
        return payload

    def api_search(
        provider: str,
        query: str,
        max_results: int = 10,
        locale: str | None = None,
        safe_search: bool = True,
    ) -> dict[str, Any]:
        response = active_registry.search(
            provider,
            query,
            max(1, min(int(max_results), 50)),
            locale=locale,
            safe_search=safe_search,
            brokered_execution=True,
        )
        payload = response.to_dict()
        payload["_audit"] = {
            "network_domains": list(response.provider_domains) if response.live_call_performed or response.status == "ok" else [],
            "result_summary": f"Official API search evaluated for provider={response.provider}; status={response.status}; live_call_performed={response.live_call_performed}.",
        }
        return payload

    return {
        "web.official_apis": official_apis,
        "web.official_api.status": api_status,
        "web.official_api.search": api_search,
    }
