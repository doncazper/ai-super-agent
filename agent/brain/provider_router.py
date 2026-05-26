from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Mapping

from agent.brain.base import BrainProvider
from agent.brain.config import BrainRuntimeConfig
from agent.brain.registry import BrainProviderRegistry


CLOUD_PROVIDER_IDS = frozenset({"openai", "anthropic", "gemini", "azure_openai", "bedrock", "mistral"})


@dataclass(frozen=True)
class BrainRouteRequest:
    requested_provider: str | None = None
    task_type: str = "chat"
    requires_tool_calls: bool = False
    requires_streaming: bool = False
    requires_json_schema: bool = False
    safe_mode: bool = False
    no_tools: bool = False
    user_override: bool = False
    include_health: bool = False


@dataclass(frozen=True)
class ProviderRouteAttempt:
    provider_id: str
    status: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"provider_id": self.provider_id, "status": self.status, "reason": self.reason}


@dataclass(frozen=True)
class BrainProviderRouteDecision:
    status: str
    selected_provider: str | None
    reason: str
    requested_provider: str | None = None
    task_type: str = "chat"
    fallback_enabled: bool = False
    fallback_used: bool = False
    attempts: tuple[ProviderRouteAttempt, ...] = ()
    provider_order: tuple[str, ...] = ()
    health_checked: bool = False
    audit_event: Mapping[str, object] = field(default_factory=dict)
    safety: Mapping[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "selected_provider": self.selected_provider,
            "reason": self.reason,
            "requested_provider": self.requested_provider,
            "task_type": self.task_type,
            "fallback_enabled": self.fallback_enabled,
            "fallback_used": self.fallback_used,
            "attempts": [attempt.to_dict() for attempt in self.attempts],
            "provider_order": list(self.provider_order),
            "health_checked": self.health_checked,
            "audit_event": dict(self.audit_event),
            "safety": dict(self.safety),
        }


class BrainProviderRouter:
    """Deterministic provider selection without model generation.

    The router records a decision only. It does not execute model calls, grant
    tools, change policy, or switch persisted configuration.
    """

    def __init__(self, registry: BrainProviderRegistry) -> None:
        self.registry = registry
        self.config = registry.config

    def route(self, request: BrainRouteRequest) -> BrainProviderRouteDecision:
        candidates = self._candidate_order(request)
        attempts: list[ProviderRouteAttempt] = []
        max_attempts = self._max_attempts(request)
        for provider_id in candidates[:max_attempts]:
            attempt = self._evaluate_provider(provider_id, request)
            attempts.append(attempt)
            if attempt.status == "selected":
                return self._decision(
                    status="selected",
                    selected_provider=provider_id,
                    reason=attempt.reason,
                    request=request,
                    attempts=attempts,
                    fallback_used=bool(request.requested_provider and provider_id != _normalize(request.requested_provider)),
                )
            if request.requested_provider and not self.config.fallback_enabled:
                break
        reason = attempts[-1].reason if attempts else "no_provider_candidates"
        return self._decision(
            status="blocked",
            selected_provider=None,
            reason=reason,
            request=request,
            attempts=attempts,
            fallback_used=False,
        )

    def _candidate_order(self, request: BrainRouteRequest) -> tuple[str, ...]:
        requested = _normalize(request.requested_provider or "")
        if requested:
            if not self.config.fallback_enabled:
                return (requested,)
            order = [requested]
            order.extend(provider_id for provider_id in self.config.provider_order if _normalize(provider_id) != requested)
            return tuple(order)
        task_provider = _normalize((self.config.task_provider_map or {}).get(_normalize(request.task_type), ""))
        if task_provider:
            if not self.config.fallback_enabled:
                return (task_provider,)
            order = [task_provider]
            order.extend(provider_id for provider_id in self.config.provider_order if _normalize(provider_id) != task_provider)
            return tuple(order)
        return tuple(_normalize(provider_id) for provider_id in self.config.provider_order)

    def _max_attempts(self, request: BrainRouteRequest) -> int:
        if not self.config.fallback_enabled:
            return 1
        configured = max(1, self.config.max_fallback_attempts)
        if request.requested_provider:
            return min(configured + 1, len(self.config.provider_order) + 1)
        return min(configured, len(self.config.provider_order))

    def _evaluate_provider(self, provider_id: str, request: BrainRouteRequest) -> ProviderRouteAttempt:
        normalized = _normalize(provider_id)
        if normalized in CLOUD_PROVIDER_IDS and not self.config.allow_cloud_fallback:
            return ProviderRouteAttempt(normalized, "skipped", "cloud_fallback_disabled")
        provider = self.registry.get_provider(normalized)
        if provider is None:
            return ProviderRouteAttempt(normalized, "skipped", "unknown_provider")
        if not provider.is_configured():
            return ProviderRouteAttempt(normalized, "skipped", "provider_not_configured")
        if not provider.is_available():
            return ProviderRouteAttempt(normalized, "skipped", "provider_unavailable")
        if request.requires_tool_calls and not request.no_tools and self.config.require_tool_call_support_for_tools:
            if not provider.supports_tool_calls():
                return ProviderRouteAttempt(normalized, "skipped", "tool_call_support_required")
        if request.requires_streaming and not provider.supports_streaming():
            return ProviderRouteAttempt(normalized, "skipped", "streaming_not_supported")
        if request.requires_json_schema and not provider.supports_json_schema():
            return ProviderRouteAttempt(normalized, "skipped", "json_schema_not_supported")
        return ProviderRouteAttempt(normalized, "selected", "provider_matches_requirements")

    def _decision(
        self,
        *,
        status: str,
        selected_provider: str | None,
        reason: str,
        request: BrainRouteRequest,
        attempts: list[ProviderRouteAttempt],
        fallback_used: bool,
    ) -> BrainProviderRouteDecision:
        return BrainProviderRouteDecision(
            status=status,
            selected_provider=selected_provider,
            reason=reason,
            requested_provider=_normalize(request.requested_provider or "") or None,
            task_type=_normalize(request.task_type) or "chat",
            fallback_enabled=self.config.fallback_enabled,
            fallback_used=fallback_used,
            attempts=tuple(attempts),
            provider_order=tuple(_normalize(provider_id) for provider_id in self.config.provider_order),
            health_checked=request.include_health,
            audit_event={
                "event_type": "brain.provider_route_decision",
                "recorded_at": datetime.now(timezone.utc).isoformat(),
                "selected_provider": selected_provider,
                "fallback_used": fallback_used,
                "model_call_performed": False,
                "tool_execution_performed": False,
            },
            safety={
                "no_model_call": True,
                "no_tool_execution": True,
                "policy_unchanged": True,
                "approval_rules_unchanged": True,
                "cloud_fallback_allowed": self.config.allow_cloud_fallback,
                "auto_switch_on_failure": self.config.auto_switch_on_failure,
            },
        )


def _normalize(value: str) -> str:
    return value.strip().casefold().replace("-", "_")


def infer_route_request_from_message(message: str, *, provider_id: str | None = None) -> BrainRouteRequest:
    lowered = message.casefold()
    requires_tool_calls = any(token in lowered for token in ("tool", "weather", "search", "fetch", "time", "file"))
    requires_json_schema = any(token in lowered for token in ("json", "schema", "structured"))
    return BrainRouteRequest(
        requested_provider=provider_id,
        task_type="tool_call" if requires_tool_calls else "chat",
        requires_tool_calls=requires_tool_calls,
        requires_json_schema=requires_json_schema,
    )


def route_provider(
    registry: BrainProviderRegistry,
    request: BrainRouteRequest | None = None,
) -> BrainProviderRouteDecision:
    return BrainProviderRouter(registry).route(request or BrainRouteRequest())


def provider_capabilities(provider: BrainProvider) -> dict[str, bool]:
    return {
        "supports_tool_calls": provider.supports_tool_calls(),
        "supports_streaming": provider.supports_streaming(),
        "supports_json_schema": provider.supports_json_schema(),
        "supports_reasoning_content": provider.supports_reasoning_content(),
    }
