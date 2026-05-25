from __future__ import annotations

import json

import pytest

from agent.config.loader import load_capabilities_config
from agent.core.tool_broker import ToolBroker
from agent.messaging.errors import DirectSendNotSupportedError, MessageValidationError, UnknownChannelError
from agent.messaging.models import MessageChannel, MessageDraft, MessageRecipient, MessageSendRequest
from agent.messaging.registry import MessageChannelRegistry
from agent.messaging.validation import draft_from_dict, validate_draft, validate_send_request
from agent.safety.approvals import ApprovalManager
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.safety.trust import TrustLevel
from agent.tools.registry import default_registry


def _recipient() -> MessageRecipient:
    return MessageRecipient(recipient_id="sam", channel_address="sam", display_name="Sam")


def _draft(**overrides) -> MessageDraft:
    values = {
        "draft_id": "draft-1",
        "channel": MessageChannel.MANUAL_HANDOFF,
        "recipient": _recipient(),
        "recipient_display": "Sam",
        "body": "Reviewed draft only.",
        "source_context": {"source": "model"},
    }
    values.update(overrides)
    return MessageDraft(**values)


def _call(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    return {
        "id": f"call_{tool_name}",
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments)},
    }


def _broker(tmp_path) -> ToolBroker:
    capabilities = {
        "messaging.channels": Capability("messaging.channels", RiskLevel.SAFE, default_enabled=True),
        "messaging.draft_show": Capability("messaging.draft_show", RiskLevel.LOW, default_enabled=True),
        "messaging.draft_validate": Capability("messaging.draft_validate", RiskLevel.LOW, default_enabled=True),
    }
    return ToolBroker(
        default_registry(project_root=tmp_path),
        PolicyEngine(capabilities),
        AuditLogger(tmp_path / "audit.jsonl"),
        session_id="messaging-test",
        model="test-model",
        route="test",
        approval_manager=ApprovalManager(),
    )


def test_draft_model_validates() -> None:
    draft = _draft()

    validate_draft(draft)

    assert draft.channel is MessageChannel.MANUAL_HANDOFF
    assert draft.status.value == "draft"
    assert draft.to_dict()["body"] == "Reviewed draft only."


def test_missing_recipient_rejected() -> None:
    draft = _draft(recipient=MessageRecipient(recipient_id="", channel_address=""))

    with pytest.raises(MessageValidationError, match="recipient"):
        validate_draft(draft)


def test_empty_body_rejected_unless_explicitly_allowed() -> None:
    draft = _draft(body="")

    with pytest.raises(MessageValidationError, match="body"):
        validate_draft(draft)
    validate_draft(draft, allow_empty_body=True)


def test_multiple_recipients_rejected_in_v1() -> None:
    draft = _draft(recipient=MessageRecipient(recipient_id="sam,alex", channel_address="sam,alex"))

    with pytest.raises(MessageValidationError, match="multiple recipients"):
        validate_draft(draft)


def test_unknown_channel_rejected() -> None:
    with pytest.raises(UnknownChannelError, match="unknown message channel"):
        MessageChannelRegistry().get("unknown_channel")


def test_send_request_is_critical_and_approval_reuse_false() -> None:
    request = MessageSendRequest(
        action_id="act_1",
        draft_id="draft-1",
        channel=MessageChannel.MANUAL_HANDOFF,
        recipient=_recipient(),
        body="Reviewed body",
    )

    assert request.risk_level is RiskLevel.CRITICAL
    assert request.approval_required is True
    assert request.approval_reuse_allowed is False
    with pytest.raises(DirectSendNotSupportedError, match="does not support sending"):
        validate_send_request(request)


def test_untrusted_source_content_labeled_correctly() -> None:
    draft = draft_from_dict(
        {
            "draft_id": "draft-2",
            "channel": "manual_handoff",
            "recipient": {"recipient_id": "sam", "channel_address": "sam"},
            "recipient_display": "Sam",
            "body": "Reply draft",
            "source_context": {"source": "email_thread"},
        }
    )

    assert draft.trust_level is TrustLevel.UNTRUSTED_EMAIL


def test_no_direct_send_path_exists() -> None:
    registry = default_registry()
    channels = MessageChannelRegistry().list_channels()
    tools = load_capabilities_config("config/capabilities.yaml")["tools"]

    assert registry.get("messaging.send") is None
    assert all(channel.supports_send is False for channel in channels)
    assert "messaging.channels" in tools
    assert tools["messages.send_approved"]["default_enabled"] is False


def test_brokered_messaging_channels_and_draft_validation(tmp_path) -> None:
    draft_dir = tmp_path / "workspace" / "messaging" / "drafts"
    draft_dir.mkdir(parents=True)
    (draft_dir / "draft-1.json").write_text(
        json.dumps(
            {
                "draft_id": "draft-1",
                "channel": "manual_handoff",
                "recipient": {"recipient_id": "sam", "channel_address": "sam"},
                "recipient_display": "Sam",
                "body": "Reviewed draft only.",
                "source_context": {"source": "message_thread"},
            }
        ),
        encoding="utf-8",
    )
    broker = _broker(tmp_path)

    channels_result = broker.execute(_call("messaging.channels", {}))
    validate_result = broker.execute(_call("messaging.draft_validate", {"draft_id": "draft-1"}))

    assert channels_result.allowed is True
    assert json.loads(channels_result.content)["direct_send_supported"] is False
    payload = json.loads(validate_result.content)
    assert validate_result.allowed is True
    assert payload["valid"] is True
    assert payload["trust_level"] == "UNTRUSTED_MESSAGE"
