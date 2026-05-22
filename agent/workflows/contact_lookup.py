from __future__ import annotations

from agent.core.tool_broker import ToolBroker
from agent.workflows.base import WorkflowReport, WorkflowRunner, WorkflowStep


def contact_lookup(broker: ToolBroker, query: str) -> WorkflowReport:
    return WorkflowRunner(broker).run(
        "contact_lookup",
        [WorkflowStep("contacts.search", {"query": query})],
    )
