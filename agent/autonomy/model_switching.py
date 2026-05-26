from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Mapping
from uuid import uuid4

from agent.brain.config import BrainRuntimeConfig
from agent.brain.provider_router import BrainRouteRequest, CLOUD_PROVIDER_IDS, route_provider
from agent.brain.registry import BrainProviderRegistry, default_registry


@dataclass(frozen=True)
class ModelSwitchCompatibilityCheck:
    status: str
    provider_known: bool
    provider_configured: bool
    provider_available: bool
    tool_call_compatible: bool
    cloud_or_paid_blocked: bool
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "provider_known": self.provider_known,
            "provider_configured": self.provider_configured,
            "provider_available": self.provider_available,
            "tool_call_compatible": self.tool_call_compatible,
            "cloud_or_paid_blocked": self.cloud_or_paid_blocked,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ModelSwitchRecord:
    switch_id: str
    from_provider: str
    from_model: str
    to_provider: str
    to_model: str
    reason: str
    session_id: str
    tool_call_support_required: bool
    compatibility_check: ModelSwitchCompatibilityCheck
    context_migration_summary: str
    risk_level: str
    approved_by_user: bool
    audit_ids: tuple[str, ...] = ()
    rollback_plan: Mapping[str, object] = field(default_factory=dict)
    status: str = "preview"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, object]:
        return {
            "switch_id": self.switch_id,
            "from_provider": self.from_provider,
            "from_model": self.from_model,
            "to_provider": self.to_provider,
            "to_model": self.to_model,
            "reason": self.reason,
            "session_id": self.session_id,
            "tool_call_support_required": self.tool_call_support_required,
            "compatibility_check": self.compatibility_check.to_dict(),
            "context_migration_summary": self.context_migration_summary,
            "risk_level": self.risk_level,
            "approved_by_user": self.approved_by_user,
            "audit_ids": list(self.audit_ids),
            "rollback_plan": dict(self.rollback_plan),
            "status": self.status,
            "created_at": self.created_at,
        }


def build_model_switch_record(
    provider_id: str,
    *,
    registry: BrainProviderRegistry | None = None,
    reason: str = "manual_switch",
    session_id: str = "",
    tool_call_support_required: bool = False,
    approved_by_user: bool = False,
    dry_run: bool = True,
) -> tuple[ModelSwitchRecord, dict[str, object]]:
    active_registry = registry or default_registry(BrainRuntimeConfig.from_env())
    normalized_provider = _normalize_provider_id(provider_id)
    decision = route_provider(
        active_registry,
        BrainRouteRequest(
            requested_provider=normalized_provider,
            task_type="manual_switch",
            requires_tool_calls=tool_call_support_required,
            user_override=True,
        ),
    )
    compatibility = _compatibility_from_decision(
        active_registry,
        normalized_provider,
        decision_reason=str(decision.reason),
        selected_provider=decision.selected_provider,
        tool_call_support_required=tool_call_support_required,
    )
    from_provider = active_registry.config.default_provider
    record_status = "preview" if dry_run and decision.selected_provider else "blocked"
    if not dry_run:
        record_status = "blocked"
    record = ModelSwitchRecord(
        switch_id=f"model_switch_{uuid4().hex[:12]}",
        from_provider=from_provider,
        from_model=_configured_model(active_registry, from_provider),
        to_provider=normalized_provider,
        to_model=_configured_model(active_registry, normalized_provider),
        reason=_redact_reason(reason),
        session_id=session_id,
        tool_call_support_required=tool_call_support_required,
        compatibility_check=compatibility,
        context_migration_summary=(
            "No context migrated. Session continuity is opt-in, redacted, and does not carry personal data by default."
        ),
        risk_level="LOW" if dry_run else "MEDIUM",
        approved_by_user=approved_by_user,
        audit_ids=(),
        rollback_plan={
            "previous_provider": from_provider,
            "previous_model": _configured_model(active_registry, from_provider),
            "persisted_config_changed": False,
            "rollback_available": True,
            "rollback_steps": [
                "Keep existing default provider configuration unchanged.",
                "If a future approved switch fails, restore the previous provider/model before another model call.",
            ],
        },
        status=record_status,
    )
    return record, decision.to_dict()


def model_switch_payload(
    provider_id: str,
    *,
    env: Mapping[str, str] | None = None,
    dry_run: bool = True,
    reason: str = "manual_switch",
    session_id: str = "",
    tool_call_support_required: bool = False,
) -> dict[str, object]:
    registry = default_registry(BrainRuntimeConfig.from_env(env))
    record, decision = build_model_switch_record(
        provider_id,
        registry=registry,
        reason=reason,
        session_id=session_id,
        tool_call_support_required=tool_call_support_required,
        approved_by_user=False,
        dry_run=dry_run,
    )
    blocked_reason = ""
    if not dry_run:
        blocked_reason = "persistent_model_switch_not_implemented"
    elif not decision.get("selected_provider"):
        blocked_reason = str(decision.get("reason") or "provider_not_selected")
    return {
        "status": "ok" if dry_run and decision.get("selected_provider") else "blocked",
        "dry_run": dry_run,
        "switch_record": record.to_dict(),
        "decision": decision,
        "blocked_reason": blocked_reason,
        "persisted_config_changed": False,
        "model_call_performed": False,
        "tool_execution_performed": False,
        "memory_written": False,
        "user_visible_notice": _notice(record),
    }


def _compatibility_from_decision(
    registry: BrainProviderRegistry,
    provider_id: str,
    *,
    decision_reason: str,
    selected_provider: str | None,
    tool_call_support_required: bool,
) -> ModelSwitchCompatibilityCheck:
    provider = registry.get_provider(provider_id)
    provider_known = provider is not None
    provider_configured = bool(provider and provider.is_configured())
    provider_available = bool(provider and provider.is_available())
    tool_call_compatible = bool(provider and (not tool_call_support_required or provider.supports_tool_calls()))
    cloud_or_paid_blocked = provider_id in CLOUD_PROVIDER_IDS and not registry.config.allow_cloud_fallback
    return ModelSwitchCompatibilityCheck(
        status="compatible" if selected_provider else "blocked",
        provider_known=provider_known,
        provider_configured=provider_configured,
        provider_available=provider_available,
        tool_call_compatible=tool_call_compatible,
        cloud_or_paid_blocked=cloud_or_paid_blocked,
        reason=decision_reason,
    )


def _configured_model(registry: BrainProviderRegistry, provider_id: str) -> str:
    normalized = _normalize_provider_id(provider_id)
    config = registry.config
    if normalized == "lmstudio":
        import os

        return os.getenv("LMSTUDIO_MODEL", "")
    if normalized == "llama_cpp_server":
        return config.llama_cpp_server_model
    if normalized == "ollama":
        return config.ollama_model
    if normalized == "llama_cpp_inprocess":
        return config.llama_cpp_inprocess_model_path
    if normalized == "mlx":
        return config.mlx_model
    return ""


def _notice(record: ModelSwitchRecord) -> str:
    if record.status == "preview":
        return f"Dry-run only: {record.from_provider} would switch to {record.to_provider}; no config was changed."
    return f"Model switch to {record.to_provider} is blocked; no config was changed."


def _redact_reason(reason: str) -> str:
    text = " ".join(reason.split())
    lowered = text.casefold()
    sensitive_tokens = ("api_key", "token", "secret", "password", "authorization")
    if any(token in lowered for token in sensitive_tokens):
        return "[REDACTED]"
    return text[:200]


def _normalize_provider_id(provider_id: str) -> str:
    return provider_id.strip().casefold().replace("-", "_")
