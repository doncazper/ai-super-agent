from __future__ import annotations

from agent.core.tool_broker import ToolBroker
from agent.workflows.base import WorkflowReport, WorkflowRunner, WorkflowStep


def text_draft_reply(
    broker: ToolBroker,
    thread_text: str,
    user_instruction: str = "",
) -> WorkflowReport:
    return WorkflowRunner(broker).run(
        "text_draft_reply",
        [
            WorkflowStep(
                "messages.draft_reply",
                {"thread_text": thread_text, "user_instruction": user_instruction},
            )
        ],
    )
