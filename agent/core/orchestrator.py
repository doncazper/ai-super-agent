from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from agent.core.lmstudio_client import LMStudioClient
from agent.core.messages import MINIMAL_SYSTEM_PROMPT, clean_assistant_message, initial_messages
from agent.core.router import RouteDecision, Router
from agent.core.tool_broker import ToolBroker
from agent.tools.registry import ToolRegistry


@dataclass
class OrchestratorResult:
    content: str
    messages: list[dict[str, Any]]
    tool_results: list[dict[str, Any]] = field(default_factory=list)


class Orchestrator:
    def __init__(
        self,
        client: LMStudioClient,
        registry: ToolRegistry,
        broker: ToolBroker,
        *,
        max_tool_iterations: int = 3,
        debug: bool = False,
        router: Router | None = None,
    ) -> None:
        self.client = client
        self.registry = registry
        self.broker = broker
        self.max_tool_iterations = max_tool_iterations
        self.debug = debug
        self.router = router or Router()

    def run(
        self,
        user_message: str,
        *,
        no_tools: bool = False,
        route: RouteDecision | None = None,
    ) -> OrchestratorResult:
        messages = initial_messages(user_message)
        route_decision = route or self.router.route(user_message, force_no_tools=no_tools)
        tools = self.registry.schemas(route_decision.tool_names) if route_decision.use_tools else None

        response = self.client.chat(messages, tools=tools)
        assistant_message = self._assistant_message(response)
        messages.append(assistant_message)

        tool_results: list[dict[str, Any]] = []
        iterations = 0
        while assistant_message.get("tool_calls") and not no_tools:
            if iterations >= self.max_tool_iterations:
                return OrchestratorResult(
                    content="Tool iteration limit reached before final model response.",
                    messages=messages,
                    tool_results=tool_results,
                )
            iterations += 1
            for tool_call in assistant_message["tool_calls"]:
                execution = self.broker.execute(tool_call)
                tool_message = {
                    "role": "tool",
                    "tool_call_id": execution.tool_call_id,
                    "name": execution.tool_name,
                    "content": execution.content,
                }
                messages.append(tool_message)
                tool_results.append(tool_message)

            response = self.client.chat(messages, tools=tools)
            assistant_message = self._assistant_message(response)
            messages.append(assistant_message)

        return OrchestratorResult(
            content=str(assistant_message.get("content") or ""),
            messages=messages,
            tool_results=tool_results,
        )

    def _assistant_message(self, response: dict[str, Any]) -> dict[str, Any]:
        message = response["choices"][0]["message"]
        return clean_assistant_message(message)


def new_session_id() -> str:
    return str(uuid4())


def format_debug_payload(payload: Any) -> str:
    from agent.safety.redaction import SecretRedactor

    return json.dumps(SecretRedactor().redact(payload), indent=2, sort_keys=True)
