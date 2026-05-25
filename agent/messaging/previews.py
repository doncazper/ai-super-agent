from __future__ import annotations

from typing import Any

from agent.messaging.models import MessageDraft, MessageSendRequest
from agent.safety.redaction import SecretRedactor


def draft_preview(draft: MessageDraft) -> dict[str, Any]:
    redactor = SecretRedactor()
    payload = draft.to_dict()
    payload["body"] = redactor.redact(str(payload["body"]))
    payload["send_supported"] = False
    payload["sent"] = False
    payload["memory_behavior"] = "no_store"
    return payload


def send_request_preview(request: MessageSendRequest) -> dict[str, Any]:
    redactor = SecretRedactor()
    return {
        "action_id": request.action_id,
        "draft_id": request.draft_id,
        "channel": request.channel.value,
        "recipient": request.recipient.to_dict(),
        "body": redactor.redact(request.body),
        "attachments": [attachment.to_dict() for attachment in request.attachments],
        "risk_level": request.risk_level.value,
        "approval_required": request.approval_required,
        "approval_reuse_allowed": request.approval_reuse_allowed,
        "source_workflow": request.source_workflow,
        "exact_preview_required": request.exact_preview_required,
        "rollback_available": False,
        "rollback_note": "Message sending is irreversible after provider acceptance.",
        "execution_note": "Messaging abstraction v1 does not execute sends directly.",
    }
