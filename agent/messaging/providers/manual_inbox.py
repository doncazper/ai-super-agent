from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.messaging.inbound import (
    draft_reply_to_incoming_message,
    import_manual_message,
    list_incoming_messages,
    show_incoming_message,
)


class ManualInboxProvider:
    """Workspace-only manual inbox provider. It never reads Messages.app storage."""

    provider_id = "manual"

    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root).resolve()

    def import_from_file(self, from_file: str) -> dict[str, Any]:
        message, store_path = import_manual_message(self.project_root, from_file)
        return {
            "status": "ok",
            "message": message.to_dict(include_body=True),
            "message_id": message.message_id,
            "stored_path": str(store_path),
            "trust_level": "UNTRUSTED_MESSAGE",
            "stored_in_memory": False,
            "private_messages_database_accessed": False,
            "full_disk_access_required": False,
            "background_watcher": False,
            "_audit": {
                "files_read": [message.source_ref],
                "files_written": [str(store_path)],
                "result_summary": f"Manual incoming message {message.message_id} imported from workspace; no Messages database read.",
            },
        }

    def list(self, *, include_mock: bool = True, limit: int = 25, mock_messages: list[Any] | None = None) -> dict[str, Any]:
        payload = list_incoming_messages(
            self.project_root,
            include_mock=include_mock,
            limit=limit,
            mock_messages=mock_messages,
        )
        payload["_audit"] = {"result_summary": "Incoming message inbox listed; no private Messages database read."}
        return payload

    def show(self, message_id: str, *, mock_messages: list[Any] | None = None) -> dict[str, Any]:
        payload = show_incoming_message(self.project_root, message_id, mock_messages=mock_messages)
        payload["_audit"] = {"result_summary": f"Incoming message {message_id} shown; no private Messages database read."}
        return payload

    def draft_reply(self, message_id: str, *, mock_messages: list[Any] | None = None) -> dict[str, Any]:
        payload = draft_reply_to_incoming_message(self.project_root, message_id, mock_messages=mock_messages)
        payload["_audit"] = {
            "files_written": [str(payload["draft_path"])],
            "result_summary": f"Draft reply created for incoming message {message_id}; no send executed.",
        }
        return payload
