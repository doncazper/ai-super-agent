#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
import sys

from agent.config.runtime import RuntimeConfig, RuntimeConfigError
from agent.core.lmstudio_client import LMStudioClient, LMStudioConfig, LMStudioError
from agent.core.orchestrator import Orchestrator, OrchestratorResult, new_session_id
from agent.core.tool_broker import ToolBroker
from agent.config.loader import load_capabilities_config
from agent.safety.audit import AuditLogError, AuditLogger
from agent.safety.policy import PolicyEngine
from agent.safety.validation import validate_startup_policy
from agent.tools.registry import default_registry
from agent.ui.cli_commands import dispatch_cli
from agent.ui.interactive import InteractiveState, run_interactive


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safety-first local Mac AI agent.")
    parser.add_argument("message", nargs="*", help="User message to send to the local model.")
    parser.add_argument("--interactive", action="store_true", help="Start an interactive local chat shell.")
    parser.add_argument("--no-tools", action="store_true", help="Do not attach tool schemas.")
    parser.add_argument("--force-tools", action="store_true", help="Attach available safe tool schemas.")
    parser.add_argument("--debug", action="store_true", help="Print debug details to stderr.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    raw_argv = argv or sys.argv[1:]
    cli_result = dispatch_cli(raw_argv)
    if cli_result is not None:
        return cli_result
    args = parse_args(raw_argv)
    try:
        runtime_config = RuntimeConfig.from_env()
        config = LMStudioConfig.from_runtime(runtime_config)
        validate_startup_policy(runtime_config.capabilities_path)
        policy_engine = PolicyEngine.from_config(load_capabilities_config(runtime_config.capabilities_path))
    except RuntimeConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    try:
        registry = default_registry()
    except RuntimeConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    audit_logger = AuditLogger(runtime_config.audit_log_path)
    session_id = new_session_id()
    broker = ToolBroker(
        registry,
        policy_engine,
        audit_logger,
        session_id=session_id,
        model=config.model,
        route="cli",
    )
    debug_enabled = args.debug or runtime_config.debug

    if args.message and args.message[0] == "web":
        return _run_web_search_command(args.message[1:], broker, debug=debug_enabled)

    try:
        client = LMStudioClient(config)
    except LMStudioError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    orchestrator = Orchestrator(client, registry, broker, debug=debug_enabled)

    if debug_enabled:
        tool_state = "disabled" if args.no_tools else runtime_config.tool_mode
        print(
            "[debug] "
            f"session_id={session_id} model={config.model} base_url={config.base_url} tools={tool_state} "
            f"temperature={config.temperature} top_p={config.top_p} max_tokens={config.max_tokens}",
            file=sys.stderr,
        )

    force_time = args.force_tools or runtime_config.tool_mode == "force-time"
    no_tools = args.no_tools or runtime_config.tool_mode == "no-tools"

    def respond(user_message: str, state: InteractiveState) -> str:
        result = _run_turn(
            orchestrator,
            user_message,
            no_tools=state.no_tools,
            force_time=force_time,
        )
        if state.debug:
            _print_debug_events(result)
        return result.content

    if args.interactive:
        return run_interactive(
            respond,
            registry=registry,
            state=InteractiveState(no_tools=no_tools, debug=debug_enabled),
        )

    if not args.message:
        print("usage: smart_agent.py [--interactive] [--no-tools] [--debug] <message>", file=sys.stderr)
        return 2

    message = " ".join(args.message)
    try:
        result = _run_turn(orchestrator, message, no_tools=no_tools, force_time=force_time)
    except LMStudioError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except AuditLogError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if debug_enabled:
        _print_debug_events(result)
    print(result.content)
    return 0


def _run_turn(
    orchestrator: Orchestrator,
    message: str,
    *,
    no_tools: bool,
    force_time: bool,
) -> OrchestratorResult:
    route = None
    if force_time and not no_tools:
        from agent.core.router import RouteDecision
        from agent.safety.policy import RiskLevel

        route = RouteDecision(
            name="cli.force_tools",
            use_tools=True,
            tool_names={"time.get_current_time"},
            risk_level=RiskLevel.SAFE,
        )
    return orchestrator.run(message, no_tools=no_tools, route=route)


def _run_web_search_command(argv: list[str], broker: ToolBroker, *, debug: bool = False) -> int:
    query = " ".join(argv).strip()
    if not query:
        print('usage: smart_agent.py web "query"', file=sys.stderr)
        return 2
    tool_call = {
        "id": "cli_web_search",
        "type": "function",
        "function": {
            "name": "web.search",
            "arguments": json.dumps({"query": query}),
        },
    }
    try:
        result = broker.execute(tool_call)
    except AuditLogError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if debug and result.debug:
        from agent.core.orchestrator import format_debug_payload

        print("[debug] " + format_debug_payload({"event": "tool_broker", **result.debug}), file=sys.stderr)
    print(json.dumps(json.loads(result.content), indent=2, sort_keys=True))
    return 0 if result.allowed else 2


def _print_debug_events(result: OrchestratorResult) -> None:
    from agent.core.orchestrator import format_debug_payload

    for event in result.debug_events:
        print("[debug] " + format_debug_payload(event), file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
