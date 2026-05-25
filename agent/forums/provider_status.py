from __future__ import annotations

from typing import Any

from agent.forums.registry import ForumProviderRegistry, default_forum_provider_registry


def providers_report(registry: ForumProviderRegistry | None = None) -> dict[str, Any]:
    forum_registry = registry or default_forum_provider_registry()
    providers = [provider.to_dict() for provider in forum_registry.list_providers()]
    return {
        "status": "ok",
        "providers": providers,
        "provider_count": len(providers),
        "personal_data_accessed": False,
        "logged_in_read_performed": False,
        "network_call_performed": False,
        "write_capabilities_enabled": any(provider.get("write_capabilities") for provider in providers),
    }


def provider_status_report(provider_id: str, registry: ForumProviderRegistry | None = None) -> dict[str, Any]:
    forum_registry = registry or default_forum_provider_registry()
    provider = forum_registry.get_provider(provider_id)
    payload = provider.to_dict()
    payload.update(
        {
            "status_check": {
                "personal_data_accessed": False,
                "logged_in_read_performed": False,
                "network_call_performed": False,
                "write_capabilities_enabled": bool(provider.write_capabilities),
            }
        }
    )
    return payload


def provider_capabilities_report(provider_id: str, registry: ForumProviderRegistry | None = None) -> dict[str, Any]:
    forum_registry = registry or default_forum_provider_registry()
    payload = forum_registry.capability_summary(provider_id)
    payload.update(
        {
            "personal_data_accessed": False,
            "logged_in_read_performed": False,
            "network_call_performed": False,
        }
    )
    return payload


def provider_doctor_report(registry: ForumProviderRegistry | None = None) -> dict[str, Any]:
    forum_registry = registry or default_forum_provider_registry()
    return forum_registry.doctor()
