from __future__ import annotations

from agent.channels.errors import UnknownChannelError
from agent.channels.models import ChannelDefinition, ChannelStatus, ChannelType


DEFAULT_CHANNELS: tuple[ChannelDefinition, ...] = (
    ChannelDefinition(
        channel_id="cli",
        channel_type=ChannelType.CLI,
        display_name="CLI",
        description="Trusted local command-line user input.",
        status=ChannelStatus.AVAILABLE,
        default_enabled=True,
        remote=False,
        supports_inbound=True,
        supports_outbound=True,
        can_send=False,
        trust_level="TRUSTED_USER",
        risk_level="SAFE",
        setup_hint="Use the local CLI; no external channel setup is required.",
        docs_path="docs/channels/GATEWAY_CHANNEL_ARCHITECTURE.md",
    ),
    ChannelDefinition(
        channel_id="interactive_cli",
        channel_type=ChannelType.INTERACTIVE_CLI,
        display_name="Interactive CLI",
        description="Trusted local interactive shell input.",
        status=ChannelStatus.AVAILABLE,
        default_enabled=True,
        remote=False,
        supports_inbound=True,
        supports_outbound=True,
        can_send=False,
        trust_level="TRUSTED_USER",
        risk_level="SAFE",
        setup_hint="Run python smart_agent.py --interactive.",
        docs_path="docs/channels/GATEWAY_CHANNEL_ARCHITECTURE.md",
    ),
    ChannelDefinition(
        channel_id="manual_handoff",
        channel_type=ChannelType.MANUAL_HANDOFF,
        display_name="Manual handoff",
        description="Local user-mediated handoff channel for reviewed output.",
        status=ChannelStatus.AVAILABLE,
        default_enabled=True,
        remote=False,
        supports_inbound=False,
        supports_outbound=True,
        can_send=False,
        trust_level="TRUSTED_USER",
        risk_level="LOW",
        setup_hint="Use existing draft/copy/save handoff workflows; this gateway does not send.",
        docs_path="docs/channels/GATEWAY_CHANNEL_ARCHITECTURE.md",
    ),
    ChannelDefinition(
        channel_id="mock",
        channel_type=ChannelType.MOCK,
        display_name="Mock channel",
        description="Test-only channel for gateway request normalization.",
        status=ChannelStatus.AVAILABLE,
        default_enabled=True,
        remote=False,
        supports_inbound=True,
        supports_outbound=True,
        can_send=False,
        trust_level="UNTRUSTED_MESSAGE",
        risk_level="SAFE",
        setup_hint="Use only in tests and dogfood fixtures.",
        docs_path="docs/channels/GATEWAY_CHANNEL_ARCHITECTURE.md",
    ),
    ChannelDefinition(
        channel_id="telegram",
        channel_type=ChannelType.TELEGRAM,
        display_name="Telegram",
        description="Future Telegram/mobile channel scaffold.",
        status=ChannelStatus.DISABLED,
        default_enabled=False,
        remote=True,
        supports_inbound=False,
        supports_outbound=False,
        can_send=False,
        trust_level="UNTRUSTED_MESSAGE",
        risk_level="MEDIUM",
        setup_hint="Future prompt must add connector-specific policy, webhook/polling boundaries, tests, and audit before use.",
        docs_path="docs/channels/CHANNEL_SECURITY_MODEL.md",
    ),
    ChannelDefinition(
        channel_id="ios_companion",
        channel_type=ChannelType.IOS_COMPANION,
        display_name="iOS companion",
        description="Future paired mobile companion channel scaffold.",
        status=ChannelStatus.DISABLED,
        default_enabled=False,
        remote=True,
        supports_inbound=False,
        supports_outbound=False,
        can_send=False,
        trust_level="UNTRUSTED_MESSAGE",
        risk_level="MEDIUM",
        setup_hint="Requires future pairing, approval, and app-bridge prompts; no companion behavior exists now.",
        docs_path="docs/channels/CHANNEL_SECURITY_MODEL.md",
    ),
    ChannelDefinition(
        channel_id="mac_app",
        channel_type=ChannelType.MAC_APP,
        display_name="Mac app",
        description="Future local native macOS frontend channel scaffold.",
        status=ChannelStatus.DISABLED,
        default_enabled=False,
        remote=False,
        supports_inbound=False,
        supports_outbound=False,
        can_send=False,
        trust_level="UNTRUSTED_MESSAGE",
        risk_level="MEDIUM",
        setup_hint="Requires future app bridge pairing and approval flow; no native app frontend is enabled.",
        docs_path="docs/platforms/APP_BRIDGE_API.md",
    ),
    ChannelDefinition(
        channel_id="windows_app",
        channel_type=ChannelType.WINDOWS_APP,
        display_name="Windows app",
        description="Future local native Windows frontend channel scaffold.",
        status=ChannelStatus.DISABLED,
        default_enabled=False,
        remote=False,
        supports_inbound=False,
        supports_outbound=False,
        can_send=False,
        trust_level="UNTRUSTED_MESSAGE",
        risk_level="MEDIUM",
        setup_hint="Requires future app bridge pairing and Windows release gate; no Windows app behavior is enabled.",
        docs_path="docs/platforms/FUTURE_WINDOWS_BRIDGE_GUIDE.md",
    ),
    ChannelDefinition(
        channel_id="local_web_dashboard",
        channel_type=ChannelType.LOCAL_WEB_DASHBOARD,
        display_name="Local web dashboard",
        description="Future localhost dashboard channel scaffold.",
        status=ChannelStatus.DISABLED,
        default_enabled=False,
        remote=False,
        supports_inbound=False,
        supports_outbound=False,
        can_send=False,
        trust_level="UNTRUSTED_MESSAGE",
        risk_level="MEDIUM",
        setup_hint="Requires future disabled-by-default app bridge server work; no listener starts now.",
        docs_path="docs/platforms/FUTURE_APP_FRONTEND_GUIDE.md",
    ),
    ChannelDefinition(
        channel_id="email",
        channel_type=ChannelType.EMAIL,
        display_name="Email",
        description="Future channel gateway metadata for email access.",
        status=ChannelStatus.DISABLED,
        default_enabled=False,
        remote=True,
        supports_inbound=False,
        supports_outbound=False,
        can_send=False,
        trust_level="UNTRUSTED_MESSAGE",
        risk_level="HIGH",
        setup_hint="Use existing explicit email workflows only; this gateway adds no email read/send behavior.",
        docs_path="docs/channels/CHANNEL_SECURITY_MODEL.md",
    ),
)


class ChannelRegistry:
    def __init__(self, channels: tuple[ChannelDefinition, ...] = DEFAULT_CHANNELS) -> None:
        self._channels = {channel.channel_id: channel for channel in channels}

    def list_channels(self) -> list[ChannelDefinition]:
        return list(self._channels.values())

    def get(self, channel_id: str) -> ChannelDefinition:
        normalized = str(channel_id).strip()
        definition = self._channels.get(normalized)
        if definition is None:
            raise UnknownChannelError(f"unknown channel: {channel_id}")
        return definition

    def enabled_channels(self) -> list[ChannelDefinition]:
        return [channel for channel in self.list_channels() if channel.default_enabled]

    def disabled_channels(self) -> list[ChannelDefinition]:
        return [channel for channel in self.list_channels() if not channel.default_enabled]
