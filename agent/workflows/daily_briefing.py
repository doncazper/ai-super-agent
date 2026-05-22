from __future__ import annotations

from agent.core.tool_broker import ToolBroker
from agent.workflows.base import WorkflowReport, WorkflowRunner, WorkflowStep


def daily_briefing(broker: ToolBroker, timezone: str = "UTC") -> WorkflowReport:
    return WorkflowRunner(broker).run(
        "daily_briefing",
        [WorkflowStep("time.get_current_time", {"timezone": timezone})],
    )
