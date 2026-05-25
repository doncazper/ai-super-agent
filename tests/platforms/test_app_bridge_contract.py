from __future__ import annotations

import importlib
import sys

import pytest

from agent.platforms.app_bridge.errors import (
    AppBridgeApprovalError,
    AppBridgePairingRequiredError,
    AppBridgeValidationError,
)
from agent.platforms.app_bridge.models import AppBridgeSurface, PairingStatus
from agent.platforms.app_bridge.validation import (
    build_disabled_status_payload,
    redact_sensitive_fields,
    validate_app_bridge_request,
    validate_status_payload,
)
from agent.platforms.config import AppBridgeTransport, load_platform_config


def _base_request(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "request_id": "req_1",
        "frontend_id": "mac_app_local",
        "frontend_platform": "macos",
        "surface": "status",
        "pairing_status": "unpaired",
        "trust_level": "LOCAL_PRIVATE_DATA",
        "audit_correlation_id": "audit_req_1",
        "risk_level": "SAFE",
    }
    payload.update(overrides)
    return payload


def test_app_bridge_schema_validates_status_request() -> None:
    request = validate_app_bridge_request(_base_request())

    assert request.surface is AppBridgeSurface.STATUS
    assert request.pairing_status is PairingStatus.UNPAIRED
    assert request.audit_correlation_id == "audit_req_1"


def test_invalid_payload_rejected() -> None:
    with pytest.raises(AppBridgeValidationError):
        validate_app_bridge_request({"frontend_id": "missing_required_fields"})

    with pytest.raises(AppBridgeValidationError):
        validate_app_bridge_request(_base_request(surface="remote_admin"))


def test_unpaired_sensitive_request_denied() -> None:
    with pytest.raises(AppBridgePairingRequiredError):
        validate_app_bridge_request(
            _base_request(
                surface="request_action_preview",
                pairing_status="unpaired",
                requested_capability="app_bridge.submit_approval",
                action_payload={"summary": "preview only"},
                risk_level="HIGH",
            )
        )


def test_frontend_cannot_bypass_approval_manager_or_user_interaction() -> None:
    with pytest.raises(AppBridgeApprovalError, match="ApprovalManager"):
        validate_app_bridge_request(
            _base_request(
                surface="submit_approval_decision",
                pairing_status="paired",
                risk_level="HIGH",
                user_interaction_confirmed=True,
                approval_payload={
                    "action_id": "act_1",
                    "decision": "approve",
                    "user_interaction_confirmed": True,
                    "approval_manager_required": False,
                    "audit_correlation_id": "audit_req_1",
                },
            )
        )

    with pytest.raises(AppBridgeApprovalError, match="user interaction"):
        validate_app_bridge_request(
            _base_request(
                surface="submit_approval_decision",
                pairing_status="paired",
                risk_level="HIGH",
                generated_by_frontend=True,
                approval_payload={
                    "action_id": "act_1",
                    "decision": "approve",
                    "user_interaction_confirmed": False,
                    "approval_manager_required": True,
                    "generated_by_frontend": True,
                    "audit_correlation_id": "audit_req_1",
                },
            )
        )


def test_critical_action_requires_exact_preview_and_per_action_approval() -> None:
    with pytest.raises(AppBridgeApprovalError, match="exact preview"):
        validate_app_bridge_request(
            _base_request(
                surface="submit_approval_decision",
                pairing_status="paired",
                risk_level="CRITICAL",
                user_interaction_confirmed=True,
                approval_payload={
                    "action_id": "act_critical",
                    "decision": "approve",
                    "user_interaction_confirmed": True,
                    "approval_manager_required": True,
                    "per_action_approval": True,
                    "approval_reuse_requested": False,
                    "audit_correlation_id": "audit_req_1",
                },
            )
        )

    request = validate_app_bridge_request(
        _base_request(
            surface="submit_approval_decision",
            pairing_status="paired",
            risk_level="CRITICAL",
            user_interaction_confirmed=True,
            approval_payload={
                "action_id": "act_critical",
                "decision": "approve",
                "user_interaction_confirmed": True,
                "approval_manager_required": True,
                "exact_preview_confirmed": True,
                "per_action_approval": True,
                "approval_reuse_requested": False,
                "audit_correlation_id": "audit_req_1",
            },
        )
    )
    assert request.risk_level.value == "CRITICAL"


def test_status_payload_contains_no_personal_data() -> None:
    status = validate_status_payload({"enabled": False, "server_started": False})

    assert status.personal_data_included is False
    with pytest.raises(AppBridgeValidationError):
        validate_status_payload({"enabled": False, "email": "person@example.com"})


def test_app_bridge_config_defaults_are_safe() -> None:
    config = load_platform_config({})

    assert config.app_bridge_enabled is False
    assert config.app_bridge_host == "127.0.0.1"
    assert config.app_bridge_port == ""
    assert config.app_bridge_transport is AppBridgeTransport.STDIO
    assert config.app_bridge_require_pairing is True
    assert config.app_bridge_allow_remote is False
    assert build_disabled_status_payload(config).server_started is False


def test_remote_access_config_is_forced_off() -> None:
    config = load_platform_config({"APP_BRIDGE_ALLOW_REMOTE": "true", "APP_BRIDGE_HOST": "0.0.0.0"})

    assert config.app_bridge_allow_remote is False
    assert config.app_bridge_host == "127.0.0.1"
    assert any("unsupported" in warning or "localhost" in warning for warning in config.warnings)


def test_audit_correlation_required_for_result_payload() -> None:
    with pytest.raises(AppBridgeValidationError, match="audit_correlation_id"):
        validate_app_bridge_request(
            _base_request(
                surface="submit_action_result",
                pairing_status="paired",
                result_payload={"action_id": "act_1", "status": "ok"},
            )
        )


def test_no_server_starts_during_import() -> None:
    before_modules = set(sys.modules)
    importlib.import_module("agent.platforms.app_bridge")
    after_modules = set(sys.modules)

    newly_loaded = after_modules - before_modules
    assert "uvicorn" not in newly_loaded
    assert "fastapi" not in newly_loaded
    assert "socketserver" not in newly_loaded


def test_sensitive_fields_redacted() -> None:
    redacted = redact_sensitive_fields(
        {
            "frontend_id": "mac",
            "client_secret": "secret-value",
            "nested": {"refresh_token": "token-value"},
        }
    )

    assert redacted["client_secret"] == "[REDACTED]"
    assert redacted["nested"]["refresh_token"] == "[REDACTED]"
