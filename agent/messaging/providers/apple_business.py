from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

from agent.leads.classifier import sanitize_untrusted_lead_text
from agent.leads.models import LeadPriority, LeadRecord, LeadSourceType, LeadStatus
from agent.messaging.actions import create_message_draft
from agent.safety.actions import ActionCenter
from agent.safety.policy import RiskLevel
from agent.safety.trust import TrustLevel
from agent.tools.errors import ToolError


APPLE_BUSINESS_SCHEMAS: dict[str, dict[str, Any]] = {
    "apple_business.doctor": {
        "type": "function",
        "function": {
            "name": "apple_business.doctor",
            "description": "Inspect Apple Messages for Business provider readiness without using credentials or sending.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    "apple_business.status": {
        "type": "function",
        "function": {
            "name": "apple_business.status",
            "description": "Show disabled-by-default Apple Messages for Business provider status.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    "apple_business.inbound.receive": {
        "type": "function",
        "function": {
            "name": "apple_business.inbound.receive",
            "description": "Create a local mock Apple Messages for Business inbound lead; no live webhook is read.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sender": {"type": "string"},
                    "message": {"type": "string"},
                    "subject": {"type": "string"},
                    "conversation_id": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
    },
    "apple_business.message.draft_response": {
        "type": "function",
        "function": {
            "name": "apple_business.message.draft_response",
            "description": "Create a local MessageDraft response for one mock Apple Business lead; does not send.",
            "parameters": {
                "type": "object",
                "properties": {"lead_id": {"type": "string"}},
                "required": ["lead_id"],
                "additionalProperties": False,
            },
        },
    },
    "apple_business.conversation.status": {
        "type": "function",
        "function": {
            "name": "apple_business.conversation.status",
            "description": "Show local mock Apple Business conversation status metadata without provider calls.",
            "parameters": {
                "type": "object",
                "properties": {"lead_id": {"type": "string"}},
                "required": ["lead_id"],
                "additionalProperties": False,
            },
        },
    },
}


@dataclass(frozen=True)
class AppleBusinessProviderModel:
    provider_name: str
    configured: bool
    account_id: str = ""
    webhook_url: str = ""
    send_endpoint: str = ""
    inbound_events: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    setup_hint: str = ""
    enabled: bool = False
    send_enabled: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["webhook_url"] = _safe_endpoint(self.webhook_url)
        payload["send_endpoint"] = _safe_endpoint(self.send_endpoint)
        return payload


class AppleBusinessProviderError(ToolError):
    pass


class AppleBusinessProviderStub:
    def __init__(self, project_root: str | Path, *, environ: Mapping[str, str] | None = None) -> None:
        self.project_root = Path(project_root).resolve()
        self.environ = environ or os.environ
        self.store_dir = self.project_root / "workspace" / "leads" / "apple_business"

    def provider_model(self) -> AppleBusinessProviderModel:
        provider = _env(self.environ, "APPLE_BUSINESS_PROVIDER", "disabled")
        enabled = _env_bool(self.environ, "APPLE_BUSINESS_ENABLED", default=False)
        account_id = _env(self.environ, "APPLE_BUSINESS_ACCOUNT_ID")
        webhook_url = _env(self.environ, "APPLE_BUSINESS_WEBHOOK_URL")
        send_endpoint = _env(self.environ, "APPLE_BUSINESS_SEND_ENDPOINT")
        configured = enabled and provider not in {"", "disabled"} and bool(account_id)
        return AppleBusinessProviderModel(
            provider_name=provider,
            configured=configured,
            enabled=enabled,
            account_id=account_id if configured else "",
            webhook_url=webhook_url if configured else "",
            send_endpoint=send_endpoint if configured else "",
            inbound_events=["mock_inbound"] if not configured else ["webhook_placeholder", "mock_inbound"],
            capabilities=[
                "apple_business.inbound.receive",
                "apple_business.message.draft_response",
                "apple_business.conversation.status",
                "apple_business.message.send_approved_future_disabled",
            ],
            setup_hint=(
                "Apple Messages for Business provider is disabled. Choose and configure an official Apple Messages "
                "for Business provider path, set account/webhook metadata, then pass a separate live-provider release gate."
            ),
            send_enabled=False,
        )

    def status(self) -> dict[str, Any]:
        model = self.provider_model()
        return {
            "status": "ok",
            "provider": model.to_dict(),
            "configured": model.configured,
            "enabled": model.enabled,
            "send_enabled": False,
            "credentials_required_for_v1": False,
            "credentials_loaded": False,
            "hardcoded_credentials": False,
            "personal_imessage_automation_used": False,
            "private_messages_database_accessed": False,
            "full_disk_access_required": False,
            "sends_message": False,
            "setup_hint": model.setup_hint,
            "_audit": {"result_summary": "Apple Business provider status inspected; no provider call or send."},
        }

    def doctor(self) -> dict[str, Any]:
        model = self.provider_model()
        warnings: list[str] = []
        if not model.enabled:
            warnings.append("Provider disabled by default: set APPLE_BUSINESS_ENABLED=true only after provider review.")
        if not model.configured:
            warnings.append("Live provider is not configured; mock inbound remains available for local tests only.")
        if _env(self.environ, "APPLE_BUSINESS_API_KEY") or _env(self.environ, "APPLE_BUSINESS_CLIENT_SECRET"):
            warnings.append("Secret-like Apple Business env vars are present; doctor reports presence only and never prints values.")
        return {
            "status": "ok",
            "provider": model.to_dict(),
            "warnings": warnings,
            "setup_options": [
                "Apple Messages for Business account/provider setup",
                "provider webhook integration reviewed as selected-scope lead intake",
                "mock provider for local tests",
            ],
            "not_endorsements": True,
            "no_live_provider_call": True,
            "send_disabled_by_default": True,
            "send_risk_level": RiskLevel.CRITICAL.value,
            "_audit": {"result_summary": "Apple Business provider doctor inspected config metadata only."},
        }

    def mock_inbound(
        self,
        *,
        sender: str = "",
        message: str = "",
        subject: str = "",
        conversation_id: str = "",
    ) -> dict[str, Any]:
        safe_sender = sender.strip() or "Apple Business Mock Customer"
        body = message.strip() or "I'd like help with a business inquiry and would appreciate a follow-up."
        subject_value = subject.strip() or "Apple Business mock inquiry"
        conversation = _simple_id(conversation_id.strip() or f"apple-business-{_hash_short(safe_sender + body)}")
        lead = LeadRecord(
            lead_id=f"amb-{_hash_short(conversation + safe_sender + body)}",
            source=LeadSourceType.APPLE_MESSAGES_FOR_BUSINESS,
            channel="apple_messages_for_business",
            sender_ref=f"apple-business:{conversation}",
            sender_display=safe_sender,
            received_at=datetime.now(UTC).isoformat(),
            subject_or_context=subject_value,
            message_preview=body,
            full_message_ref=f"apple-business://conversation/{conversation}",
            trust_level=TrustLevel.UNTRUSTED_MESSAGE,
            risk_level=RiskLevel.MEDIUM,
            status=LeadStatus.NEW,
            tags=["apple_business", "mock_inbound"],
            priority=LeadPriority.NORMAL,
        )
        path = self._write_lead(lead)
        return {
            "status": "ok",
            "lead": lead.to_dict(),
            "lead_id": lead.lead_id,
            "lead_path": str(path),
            "mapped_to_lead_inbox": True,
            "trust_level": TrustLevel.UNTRUSTED_MESSAGE.value,
            "provider_configured": self.provider_model().configured,
            "send_executed": False,
            "stored_in_memory": False,
            "_audit": {
                "files_written": [str(path)],
                "result_summary": f"Mock Apple Business inbound lead {lead.lead_id} stored; no provider read or send.",
            },
        }

    def draft_response(self, lead_id: str, *, action_center: ActionCenter | None = None) -> dict[str, Any]:
        lead = self._read_lead(lead_id)
        safe_preview = sanitize_untrusted_lead_text(lead.message_preview)
        draft, draft_path, invalidated = create_message_draft(
            str(self.project_root),
            channel="apple_messages_for_business",
            recipient=lead.sender_display or lead.sender_ref,
            body=_draft_body(lead, safe_preview),
            recipient_display=lead.sender_display,
            source_context={
                "source": "apple_business_message",
                "lead_id": lead.lead_id,
                "lead_source": lead.source.value,
                "trust": lead.trust_level.value,
                "requested_by": "apple_business_cli",
            },
            risk_level=RiskLevel.MEDIUM,
            action_center=action_center,
        )
        return {
            "status": "ok",
            "lead_id": lead.lead_id,
            "message_draft": draft.to_dict(),
            "draft_path": draft_path,
            "send_executed": False,
            "send_action_created": False,
            "invalidated_action_ids": invalidated,
            "stored_in_memory": False,
            "_audit": {
                "files_read": [str(self._lead_path(lead_id))],
                "files_written": [draft_path],
                "result_summary": f"Apple Business draft response created for {lead_id}; no send action created.",
            },
        }

    def conversation_status(self, lead_id: str) -> dict[str, Any]:
        lead = self._read_lead(lead_id)
        return {
            "status": "ok",
            "lead_id": lead.lead_id,
            "conversation": {
                "source": lead.source.value,
                "channel": lead.channel,
                "status": lead.status.value,
                "full_message_ref": lead.full_message_ref,
                "send_enabled": False,
                "approval_required_for_send": "per_action",
            },
            "provider_configured": self.provider_model().configured,
            "stored_in_memory": False,
            "_audit": {
                "files_read": [str(self._lead_path(lead_id))],
                "result_summary": f"Apple Business conversation status shown for {lead_id}; no provider call or send.",
            },
        }

    def _write_lead(self, lead: LeadRecord) -> Path:
        self.store_dir.mkdir(parents=True, exist_ok=True)
        path = self._lead_path(lead.lead_id)
        path.write_text(json.dumps(lead.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return path

    def _read_lead(self, lead_id: str) -> LeadRecord:
        if not lead_id or "/" in lead_id or "\\" in lead_id or ".." in lead_id:
            raise AppleBusinessProviderError("lead_id must be a simple local Apple Business lead id")
        path = self._lead_path(lead_id)
        if not path.exists():
            raise AppleBusinessProviderError(f"Apple Business lead not found: {lead_id}. Run apple-business mock-inbound first.")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise AppleBusinessProviderError("Apple Business lead file must contain a JSON object")
        return LeadRecord(
            lead_id=str(payload["lead_id"]),
            source=LeadSourceType(str(payload["source"])),
            channel=str(payload["channel"]),
            sender_ref=str(payload.get("sender_ref", "")),
            sender_display=str(payload.get("sender_display", "")),
            received_at=str(payload.get("received_at", "")),
            subject_or_context=str(payload.get("subject_or_context", "")),
            message_preview=str(payload.get("message_preview", "")),
            full_message_ref=str(payload.get("full_message_ref", "")),
            trust_level=TrustLevel(str(payload.get("trust_level", TrustLevel.UNTRUSTED_MESSAGE.value))),
            risk_level=RiskLevel(str(payload.get("risk_level", RiskLevel.MEDIUM.value))),
            status=LeadStatus(str(payload.get("status", LeadStatus.NEW.value))),
            tags=[str(item) for item in payload.get("tags", [])],
            priority=LeadPriority(str(payload.get("priority", LeadPriority.NORMAL.value))),
        )

    def _lead_path(self, lead_id: str) -> Path:
        return self.store_dir / f"{lead_id}.json"


def make_apple_business_tools(
    project_root: str | Path,
    *,
    action_center: ActionCenter | None = None,
) -> dict[str, Any]:
    provider = AppleBusinessProviderStub(project_root)
    return {
        "apple_business.doctor": provider.doctor,
        "apple_business.status": provider.status,
        "apple_business.inbound.receive": provider.mock_inbound,
        "apple_business.message.draft_response": lambda lead_id: provider.draft_response(
            lead_id,
            action_center=action_center,
        ),
        "apple_business.conversation.status": provider.conversation_status,
    }


def _draft_body(lead: LeadRecord, safe_preview: str) -> str:
    return (
        f"Hi {lead.sender_display or 'there'},\n\n"
        f"Thanks for reaching out through Apple Messages for Business about {lead.subject_or_context}.\n"
        "I can help with that. Could you share the best next detail or a few times that work for you?\n\n"
        "Best,\n\n"
        "[Your name]\n\n"
        f"Context used for draft: {safe_preview}"
    )


def _hash_short(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def _simple_id(value: str) -> str:
    cleaned = "".join(ch for ch in value if ch.isalnum() or ch in {"-", "_"})
    return cleaned[:80] or f"conversation-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"


def _env(env: Mapping[str, str], key: str, default: str = "") -> str:
    return env.get(key, default) or default


def _env_bool(env: Mapping[str, str], key: str, *, default: bool) -> bool:
    raw = _env(env, key)
    if not raw:
        return default
    return raw.casefold() in {"1", "true", "yes", "on"}


def _safe_endpoint(value: str) -> str:
    if not value:
        return ""
    if any(marker in value.casefold() for marker in ("token=", "key=", "secret=", "password=")):
        return "[REDACTED_ENDPOINT]"
    return value
