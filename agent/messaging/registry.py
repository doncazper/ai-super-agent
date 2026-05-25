from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from agent.messaging.errors import UnknownChannelError
from agent.messaging.models import MessageChannel, MessageDraft
from agent.messaging.validation import draft_from_dict


@dataclass(frozen=True)
class MessageChannelDefinition:
    channel: MessageChannel
    display_name: str
    supports_drafts: bool = True
    supports_send: bool = False
    enabled_by_default: bool = False
    adapter_status: str = "stubbed"
    setup_hint: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["channel"] = self.channel.value
        return payload


DEFAULT_CHANNELS: tuple[MessageChannelDefinition, ...] = (
    MessageChannelDefinition(
        MessageChannel.IOS_COMPOSE,
        "iOS user-confirmed compose",
        supports_send=False,
        adapter_status="mock_handoff_available",
        setup_hint="Creates a local handoff payload for a future iOS companion app; the user must tap Send in iOS compose UI.",
    ),
    MessageChannelDefinition(
        MessageChannel.MACOS_MESSAGES,
        "macOS Messages automation",
        supports_send=False,
        adapter_status="blocked",
        setup_hint="No macOS Messages automation adapter is enabled; no Messages database scraping or Full Disk Access.",
    ),
    MessageChannelDefinition(
        MessageChannel.APPLE_MESSAGES_FOR_BUSINESS,
        "Apple Messages for Business",
        supports_send=False,
        adapter_status="provider_stub_mock_only",
        setup_hint="Mock inbound and draft-response stubs exist; live provider setup and sends remain disabled.",
    ),
    MessageChannelDefinition(
        MessageChannel.TELEGRAM,
        "Telegram",
        supports_send=False,
        adapter_status="doctor_only",
        setup_hint="Telegram doctor can inspect config; no reads or sends are implemented here.",
    ),
    MessageChannelDefinition(
        MessageChannel.EMAIL,
        "Email",
        supports_send=False,
        adapter_status="separate_email_workflow",
        setup_hint="Email send remains a separate CRITICAL Action Center workflow; this layer only normalizes message schema.",
    ),
    MessageChannelDefinition(
        MessageChannel.MANUAL_HANDOFF,
        "Manual handoff",
        supports_send=False,
        adapter_status="available",
        setup_hint="Use reviewed save/copy handoff workflows; no automatic send.",
    ),
    MessageChannelDefinition(
        MessageChannel.MOCK,
        "Mock",
        supports_send=False,
        adapter_status="tests_only",
        setup_hint="Mock channel validates schemas in tests only; no direct send path exists.",
    ),
)


class MessageChannelRegistry:
    def __init__(self, channels: tuple[MessageChannelDefinition, ...] = DEFAULT_CHANNELS) -> None:
        self._channels = {definition.channel: definition for definition in channels}

    def list_channels(self) -> list[MessageChannelDefinition]:
        return list(self._channels.values())

    def get(self, channel: str | MessageChannel) -> MessageChannelDefinition:
        try:
            parsed = channel if isinstance(channel, MessageChannel) else MessageChannel(str(channel))
        except ValueError as exc:
            raise UnknownChannelError(f"unknown message channel: {channel}") from exc
        definition = self._channels.get(parsed)
        if definition is None:
            raise UnknownChannelError(f"unknown message channel: {parsed.value}")
        return definition

    def supports_send(self, channel: str | MessageChannel) -> bool:
        return self.get(channel).supports_send


def draft_store_dir(project_root: str | Path) -> Path:
    return Path(project_root).resolve() / "workspace" / "messaging" / "drafts"


def save_draft(project_root: str | Path, draft: MessageDraft) -> Path:
    if not draft.draft_id or "/" in draft.draft_id or "\\" in draft.draft_id or ".." in draft.draft_id:
        raise UnknownChannelError("draft_id must be a simple local draft id")
    path = draft_store_dir(project_root) / f"{draft.draft_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(draft.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return path


def load_draft(project_root: str | Path, draft_id: str) -> MessageDraft:
    if not draft_id or "/" in draft_id or "\\" in draft_id or ".." in draft_id:
        raise UnknownChannelError("draft_id must be a simple local draft id")
    path = draft_store_dir(project_root) / f"{draft_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"message draft not found: {draft_id}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("message draft file must contain a JSON object")
    return draft_from_dict(payload)
