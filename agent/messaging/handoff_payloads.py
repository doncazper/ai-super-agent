from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agent.messaging.errors import MessagingError
from agent.safety.policy import RiskLevel


@dataclass(frozen=True)
class IOSComposeHandoffPayload:
    draft_id: str
    recipient: str
    body: str
    expires_at: str
    action_id: str = ""
    nonce: str = ""
    integrity_hash: str = ""
    risk_level: RiskLevel = RiskLevel.CRITICAL
    approval_status: str = "user_confirmed_compose_mode"
    attachments: list[dict[str, Any]] = field(default_factory=list)
    channel: str = "ios_compose"
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    requires_user_tap_send: bool = True
    silent_send_supported: bool = False
    send_executed: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["risk_level"] = self.risk_level.value
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "IOSComposeHandoffPayload":
        return cls(
            draft_id=str(payload["draft_id"]),
            recipient=str(payload["recipient"]),
            body=str(payload["body"]),
            attachments=list(payload.get("attachments") or []),
            expires_at=str(payload["expires_at"]),
            action_id=str(payload.get("action_id") or ""),
            nonce=str(payload.get("nonce") or ""),
            integrity_hash=str(payload.get("integrity_hash") or ""),
            risk_level=RiskLevel(str(payload.get("risk_level") or RiskLevel.CRITICAL.value)),
            approval_status=str(payload.get("approval_status") or "user_confirmed_compose_mode"),
            channel=str(payload.get("channel") or "ios_compose"),
            created_at=str(payload.get("created_at") or datetime.now(UTC).isoformat()),
            requires_user_tap_send=bool(payload.get("requires_user_tap_send", True)),
            silent_send_supported=bool(payload.get("silent_send_supported", False)),
            send_executed=bool(payload.get("send_executed", False)),
        )

    def is_expired(self, now: datetime | None = None) -> bool:
        check_time = now or datetime.now(UTC)
        try:
            expires_at = datetime.fromisoformat(self.expires_at)
        except ValueError:
            return True
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        return check_time >= expires_at


def ios_compose_payload_dir(project_root: str | Path) -> Path:
    return Path(project_root).resolve() / "workspace" / "messaging" / "ios_compose" / "payloads"


def ios_compose_result_dir(project_root: str | Path) -> Path:
    return Path(project_root).resolve() / "workspace" / "messaging" / "ios_compose" / "results"


def payload_path(project_root: str | Path, draft_id: str) -> Path:
    _validate_simple_id(draft_id, "draft_id")
    return ios_compose_payload_dir(project_root) / f"{draft_id}.json"


def result_path(project_root: str | Path, draft_id: str) -> Path:
    _validate_simple_id(draft_id, "draft_id")
    return ios_compose_result_dir(project_root) / f"{draft_id}.json"


def save_handoff_payload(project_root: str | Path, payload: IOSComposeHandoffPayload) -> Path:
    path = payload_path(project_root, payload.draft_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return path


def load_handoff_payload(project_root: str | Path, draft_id: str) -> IOSComposeHandoffPayload:
    path = payload_path(project_root, draft_id)
    if not path.exists():
        raise FileNotFoundError(f"iOS compose handoff payload not found: {draft_id}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("iOS compose handoff payload must contain a JSON object")
    parsed = IOSComposeHandoffPayload.from_dict(payload)
    expected = integrity_hash(parsed)
    if parsed.integrity_hash and parsed.integrity_hash != expected:
        raise MessagingError("iOS compose handoff payload integrity hash mismatch")
    return parsed


def save_compose_result(project_root: str | Path, draft_id: str, result: dict[str, Any]) -> Path:
    path = result_path(project_root, draft_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return path


def load_compose_result(project_root: str | Path, draft_id: str) -> dict[str, Any] | None:
    path = result_path(project_root, draft_id)
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("iOS compose result must contain a JSON object")
    return payload


def integrity_hash(payload: IOSComposeHandoffPayload | dict[str, Any]) -> str:
    raw = payload.to_dict() if isinstance(payload, IOSComposeHandoffPayload) else dict(payload)
    raw.pop("integrity_hash", None)
    encoded = json.dumps(raw, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _validate_simple_id(value: str, name: str) -> None:
    if not value or "/" in value or "\\" in value or ".." in value:
        raise MessagingError(f"{name} must be a simple local id")
