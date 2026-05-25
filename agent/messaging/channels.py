from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.messaging.actions import create_message_draft, create_send_action_from_draft
from agent.messaging.errors import MessagingError
from agent.messaging.ios_compose import IOS_COMPOSE_SCHEMAS, make_ios_compose_tools
from agent.messaging.macos_probe import MACOS_PROBE_SCHEMAS, make_macos_probe_tools
from agent.messaging.macos_send import MACOS_SEND_SCHEMAS, make_macos_send_tools
from agent.messaging.previews import draft_preview
from agent.messaging.providers.apple_business import APPLE_BUSINESS_SCHEMAS, make_apple_business_tools
from agent.messaging.providers.manual_inbox import ManualInboxProvider
from agent.messaging.providers.mock_inbox import MockInboxProvider
from agent.messaging.registry import MessageChannelRegistry, load_draft
from agent.messaging.validation import validate_draft
from agent.safety.actions import ActionCenter
from agent.safety.policy import RiskLevel
from agent.tools.errors import ToolError


MESSAGING_SCHEMAS: dict[str, dict[str, Any]] = {
    "messaging.channels": {
        "type": "function",
        "function": {
            "name": "messaging.channels",
            "description": "List channel-neutral messaging adapters and safety status; does not send or read private app data.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    "messaging.draft_show": {
        "type": "function",
        "function": {
            "name": "messaging.draft_show",
            "description": "Show one local workspace message draft preview with redaction; does not send.",
            "parameters": {
                "type": "object",
                "properties": {"draft_id": {"type": "string"}},
                "required": ["draft_id"],
                "additionalProperties": False,
            },
        },
    },
    "messaging.draft.preview": {
        "type": "function",
        "function": {
            "name": "messaging.draft.preview",
            "description": "Show one local workspace message draft preview with redaction; does not send.",
            "parameters": {
                "type": "object",
                "properties": {"draft_id": {"type": "string"}},
                "required": ["draft_id"],
                "additionalProperties": False,
            },
        },
    },
    "messaging.draft.create": {
        "type": "function",
        "function": {
            "name": "messaging.draft.create",
            "description": "Create or replace a local workspace message draft without sending.",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel": {"type": "string"},
                    "to": {"type": "string"},
                    "body": {"type": "string"},
                    "draft_id": {"type": "string"},
                    "recipient_display": {"type": "string"},
                    "source_context": {"type": "object"},
                    "risk_level": {"type": "string"},
                },
                "required": ["channel", "to", "body"],
                "additionalProperties": False,
            },
        },
    },
    "messaging.draft_validate": {
        "type": "function",
        "function": {
            "name": "messaging.draft_validate",
            "description": "Validate one local workspace message draft against the channel-neutral schema.",
            "parameters": {
                "type": "object",
                "properties": {"draft_id": {"type": "string"}},
                "required": ["draft_id"],
                "additionalProperties": False,
            },
        },
    },
    "messaging.action.create_send": {
        "type": "function",
        "function": {
            "name": "messaging.action.create_send",
            "description": "Create a CRITICAL Action Center message send proposal from a reviewed local draft. Does not send.",
            "parameters": {
                "type": "object",
                "properties": {
                    "draft_id": {"type": "string"},
                    "source_workflow": {"type": "string"},
                    "user_requested": {"type": "boolean"},
                },
                "required": ["draft_id"],
                "additionalProperties": False,
            },
        },
    },
    "messages.inbox.import_manual": {
        "type": "function",
        "function": {
            "name": "messages.inbox.import_manual",
            "description": "Import one manually selected workspace message file into the local inbox; no Messages database read.",
            "parameters": {
                "type": "object",
                "properties": {"from_file": {"type": "string"}},
                "required": ["from_file"],
                "additionalProperties": False,
            },
        },
    },
    "messages.inbox.list": {
        "type": "function",
        "function": {
            "name": "messages.inbox.list",
            "description": "List manual/mock incoming messages without reading private Messages data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "include_mock": {"type": "boolean"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                },
                "additionalProperties": False,
            },
        },
    },
    "messages.inbox.show": {
        "type": "function",
        "function": {
            "name": "messages.inbox.show",
            "description": "Show one manual/mock incoming message as untrusted message data; no private Messages data read.",
            "parameters": {
                "type": "object",
                "properties": {"message_id": {"type": "string"}},
                "required": ["message_id"],
                "additionalProperties": False,
            },
        },
    },
    "messages.inbox.draft_reply": {
        "type": "function",
        "function": {
            "name": "messages.inbox.draft_reply",
            "description": "Create a local draft reply to one manual/mock incoming message; does not send.",
            "parameters": {
                "type": "object",
                "properties": {"message_id": {"type": "string"}},
                "required": ["message_id"],
                "additionalProperties": False,
            },
        },
    },
}
MESSAGING_SCHEMAS.update(IOS_COMPOSE_SCHEMAS)
MESSAGING_SCHEMAS.update(MACOS_PROBE_SCHEMAS)
MESSAGING_SCHEMAS.update(MACOS_SEND_SCHEMAS)
MESSAGING_SCHEMAS.update(APPLE_BUSINESS_SCHEMAS)


def make_messaging_tools(project_root: str | Path, action_center: ActionCenter | None = None) -> dict[str, Any]:
    root = Path(project_root).resolve()
    registry = MessageChannelRegistry()
    manual_inbox = ManualInboxProvider(root)
    mock_inbox = MockInboxProvider()

    def channels() -> dict[str, Any]:
        return {
            "status": "ok",
            "channels": [definition.to_dict() for definition in registry.list_channels()],
            "send_tools_registered": True,
            "direct_send_supported": False,
            "notes": [
                "Messaging abstraction v1 is draft/preview/validation first.",
                "The macOS Messages approved-send adapter is registered but disabled by default and gated by Action Center, allowlist, live probe, and rate limits.",
                "No channel supports direct, silent, background, bulk, or ungated sending.",
            ],
            "_audit": {"result_summary": "Messaging channel registry inspected; no private app data read and no send executed."},
        }

    def draft_show(draft_id: str) -> dict[str, Any]:
        try:
            draft = load_draft(root, draft_id)
        except FileNotFoundError as exc:
            raise ToolError(str(exc)) from exc
        except (MessagingError, ValueError, FileNotFoundError) as exc:
            raise ToolError(str(exc)) from exc
        return {
            "status": "ok",
            "draft": draft_preview(draft),
            "sent": False,
            "_audit": {"result_summary": f"Messaging draft preview shown for {draft_id}; no send executed."},
        }

    def draft_create(
        channel: str,
        to: str,
        body: str,
        draft_id: str = "",
        recipient_display: str = "",
        source_context: dict[str, Any] | None = None,
        risk_level: str = "",
    ) -> dict[str, Any]:
        try:
            parsed_risk = RiskLevel(risk_level) if risk_level else None
            draft, path, invalidated = create_message_draft(
                str(root),
                channel=channel,
                recipient=to,
                body=body,
                draft_id=draft_id,
                recipient_display=recipient_display,
                source_context=source_context,
                risk_level=parsed_risk,
                action_center=action_center,
            )
        except (MessagingError, ValueError, FileNotFoundError) as exc:
            raise ToolError(str(exc)) from exc
        return {
            "status": "ok",
            "draft_id": draft.draft_id,
            "draft": draft_preview(draft),
            "path": path,
            "invalidated_action_ids": invalidated,
            "sent": False,
            "stored_in_memory": False,
            "_audit": {
                "files_written": [path],
                "result_summary": (
                    f"Messaging draft {draft.draft_id} stored locally; {len(invalidated)} send action(s) invalidated; no send executed."
                ),
            },
        }

    def draft_validate(draft_id: str) -> dict[str, Any]:
        try:
            draft = load_draft(root, draft_id)
            validate_draft(draft)
        except FileNotFoundError as exc:
            raise ToolError(str(exc)) from exc
        except (MessagingError, ValueError, FileNotFoundError) as exc:
            raise ToolError(str(exc)) from exc
        return {
            "status": "ok",
            "draft_id": draft.draft_id,
            "valid": True,
            "channel": draft.channel.value,
            "risk_level": draft.risk_level.value,
            "trust_level": draft.trust_level.value,
            "sent": False,
            "_audit": {"result_summary": f"Messaging draft validated for {draft_id}; no send executed."},
        }

    def action_create_send(
        draft_id: str,
        source_workflow: str = "messaging.create-send-action",
        user_requested: bool = True,
    ) -> dict[str, Any]:
        if action_center is None:
            raise ToolError("Action Center is required to create message send actions")
        try:
            action = create_send_action_from_draft(
                str(root),
                action_center,
                draft_id=draft_id,
                source_workflow=source_workflow,
                user_requested=user_requested,
            )
        except (MessagingError, ValueError, FileNotFoundError) as exc:
            raise ToolError(str(exc)) from exc
        return {
            "status": "ok",
            "action": action.to_dict(),
            "send_executed": False,
            "execution_supported": bool(action.sanitized_args.get("execution_supported", False)),
            "next_steps": [
                f"Review with actions show {action.action_id}.",
                f"Approve only if the exact preview is correct: actions approve {action.action_id}.",
                (
                    "For macOS Messages, execution is still disabled until config, allowlist, live probe, and `messages send --from-action` all pass."
                    if action.action_type == "messages.macos.send_approved"
                    else "No message send adapter exists for this channel in v1, so approval cannot silently send."
                ),
            ],
            "_audit": {"result_summary": f"Messaging send action {action.action_id} queued; no send executed."},
        }

    def inbox_import_manual(from_file: str) -> dict[str, Any]:
        return manual_inbox.import_from_file(from_file)

    def inbox_list(include_mock: bool = True, limit: int = 25) -> dict[str, Any]:
        return manual_inbox.list(
            include_mock=include_mock,
            limit=limit,
            mock_messages=mock_inbox.list_messages(),
        )

    def inbox_show(message_id: str) -> dict[str, Any]:
        return manual_inbox.show(message_id, mock_messages=mock_inbox.list_messages())

    def inbox_draft_reply(message_id: str) -> dict[str, Any]:
        return manual_inbox.draft_reply(message_id, mock_messages=mock_inbox.list_messages())

    tools = {
        "messaging.channels": channels,
        "messaging.draft_show": draft_show,
        "messaging.draft.preview": draft_show,
        "messaging.draft.create": draft_create,
        "messaging.draft_validate": draft_validate,
        "messaging.action.create_send": action_create_send,
        "messages.inbox.import_manual": inbox_import_manual,
        "messages.inbox.list": inbox_list,
        "messages.inbox.show": inbox_show,
        "messages.inbox.draft_reply": inbox_draft_reply,
    }
    tools.update(make_ios_compose_tools(root, action_center=action_center))
    tools.update(make_macos_probe_tools(root))
    tools.update(make_macos_send_tools(root, action_center=action_center))
    tools.update(make_apple_business_tools(root, action_center=action_center))
    return tools
