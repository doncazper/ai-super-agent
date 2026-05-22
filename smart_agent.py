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
from agent.safety.approvals import ApprovalManager, ApprovalStore
from agent.safety.policy import PolicyEngine
from agent.safety.validation import validate_startup_policy
from agent.tools.registry import default_registry
from agent.tools.weather.formatter import format_weather_answer
from agent.ui.approvals_ui import ConsoleApprovalPrompt
from agent.ui.cli_commands import dispatch_cli
from agent.ui.interactive import InteractiveState, run_interactive
from agent.workflows.research import source_grounded_research


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safety-first local Mac AI agent.")
    parser.add_argument("message", nargs=argparse.REMAINDER, help="User message to send to the local model.")
    parser.add_argument("--interactive", action="store_true", help="Start an interactive local chat shell.")
    parser.add_argument("--no-tools", action="store_true", help="Do not attach tool schemas.")
    parser.add_argument("--force-tools", action="store_true", help="Attach available safe tool schemas.")
    parser.add_argument("--debug", action="store_true", help="Print debug details to stderr.")
    parser.add_argument("--dry-run", action="store_true", help="Evaluate policy and previews without executing tools.")
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
    approval_store = ApprovalStore()
    approval_interactive = args.interactive or (
        bool(args.message) and args.message[0] in {"calendar", "contacts", "email", "messages"} and sys.stdin.isatty()
    )
    approval_prompt = ConsoleApprovalPrompt(interactive=approval_interactive)
    broker = ToolBroker(
        registry,
        policy_engine,
        audit_logger,
        session_id=session_id,
        model=config.model,
        route="cli",
        approval_manager=ApprovalManager(
            store=approval_store,
            decision_provider=approval_prompt.prompt if approval_interactive else None,
        ),
        dry_run=args.dry_run,
    )
    debug_enabled = args.debug or runtime_config.debug

    if args.message and args.message[0] == "web":
        return _run_web_search_command(args.message[1:], broker, debug=debug_enabled)
    if args.message and args.message[0] == "research":
        return _run_research_command(args.message[1:], broker)
    if args.message and args.message[0] == "weather":
        return _run_weather_command(args.message[1:], broker, debug=debug_enabled)
    if args.message and args.message[0] == "calendar":
        return _run_calendar_command(args.message[1:], broker, debug=debug_enabled)
    if args.message and args.message[0] == "contacts":
        return _run_contacts_command(args.message[1:], broker, debug=debug_enabled)
    if args.message and args.message[0] == "email":
        return _run_email_command(args.message[1:], broker, debug=debug_enabled)
    if args.message and args.message[0] == "messages":
        return _run_messages_command(args.message[1:], broker, debug=debug_enabled)

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
            f"temperature={config.temperature} top_p={config.top_p} max_tokens={config.max_tokens} "
            f"dry_run={args.dry_run}",
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
            approval_store=approval_store,
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


def _run_research_command(argv: list[str], broker: ToolBroker) -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py research", description="Run source-grounded web research.")
    parser.add_argument("query", nargs="*", help="Research query.")
    parser.add_argument("--max-results", type=int, default=3, help="Number of search results to use, 1-5.")
    parser.add_argument("--no-fetch", action="store_true", help="Use search snippets only; do not fetch result pages.")
    parser.add_argument("--locale", default=None, help="Optional search locale, such as en-US or es.")
    parser.add_argument("--summary-language", default="en", help="Summary language label; defaults to en.")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    query = " ".join(parsed.query).strip()
    if not query:
        print('usage: smart_agent.py research "query"', file=sys.stderr)
        return 2
    try:
        report = source_grounded_research(
            broker,
            query,
            max_results=parsed.max_results,
            fetch_pages=not parsed.no_fetch,
            locale=parsed.locale,
            summary_language=parsed.summary_language,
        )
    except AuditLogError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("status") == "ok" else 2


def _run_weather_command(argv: list[str], broker: ToolBroker, *, debug: bool = False) -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py weather", description="Weather lookups for user-provided locations.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="Check weather provider configuration without fetching weather data.")
    cache_parser = subparsers.add_parser("cache", help="Manage the local TTL weather cache.")
    cache_subparsers = cache_parser.add_subparsers(dest="cache_command", required=True)
    cache_subparsers.add_parser("clear", help="Clear cached weather responses.")

    smoke_parser = subparsers.add_parser("smoke", help="Run current and forecast checks for a user-provided location.")
    smoke_parser.add_argument("location", nargs="+", help="City, ZIP/postal code, or other user-provided location.")
    smoke_parser.add_argument("--days", type=int, default=3)
    smoke_parser.add_argument("--units", choices=["metric", "imperial"], default=None)
    smoke_parser.add_argument("--locale", default=None)
    smoke_parser.add_argument("--hourly", action="store_true", help="Include hourly forecast slices when supported.")

    current_parser = subparsers.add_parser("current", help="Fetch current weather for a user-provided location.")
    current_parser.add_argument("location", nargs="+", help="City, ZIP/postal code, or other user-provided location.")
    current_parser.add_argument("--units", choices=["metric", "imperial"], default=None)
    current_parser.add_argument("--locale", default=None)
    current_parser.add_argument("--no-cache", action="store_true", help="Bypass the local weather cache for this request.")
    current_parser.add_argument("--json", action="store_true", help="Print the raw structured weather payload.")

    forecast_parser = subparsers.add_parser("forecast", help="Fetch a forecast for a user-provided location.")
    forecast_parser.add_argument("location", nargs="+", help="City, ZIP/postal code, or other user-provided location.")
    forecast_parser.add_argument("--days", type=int, default=None)
    forecast_parser.add_argument("--units", choices=["metric", "imperial"], default=None)
    forecast_parser.add_argument("--locale", default=None)
    forecast_parser.add_argument("--hourly", action="store_true", help="Include hourly forecast slices when supported.")
    forecast_parser.add_argument("--no-cache", action="store_true", help="Bypass the local weather cache for this request.")
    forecast_parser.add_argument("--json", action="store_true", help="Print the raw structured weather payload.")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    if parsed.command == "doctor":
        try:
            result = _execute_weather_tool(broker, "weather.status", {}, debug=debug)
        except AuditLogError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        payload = json.loads(result.content)
        payload["capabilities"] = _weather_capability_status(broker)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if result.allowed else 2

    if parsed.command == "cache":
        try:
            result = _execute_weather_tool(broker, "weather.cache_clear", {}, debug=debug)
        except AuditLogError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(json.dumps(json.loads(result.content), indent=2, sort_keys=True))
        return 0 if result.allowed else 2

    if parsed.command == "smoke":
        location = " ".join(parsed.location)
        base_args: dict[str, object] = {"location": location}
        if parsed.units is not None:
            base_args["units"] = parsed.units
        if parsed.locale is not None:
            base_args["locale"] = parsed.locale
        forecast_args = dict(base_args)
        forecast_args["days"] = parsed.days
        if parsed.hourly:
            forecast_args["include_hourly"] = True
        try:
            status_result = _execute_weather_tool(broker, "weather.status", {}, debug=debug)
            status_payload = json.loads(status_result.content)
            report: dict[str, object] = {
                "status": "ok",
                "provider": status_payload.get("provider"),
                "configured": status_payload.get("configured"),
                "provider_status": status_payload,
                "capabilities": _weather_capability_status(broker),
                "checks": [],
            }
            if not status_payload.get("configured"):
                report["status"] = "error"
                report["error"] = status_payload.get("error") or "weather provider is not configured"
                print(json.dumps(report, indent=2, sort_keys=True))
                return 2
            current_result = _execute_weather_tool(broker, "weather.current", base_args, debug=debug)
            forecast_result = _execute_weather_tool(broker, "weather.forecast", forecast_args, debug=debug)
        except AuditLogError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        current_payload = json.loads(current_result.content)
        forecast_payload = json.loads(forecast_result.content)
        checks = [
            {"name": "weather.current", "allowed": current_result.allowed, "status": current_payload.get("status")},
            {"name": "weather.forecast", "allowed": forecast_result.allowed, "status": forecast_payload.get("status")},
        ]
        ok = all(check["allowed"] and check["status"] == "ok" for check in checks)
        report.update(
            {
                "status": "ok" if ok else "error",
                "checks": checks,
                "current": current_payload,
                "forecast": forecast_payload,
            }
        )
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if ok else 2

    tool_name = "weather.current" if parsed.command == "current" else "weather.forecast"
    arguments: dict[str, object] = {"location": " ".join(parsed.location)}
    if parsed.units is not None:
        arguments["units"] = parsed.units
    if parsed.locale is not None:
        arguments["locale"] = parsed.locale
    if parsed.command == "forecast" and parsed.days is not None:
        arguments["days"] = parsed.days
    if parsed.command == "forecast" and parsed.hourly:
        arguments["include_hourly"] = True
    if getattr(parsed, "no_cache", False):
        arguments["no_cache"] = True
    try:
        result = _execute_weather_tool(broker, tool_name, arguments, debug=debug)
    except AuditLogError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    payload = json.loads(result.content)
    if getattr(parsed, "json", False):
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(format_weather_answer(payload, mode=parsed.command))
    return 0 if result.allowed else 2


def _execute_weather_tool(
    broker: ToolBroker,
    tool_name: str,
    arguments: dict[str, object],
    *,
    debug: bool = False,
):
    tool_call = {
        "id": f"cli_{tool_name.replace('.', '_')}",
        "type": "function",
        "function": {
            "name": tool_name,
            "arguments": json.dumps(arguments),
        },
    }
    result = broker.execute(tool_call)
    if debug and result.debug:
        from agent.core.orchestrator import format_debug_payload

        print("[debug] " + format_debug_payload({"event": "tool_broker", **result.debug}), file=sys.stderr)
    return result


def _weather_capability_status(broker: ToolBroker) -> dict[str, dict[str, object]]:
    statuses: dict[str, dict[str, object]] = {}
    for capability_name in ("weather.status", "weather.current", "weather.forecast"):
        policy = broker.policy_engine.evaluate(capability_name)
        statuses[capability_name] = {
            "decision": policy.decision.value,
            "risk_level": policy.capability.risk_level.value if policy.capability else "FORBIDDEN",
            "reason": policy.reason,
        }
    return statuses


def _run_calendar_command(argv: list[str], broker: ToolBroker, *, debug: bool = False) -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py calendar", description="Read selected calendar ranges.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    read_parser = subparsers.add_parser("read", help="Read compact event summaries for a selected date range.")
    read_parser.add_argument("--start", required=True, help="Start date/datetime, e.g. 2026-05-22.")
    read_parser.add_argument("--end", required=True, help="End date/datetime, e.g. 2026-05-23.")
    read_parser.add_argument("--calendar", action="append", default=[], help="Optional calendar name filter.")

    availability_parser = subparsers.add_parser("availability", help="Find availability without event details.")
    availability_parser.add_argument("--start", required=True, help="Start date/datetime, e.g. 2026-05-22.")
    availability_parser.add_argument("--end", required=True, help="End date/datetime, e.g. 2026-05-23.")
    availability_parser.add_argument("--duration", type=int, default=30, help="Required slot duration in minutes.")
    availability_parser.add_argument("--work-start", default="09:00", help="Working-hours start, HH:MM.")
    availability_parser.add_argument("--work-end", default="17:00", help="Working-hours end, HH:MM.")
    availability_parser.add_argument("--calendar", action="append", default=[], help="Optional calendar name filter.")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    tool_name = "calendar.read_date_range" if parsed.command == "read" else "calendar.find_availability"
    arguments: dict[str, object] = {
        "start": parsed.start,
        "end": parsed.end,
        "calendar_filters": parsed.calendar,
    }
    if parsed.command == "availability":
        arguments.update(
            {
                "duration_minutes": parsed.duration,
                "working_hours_start": parsed.work_start,
                "working_hours_end": parsed.work_end,
            }
        )
    tool_call = {
        "id": f"cli_{tool_name.replace('.', '_')}",
        "type": "function",
        "function": {
            "name": tool_name,
            "arguments": json.dumps(arguments),
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


def _run_contacts_command(argv: list[str], broker: ToolBroker, *, debug: bool = False) -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py contacts", description="Read selected contacts.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    search_parser = subparsers.add_parser("search", help="Search compact contact candidates.")
    search_parser.add_argument("query", nargs="?", help="Search query, at least 2 characters.")
    search_parser.add_argument("--query", dest="query_option", default=None, help="Search query, at least 2 characters.")
    search_parser.add_argument("--max-results", type=int, default=None, help="Max candidates, capped by config.")

    read_parser = subparsers.add_parser("read", help="Read one explicitly selected contact.")
    read_parser.add_argument("contact_id", nargs="?", help="Selected contact id/token returned by contacts search.")
    read_parser.add_argument("--token", default=None, help="Selected scope token returned by contacts search.")
    read_parser.add_argument("--field", action="append", default=[], help="Requested field; may be repeated.")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    if parsed.command == "search":
        tool_name = "contacts.search"
        query = parsed.query_option or parsed.query
        if not query:
            parser.error('contacts search requires a query, e.g. contacts search "Sam"')
        arguments: dict[str, object] = {"query": query}
        if parsed.max_results is not None:
            arguments["max_results"] = parsed.max_results
    else:
        tool_name = "contacts.read_selected"
        token = parsed.token or parsed.contact_id
        if not token:
            parser.error('contacts read requires a selected contact id, e.g. contacts read "<contact_id>"')
        arguments = {"selected_scope_token": token}
        if parsed.field:
            arguments["requested_fields"] = parsed.field
    tool_call = {
        "id": f"cli_{tool_name.replace('.', '_')}",
        "type": "function",
        "function": {
            "name": tool_name,
            "arguments": json.dumps(arguments),
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


def _run_email_command(argv: list[str], broker: ToolBroker, *, debug: bool = False) -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py email", description="Email metadata, selected-thread reads, summaries, and draft-only replies.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    metadata_parser = subparsers.add_parser("metadata", help="List email metadata only, no bodies.")
    metadata_parser.add_argument("--max-results", type=int, default=None, help="Max metadata rows, capped by config.")

    read_parser = subparsers.add_parser("read", help="Read one selected email thread.")
    read_parser.add_argument("thread_id", help="Selected email thread id.")

    summarize_parser = subparsers.add_parser("summarize", help="Summarize one selected email thread.")
    summarize_parser.add_argument("thread_id", help="Selected email thread id.")

    draft_parser = subparsers.add_parser("draft-reply", help="Draft a reply without sending.")
    draft_parser.add_argument("thread_id", help="Selected email thread id.")
    draft_parser.add_argument("--instruction", default="", help="Optional drafting instruction.")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    if parsed.command == "metadata":
        tool_name = "email.list_metadata"
        arguments: dict[str, object] = {}
        if parsed.max_results is not None:
            arguments["max_results"] = parsed.max_results
    elif parsed.command == "read":
        tool_name = "email.read_selected_thread"
        arguments = {"thread_id": parsed.thread_id}
    elif parsed.command == "summarize":
        tool_name = "email.summarize_thread"
        arguments = {"thread_id": parsed.thread_id}
    else:
        tool_name = "email.draft_reply"
        arguments = {"thread_id": parsed.thread_id, "user_instruction": parsed.instruction}
    tool_call = {
        "id": f"cli_{tool_name.replace('.', '_')}",
        "type": "function",
        "function": {
            "name": tool_name,
            "arguments": json.dumps(arguments),
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


def _run_messages_command(argv: list[str], broker: ToolBroker, *, debug: bool = False) -> int:
    parser = argparse.ArgumentParser(
        prog="smart_agent.py messages",
        description="Messages selected-thread stubs and manual draft-only replies.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    read_parser = subparsers.add_parser("read", help="Read one selected message thread if a safe connector is configured.")
    read_parser.add_argument("thread_id", help="Selected message thread id.")

    summarize_parser = subparsers.add_parser("summarize", help="Summarize one selected message thread.")
    summarize_parser.add_argument("thread_id", help="Selected message thread id.")

    draft_parser = subparsers.add_parser("draft-reply", help="Draft a message reply without sending.")
    draft_parser.add_argument("thread_id", help="Selected message thread id.")
    draft_parser.add_argument("--to", default="", help="Recipient display name for the draft.")
    draft_parser.add_argument("--instruction", default="", help="Optional drafting instruction.")

    manual_parser = subparsers.add_parser("draft-from-text", help="Draft from a manually provided ./workspace text file.")
    manual_parser.add_argument("--to", required=True, help="Recipient display name for the draft.")
    manual_parser.add_argument("--context-file", required=True, help="Path to a UTF-8 text file inside ./workspace.")
    manual_parser.add_argument("--instruction", default="", help="Optional drafting instruction.")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    if parsed.command == "read":
        tool_name = "messages.read_selected_thread"
        arguments: dict[str, object] = {"thread_id": parsed.thread_id}
    elif parsed.command == "summarize":
        tool_name = "messages.summarize_thread"
        arguments = {"thread_id": parsed.thread_id}
    elif parsed.command == "draft-reply":
        tool_name = "messages.draft_reply"
        arguments = {"thread_id": parsed.thread_id, "user_instruction": parsed.instruction}
        if parsed.to:
            arguments["to"] = parsed.to
    else:
        tool_name = "messages.draft_reply"
        arguments = {
            "to": parsed.to,
            "context_file": parsed.context_file,
            "user_instruction": parsed.instruction,
        }
    tool_call = {
        "id": f"cli_{tool_name.replace('.', '_')}",
        "type": "function",
        "function": {
            "name": tool_name,
            "arguments": json.dumps(arguments),
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
