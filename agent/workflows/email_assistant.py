from __future__ import annotations

from agent.core.tool_broker import ToolBroker
from agent.workflows.base import WorkflowReport, WorkflowRunner, WorkflowStep


def email_summary(broker: ToolBroker, selected_scope_token: str) -> WorkflowReport:
    return WorkflowRunner(broker).run(
        "email_summary",
        [WorkflowStep("email.read_selected_thread", {"selected_scope_token": selected_scope_token})],
    )


def email_draft_reply(
    broker: ToolBroker,
    thread_text: str,
    user_instruction: str = "",
) -> WorkflowReport:
    return WorkflowRunner(broker).run(
        "email_draft_reply",
        [
            WorkflowStep(
                "email.draft_reply",
                {"thread_text": thread_text, "user_instruction": user_instruction},
            )
        ],
    )
