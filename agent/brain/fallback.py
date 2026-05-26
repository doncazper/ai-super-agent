from __future__ import annotations

from agent.brain.provider_router import BrainProviderRouteDecision, BrainRouteRequest, route_provider
from agent.brain.registry import BrainProviderRegistry


def fallback_status(registry: BrainProviderRegistry) -> dict[str, object]:
    config = registry.config
    return {
        "status": "ok",
        "fallback_enabled": config.fallback_enabled,
        "auto_switch_on_failure": config.auto_switch_on_failure,
        "max_fallback_attempts": config.max_fallback_attempts,
        "allow_cloud_fallback": config.allow_cloud_fallback,
        "provider_order": list(config.provider_order),
        "task_provider_map": dict(config.task_provider_map or {}),
        "notes": [
            "Fallback is disabled by default.",
            "Provider routing does not execute model calls or tools.",
            "Cloud/paid fallback is disabled unless explicitly configured and policy-reviewed.",
        ],
    }


def dry_run_switch(registry: BrainProviderRegistry, provider_id: str) -> dict[str, object]:
    decision = route_provider(
        registry,
        BrainRouteRequest(requested_provider=provider_id, user_override=True, task_type="manual_switch"),
    )
    return {
        "status": "ok" if decision.selected_provider else "blocked",
        "dry_run": True,
        "would_select": decision.selected_provider,
        "decision": decision.to_dict(),
        "persisted_config_changed": False,
        "model_call_performed": False,
        "tool_execution_performed": False,
    }


def decision_to_payload(decision: BrainProviderRouteDecision) -> dict[str, object]:
    return decision.to_dict()
