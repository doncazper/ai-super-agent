from __future__ import annotations

from typing import Any

from agent.channels.errors import ChannelDisabledError
from agent.channels.models import ChannelRequest, ChannelResponse, ChannelStatus, GatewaySubmission, utc_now_iso
from agent.channels.registry import ChannelRegistry
from agent.channels.security import (
    deny_channel_self_approval,
    deny_direct_tool_execution,
    redact_metadata,
    require_correlation_id,
    trust_level_for_channel,
)


class ChannelGateway:
    def __init__(self, registry: ChannelRegistry | None = None) -> None:
        self._registry = registry or ChannelRegistry()

    def submit_request(
        self,
        *,
        channel_id: str,
        user_ref: str,
        session_id: str,
        message_text: str,
        correlation_id: str,
        attachments: list[dict[str, Any]] | None = None,
        risk_context: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> GatewaySubmission:
        definition = self._registry.get(channel_id)
        if not definition.default_enabled or definition.status != ChannelStatus.AVAILABLE:
            raise ChannelDisabledError(f"channel is disabled or unavailable: {channel_id}")
        audit_correlation_id = require_correlation_id(correlation_id)
        request = ChannelRequest(
            channel_id=definition.channel_id,
            channel_type=definition.channel_type.value,
            user_ref=str(user_ref),
            session_id=str(session_id),
            message_text=str(message_text),
            attachments=attachments or [],
            trust_level=trust_level_for_channel(definition),
            risk_context=redact_metadata(risk_context or {}),
            received_at=utc_now_iso(),
            metadata_redacted=redact_metadata(metadata or {}),
            correlation_id=audit_correlation_id,
        )
        return GatewaySubmission(
            status="submitted",
            request=request,
            audit_correlation_id=audit_correlation_id,
            notes=[
                "Gateway submission is a structured handoff to the orchestrator/runtime.",
                "The gateway did not execute tools, approve actions, access personal data, or start background persistence.",
            ],
        )

    def execute_tool(self, *_args: Any, **_kwargs: Any) -> None:
        deny_direct_tool_execution()

    def approve_action(self, *_args: Any, **_kwargs: Any) -> None:
        deny_channel_self_approval()

    def build_response(
        self,
        *,
        response_id: str,
        session_id: str,
        channel_id: str,
        content: str,
        actions: list[dict[str, Any]] | None = None,
        audit_ids: list[str] | None = None,
    ) -> ChannelResponse:
        self._registry.get(channel_id)
        return ChannelResponse(
            response_id=str(response_id),
            session_id=str(session_id),
            channel_id=str(channel_id),
            content=str(content),
            actions=actions or [],
            approval_required=bool(actions),
            audit_ids=audit_ids or [],
            safe_to_display=True,
            redaction_status="metadata_redacted",
        )
