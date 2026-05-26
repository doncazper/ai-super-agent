from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from agent.channels.errors import ChannelSecurityError
from agent.channels.models import ChannelDefinition, ChannelType


SENSITIVE_KEY_MARKERS = (
    "secret",
    "token",
    "password",
    "credential",
    "api_key",
    "apikey",
    "authorization",
    "auth",
    "cookie",
    "session",
)


def redact_metadata(value: Any) -> Any:
    if isinstance(value, Mapping):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if any(marker in key_text.lower() for marker in SENSITIVE_KEY_MARKERS):
                redacted[key_text] = "[REDACTED]"
            else:
                redacted[key_text] = redact_metadata(item)
        return redacted
    if isinstance(value, str):
        return value if len(value) <= 160 else f"{value[:157]}..."
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [redact_metadata(item) for item in value]
    return value


def trust_level_for_channel(definition: ChannelDefinition) -> str:
    if definition.channel_type in {ChannelType.CLI, ChannelType.INTERACTIVE_CLI}:
        return "TRUSTED_USER"
    return "UNTRUSTED_MESSAGE"


def require_correlation_id(correlation_id: str) -> str:
    normalized = str(correlation_id).strip()
    if not normalized:
        raise ChannelSecurityError("channel gateway requests require an audit correlation id")
    return normalized


def deny_direct_tool_execution() -> None:
    raise ChannelSecurityError("channel gateways cannot execute tools directly; route through the orchestrator and ToolBroker")


def deny_channel_self_approval() -> None:
    raise ChannelSecurityError("channels cannot approve their own actions; ApprovalManager user interaction is required")
