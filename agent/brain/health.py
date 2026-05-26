from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping

from agent.brain.config import BrainRuntimeConfig
from agent.brain.registry import BrainProviderRegistry, default_registry


@dataclass(frozen=True)
class BrainHealthOptions:
    provider_id: str | None = None
    include_unconfigured: bool = True


def collect_health(
    options: BrainHealthOptions | None = None,
    *,
    registry: BrainProviderRegistry | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, object]:
    active_options = options or BrainHealthOptions()
    active_registry = registry or default_registry(BrainRuntimeConfig.from_env(env))
    retrieved_at = datetime.now(timezone.utc).isoformat()
    if active_options.provider_id:
        provider = active_registry.get_provider(active_options.provider_id)
        if provider is None:
            return {
                "status": "unknown_provider",
                "provider_id": active_options.provider_id,
                "retrieved_at": retrieved_at,
                "setup_hint": "Configure or register a supported brain provider.",
                "no_model_generation": True,
                "no_tool_execution": True,
                "personal_data_used": False,
            }
        return {
            "status": "ok",
            "retrieved_at": retrieved_at,
            "provider": provider.health_check().to_dict(),
            "no_model_generation": True,
            "no_tool_execution": True,
            "personal_data_used": False,
        }
    return {
        "status": "ok",
        "retrieved_at": retrieved_at,
        "health": active_registry.health_summary(include_unconfigured=active_options.include_unconfigured),
        "no_model_generation": True,
        "no_tool_execution": True,
        "personal_data_used": False,
    }
