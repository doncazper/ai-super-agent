from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.leads.inbox import LeadInbox, MockLeadProvider
from agent.safety.actions import ActionCenter
from agent.tools.errors import ToolError


LEAD_SCHEMAS: dict[str, dict[str, Any]] = {
    "lead.inbox.list": {
        "type": "function",
        "function": {
            "name": "lead.inbox.list",
            "description": "List synthetic/mock lead metadata only; does not read real providers or export full messages.",
            "parameters": {
                "type": "object",
                "properties": {"max_results": {"type": "integer"}},
                "additionalProperties": False,
            },
        },
    },
    "lead.inbox.read_selected": {
        "type": "function",
        "function": {
            "name": "lead.inbox.read_selected",
            "description": "Read one selected lead record; future personal/customer providers require approval and remain disabled by default.",
            "parameters": {
                "type": "object",
                "properties": {"lead_id": {"type": "string"}},
                "required": ["lead_id"],
                "additionalProperties": False,
            },
        },
    },
    "lead.classify": {
        "type": "function",
        "function": {
            "name": "lead.classify",
            "description": "Classify one local/mock lead from metadata and preview text without creating actions.",
            "parameters": {
                "type": "object",
                "properties": {"lead_id": {"type": "string"}},
                "required": ["lead_id"],
                "additionalProperties": False,
            },
        },
    },
    "lead.summarize": {
        "type": "function",
        "function": {
            "name": "lead.summarize",
            "description": "Summarize one local/mock lead preview as untrusted data.",
            "parameters": {
                "type": "object",
                "properties": {"lead_id": {"type": "string"}},
                "required": ["lead_id"],
                "additionalProperties": False,
            },
        },
    },
    "lead.draft_response": {
        "type": "function",
        "function": {
            "name": "lead.draft_response",
            "description": "Create a local MessageDraft for one mock/selected lead; does not send or create a send action.",
            "parameters": {
                "type": "object",
                "properties": {"lead_id": {"type": "string"}},
                "required": ["lead_id"],
                "additionalProperties": False,
            },
        },
    },
    "lead.create_follow_up_task": {
        "type": "function",
        "function": {
            "name": "lead.create_follow_up_task",
            "description": "Create a pending Action Center task action for one lead; does not create a real task.",
            "parameters": {
                "type": "object",
                "properties": {"lead_id": {"type": "string"}},
                "required": ["lead_id"],
                "additionalProperties": False,
            },
        },
    },
    "lead.suggest_meeting_times": {
        "type": "function",
        "function": {
            "name": "lead.suggest_meeting_times",
            "description": "Return safe setup guidance for future lead scheduling; does not read calendars.",
            "parameters": {
                "type": "object",
                "properties": {"lead_id": {"type": "string"}},
                "required": ["lead_id"],
            "additionalProperties": False,
            },
        },
    },
    "lead.create_send_action": {
        "type": "function",
        "function": {
            "name": "lead.create_send_action",
            "description": "Create a CRITICAL Action Center send proposal from a lead response draft; does not send.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lead_id": {"type": "string"},
                    "draft_id": {"type": "string"},
                    "allow_channel_override": {"type": "boolean"},
                },
                "required": ["lead_id", "draft_id"],
                "additionalProperties": False,
            },
        },
    },
    "lead.handoff": {
        "type": "function",
        "function": {
            "name": "lead.handoff",
            "description": "Create save/copy Action Center handoff items for a lead response draft; does not send.",
            "parameters": {
                "type": "object",
                "properties": {
                    "draft_id": {"type": "string"},
                    "save_path": {"type": "string"},
                },
                "required": ["draft_id"],
                "additionalProperties": False,
            },
        },
    },
    "lead.mark_responded": {
        "type": "function",
        "function": {
            "name": "lead.mark_responded",
            "description": "Mark one local lead status as responded after a verified send or explicit user handoff.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lead_id": {"type": "string"},
                    "action_id": {"type": "string"},
                    "draft_id": {"type": "string"},
                    "channel": {"type": "string"},
                    "note": {"type": "string"},
                },
                "required": ["lead_id"],
                "additionalProperties": False,
            },
        },
    },
}


def make_lead_tools(
    project_root: str | Path,
    *,
    action_center: ActionCenter | None = None,
    provider: MockLeadProvider | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()

    def _inbox() -> LeadInbox:
        return LeadInbox(root, provider=provider, action_center=action_center)

    def list_leads(max_results: int = 20) -> dict[str, Any]:
        payload = _inbox().list(max_results=max_results)
        payload["_audit"] = {"result_summary": "Lead inbox metadata listed from mock provider; no real provider read."}
        return payload

    def read_selected(lead_id: str) -> dict[str, Any]:
        payload = _inbox().read_selected(lead_id)
        payload["_audit"] = {"result_summary": f"Selected lead {lead_id} read; no memory write."}
        return payload

    def classify(lead_id: str) -> dict[str, Any]:
        payload = _inbox().classify(lead_id)
        payload["_audit"] = {"result_summary": f"Lead {lead_id} classified; no actions executed."}
        return payload

    def summarize(lead_id: str) -> dict[str, Any]:
        payload = _inbox().summarize(lead_id)
        payload["_audit"] = {"result_summary": f"Lead {lead_id} summarized from untrusted preview; no memory write."}
        return payload

    def draft_response(lead_id: str) -> dict[str, Any]:
        payload = _inbox().draft_response(lead_id)
        payload["_audit"] = {
            "files_written": [payload["draft_path"]],
            "result_summary": f"Lead response workflow drafted response for {lead_id}; no send action created.",
        }
        return payload

    def create_follow_up_task(lead_id: str) -> dict[str, Any]:
        if action_center is None:
            raise ToolError("Action Center is required to create lead follow-up task actions")
        payload = _inbox().suggest_followup(lead_id)
        payload["_audit"] = {"result_summary": f"Lead follow-up suggestion queued pending task action for {lead_id}; no task created."}
        return payload

    def suggest_meeting_times(lead_id: str) -> dict[str, Any]:
        payload = _inbox().suggest_meeting(lead_id)
        payload["_audit"] = {"result_summary": f"Lead meeting suggestion created for {lead_id}; no calendar read or event created."}
        return payload

    def create_send_action(
        lead_id: str,
        draft_id: str,
        allow_channel_override: bool = False,
    ) -> dict[str, Any]:
        if action_center is None:
            raise ToolError("Action Center is required to create lead response send actions")
        payload = _inbox().create_send_action(
            lead_id,
            draft_id,
            allow_channel_override=allow_channel_override,
        )
        payload["_audit"] = {
            "files_written": [payload["lead_status_path"]],
            "result_summary": f"Lead response send action {payload['action_id']} queued for {lead_id}; no send executed.",
        }
        return payload

    def handoff(draft_id: str, save_path: str = "") -> dict[str, Any]:
        if action_center is None:
            raise ToolError("Action Center is required to create lead response handoff actions")
        payload = _inbox().handoff(draft_id, save_path=save_path)
        payload["_audit"] = {
            "result_summary": f"Lead response handoff actions created for {draft_id}; no send executed.",
        }
        return payload

    def mark_responded(
        lead_id: str,
        action_id: str = "",
        draft_id: str = "",
        channel: str = "",
        note: str = "",
    ) -> dict[str, Any]:
        payload = _inbox().mark_responded(
            lead_id,
            action_id=action_id,
            draft_id=draft_id,
            channel=channel,
            note=note,
        )
        payload["_audit"] = {
            "files_written": [payload["path"]],
            "result_summary": f"Lead {lead_id} marked responded by explicit user command.",
        }
        return payload

    return {
        "lead.inbox.list": list_leads,
        "lead.inbox.read_selected": read_selected,
        "lead.classify": classify,
        "lead.summarize": summarize,
        "lead.draft_response": draft_response,
        "lead.create_follow_up_task": create_follow_up_task,
        "lead.suggest_meeting_times": suggest_meeting_times,
        "lead.create_send_action": create_send_action,
        "lead.handoff": handoff,
        "lead.mark_responded": mark_responded,
    }
