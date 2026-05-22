#!/usr/bin/env python
from __future__ import annotations

import argparse
import os
import sys

from agent.core.lmstudio_client import LMStudioClient, LMStudioConfig
from agent.core.orchestrator import Orchestrator, new_session_id
from agent.core.tool_broker import ToolBroker
from agent.config.loader import load_capabilities_config
from agent.safety.audit import AuditLogger
from agent.safety.policy import PolicyEngine
from agent.safety.validation import validate_startup_policy
from agent.tools.registry import default_registry
from agent.ui.cli_commands import dispatch_cli


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safety-first local Mac AI agent.")
    parser.add_argument("message", nargs="+", help="User message to send to the local model.")
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
    config = LMStudioConfig.from_env()
    validate_startup_policy()
    policy_engine = PolicyEngine.from_config(load_capabilities_config())
    registry = default_registry()
    audit_logger = AuditLogger(os.getenv("AGENT_AUDIT_LOG", "logs/audit.jsonl"))
    session_id = new_session_id()
    client = LMStudioClient(config)
    broker = ToolBroker(
        registry,
        policy_engine,
        audit_logger,
        session_id=session_id,
        model=config.model,
        route="cli",
    )
    orchestrator = Orchestrator(client, registry, broker, debug=args.debug)

    if args.debug:
        tool_state = "disabled" if args.no_tools else "enabled"
        print(f"[debug] session_id={session_id} model={config.model} tools={tool_state}", file=sys.stderr)

    message = " ".join(args.message)
    route = None
    if args.force_tools and not args.no_tools:
        from agent.core.router import RouteDecision
        from agent.safety.policy import RiskLevel

        route = RouteDecision(
            name="cli.force_tools",
            use_tools=True,
            tool_names={"time.get_current_time"},
            risk_level=RiskLevel.SAFE,
        )

    result = orchestrator.run(message, no_tools=args.no_tools, route=route)
    print(result.content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
