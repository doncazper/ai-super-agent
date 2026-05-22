from __future__ import annotations

from agent.core.tool_broker import ToolBroker
from agent.workflows.base import WorkflowReport, WorkflowRunner, WorkflowStep


def multilingual_web_research(
    broker: ToolBroker,
    query: str,
    language: str,
    max_results: int = 5,
) -> WorkflowReport:
    return WorkflowRunner(broker).run(
        "multilingual_web_research",
        [
            WorkflowStep(
                "web.search",
                {"query": query, "language": language, "max_results": max_results},
            )
        ],
    )
