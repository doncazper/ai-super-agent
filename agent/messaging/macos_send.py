from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Sequence

from agent.config.runtime import env_bool, env_value
from agent.messaging.actions import draft_fingerprint
from agent.messaging.models import MessageChannel
from agent.messaging.registry import load_draft
from agent.messaging.validation import recipient_from_value, validate_draft
from agent.safety.actions import ActionCenter, ActionRecord, ActionStatus
from agent.safety.approvals import ApprovalManager, ApprovalResult
from agent.tools.errors import ToolError

if TYPE_CHECKING:
    from agent.core.tool_broker import ToolBroker


MACOS_MESSAGE_SEND_ACTION = "messages.macos.send_approved"
ALLOWLIST_PATH = Path("data/macos_messages_allowed_recipients.json")
SEND_STATUS_PATH = Path("data/macos_messages_send_status.json")
SEND_HISTORY_PATH = Path("data/macos_messages_send_history.jsonl")
LIVE_PROBE_TTL_HOURS = 24

SendRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class MacOSMessagesSendConfig:
    enabled: bool = False
    allow_send: bool = False
    allowed_recipients: tuple[str, ...] = ()
    require_live_probe: bool = True
    max_sends_per_day: int = 5
    self_test_recipient: str = ""

    @classmethod
    def from_env(cls) -> "MacOSMessagesSendConfig":
        return cls(
            enabled=env_bool("MACOS_MESSAGES_ENABLED", default=False),
            allow_send=env_bool("MACOS_MESSAGES_ALLOW_SEND", default=False),
            allowed_recipients=_parse_recipients(env_value("MACOS_MESSAGES_ALLOWED_RECIPIENTS", default="")),
            require_live_probe=env_bool("MACOS_MESSAGES_REQUIRE_LIVE_PROBE", default=True),
            max_sends_per_day=_parse_positive_int(env_value("MACOS_MESSAGES_MAX_SENDS_PER_DAY", default="5"), default=5),
            self_test_recipient=env_value("MACOS_MESSAGES_SELF_TEST_RECIPIENT", default="").strip(),
        )


@dataclass(frozen=True)
class MacOSMessagesStatus:
    status: str
    connector_enabled: bool
    send_allowed: bool
    allowed_recipient_count: int
    live_probe_required: bool
    live_probe_passed_recently: bool
    last_live_probe: dict[str, Any] | None = None
    max_sends_per_day: int = 5
    sends_today: int = 0
    send_capability_enabled: bool = False
    supported: bool | str = "unknown"
    limitations: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    private_messages_db_accessed: bool = False
    full_disk_access_required: bool = False
    sends_message: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def macos_messages_status(project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root).resolve()
    config = MacOSMessagesSendConfig.from_env()
    allowlisted = _load_allowed_recipients(root, config)
    probe = _load_send_status(root)
    sends_today = _count_sends_today(root)
    live_recent = _live_probe_recent_and_passed(probe)
    limitations: list[str] = []
    next_steps: list[str] = []
    if not config.enabled:
        limitations.append("MACOS_MESSAGES_ENABLED is false; the macOS Messages send adapter is disabled.")
        next_steps.append("Use iOS compose, manual draft handoff, or Apple Messages for Business planning until explicitly enabled.")
    if not config.allow_send:
        limitations.append("MACOS_MESSAGES_ALLOW_SEND is false; sends are blocked even if a draft is approved.")
    if config.require_live_probe and not live_recent:
        limitations.append("No recent passing live-send probe is recorded.")
        next_steps.append("Run `messages macos live-send-probe --to <self-test recipient>` only after explicit approval.")
    if not allowlisted:
        limitations.append("No macOS Messages recipients are allowlisted.")
        next_steps.append("Use `messages macos allow-recipient <recipient>` for a selected recipient before any approved send.")
    send_capability_enabled = (
        config.enabled
        and config.allow_send
        and bool(allowlisted)
        and (live_recent or not config.require_live_probe)
        and sends_today < config.max_sends_per_day
    )
    status = MacOSMessagesStatus(
        status="ok",
        connector_enabled=config.enabled,
        send_allowed=config.allow_send,
        allowed_recipient_count=len(allowlisted),
        live_probe_required=config.require_live_probe,
        live_probe_passed_recently=live_recent,
        last_live_probe=_public_probe_status(probe),
        max_sends_per_day=config.max_sends_per_day,
        sends_today=sends_today,
        send_capability_enabled=send_capability_enabled,
        supported=True if send_capability_enabled else "unknown",
        limitations=limitations,
        next_steps=next_steps,
        sends_message=False,
    )
    return status.to_dict()


def allow_macos_messages_recipient(project_root: str | Path, recipient: str) -> dict[str, Any]:
    parsed = recipient_from_value(recipient)
    address = parsed.channel_address or parsed.recipient_id
    if not address.strip():
        raise ToolError("macOS Messages allowlist requires one recipient")
    root = Path(project_root).resolve()
    config = MacOSMessagesSendConfig.from_env()
    current = set(_load_allowed_recipients(root, config))
    current.add(address)
    path = root / ALLOWLIST_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"allowed_recipients": sorted(current), "updated_at": _now()}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "status": "ok",
        "recipient": address,
        "allowed": True,
        "allowed_recipient_count": len(current),
        "path": str(path),
        "send_enabled": False,
        "notes": [
            "Allowlisting a recipient does not enable macOS Messages sending.",
            "A CRITICAL Action Center approval and recent live-send probe are still required.",
        ],
        "_audit": {
            "files_written": [str(path)],
            "result_summary": "macOS Messages recipient allowlist updated; no message was sent.",
        },
    }


def run_live_send_probe(
    project_root: str | Path,
    *,
    to: str,
    runner: SendRunner | None = None,
    platform_name: str | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    config = MacOSMessagesSendConfig.from_env()
    recipient = recipient_from_value(to).channel_address or to.strip()
    _require_single_recipient(recipient)
    if config.self_test_recipient and recipient != config.self_test_recipient:
        raise ToolError("live-send probe may only target MACOS_MESSAGES_SELF_TEST_RECIPIENT")
    if not config.enabled or not config.allow_send:
        result = _probe_failure(
            root,
            recipient=recipient,
            reason="macOS Messages send connector is disabled by config",
            status="disabled",
        )
        return result
    allowed = _load_allowed_recipients(root, config)
    if recipient not in allowed:
        result = _probe_failure(
            root,
            recipient=recipient,
            reason="recipient is not allowlisted",
            status="not_allowlisted",
        )
        return result
    body = f"AI Super Agent macOS Messages live-send probe at {_now()}. No reply needed."
    send = _attempt_macos_messages_send(
        recipient,
        body,
        runner=runner,
        platform_name=platform_name,
    )
    passed = bool(send["sent"])
    status = "passed" if passed else "unsupported"
    payload = {
        "status": status,
        "passed": passed,
        "recipient": recipient,
        "sent": passed,
        "body": body,
        "timestamp": _now(),
        "send_capability_known": passed,
        "failure_reason": "" if passed else send["error"],
        "commands_run": send["commands_run"],
        "private_messages_db_accessed": False,
        "full_disk_access_required": False,
        "limitations": [] if passed else ["Messages.app automation send path failed or is unsupported on this machine."],
        "next_steps": (
            ["A recent live-send probe is now recorded. Approved sends still require exact CRITICAL Action Center approval."]
            if passed
            else ["Use iOS compose, manual draft handoff, or Apple Messages for Business; do not fake send success."]
        ),
    }
    path = _save_send_status(root, payload)
    if passed:
        _record_send_history(root, "live_probe", recipient, status="sent")
    return {
        **payload,
        "connector_status_path": str(path),
        "_audit": {
            "files_written": [str(path)],
            "commands_run": send["commands_run"],
            "result_summary": f"macOS Messages live-send probe {status}; no private database read occurred.",
        },
    }


def send_approved_macos_message(
    project_root: str | Path,
    action_center: ActionCenter | None,
    *,
    action_id: str,
    draft_id: str,
    channel: str,
    to: str,
    body: str,
    attachments: list[str] | None = None,
    draft_fingerprint_value: str = "",
    runner: SendRunner | None = None,
    platform_name: str | None = None,
    **_: Any,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    record = _require_approved_action(action_center, action_id=action_id)
    approved_args = {
        "draft_id": draft_id,
        "channel": channel,
        "to": to,
        "body": body,
        "attachments": attachments or [],
    }
    _require_matching_args(record, approved_args)
    if channel != MessageChannel.MACOS_MESSAGES.value:
        raise ToolError("messages.macos.send_approved only supports channel=macos_messages")
    if attachments:
        raise ToolError("macOS Messages send v1 blocks attachments")
    recipient = recipient_from_value(to).channel_address or to.strip()
    _require_single_recipient(recipient)
    draft = load_draft(root, draft_id)
    validate_draft(draft)
    current_fingerprint = draft_fingerprint(draft)
    approved_fingerprint = draft_fingerprint_value or str(record.sanitized_args.get("draft_fingerprint") or "")
    if current_fingerprint != approved_fingerprint:
        raise ToolError("message draft changed after approval; create and approve a new send action")
    config = MacOSMessagesSendConfig.from_env()
    if not config.enabled or not config.allow_send:
        raise ToolError("macOS Messages send connector is disabled by config")
    if recipient not in _load_allowed_recipients(root, config):
        raise ToolError("recipient is not allowlisted for macOS Messages sending")
    probe = _load_send_status(root)
    if config.require_live_probe and not _live_probe_recent_and_passed(probe):
        raise ToolError("macOS Messages send requires a recent passing live-send probe")
    sends_today = _count_sends_today(root)
    if sends_today >= config.max_sends_per_day:
        raise ToolError("macOS Messages daily send rate limit exceeded")
    send = _attempt_macos_messages_send(recipient, body, runner=runner, platform_name=platform_name)
    if not send["sent"]:
        _save_send_status(
            root,
            {
                "status": "unsupported",
                "passed": False,
                "timestamp": _now(),
                "send_capability_known": False,
                "failure_reason": send["error"],
                "private_messages_db_accessed": False,
                "full_disk_access_required": False,
            },
        )
        raise ToolError(f"macOS Messages send unsupported or failed: {send['error']}")
    _record_send_history(root, action_id, recipient, status="sent")
    return {
        "status": "ok",
        "action": MACOS_MESSAGE_SEND_ACTION,
        "executed": True,
        "sent": True,
        "channel": channel,
        "to": recipient,
        "body": body,
        "attachments": [],
        "draft_id": draft_id,
        "action_id": action_id,
        "verification": "osascript_returncode_0_provider_accepted",
        "rollback_available": False,
        "rollback_note": "Message sending is irreversible after Messages.app accepts the send command.",
        "private_messages_db_accessed": False,
        "full_disk_access_required": False,
        "timestamp": _now(),
        "_audit": {
            "files_written": [str(root / SEND_HISTORY_PATH)],
            "commands_run": send["commands_run"],
            "result_summary": "macOS Messages approved send executed after Action Center approval, allowlist, live probe, and rate-limit checks.",
        },
    }


def execute_macos_message_send_action(
    broker: ToolBroker,
    center: ActionCenter,
    *,
    action_id: str,
) -> dict[str, Any]:
    record = center.get_action(action_id)
    if record is None:
        return {"status": "error", "executed": False, "error": "action not found", "action_id": action_id}
    if record.action_type != MACOS_MESSAGE_SEND_ACTION:
        center.record_failure(action_id, "macOS message send action type mismatch")
        return {
            "status": "error",
            "executed": False,
            "error": f"action type mismatch: expected {MACOS_MESSAGE_SEND_ACTION}, got {record.action_type}",
            "action_id": action_id,
            "action_status": record.status.value,
        }
    if record.status is not ActionStatus.APPROVED:
        center.record_failure(action_id, "macOS message send blocked because approval is missing")
        return {
            "status": "error",
            "executed": False,
            "error": "action must be approved in Action Center before execution",
            "action_id": action_id,
            "action_status": record.status.value,
        }
    tool_args = dict(record.sanitized_args)
    tool_args["action_id"] = action_id
    tool_call = {
        "id": f"action_{action_id}",
        "type": "function",
        "function": {
            "name": record.tool_name,
            "arguments": json.dumps(tool_args),
        },
    }
    previous_manager = broker.approval_manager

    def decision_provider(request: Any) -> ApprovalResult:
        if request.capability == record.capability and record.status is ActionStatus.APPROVED:
            return ApprovalResult.APPROVED
        return ApprovalResult.DENIED

    broker.approval_manager = ApprovalManager(
        decision_provider=decision_provider,
        store=center.approval_store,
    )
    broker.approval_manager.configure_audit(
        broker.audit_logger,
        session_id=broker.session_id,
        model=broker.model,
        route=broker.route,
    )
    try:
        result = broker.execute(tool_call)
    finally:
        broker.approval_manager = previous_manager
    payload = json.loads(result.content)
    if result.allowed:
        center.consume_approval_once(action_id)
    else:
        center.record_failure(action_id, "macOS message send ToolBroker execution failed or was denied")
    refreshed = center.get_action(action_id)
    return {
        "status": "ok" if result.allowed else "error",
        "executed": result.allowed,
        "action_id": action_id,
        "action_status": refreshed.status.value if refreshed else "unknown",
        "tool_name": record.tool_name,
        "tool_result": payload,
        "debug": result.debug or {},
    }


def make_macos_send_tools(project_root: str | Path, action_center: ActionCenter | None = None) -> dict[str, Any]:
    root = Path(project_root).resolve()

    def status() -> dict[str, Any]:
        return {
            **macos_messages_status(root),
            "_audit": {
                "result_summary": "macOS Messages send adapter status inspected; no message was sent and no private database was read."
            },
        }

    def allow_recipient(recipient: str) -> dict[str, Any]:
        return allow_macos_messages_recipient(root, recipient)

    def live_send_probe(to: str) -> dict[str, Any]:
        return run_live_send_probe(root, to=to)

    def send_approved(
        action_id: str,
        draft_id: str,
        channel: str,
        to: str,
        body: str,
        attachments: list[str] | None = None,
        draft_fingerprint: str = "",
        **kwargs: Any,
    ) -> dict[str, Any]:
        return send_approved_macos_message(
            root,
            action_center,
            action_id=action_id,
            draft_id=draft_id,
            channel=channel,
            to=to,
            body=body,
            attachments=attachments or [],
            draft_fingerprint_value=draft_fingerprint,
            **kwargs,
        )

    return {
        "messages.macos.status": status,
        "messages.macos.allowed_recipients.manage": allow_recipient,
        "messages.macos.live_send_probe": live_send_probe,
        "messages.macos.send_approved": send_approved,
    }


MACOS_SEND_SCHEMAS: dict[str, dict[str, Any]] = {
    "messages.macos.status": {
        "type": "function",
        "function": {
            "name": "messages.macos.status",
            "description": "Inspect disabled-by-default macOS Messages send adapter status without sending or reading private data.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    "messages.macos.allowed_recipients.manage": {
        "type": "function",
        "function": {
            "name": "messages.macos.allowed_recipients.manage",
            "description": "Add one selected recipient to the local macOS Messages allowlist; does not send.",
            "parameters": {
                "type": "object",
                "properties": {"recipient": {"type": "string"}},
                "required": ["recipient"],
                "additionalProperties": False,
            },
        },
    },
    "messages.macos.live_send_probe": {
        "type": "function",
        "function": {
            "name": "messages.macos.live_send_probe",
            "description": "Approval-gated harmless self-test send probe for macOS Messages; disabled by default.",
            "parameters": {
                "type": "object",
                "properties": {"to": {"type": "string"}},
                "required": ["to"],
                "additionalProperties": False,
            },
        },
    },
    "messages.macos.send_approved": {
        "type": "function",
        "function": {
            "name": "messages.macos.send_approved",
            "description": "Send one approved macOS Messages draft after exact Action Center approval, live probe, allowlist, and rate-limit checks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action_id": {"type": "string"},
                    "draft_id": {"type": "string"},
                    "channel": {"type": "string"},
                    "to": {"type": "string"},
                    "body": {"type": "string"},
                    "attachments": {"type": "array", "items": {"type": "string"}},
                    "draft_fingerprint": {"type": "string"},
                },
                "required": ["action_id", "draft_id", "channel", "to", "body"],
                "additionalProperties": False,
            },
        },
    },
}


def _require_approved_action(action_center: ActionCenter | None, *, action_id: str) -> ActionRecord:
    if not action_id:
        raise ToolError("messages.macos.send_approved must originate from an approved Action Center item")
    if action_center is None:
        raise ToolError("messages.macos.send_approved requires Action Center verification")
    record = action_center.get_action(action_id)
    if record is None:
        raise ToolError("messages.macos.send_approved Action Center item was not found")
    if record.action_type != MACOS_MESSAGE_SEND_ACTION:
        raise ToolError("messages.macos.send_approved Action Center item type mismatch")
    if record.status is not ActionStatus.APPROVED:
        raise ToolError("messages.macos.send_approved Action Center item must be approved before execution")
    return record


def _require_matching_args(record: ActionRecord, submitted_args: dict[str, Any]) -> None:
    for key, submitted_value in submitted_args.items():
        if record.sanitized_args.get(key) != submitted_value:
            raise ToolError("messages.macos.send_approved arguments must match the approved Action Center preview")


def _attempt_macos_messages_send(
    recipient: str,
    body: str,
    *,
    runner: SendRunner | None = None,
    platform_name: str | None = None,
) -> dict[str, Any]:
    current_platform = platform_name or platform.system()
    if current_platform != "Darwin":
        return {
            "sent": False,
            "error": "macOS Messages sending is supported only on macOS",
            "commands_run": [],
        }
    osascript = shutil.which("osascript")
    if not osascript:
        return {"sent": False, "error": "`osascript` is unavailable", "commands_run": []}
    script = _messages_send_applescript(recipient, body)
    command = [osascript, "-e", script]
    run = runner or _run_command
    try:
        completed = run(command)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"sent": False, "error": str(exc), "commands_run": ["osascript -e <Messages send script redacted>"]}
    error = " ".join((completed.stderr or "").split())[:300]
    return {
        "sent": completed.returncode == 0,
        "error": "" if completed.returncode == 0 else (error or f"osascript exited {completed.returncode}"),
        "commands_run": ["osascript -e <Messages send script redacted>"],
    }


def _messages_send_applescript(recipient: str, body: str) -> str:
    return (
        'tell application "Messages"\n'
        '  set targetService to first service whose service type = iMessage\n'
        f"  set targetBuddy to buddy {_applescript_string(recipient)} of targetService\n"
        f"  send {_applescript_string(body)} to targetBuddy\n"
        "end tell"
    )


def _applescript_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _run_command(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        capture_output=True,
        check=False,
        text=True,
        timeout=10,
    )


def _probe_failure(root: Path, *, recipient: str, reason: str, status: str) -> dict[str, Any]:
    payload = {
        "status": status,
        "passed": False,
        "recipient": recipient,
        "sent": False,
        "timestamp": _now(),
        "send_capability_known": False,
        "failure_reason": reason,
        "commands_run": [],
        "private_messages_db_accessed": False,
        "full_disk_access_required": False,
        "limitations": [reason],
        "next_steps": ["Use iOS compose, manual draft handoff, or Apple Messages for Business until the connector is explicitly enabled."],
    }
    path = _save_send_status(root, payload)
    return {
        **payload,
        "connector_status_path": str(path),
        "_audit": {
            "files_written": [str(path)],
            "commands_run": [],
            "result_summary": f"macOS Messages live-send probe did not run send command: {reason}.",
        },
    }


def _save_send_status(root: Path, payload: dict[str, Any]) -> Path:
    path = root / SEND_STATUS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _load_send_status(root: Path) -> dict[str, Any] | None:
    path = root / SEND_STATUS_PATH
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"status": "unreadable"}
    return payload if isinstance(payload, dict) else {"status": "invalid"}


def _public_probe_status(probe: dict[str, Any] | None) -> dict[str, Any] | None:
    if not probe:
        return None
    return {
        "status": probe.get("status", "unknown"),
        "passed": bool(probe.get("passed")),
        "timestamp": probe.get("timestamp", ""),
        "send_capability_known": bool(probe.get("send_capability_known")),
        "failure_reason": probe.get("failure_reason", ""),
    }


def _live_probe_recent_and_passed(probe: dict[str, Any] | None) -> bool:
    if not probe or not probe.get("passed"):
        return False
    try:
        timestamp = datetime.fromisoformat(str(probe.get("timestamp")))
    except ValueError:
        return False
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)
    return datetime.now(UTC) - timestamp <= timedelta(hours=LIVE_PROBE_TTL_HOURS)


def _record_send_history(root: Path, action_id: str, recipient: str, *, status: str) -> None:
    path = root / SEND_HISTORY_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp": _now(),
        "action_id": action_id,
        "recipient": recipient,
        "status": status,
        "private_messages_db_accessed": False,
        "full_disk_access_required": False,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def _count_sends_today(root: Path) -> int:
    path = root / SEND_HISTORY_PATH
    if not path.exists():
        return 0
    today = datetime.now(UTC).date().isoformat()
    count = 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if str(payload.get("status")) != "sent":
            continue
        if str(payload.get("timestamp", "")).startswith(today):
            count += 1
    return count


def _load_allowed_recipients(root: Path, config: MacOSMessagesSendConfig) -> tuple[str, ...]:
    recipients = set(config.allowed_recipients)
    path = root / ALLOWLIST_PATH
    if path.exists():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            values = payload.get("allowed_recipients", []) if isinstance(payload, dict) else []
        except (OSError, json.JSONDecodeError):
            values = []
        for value in values:
            if isinstance(value, str) and value.strip():
                recipients.add(value.strip())
    return tuple(sorted(recipients))


def _parse_recipients(raw: str) -> tuple[str, ...]:
    recipients: list[str] = []
    for part in raw.replace(";", ",").split(","):
        stripped = part.strip()
        if stripped:
            recipients.append(stripped)
    return tuple(recipients)


def _parse_positive_int(raw: str, *, default: int) -> int:
    try:
        parsed = int(raw)
    except ValueError:
        return default
    return parsed if parsed > 0 else default


def _require_single_recipient(recipient: str) -> None:
    if not recipient.strip():
        raise ToolError("macOS Messages send requires exactly one recipient")
    if "," in recipient or ";" in recipient:
        raise ToolError("bulk or group macOS Messages sends are denied")


def _now() -> str:
    return datetime.now(UTC).isoformat()
