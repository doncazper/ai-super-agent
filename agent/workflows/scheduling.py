from __future__ import annotations

from agent.core.tool_broker import ToolBroker
from agent.workflows.base import WorkflowReport, WorkflowRunner, WorkflowStep


def calendar_availability(
    broker: ToolBroker,
    start_date: str,
    end_date: str,
    selected_scope_token: str,
) -> WorkflowReport:
    return WorkflowRunner(broker).run(
        "calendar_availability",
        [
            WorkflowStep(
                "calendar.find_availability",
                {
                    "start_date": start_date,
                    "end_date": end_date,
                    "selected_scope_token": selected_scope_token,
                },
            )
        ],
    )
