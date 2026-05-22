from __future__ import annotations

import sys
import json
from dataclasses import dataclass
from typing import Callable

from agent.safety.approvals import ApprovalStore
from agent.tools.registry import ToolRegistry
from agent.ui.approvals_ui import format_approval_preview
from agent.ui.config_viewer import config_as_json
from agent.ui.doctor import doctor_exit_code, format_doctor, run_doctor


@dataclass
class InteractiveState:
    no_tools: bool = False
    debug: bool = False


RespondFn = Callable[[str, InteractiveState], str]
InputFn = Callable[[str], str]
OutputFn = Callable[[str], None]


HELP_TEXT = """Commands:
  :help             Show this help.
  :doctor           Run local runtime diagnostics without sending a model prompt.
  :tools            List registered tool schemas.
  :config           Show runtime and capability configuration.
  :no-tools on      Disable tool schemas for chat turns.
  :no-tools off     Allow router-selected tools for chat turns.
  :debug on         Print debug details for chat turns.
  :debug off        Hide debug details for chat turns.
  :approvals        List queued approval requests.
  :approvals <id>   Show one queued approval request.
  :exit             Quit interactive mode."""


def run_interactive(
    respond: RespondFn,
    *,
    registry: ToolRegistry,
    state: InteractiveState | None = None,
    approval_store: ApprovalStore | None = None,
    input_fn: InputFn = input,
    output_fn: OutputFn = print,
    error_fn: OutputFn | None = None,
) -> int:
    current = state or InteractiveState()
    write_error = error_fn or (lambda message: print(message, file=sys.stderr))
    output_fn("Interactive mode. Type :help for commands, :exit to quit.")
    while True:
        try:
            line = input_fn("agent> ")
        except EOFError:
            output_fn("")
            return 0
        except KeyboardInterrupt:
            output_fn("")
            return 130

        text = line.strip()
        if not text:
            continue
        lowered = text.lower()
        if lowered in {":exit", ":quit", "exit", "quit"}:
            output_fn("Goodbye.")
            return 0
        if lowered.startswith(":"):
            _handle_command(
                lowered,
                registry=registry,
                state=current,
                approval_store=approval_store,
                output_fn=output_fn,
                error_fn=write_error,
            )
            continue
        try:
            answer = respond(text, current)
        except Exception as exc:  # pragma: no cover - concrete failures are tested at the caller boundary.
            write_error(str(exc))
            continue
        if answer:
            output_fn(answer)


def _handle_command(
    command: str,
    *,
    registry: ToolRegistry,
    state: InteractiveState,
    approval_store: ApprovalStore | None,
    output_fn: OutputFn,
    error_fn: OutputFn,
) -> None:
    if command == ":help":
        output_fn(HELP_TEXT)
        return
    if command == ":doctor":
        checks = run_doctor()
        output_fn(format_doctor(checks))
        if doctor_exit_code(checks) != 0:
            error_fn("Doctor found one or more blocking issues.")
        return
    if command == ":tools":
        for schema in registry.schemas():
            output_fn(schema["function"]["name"])
        return
    if command == ":config":
        output_fn(config_as_json())
        return
    if command in {":no-tools on", ":no-tools true"}:
        state.no_tools = True
        output_fn("No-tools mode is on.")
        return
    if command in {":no-tools off", ":no-tools false"}:
        state.no_tools = False
        output_fn("No-tools mode is off.")
        return
    if command in {":debug on", ":debug true"}:
        state.debug = True
        output_fn("Debug output is on.")
        return
    if command in {":debug off", ":debug false"}:
        state.debug = False
        output_fn("Debug output is off.")
        return
    if command == ":approvals":
        if approval_store is None:
            error_fn("Approval queue is not available in this session.")
            return
        output_fn(_format_approval_list(approval_store))
        return
    if command.startswith(":approvals "):
        if approval_store is None:
            error_fn("Approval queue is not available in this session.")
            return
        request_id = command.split(maxsplit=1)[1].strip()
        request = approval_store.get(request_id)
        if request is None:
            error_fn("Approval request not found.")
            return
        output_fn(format_approval_preview(request))
        return
    error_fn("Unknown command. Type :help for interactive commands.")


def _format_approval_list(approval_store: ApprovalStore) -> str:
    payload = [
        {
            "request_id": request.request_id,
            "timestamp": request.timestamp,
            "tool_name": request.tool_name,
            "capability": request.capability,
            "risk_level": request.risk_level.value,
            "status": request.status.value,
            "expires_at": request.expires_at,
        }
        for request in approval_store.list()
    ]
    return json.dumps({"approvals": payload}, indent=2, sort_keys=True)
