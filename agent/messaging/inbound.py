from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agent.messaging.actions import create_message_draft
from agent.messaging.errors import MessagingError
from agent.safety.policy import RiskLevel
from agent.safety.redaction import SecretRedactor
from agent.safety.trust import TrustLevel
from agent.tools.errors import ToolError


PRIVATE_MESSAGES_PATH_MARKERS = (
    "/library/messages",
    "\\library\\messages",
    "chat.db",
)


@dataclass(frozen=True)
class IncomingMessage:
    message_id: str
    provider: str
    channel: str
    sender_ref: str
    sender_display: str
    received_at: str
    subject_or_context: str
    body: str
    message_preview: str
    full_message_ref: str
    source_ref: str
    trust_level: TrustLevel = TrustLevel.UNTRUSTED_MESSAGE
    risk_level: RiskLevel = RiskLevel.MEDIUM
    status: str = "new"
    tags: list[str] = field(default_factory=list)
    stored_in_memory: bool = False

    def to_dict(self, *, include_body: bool = True) -> dict[str, Any]:
        payload = asdict(self)
        payload["trust_level"] = self.trust_level.value
        payload["risk_level"] = self.risk_level.value
        if not include_body:
            payload.pop("body", None)
            payload["full_message_ref"] = "[SELECTED_SHOW_REQUIRED]"
        payload["lead_candidate"] = incoming_message_to_lead_candidate(self, include_body_ref=include_body)
        return payload


def inbound_store_dir(project_root: str | Path) -> Path:
    return Path(project_root).resolve() / "workspace" / "messaging" / "inbound"


def inbound_store_path(project_root: str | Path) -> Path:
    return inbound_store_dir(project_root) / "messages.jsonl"


def import_manual_message(project_root: str | Path, from_file: str | Path) -> tuple[IncomingMessage, Path]:
    root = Path(project_root).resolve()
    source = _resolve_workspace_file(root, from_file)
    text = source.read_text(encoding="utf-8")
    message_id = _message_id("manual", str(source), text)
    message = IncomingMessage(
        message_id=message_id,
        provider="manual",
        channel="manual_handoff",
        sender_ref="manual-import",
        sender_display="Manual import",
        received_at=datetime.now(UTC).isoformat(),
        subject_or_context=source.name,
        body=text,
        message_preview=_preview(text),
        full_message_ref=str(source),
        source_ref=str(source),
        tags=["manual_import", "workspace_file"],
    )
    path = save_incoming_message(root, message)
    return message, path


def save_incoming_message(project_root: str | Path, message: IncomingMessage) -> Path:
    path = inbound_store_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = {item.message_id: item for item in load_manual_messages(project_root)}
    existing[message.message_id] = message
    with path.open("w", encoding="utf-8") as handle:
        for item in sorted(existing.values(), key=lambda item: item.received_at):
            handle.write(json.dumps(item.to_dict(include_body=True), sort_keys=True) + "\n")
    return path


def load_manual_messages(project_root: str | Path) -> list[IncomingMessage]:
    path = inbound_store_path(project_root)
    if not path.exists():
        return []
    messages: list[IncomingMessage] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ToolError(f"malformed inbound message store: {path}") from exc
        if isinstance(payload, dict):
            messages.append(_message_from_payload(payload))
    return messages


def get_incoming_message(project_root: str | Path, message_id: str, extra_messages: list[IncomingMessage] | None = None) -> IncomingMessage:
    for message in [*load_manual_messages(project_root), *(extra_messages or [])]:
        if message.message_id == message_id:
            return message
    raise ToolError(f"incoming message not found: {message_id}")


def list_incoming_messages(
    project_root: str | Path,
    *,
    include_mock: bool = True,
    limit: int = 25,
    mock_messages: list[IncomingMessage] | None = None,
) -> dict[str, Any]:
    messages = load_manual_messages(project_root)
    if include_mock:
        messages.extend(mock_messages or [])
    messages = sorted(messages, key=lambda item: item.received_at, reverse=True)[: max(1, min(limit, 100))]
    return {
        "status": "ok",
        "messages": [message.to_dict(include_body=False) for message in messages],
        "count": len(messages),
        "providers": sorted({message.provider for message in messages}),
        "mock_provider_included": include_mock,
        "private_messages_database_accessed": False,
        "full_disk_access_required": False,
        "background_watcher": False,
        "stored_in_memory": False,
    }


def show_incoming_message(
    project_root: str | Path,
    message_id: str,
    *,
    mock_messages: list[IncomingMessage] | None = None,
) -> dict[str, Any]:
    message = get_incoming_message(project_root, message_id, extra_messages=mock_messages)
    return {
        "status": "ok",
        "message": message.to_dict(include_body=True),
        "trust_level": TrustLevel.UNTRUSTED_MESSAGE.value,
        "private_messages_database_accessed": False,
        "full_disk_access_required": False,
        "stored_in_memory": False,
    }


def draft_reply_to_incoming_message(
    project_root: str | Path,
    message_id: str,
    *,
    mock_messages: list[IncomingMessage] | None = None,
) -> dict[str, Any]:
    message = get_incoming_message(project_root, message_id, extra_messages=mock_messages)
    draft_body = _draft_reply_body(message.body)
    try:
        draft, path, invalidated = create_message_draft(
            str(Path(project_root).resolve()),
            channel="manual_handoff",
            recipient=message.sender_display or message.sender_ref or "Manual recipient",
            body=draft_body,
            recipient_display=message.sender_display,
            source_context={
                "source": "incoming_message",
                "message_id": message.message_id,
                "provider": message.provider,
                "trust": TrustLevel.UNTRUSTED_MESSAGE.value,
                "requested_by": "messages_inbox_draft_reply",
            },
            risk_level=RiskLevel.HIGH,
        )
    except (MessagingError, ValueError, FileNotFoundError) as exc:
        raise ToolError(str(exc)) from exc
    return {
        "status": "ok",
        "message_id": message.message_id,
        "draft_id": draft.draft_id,
        "message_draft": draft.to_dict(),
        "draft_path": path,
        "invalidated_action_ids": invalidated,
        "send_executed": False,
        "send_action_created": False,
        "automatic_reply": False,
        "stored_in_memory": False,
        "trust_level": TrustLevel.UNTRUSTED_MESSAGE.value,
    }


def incoming_message_to_lead_candidate(message: IncomingMessage, *, include_body_ref: bool = True) -> dict[str, Any]:
    return {
        "lead_id": f"inbound-{message.message_id}",
        "source": message.provider,
        "channel": message.channel,
        "sender": message.sender_display or message.sender_ref,
        "received_at": message.received_at,
        "subject_or_context": message.subject_or_context,
        "message_preview": message.message_preview,
        "full_message_ref": message.full_message_ref if include_body_ref else "[SELECTED_SHOW_REQUIRED]",
        "trust_level": TrustLevel.UNTRUSTED_MESSAGE.value,
        "risk_level": message.risk_level.value,
        "status": "new",
        "linked_thread_id": message.message_id,
        "linked_actions": [],
        "stored_in_memory": False,
    }


def _resolve_workspace_file(root: Path, from_file: str | Path) -> Path:
    raw = str(from_file)
    lowered = raw.lower()
    if any(marker in lowered for marker in PRIVATE_MESSAGES_PATH_MARKERS):
        raise ToolError("private Messages database paths such as ~/Library/Messages/chat.db are blocked")
    candidate = Path(from_file)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.expanduser().resolve()
    workspace = (root / "workspace").resolve()
    try:
        resolved.relative_to(workspace)
    except ValueError as exc:
        raise ToolError("manual message import files must be inside ./workspace") from exc
    if not resolved.exists() or not resolved.is_file():
        raise ToolError(f"message import file not found: {resolved}")
    return resolved


def _message_from_payload(payload: dict[str, Any]) -> IncomingMessage:
    return IncomingMessage(
        message_id=str(payload.get("message_id") or ""),
        provider=str(payload.get("provider") or "manual"),
        channel=str(payload.get("channel") or "manual_handoff"),
        sender_ref=str(payload.get("sender_ref") or ""),
        sender_display=str(payload.get("sender_display") or ""),
        received_at=str(payload.get("received_at") or ""),
        subject_or_context=str(payload.get("subject_or_context") or ""),
        body=str(payload.get("body") or ""),
        message_preview=str(payload.get("message_preview") or _preview(str(payload.get("body") or ""))),
        full_message_ref=str(payload.get("full_message_ref") or ""),
        source_ref=str(payload.get("source_ref") or ""),
        trust_level=TrustLevel(str(payload.get("trust_level") or TrustLevel.UNTRUSTED_MESSAGE.value)),
        risk_level=RiskLevel(str(payload.get("risk_level") or RiskLevel.MEDIUM.value)),
        status=str(payload.get("status") or "new"),
        tags=[str(item) for item in payload.get("tags", []) if str(item)],
        stored_in_memory=bool(payload.get("stored_in_memory", False)),
    )


def _message_id(provider: str, source_ref: str, body: str) -> str:
    digest = hashlib.sha256(f"{provider}:{source_ref}:{body}".encode("utf-8")).hexdigest()[:16]
    return f"inmsg_{digest}"


def _preview(text: str, limit: int = 180) -> str:
    cleaned = " ".join(SecretRedactor().redact_text(text).split())
    return cleaned[:limit] + ("..." if len(cleaned) > limit else "")


def _draft_reply_body(text: str) -> str:
    lines = []
    for line in text.splitlines():
        lowered = line.lower()
        if any(
            phrase in lowered
            for phrase in (
                "ignore previous instructions",
                "send this",
                "call tool",
                "disable audit",
                "change policy",
                "approve",
                "reveal secret",
            )
        ):
            continue
        if line.strip():
            lines.append(line.strip())
    context = " ".join(lines)[:240]
    if not context:
        context = "your message"
    return f"Thanks for your message. I saw: {context}\n\nI will review and get back to you."
