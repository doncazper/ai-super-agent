from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class ChannelType(str, Enum):
    CLI = "cli"
    INTERACTIVE_CLI = "interactive_cli"
    TELEGRAM = "telegram"
    IOS_COMPANION = "ios_companion"
    MAC_APP = "mac_app"
    WINDOWS_APP = "windows_app"
    LOCAL_WEB_DASHBOARD = "local_web_dashboard"
    EMAIL = "email"
    MANUAL_HANDOFF = "manual_handoff"
    MOCK = "mock"


class ChannelStatus(str, Enum):
    AVAILABLE = "available"
    DISABLED = "disabled"
    STUBBED = "stubbed"
    PLANNED = "planned"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ChannelDefinition:
    channel_id: str
    channel_type: ChannelType
    display_name: str
    description: str
    status: ChannelStatus
    default_enabled: bool
    remote: bool
    supports_inbound: bool
    supports_outbound: bool
    can_send: bool
    trust_level: str
    risk_level: str
    setup_hint: str
    docs_path: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["channel_type"] = self.channel_type.value
        payload["status"] = self.status.value
        return payload


@dataclass(frozen=True)
class ChannelRequest:
    channel_id: str
    channel_type: str
    user_ref: str
    session_id: str
    message_text: str
    attachments: list[dict[str, Any]]
    trust_level: str
    risk_context: dict[str, Any]
    received_at: str
    metadata_redacted: dict[str, Any]
    correlation_id: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ChannelResponse:
    response_id: str
    session_id: str
    channel_id: str
    content: str
    actions: list[dict[str, Any]]
    approval_required: bool
    audit_ids: list[str]
    safe_to_display: bool
    redaction_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GatewaySubmission:
    status: str
    request: ChannelRequest
    route_target: str = "orchestrator_runtime"
    direct_tool_execution_allowed: bool = False
    channel_approval_allowed: bool = False
    personal_data_accessed: bool = False
    background_persistence_started: bool = False
    audit_correlation_id: str = ""
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["request"] = self.request.to_dict()
        return payload
