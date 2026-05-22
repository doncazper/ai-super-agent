from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from agent.core.tool_broker import ToolBroker, ToolExecutionResult


@dataclass
class WorkflowStep:
    tool_name: str
    arguments: dict[str, Any]


@dataclass
class WorkflowReport:
    name: str
    steps: list[dict[str, Any]] = field(default_factory=list)

    @property
    def allowed(self) -> bool:
        return all(step["allowed"] for step in self.steps)

    def add_result(self, result: ToolExecutionResult) -> None:
        try:
            content = json.loads(result.content)
        except json.JSONDecodeError:
            content = {"raw": result.content}
        self.steps.append(
            {
                "tool_name": result.tool_name,
                "tool_call_id": result.tool_call_id,
                "allowed": result.allowed,
                "content": content,
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "allowed": self.allowed, "steps": self.steps}


class WorkflowRunner:
    def __init__(self, broker: ToolBroker) -> None:
        self.broker = broker

    def run(self, name: str, steps: list[WorkflowStep]) -> WorkflowReport:
        report = WorkflowReport(name=name)
        for index, step in enumerate(steps):
            result = self.broker.execute(
                {
                    "id": f"{name}_{index}",
                    "type": "function",
                    "function": {
                        "name": step.tool_name,
                        "arguments": json.dumps(step.arguments),
                    },
                }
            )
            report.add_result(result)
            if not result.allowed:
                break
        return report
