from __future__ import annotations

from agent.platforms.app_bridge.models import AppBridgeSurface


BASE_REQUEST_REQUIRED_FIELDS: tuple[str, ...] = (
    "request_id",
    "frontend_id",
    "frontend_platform",
    "surface",
    "pairing_status",
    "trust_level",
    "audit_correlation_id",
)

SURFACE_REQUIRED_FIELDS: dict[AppBridgeSurface, tuple[str, ...]] = {
    AppBridgeSurface.STATUS: (),
    AppBridgeSurface.CAPABILITIES: (),
    AppBridgeSurface.HEALTH_CHECK: (),
    AppBridgeSurface.REQUEST_ACTION_PREVIEW: ("requested_capability", "action_payload"),
    AppBridgeSurface.SUBMIT_APPROVAL_DECISION: ("approval_payload",),
    AppBridgeSurface.SUBMIT_ACTION_RESULT: ("result_payload",),
    AppBridgeSurface.FETCH_PENDING_ACTIONS: (),
    AppBridgeSurface.FETCH_AUDIT_SUMMARY: (),
    AppBridgeSurface.FETCH_CONNECTOR_STATUS: (),
}

APPROVAL_PAYLOAD_REQUIRED_FIELDS: tuple[str, ...] = (
    "action_id",
    "decision",
    "user_interaction_confirmed",
    "audit_correlation_id",
)

ACTION_RESULT_REQUIRED_FIELDS: tuple[str, ...] = (
    "action_id",
    "status",
    "audit_correlation_id",
)

STATUS_FORBIDDEN_PERSONAL_FIELDS: frozenset[str] = frozenset(
    {
        "email",
        "emails",
        "phone",
        "phones",
        "contacts",
        "calendar_events",
        "messages",
        "message_bodies",
        "mail",
        "user_profile",
        "location_history",
        "browser_history",
    }
)
