"""App Bridge API contract models and validation.

Importing this package starts no server, imports no native app frameworks, and
performs no network, IPC, permission, or personal-data access.
"""

from agent.platforms.app_bridge.errors import (
    AppBridgeApprovalError,
    AppBridgePairingRequiredError,
    AppBridgeValidationError,
)
from agent.platforms.app_bridge.models import (
    APP_BRIDGE_API_SURFACES,
    AppBridgeActionPreviewRequest,
    AppBridgeApprovalDecision,
    AppBridgeRequest,
    AppBridgeResultPayload,
    AppBridgeStatusPayload,
    AppBridgeSurface,
    FrontendPlatform,
    PairingStatus,
)
from agent.platforms.app_bridge.validation import (
    build_disabled_status_payload,
    redact_sensitive_fields,
    validate_app_bridge_request,
    validate_status_payload,
)

__all__ = [
    "APP_BRIDGE_API_SURFACES",
    "AppBridgeActionPreviewRequest",
    "AppBridgeApprovalDecision",
    "AppBridgeApprovalError",
    "AppBridgePairingRequiredError",
    "AppBridgeRequest",
    "AppBridgeResultPayload",
    "AppBridgeStatusPayload",
    "AppBridgeSurface",
    "AppBridgeValidationError",
    "FrontendPlatform",
    "PairingStatus",
    "build_disabled_status_payload",
    "redact_sensitive_fields",
    "validate_app_bridge_request",
    "validate_status_payload",
]
