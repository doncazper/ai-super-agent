from __future__ import annotations

from typing import Any, Callable

from agent.channels.errors import UnknownChannelError
from agent.channels.mobile import mobile_pairing_status, mobile_status
from agent.channels.registry import ChannelRegistry
from agent.connectors.secret_doctor import telegram_doctor, telegram_status
from agent.tools.errors import ToolError


def _schema(
    name: str,
    description: str,
    properties: dict[str, Any] | None = None,
    required: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties or {},
                "required": required or [],
                "additionalProperties": False,
            },
        },
    }


CHANNEL_SCHEMAS: dict[str, dict[str, Any]] = {
    "channels.list": _schema(
        "channels.list",
        "List safe gateway channel metadata without connecting to remote channels, reading personal data, or sending messages.",
    ),
    "channels.status": _schema(
        "channels.status",
        "Show safe gateway channel status counts and disabled-by-default boundaries.",
    ),
    "channels.show": _schema(
        "channels.show",
        "Show one safe gateway channel metadata record.",
        {"channel_id": {"type": "string"}},
        ["channel_id"],
    ),
    "telegram.doctor": _schema(
        "telegram.doctor",
        "Show Telegram config readiness without API calls, polling, webhooks, chat reads, or sends.",
    ),
    "telegram.status": _schema(
        "telegram.status",
        "Show compact Telegram safety status without printing secrets or contacting Telegram.",
    ),
    "mobile.status": _schema(
        "mobile.status",
        "Show future mobile companion status without pairing, personal-data access, network calls, or background services.",
    ),
    "mobile.pairing_status": _schema(
        "mobile.pairing_status",
        "Show future mobile companion pairing status without pairing or network calls.",
    ),
}


def _with_audit(payload: dict[str, Any], summary: str) -> dict[str, Any]:
    payload["_audit"] = {
        "files_read": [],
        "files_written": [],
        "commands_run": [],
        "network_domains": [],
        "result_summary": summary,
    }
    return payload


def make_channel_tools(registry: ChannelRegistry | None = None) -> dict[str, Callable[..., dict[str, Any]]]:
    channel_registry = registry or ChannelRegistry()

    def list_channels() -> dict[str, Any]:
        channels = [channel.to_dict() for channel in channel_registry.list_channels()]
        return _with_audit(
            {
                "status": "ok",
                "channel_count": len(channels),
                "channels": channels,
                "remote_channels_enabled_by_default": False,
                "direct_tool_execution_supported": False,
                "channel_self_approval_supported": False,
                "personal_data_accessed": False,
                "background_persistence_started": False,
            },
            f"Listed {len(channels)} gateway channel records without channel connections.",
        )

    def status() -> dict[str, Any]:
        channels = channel_registry.list_channels()
        enabled = [channel.channel_id for channel in channel_registry.enabled_channels()]
        disabled = [channel.channel_id for channel in channel_registry.disabled_channels()]
        return _with_audit(
            {
                "status": "ok",
                "enabled_channels": enabled,
                "disabled_channels": disabled,
                "remote_channels": [channel.channel_id for channel in channels if channel.remote],
                "remote_channels_enabled_by_default": any(channel.remote and channel.default_enabled for channel in channels),
                "send_capable_channels": [channel.channel_id for channel in channels if channel.can_send],
                "direct_tool_execution_supported": False,
                "channel_self_approval_supported": False,
                "personal_data_accessed": False,
                "background_persistence_started": False,
                "notes": [
                    "Gateway status is metadata-only.",
                    "Remote channels are disabled by default.",
                    "No channel can send, approve actions, execute tools, or access personal data in this scaffold.",
                ],
            },
            "Read gateway channel status metadata without channel connections.",
        )

    def show(channel_id: str) -> dict[str, Any]:
        try:
            channel = channel_registry.get(channel_id)
        except UnknownChannelError as exc:
            raise ToolError(str(exc)) from exc
        return _with_audit(
            {
                "status": "ok",
                "channel": channel.to_dict(),
                "direct_tool_execution_supported": False,
                "channel_self_approval_supported": False,
                "personal_data_accessed": False,
                "background_persistence_started": False,
            },
            f"Read gateway channel metadata for {channel_id!r} without channel connections.",
        )

    return {
        "channels.list": list_channels,
        "channels.status": status,
        "channels.show": show,
        "telegram.doctor": lambda: _with_audit(
            telegram_doctor(),
            "Read Telegram config readiness without API calls, polling, webhooks, chat reads, or sends.",
        ),
        "telegram.status": lambda: _with_audit(
            telegram_status(),
            "Read Telegram safety status without API calls, polling, webhooks, chat reads, or sends.",
        ),
        "mobile.status": lambda: _with_audit(
            mobile_status(),
            "Read mobile companion status without pairing, network calls, personal-data access, or background services.",
        ),
        "mobile.pairing_status": lambda: _with_audit(
            mobile_pairing_status(),
            "Read mobile pairing status without pairing, network calls, personal-data access, or background services.",
        ),
    }
