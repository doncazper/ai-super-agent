from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping

from agent.safety.policy import RiskLevel
from agent.safety.trust import TrustLevel


class FrontendPlatform(StrEnum):
    MACOS = "macos"
    IOS_COMPANION = "ios_companion"
    WINDOWS = "windows"
    WEB = "web"
    UNKNOWN = "unknown"


class PairingStatus(StrEnum):
    UNPAIRED = "unpaired"
    PAIRING_REQUIRED = "pairing_required"
    PAIRED = "paired"
    REVOKED = "revoked"
    EXPIRED = "expired"


class AppBridgeSurface(StrEnum):
    STATUS = "status"
    CAPABILITIES = "capabilities"
    REQUEST_ACTION_PREVIEW = "request_action_preview"
    SUBMIT_APPROVAL_DECISION = "submit_approval_decision"
    SUBMIT_ACTION_RESULT = "submit_action_result"
    FETCH_PENDING_ACTIONS = "fetch_pending_actions"
    FETCH_AUDIT_SUMMARY = "fetch_audit_summary"
    FETCH_CONNECTOR_STATUS = "fetch_connector_status"
    HEALTH_CHECK = "health_check"


APP_BRIDGE_API_SURFACES: tuple[AppBridgeSurface, ...] = tuple(AppBridgeSurface)
SENSITIVE_SURFACES: frozenset[AppBridgeSurface] = frozenset(
    {
        AppBridgeSurface.REQUEST_ACTION_PREVIEW,
        AppBridgeSurface.SUBMIT_APPROVAL_DECISION,
        AppBridgeSurface.SUBMIT_ACTION_RESULT,
        AppBridgeSurface.FETCH_PENDING_ACTIONS,
        AppBridgeSurface.FETCH_AUDIT_SUMMARY,
        AppBridgeSurface.FETCH_CONNECTOR_STATUS,
    }
)


def _value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


@dataclass(frozen=True)
class AppBridgeStatusPayload:
    enabled: bool = False
    server_started: bool = False
    remote_access_allowed: bool = False
    transport: str = "stdio"
    host: str = "127.0.0.1"
    pairing_required: bool = True
    personal_data_included: bool = False
    native_dependencies_loaded: bool = False
    polling_enabled: bool = False
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "server_started": self.server_started,
            "remote_access_allowed": self.remote_access_allowed,
            "transport": self.transport,
            "host": self.host,
            "pairing_required": self.pairing_required,
            "personal_data_included": self.personal_data_included,
            "native_dependencies_loaded": self.native_dependencies_loaded,
            "polling_enabled": self.polling_enabled,
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class AppBridgeActionPreviewRequest:
    requested_capability: str
    action_payload: Mapping[str, Any]
    risk_level: RiskLevel
    trust_level: TrustLevel
    audit_correlation_id: str
    exact_preview: str = ""
    preview_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "requested_capability": self.requested_capability,
            "action_payload": dict(self.action_payload),
            "risk_level": self.risk_level.value,
            "trust_level": self.trust_level.value,
            "audit_correlation_id": self.audit_correlation_id,
            "exact_preview": self.exact_preview,
            "preview_hash": self.preview_hash,
        }


@dataclass(frozen=True)
class AppBridgeApprovalDecision:
    action_id: str
    decision: str
    user_interaction_confirmed: bool
    exact_preview_confirmed: bool
    per_action_approval: bool
    approval_reuse_requested: bool
    generated_by_frontend: bool
    audit_correlation_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "decision": self.decision,
            "user_interaction_confirmed": self.user_interaction_confirmed,
            "exact_preview_confirmed": self.exact_preview_confirmed,
            "per_action_approval": self.per_action_approval,
            "approval_reuse_requested": self.approval_reuse_requested,
            "generated_by_frontend": self.generated_by_frontend,
            "audit_correlation_id": self.audit_correlation_id,
        }


@dataclass(frozen=True)
class AppBridgeResultPayload:
    action_id: str
    status: str
    audit_correlation_id: str
    result_payload: Mapping[str, Any] = field(default_factory=dict)
    personal_data_included: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "status": self.status,
            "audit_correlation_id": self.audit_correlation_id,
            "result_payload": dict(self.result_payload),
            "personal_data_included": self.personal_data_included,
        }


@dataclass(frozen=True)
class AppBridgeRequest:
    request_id: str
    frontend_id: str
    frontend_platform: FrontendPlatform
    surface: AppBridgeSurface
    pairing_status: PairingStatus
    trust_level: TrustLevel
    audit_correlation_id: str
    requested_capability: str = ""
    action_payload: Mapping[str, Any] = field(default_factory=dict)
    approval_payload: Mapping[str, Any] = field(default_factory=dict)
    result_payload: Mapping[str, Any] = field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.SAFE
    user_interaction_confirmed: bool = False
    generated_by_frontend: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "frontend_id": self.frontend_id,
            "frontend_platform": self.frontend_platform.value,
            "surface": self.surface.value,
            "pairing_status": self.pairing_status.value,
            "trust_level": self.trust_level.value,
            "audit_correlation_id": self.audit_correlation_id,
            "requested_capability": self.requested_capability,
            "action_payload": dict(self.action_payload),
            "approval_payload": dict(self.approval_payload),
            "result_payload": dict(self.result_payload),
            "risk_level": self.risk_level.value,
            "user_interaction_confirmed": self.user_interaction_confirmed,
            "generated_by_frontend": self.generated_by_frontend,
        }
