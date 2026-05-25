from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from agent.platforms.app_bridge.errors import (
    AppBridgeApprovalError,
    AppBridgePairingRequiredError,
    AppBridgeValidationError,
)
from agent.platforms.app_bridge.models import (
    SENSITIVE_SURFACES,
    AppBridgeRequest,
    AppBridgeStatusPayload,
    AppBridgeSurface,
    FrontendPlatform,
    PairingStatus,
)
from agent.platforms.app_bridge.schemas import (
    ACTION_RESULT_REQUIRED_FIELDS,
    APPROVAL_PAYLOAD_REQUIRED_FIELDS,
    BASE_REQUEST_REQUIRED_FIELDS,
    STATUS_FORBIDDEN_PERSONAL_FIELDS,
    SURFACE_REQUIRED_FIELDS,
)
from agent.platforms.config import PlatformConfig, load_platform_config
from agent.safety.policy import RiskLevel
from agent.safety.trust import TrustLevel

SECRET_KEY_PARTS = ("secret", "token", "password", "api_key", "apikey", "client_secret", "refresh")


def validate_app_bridge_request(payload: Mapping[str, Any]) -> AppBridgeRequest:
    """Validate a future App Bridge request without executing anything."""

    _require_mapping(payload, "request")
    _require_fields(payload, BASE_REQUEST_REQUIRED_FIELDS, "request")

    surface = _parse_enum(AppBridgeSurface, payload["surface"], "surface")
    _require_fields(payload, SURFACE_REQUIRED_FIELDS[surface], surface.value)

    request = AppBridgeRequest(
        request_id=_non_empty_str(payload["request_id"], "request_id"),
        frontend_id=_non_empty_str(payload["frontend_id"], "frontend_id"),
        frontend_platform=_parse_enum(FrontendPlatform, payload["frontend_platform"], "frontend_platform"),
        surface=surface,
        pairing_status=_parse_enum(PairingStatus, payload["pairing_status"], "pairing_status"),
        trust_level=_parse_enum(TrustLevel, payload["trust_level"], "trust_level"),
        audit_correlation_id=_non_empty_str(payload["audit_correlation_id"], "audit_correlation_id"),
        requested_capability=str(payload.get("requested_capability", "")),
        action_payload=_mapping_or_empty(payload.get("action_payload"), "action_payload"),
        approval_payload=_mapping_or_empty(payload.get("approval_payload"), "approval_payload"),
        result_payload=_mapping_or_empty(payload.get("result_payload"), "result_payload"),
        risk_level=_parse_enum(RiskLevel, payload.get("risk_level", RiskLevel.SAFE.value), "risk_level"),
        user_interaction_confirmed=bool(payload.get("user_interaction_confirmed", False)),
        generated_by_frontend=bool(payload.get("generated_by_frontend", False)),
    )
    _validate_pairing(request)
    if request.surface is AppBridgeSurface.SUBMIT_APPROVAL_DECISION:
        validate_approval_payload(request)
    if request.surface is AppBridgeSurface.SUBMIT_ACTION_RESULT:
        validate_result_payload(request)
    if request.surface is AppBridgeSurface.REQUEST_ACTION_PREVIEW:
        _validate_action_preview(request)
    return request


def validate_status_payload(payload: Mapping[str, Any]) -> AppBridgeStatusPayload:
    _require_mapping(payload, "status payload")
    forbidden = sorted(set(payload).intersection(STATUS_FORBIDDEN_PERSONAL_FIELDS))
    if forbidden:
        raise AppBridgeValidationError(f"status payload must not include personal-data fields: {', '.join(forbidden)}")
    if payload.get("personal_data_included") is True:
        raise AppBridgeValidationError("status payload must not include personal data")
    if payload.get("server_started") is True:
        raise AppBridgeValidationError("app bridge server must not start during status payload validation")
    if payload.get("remote_access_allowed") is True:
        raise AppBridgeValidationError("remote app bridge access is unsupported in v1")
    return AppBridgeStatusPayload(
        enabled=bool(payload.get("enabled", False)),
        server_started=bool(payload.get("server_started", False)),
        remote_access_allowed=bool(payload.get("remote_access_allowed", False)),
        transport=str(payload.get("transport", "stdio")),
        host=str(payload.get("host", "127.0.0.1")),
        pairing_required=bool(payload.get("pairing_required", True)),
        personal_data_included=bool(payload.get("personal_data_included", False)),
        native_dependencies_loaded=bool(payload.get("native_dependencies_loaded", False)),
        polling_enabled=bool(payload.get("polling_enabled", False)),
        warnings=tuple(str(item) for item in payload.get("warnings", ())),
    )


def validate_approval_payload(request: AppBridgeRequest) -> None:
    payload = request.approval_payload
    _require_fields(payload, APPROVAL_PAYLOAD_REQUIRED_FIELDS, "approval_payload")
    if payload["audit_correlation_id"] != request.audit_correlation_id:
        raise AppBridgeApprovalError("approval payload must correlate to the request audit_correlation_id")
    if not bool(payload.get("approval_manager_required", True)):
        raise AppBridgeApprovalError("frontend cannot bypass ApprovalManager")
    user_confirmed = bool(payload.get("user_interaction_confirmed")) and request.user_interaction_confirmed
    if not user_confirmed:
        raise AppBridgeApprovalError("frontend approval decisions require explicit user interaction")
    generated_by_frontend = bool(payload.get("generated_by_frontend", request.generated_by_frontend))
    if generated_by_frontend and not user_confirmed:
        raise AppBridgeApprovalError("frontend cannot approve its own generated action without user interaction")
    if request.risk_level is RiskLevel.CRITICAL:
        if not bool(payload.get("exact_preview_confirmed")):
            raise AppBridgeApprovalError("CRITICAL app bridge actions require exact preview confirmation")
        if not bool(payload.get("per_action_approval")):
            raise AppBridgeApprovalError("CRITICAL app bridge actions require per-action approval")
        if bool(payload.get("approval_reuse_requested")):
            raise AppBridgeApprovalError("CRITICAL app bridge approval reuse is forbidden")


def validate_result_payload(request: AppBridgeRequest) -> None:
    payload = request.result_payload
    _require_fields(payload, ACTION_RESULT_REQUIRED_FIELDS, "result_payload")
    if payload["audit_correlation_id"] != request.audit_correlation_id:
        raise AppBridgeValidationError("result payload must correlate to the request audit_correlation_id")
    if payload.get("personal_data_included") is True:
        raise AppBridgeValidationError("app bridge result payloads must not include personal data in v1")


def build_disabled_status_payload(config: PlatformConfig | None = None) -> AppBridgeStatusPayload:
    config = config or load_platform_config({})
    return AppBridgeStatusPayload(
        enabled=config.app_bridge_enabled,
        server_started=False,
        remote_access_allowed=config.app_bridge_allow_remote,
        transport=config.app_bridge_transport.value,
        host=config.app_bridge_host,
        pairing_required=config.app_bridge_require_pairing,
        personal_data_included=False,
        native_dependencies_loaded=False,
        polling_enabled=False,
        warnings=config.warnings,
    )


def redact_sensitive_fields(payload: Mapping[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in payload.items():
        key_text = str(key).lower()
        if any(part in key_text for part in SECRET_KEY_PARTS):
            redacted[str(key)] = "[REDACTED]"
        elif isinstance(value, Mapping):
            redacted[str(key)] = redact_sensitive_fields(value)
        else:
            redacted[str(key)] = value
    return redacted


def _validate_pairing(request: AppBridgeRequest) -> None:
    if request.surface in SENSITIVE_SURFACES and request.pairing_status is not PairingStatus.PAIRED:
        raise AppBridgePairingRequiredError(f"{request.surface.value} requires a paired frontend")


def _validate_action_preview(request: AppBridgeRequest) -> None:
    if not request.requested_capability:
        raise AppBridgeValidationError("requested_capability is required for action previews")
    if not request.audit_correlation_id:
        raise AppBridgeValidationError("audit_correlation_id is required for action previews")
    if request.risk_level is RiskLevel.CRITICAL:
        preview = str(request.action_payload.get("exact_preview", ""))
        preview_hash = str(request.action_payload.get("preview_hash", ""))
        if not preview or not preview_hash:
            raise AppBridgeValidationError("CRITICAL action previews require exact_preview and preview_hash")


def _require_fields(payload: Mapping[str, Any], fields: tuple[str, ...], label: str) -> None:
    missing = [field for field in fields if field not in payload or payload[field] in (None, "")]
    if missing:
        raise AppBridgeValidationError(f"{label} missing required fields: {', '.join(missing)}")


def _require_mapping(payload: Mapping[str, Any], label: str) -> None:
    if not isinstance(payload, Mapping):
        raise AppBridgeValidationError(f"{label} must be an object")


def _mapping_or_empty(value: Any, label: str) -> Mapping[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise AppBridgeValidationError(f"{label} must be an object")
    return value


def _non_empty_str(value: Any, label: str) -> str:
    parsed = str(value).strip()
    if not parsed:
        raise AppBridgeValidationError(f"{label} is required")
    return parsed


def _parse_enum(enum_type: type, value: Any, label: str):
    if hasattr(value, "value"):
        value = value.value
    try:
        return enum_type(str(value))
    except ValueError as exc:
        raise AppBridgeValidationError(f"{label} has unsupported value {value!r}") from exc
