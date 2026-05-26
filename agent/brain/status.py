from __future__ import annotations

from typing import Mapping

from agent.autonomy.model_switching import model_switch_payload
from agent.brain.fallback import fallback_status
from agent.brain.provider_router import BrainRouteRequest, infer_route_request_from_message, route_provider
from agent.brain.config import BrainRuntimeConfig
from agent.brain.registry import BrainProviderRegistry, default_registry


def build_brain_registry(env: Mapping[str, str] | None = None) -> BrainProviderRegistry:
    return default_registry(BrainRuntimeConfig.from_env(env))


def brain_providers(env: Mapping[str, str] | None = None) -> dict[str, object]:
    registry = build_brain_registry(env)
    return {
        "status": "ok",
        "default_provider": registry.config.default_provider,
        "fallback_enabled": registry.config.fallback_enabled,
        "providers": [status.to_dict() for status in registry.list_provider_status()],
        "notes": [
            "Provider listing is metadata-only and does not call model runtimes.",
            "LM Studio remains the default compatibility provider.",
        ],
    }


def brain_status(env: Mapping[str, str] | None = None) -> dict[str, object]:
    registry = build_brain_registry(env)
    default_status = registry.provider_status(registry.config.default_provider)
    return {
        "status": "ok" if default_status.registered else "requires_setup",
        "default_provider": default_status.to_dict(),
        "fallback_enabled": registry.config.fallback_enabled,
        "provider_order": list(registry.config.provider_order),
        "lmstudio_default": registry.config.default_provider == "lmstudio",
        "no_model_call_performed": True,
    }


def brain_doctor(env: Mapping[str, str] | None = None, provider_id: str | None = None) -> dict[str, object]:
    registry = build_brain_registry(env)
    if provider_id:
        provider = registry.get_provider(provider_id)
        health: dict[str, object] = {
            "providers": [provider.health_check().to_dict()] if provider is not None else [],
            "default_provider_id": registry.config.default_provider,
            "default_provider_registered": registry.default_provider() is not None,
            "fallback_enabled": registry.config.fallback_enabled,
            "unknown_provider": provider_id if provider is None else "",
        }
    else:
        health = registry.health_summary()
    return {
        "status": "ok",
        "default_provider": registry.config.default_provider,
        "fallback_enabled": registry.config.fallback_enabled,
        "health": health,
        "safety": {
            "no_model_generation": True,
            "no_tool_execution": True,
            "no_mcp_server": True,
            "no_network_listener": True,
            "no_memory_write": True,
        },
    }


def brain_health(provider_id: str | None = None, env: Mapping[str, str] | None = None) -> dict[str, object]:
    registry = build_brain_registry(env)
    if provider_id:
        provider = registry.get_provider(provider_id)
        if provider is None:
            return {
                "status": "unknown_provider",
                "provider_id": provider_id,
                "setup_hint": "Configure or register a supported brain provider.",
            }
        return {
            "status": "ok",
            "provider": provider.health_check().to_dict(),
            "no_model_generation": True,
            "no_tool_execution": True,
        }
    return {
        "status": "ok",
        "health": registry.health_summary(),
        "no_model_generation": True,
        "no_tool_execution": True,
    }


def brain_fallback_status(env: Mapping[str, str] | None = None) -> dict[str, object]:
    return fallback_status(build_brain_registry(env))


def brain_switch_dry_run(
    provider_id: str,
    env: Mapping[str, str] | None = None,
    *,
    tool_call_support_required: bool = False,
    session_id: str = "",
) -> dict[str, object]:
    return model_switch_payload(
        provider_id,
        env=env,
        dry_run=True,
        session_id=session_id,
        tool_call_support_required=tool_call_support_required,
    )


def brain_switch_request(
    provider_id: str,
    env: Mapping[str, str] | None = None,
    *,
    tool_call_support_required: bool = False,
    session_id: str = "",
) -> dict[str, object]:
    return model_switch_payload(
        provider_id,
        env=env,
        dry_run=False,
        session_id=session_id,
        tool_call_support_required=tool_call_support_required,
    )


def brain_route_message(
    message: str,
    *,
    provider_id: str | None = None,
    task_type: str | None = None,
    requires_tool_calls: bool = False,
    requires_streaming: bool = False,
    requires_json_schema: bool = False,
    no_tools: bool = False,
    env: Mapping[str, str] | None = None,
) -> dict[str, object]:
    registry = build_brain_registry(env)
    inferred = infer_route_request_from_message(message, provider_id=provider_id)
    request = BrainRouteRequest(
        requested_provider=provider_id,
        task_type=task_type or inferred.task_type,
        requires_tool_calls=False if no_tools else (requires_tool_calls or inferred.requires_tool_calls),
        requires_streaming=requires_streaming,
        requires_json_schema=requires_json_schema or inferred.requires_json_schema,
        no_tools=no_tools,
        user_override=bool(provider_id),
    )
    return {
        "status": "ok",
        "message_redacted": _redact_message(message),
        "decision": route_provider(registry, request).to_dict(),
    }


def _redact_message(message: str) -> str:
    text = " ".join(message.split())
    if len(text) <= 80:
        return text
    return f"{text[:77]}..."
