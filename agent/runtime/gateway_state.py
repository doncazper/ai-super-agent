from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from typing import Any

from .models import now_iso
from .state import redact_runtime_value


@dataclass(frozen=True)
class GatewayRequestEnvelope:
    request_id: str
    frontend_id: str = "cli"
    frontend_type: str = "cli"
    correlation_id: str = ""
    requested_action: str = "status"
    capability_id: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    trust_level: str = "TRUSTED_USER"
    risk_level: str = "SAFE"
    approval_required: bool = False
    created_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return redact_runtime_value(asdict(self))


@dataclass(frozen=True)
class GatewayResponseEnvelope:
    request_id: str
    correlation_id: str
    status: str
    requires_review: bool = False
    summary: str = ""
    redacted_payload: dict[str, Any] = field(default_factory=dict)
    tool_execution: bool = False
    approved_by_gateway: bool = False
    policy_mutation: bool = False
    capability_mutation: bool = False
    created_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return redact_runtime_value(asdict(self))


@dataclass(frozen=True)
class AgentGatewayState:
    gateway_id: str = "local_cli_gateway"
    status: str = "available_metadata_only"
    primary_frontend: str = "cli"
    cli_remains_first_frontend: bool = True
    server_started: bool = False
    listeners_started: bool = False
    external_tools_exposed: bool = False
    direct_tool_execution_allowed: bool = False
    gateway_can_approve_actions: bool = False
    gateway_can_mutate_policy: bool = False
    gateway_can_mutate_capabilities: bool = False
    canonical_state_owned_by_kernel: bool = True
    durable_records_owned_by_kernel: bool = True
    generated_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return redact_runtime_value(asdict(self))


def new_request_id(prefix: str = "gw_req") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def gateway_status() -> dict[str, Any]:
    return {
        "status": "ok",
        "gateway": AgentGatewayState().to_dict(),
        "side_effects": "none; no server, listener, tool execution, or provider call",
    }


def normalize_gateway_request(
    *,
    requested_action: str,
    payload: dict[str, Any] | None = None,
    frontend_id: str = "cli",
    frontend_type: str = "cli",
    risk_level: str = "SAFE",
    approval_required: bool = False,
    capability_id: str = "",
) -> GatewayRequestEnvelope:
    request_id = new_request_id()
    return GatewayRequestEnvelope(
        request_id=request_id,
        frontend_id=frontend_id,
        frontend_type=frontend_type,
        correlation_id=f"corr_{request_id}",
        requested_action=requested_action,
        capability_id=capability_id,
        payload=payload or {},
        risk_level=risk_level,
        approval_required=approval_required,
    )


def preview_gateway_request(envelope: GatewayRequestEnvelope) -> GatewayResponseEnvelope:
    direct_tool_attempt = _payload_requests_direct_tool_execution(envelope.payload)
    requires_review = envelope.approval_required or envelope.risk_level in {"HIGH", "CRITICAL"} or direct_tool_attempt
    if direct_tool_attempt:
        status = "blocked"
        summary = "Gateway requests cannot execute tools directly; ToolBroker-owned dispatch is required."
    elif requires_review:
        status = "requires_review"
        summary = "Request requires policy/approval review before any future execution path."
    else:
        status = "accepted_for_routing_preview"
        summary = "Request envelope is normalized for future safe routing; no execution occurred."
    return GatewayResponseEnvelope(
        request_id=envelope.request_id,
        correlation_id=envelope.correlation_id,
        status=status,
        requires_review=requires_review,
        summary=summary,
        redacted_payload=envelope.to_dict(),
        tool_execution=False,
        approved_by_gateway=False,
        policy_mutation=False,
        capability_mutation=False,
    )


def _payload_requests_direct_tool_execution(payload: dict[str, Any]) -> bool:
    markers = {"execute_tool", "tool_call", "direct_tool", "bypass_toolbroker"}
    return any(str(key).lower() in markers for key in payload)
