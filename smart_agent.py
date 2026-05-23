#!/usr/bin/env python
from __future__ import annotations

import sys


MIN_PYTHON_VERSION = (3, 11)


def _python_version_error_message(
    version_info: tuple[int, int, int] | tuple[int, int],
    executable: str,
) -> str:
    version = ".".join(str(part) for part in version_info[:3])
    return f"""AI Super Agent requires Python 3.11 or newer.

Detected Python: {version}
Executable: {executable}

Recommended local setup:
  cd "/Users/sambehdjou/Documents/AI Super Agent"
  python3.11 -m venv .venv
  source .venv/bin/activate
  python -m pip install -e '.[dev]'
  export LMSTUDIO_BASE_URL="http://localhost:1234/v1"
  export LMSTUDIO_MODEL="<model id from LM Studio>"
  python smart_agent.py doctor

If Python 3.11 is not installed, install it first:
  brew install python@3.11

If you are running inside Codex, this bundled runtime also works:
  /Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 smart_agent.py doctor

To list LM Studio model IDs after starting the Developer Server:
  curl http://localhost:1234/v1/models
"""


def _enforce_python_version() -> None:
    if sys.version_info < MIN_PYTHON_VERSION:
        print(_python_version_error_message(sys.version_info, sys.executable), file=sys.stderr)
        raise SystemExit(2)


_enforce_python_version()

import argparse
import json
import os
from pathlib import Path

from agent.config.runtime import RuntimeConfig, RuntimeConfigError
from agent.core.lmstudio_client import LMStudioClient, LMStudioConfig, LMStudioError
from agent.core.orchestrator import Orchestrator, OrchestratorResult, new_session_id
from agent.core.tool_broker import ToolBroker
from agent.config.loader import load_capabilities_config
from agent.native_skills.registry import NativeSkillRegistry
from agent.safety.audit import AuditLogError, AuditLogger
from agent.safety.approvals import ApprovalManager, ApprovalStore
from agent.safety.actions import ActionCenter
from agent.safety.policy import PolicyEngine
from agent.safety.validation import validate_startup_policy
from agent.tools.registry import default_registry
from agent.tools.errors import ToolError
from agent.tools.weather.formatter import format_weather_answer
from agent.tools.weather.preferences import clear_default_location, set_default_location, weather_preferences
from agent.ui.approvals_ui import ConsoleApprovalPrompt
from agent.ui.cli_commands import dispatch_cli
from agent.ui.interactive import InteractiveState, run_interactive
from agent.ui.privacy_center import (
    CONFIRM_DELETE_MEMORY,
    format_privacy_json,
    privacy_audit_summary,
    privacy_delete_memory,
    privacy_export,
    privacy_inventory,
    privacy_permissions,
    privacy_status,
)
from agent.workflows.daily_briefing import briefing_config_load, briefing_config_set, daily_briefing_v2
from agent.workflows.browser_clipping import (
    browser_clip_url_to_workspace,
    browser_read_url,
    browser_selected_tab_stub,
    browser_summarize_url,
)
from agent.workflows.calendar_writes import (
    CALENDAR_CREATE_ACTION,
    CALENDAR_DELETE_ACTION,
    CALENDAR_UPDATE_ACTION,
    draft_calendar_create,
    draft_calendar_delete,
    draft_calendar_update,
    execute_calendar_action,
)
from agent.workflows.contact_edits import (
    CONTACT_CREATE_ACTION,
    CONTACT_UPDATE_ACTION,
    draft_contact_create,
    draft_contact_update,
    execute_contact_action,
    parse_field_assignments,
)
from agent.workflows.email_triage import email_triage
from agent.workflows.email_sends import (
    draft_email_new,
    draft_email_reply_action,
    execute_email_send_action,
    read_body_argument,
)
from agent.workflows.files import files_diff, files_list, files_patch, files_read, files_search, files_summarize, files_write
from agent.workflows.knowledge_capture import (
    capture_from_file,
    capture_from_url,
    capture_list,
    capture_note,
    capture_summarize,
    promote_capture_to_memory,
)
from agent.workflows.meeting_prep import meeting_prep
from agent.workflows.meeting_followup import meeting_follow_up
from agent.workflows.message_handoff import (
    MESSAGE_COPY_DRAFT_ACTION,
    MESSAGE_SAVE_DRAFT_ACTION,
    draft_message_handoff_actions,
    execute_message_handoff_action,
)
from agent.workflows.research import source_grounded_research
from agent.workflows.self_improvement_backlog import self_improvement_backlog
from agent.workflows.self_improvement_loop import (
    build_overnight_plan,
    create_self_improvement_commit_action,
    execute_self_improvement_commit,
    implement_approved_proposal,
    run_self_improvement_tests,
    show_self_improvement_diff,
)
from agent.workflows.tasks import TASK_CREATE_ACTION, execute_task_action
from agent.workflows.task_extraction import extract_personal_tasks


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
    audit_logger = AuditLogger(runtime_config.audit_log_path)
    session_id = new_session_id()
    action_center = ActionCenter(
        audit_logger=audit_logger,
        session_id=session_id,
        model=config.model,
        route="tasks_actions",
    )
    try:
        registry = default_registry(action_center=action_center)
    except RuntimeConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    approval_store = ApprovalStore()
    approval_interactive = args.interactive or (
        bool(args.message) and args.message[0] in {"calendar", "contacts", "email", "messages", "tasks"} and sys.stdin.isatty()
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
    if args.message and args.message[0] == "browser":
        return _run_browser_command(args.message[1:], broker)
    if args.message and args.message[0] == "capture":
        return _run_capture_command(args.message[1:], broker, debug=debug_enabled)
    if args.message and args.message[0] == "weather":
        return _run_weather_command(args.message[1:], broker, debug=debug_enabled)
    if args.message and args.message[0] == "briefing":
        return _run_briefing_command(args.message[1:], broker, debug=debug_enabled)
    if args.message and args.message[0] == "meeting":
        return _run_meeting_command(args.message[1:], broker, debug=debug_enabled)
    if args.message and args.message[0] == "files":
        return _run_files_command(args.message[1:], broker, debug=debug_enabled)
    if args.message and args.message[0] == "pdf":
        return _run_pdf_command(args.message[1:], broker, debug=debug_enabled)
    if args.message and args.message[0] == "memory":
        return _run_memory_command(args.message[1:], broker, debug=debug_enabled)
    if args.message and args.message[0] == "calendar":
        return _run_calendar_command(args.message[1:], broker, debug=debug_enabled)
    if args.message and args.message[0] == "contacts":
        return _run_contacts_command(args.message[1:], broker, debug=debug_enabled)
    if args.message and args.message[0] == "email":
        return _run_email_command(args.message[1:], broker, debug=debug_enabled)
    if args.message and args.message[0] == "messages":
        return _run_messages_command(args.message[1:], broker, debug=debug_enabled)
    if args.message and args.message[0] == "tasks":
        return _run_tasks_command(args.message[1:], broker, debug=debug_enabled)
    if args.message and args.message[0] == "skills":
        return _run_skills_command(args.message[1:], broker, debug=debug_enabled)
    if args.message and args.message[0] == "privacy":
        return _run_privacy_command(
            args.message[1:],
            broker,
            runtime=runtime_config,
            audit_logger=audit_logger,
        )
    if args.message and args.message[0] == "improve":
        return _run_improve_command(args.message[1:], broker, debug=debug_enabled)

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


def _run_browser_command(argv: list[str], broker: ToolBroker) -> int:
    parser = argparse.ArgumentParser(
        prog="smart_agent.py browser",
        description="Read, summarize, or clip an explicitly supplied URL without browser history access.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    read_parser = subparsers.add_parser("read-url", help="Fetch an explicit public URL as untrusted web data.")
    read_parser.add_argument("url")
    read_parser.add_argument("--max-chars", type=int, default=12000)
    summarize_parser = subparsers.add_parser("summarize-url", help="Summarize an explicit public URL with source metadata.")
    summarize_parser.add_argument("url")
    summarize_parser.add_argument("--max-chars", type=int, default=12000)
    clip_parser = subparsers.add_parser("clip-url", help="Clip an explicit public URL into the approved workspace.")
    clip_parser.add_argument("url")
    clip_parser.add_argument("--to", choices=["workspace"], default="workspace")
    clip_parser.add_argument("--filename", help="Optional filename under workspace/clips.")
    clip_parser.add_argument("--max-chars", type=int, default=20000)
    subparsers.add_parser("selected-tab", help="Show selected-tab setup notes; native integration is not enabled.")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    try:
        if parsed.command == "read-url":
            report = browser_read_url(broker, parsed.url, max_chars=parsed.max_chars)
        elif parsed.command == "summarize-url":
            report = browser_summarize_url(broker, parsed.url, max_chars=parsed.max_chars)
        elif parsed.command == "clip-url":
            report = browser_clip_url_to_workspace(
                broker,
                parsed.url,
                destination=parsed.to,
                filename=parsed.filename,
                max_chars=parsed.max_chars,
            )
        else:
            report = browser_selected_tab_stub(broker)
    except AuditLogError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("status") == "ok" else 2


def _run_capture_command(argv: list[str], broker: ToolBroker, *, debug: bool = False) -> int:
    parser = argparse.ArgumentParser(
        prog="smart_agent.py capture",
        description="Save explicit notes, workspace files, and URLs into the workspace knowledge inbox.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    note_parser = subparsers.add_parser("note", help="Capture user-provided text into the workspace inbox.")
    note_parser.add_argument("text")
    note_parser.add_argument("--title", default="")
    note_parser.add_argument("--tag", action="append", default=[])

    file_parser = subparsers.add_parser("from-file", help="Capture a workspace file as untrusted document data.")
    file_parser.add_argument("path")
    file_parser.add_argument("--title", default="")
    file_parser.add_argument("--tag", action="append", default=[])
    file_parser.add_argument(
        "--trusted-user",
        action="store_true",
        help="Mark this workspace file as user-authored trusted content. Defaults to untrusted document data.",
    )

    url_parser = subparsers.add_parser("from-url", help="Capture an explicit URL through web.fetch_url.")
    url_parser.add_argument("url")
    url_parser.add_argument("--title", default="")
    url_parser.add_argument("--tag", action="append", default=[])

    subparsers.add_parser("list", help="List workspace captures.")
    summarize_parser = subparsers.add_parser("summarize", help="Summarize the workspace capture inbox.")
    summarize_parser.add_argument("--limit", type=int, default=20)

    promote_parser = subparsers.add_parser("promote-to-memory", help="Promote one capture through Memory v2 policy.")
    promote_parser.add_argument("capture_id")
    promote_parser.add_argument("--category", default="project_fact")
    promote_parser.add_argument("--scope", default="default")

    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    try:
        if parsed.command == "note":
            payload = capture_note(broker, parsed.text, title=parsed.title, tags=parsed.tag)
        elif parsed.command == "from-file":
            payload = capture_from_file(
                broker,
                parsed.path,
                title=parsed.title,
                tags=parsed.tag,
                trusted_user=parsed.trusted_user,
            )
        elif parsed.command == "from-url":
            payload = capture_from_url(broker, parsed.url, title=parsed.title, tags=parsed.tag)
        elif parsed.command == "list":
            payload = capture_list(broker)
        elif parsed.command == "summarize":
            payload = capture_summarize(broker, limit=parsed.limit)
        else:
            payload = promote_capture_to_memory(
                broker,
                parsed.capture_id,
                category=parsed.category,
                scope=parsed.scope,
            )
    except AuditLogError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if debug and isinstance(payload, dict):
        steps = payload.get("steps", [])
        print(
            "[debug] "
            f"capture command={parsed.command} tools={[step.get('tool_name') for step in steps if isinstance(step, dict)]} "
            "apple_notes=false memory_write_only_on_promote=true",
            file=sys.stderr,
        )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("status") == "ok" else 2


def _run_privacy_command(
    argv: list[str],
    broker: ToolBroker,
    *,
    runtime: RuntimeConfig,
    audit_logger: AuditLogger,
) -> int:
    parser = argparse.ArgumentParser(
        prog="smart_agent.py privacy",
        description="Inspect local agent data inventory, privacy status, exports, and deletion options.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status", help="Show high-level privacy status.")
    subparsers.add_parser("inventory", help="Show metadata-only data inventory.")
    subparsers.add_parser("export", help="Export a redacted local privacy report.")
    delete_parser = subparsers.add_parser("delete-memory", help="Clear local memory through brokered memory.clear.")
    delete_parser.add_argument("--scope", default="default")
    delete_parser.add_argument("--confirm", default="")
    audit_parser = subparsers.add_parser("audit-summary", help="Summarize audit metadata without raw args.")
    audit_parser.add_argument("--limit", type=int, default=5000)
    subparsers.add_parser("permissions", help="Show grants and personal/high/critical capability rules.")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    try:
        if parsed.command == "status":
            payload = privacy_status(runtime=runtime, audit_logger=audit_logger)
        elif parsed.command == "inventory":
            payload = privacy_inventory(runtime=runtime, audit_logger=audit_logger)
        elif parsed.command == "export":
            payload = privacy_export(runtime=runtime, audit_logger=audit_logger)
        elif parsed.command == "delete-memory":
            payload = privacy_delete_memory(
                broker,
                scope=parsed.scope,
                confirm=parsed.confirm,
                audit_logger=audit_logger,
            )
        elif parsed.command == "audit-summary":
            payload = privacy_audit_summary(runtime=runtime, audit_logger=audit_logger, limit=parsed.limit)
        else:
            payload = privacy_permissions(runtime=runtime, audit_logger=audit_logger)
    except AuditLogError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(format_privacy_json(payload))
    if parsed.command == "delete-memory" and parsed.confirm != CONFIRM_DELETE_MEMORY:
        return 2
    return 0 if payload.get("status") == "ok" else 2


def _run_weather_command(argv: list[str], broker: ToolBroker, *, debug: bool = False) -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py weather", description="Weather lookups for user-provided locations.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="Check weather provider configuration without fetching weather data.")
    config_parser = subparsers.add_parser("config", help="Show or update explicit weather preferences.")
    config_subparsers = config_parser.add_subparsers(dest="config_command", required=True)
    config_subparsers.add_parser("show", help="Show safe weather preferences.")
    set_default_parser = config_subparsers.add_parser("set-default", help="Persist an explicit default weather location.")
    set_default_parser.add_argument("location", nargs="+", help="City, region, or direct lat/lon explicitly provided by the user.")
    config_subparsers.add_parser("clear-default", help="Clear the persisted default weather location.")

    cache_parser = subparsers.add_parser("cache", help="Manage the local TTL weather cache.")
    cache_subparsers = cache_parser.add_subparsers(dest="cache_command", required=True)
    cache_subparsers.add_parser("clear", help="Clear cached weather responses.")

    smoke_parser = subparsers.add_parser("smoke", help="Run current and forecast checks for a user-provided location.")
    smoke_parser.add_argument("location", nargs="+", help="City, ZIP/postal code, or other user-provided location.")
    smoke_parser.add_argument("--days", type=int, default=3)
    smoke_parser.add_argument("--units", choices=["metric", "imperial"], default=None)
    smoke_parser.add_argument("--locale", default=None)
    smoke_parser.add_argument("--hourly", action="store_true", help="Include hourly forecast slices when supported.")
    smoke_parser.add_argument("--provider", default=None, help="Override the configured weather provider for this request.")

    current_parser = subparsers.add_parser("current", help="Fetch current weather for a user-provided location.")
    current_parser.add_argument("location", nargs="*", help="City, ZIP/postal code, or other user-provided location.")
    current_parser.add_argument("--units", choices=["metric", "imperial"], default=None)
    current_parser.add_argument("--locale", default=None)
    current_parser.add_argument("--provider", default=None, help="Override the configured weather provider for this request.")
    current_parser.add_argument("--no-cache", action="store_true", help="Bypass the local weather cache for this request.")
    current_parser.add_argument("--json", action="store_true", help="Print the raw structured weather payload.")

    forecast_parser = subparsers.add_parser("forecast", help="Fetch a forecast for a user-provided location.")
    forecast_parser.add_argument("location", nargs="*", help="City, ZIP/postal code, or other user-provided location.")
    forecast_parser.add_argument("--days", type=int, default=None)
    forecast_parser.add_argument("--units", choices=["metric", "imperial"], default=None)
    forecast_parser.add_argument("--locale", default=None)
    forecast_parser.add_argument("--provider", default=None, help="Override the configured weather provider for this request.")
    forecast_parser.add_argument("--hourly", action="store_true", help="Include hourly forecast slices when supported.")
    forecast_parser.add_argument("--no-cache", action="store_true", help="Bypass the local weather cache for this request.")
    forecast_parser.add_argument("--json", action="store_true", help="Print the raw structured weather payload.")

    alerts_parser = subparsers.add_parser("alerts", help="Fetch active weather alerts for a user-provided location when supported.")
    alerts_parser.add_argument("location", nargs="*", help="City, ZIP/postal code, or other user-provided location.")
    alerts_parser.add_argument("--locale", default=None)
    alerts_parser.add_argument("--provider", default=None, help="Override the configured weather provider for this request.")
    alerts_parser.add_argument("--json", action="store_true", help="Print the raw structured weather payload.")
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

    if parsed.command == "config":
        if parsed.config_command == "show":
            print(json.dumps(weather_preferences().to_dict(), indent=2, sort_keys=True))
            return 0
        if parsed.config_command == "set-default":
            payload = set_default_location(" ".join(parsed.location))
            print(json.dumps(payload, indent=2, sort_keys=True))
            return 0 if payload.get("status") == "ok" else 2
        if parsed.config_command == "clear-default":
            print(json.dumps(clear_default_location(), indent=2, sort_keys=True))
            return 0

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
        if parsed.provider is not None:
            base_args["provider"] = parsed.provider
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

    tool_name = {
        "current": "weather.current",
        "forecast": "weather.forecast",
        "alerts": "weather.alerts",
    }[parsed.command]
    arguments: dict[str, object] = {"location": " ".join(parsed.location)}
    if getattr(parsed, "units", None) is not None:
        arguments["units"] = parsed.units
    if getattr(parsed, "locale", None) is not None:
        arguments["locale"] = parsed.locale
    if getattr(parsed, "provider", None) is not None:
        arguments["provider"] = parsed.provider
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


def _run_briefing_command(argv: list[str], broker: ToolBroker, *, debug: bool = False) -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py briefing", description="Safety-scoped briefings.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    daily_parser = subparsers.add_parser("daily", help="Build a configurable daily briefing from explicitly selected sources.")
    daily_parser.add_argument("--sections", help="Comma-separated sections: weather,calendar,tasks,email,web,memory,suggested_actions.")
    daily_parser.add_argument(
        "--weather",
        nargs="*",
        help="Include weather. Optionally pass a city, ZIP/postal code, or location string.",
    )
    daily_parser.add_argument("--weather-default", action="store_true", help="Use WEATHER_DEFAULT_LOCATION if explicitly configured.")
    daily_parser.add_argument("--calendar", action="store_true", help="Include today's selected calendar range after approval.")
    daily_parser.add_argument("--email-metadata", action="store_true", help="Include email metadata after approval; no bodies are read.")
    daily_parser.add_argument("--web-topic", action="append", default=[], help="Include public web search results for this topic.")
    daily_parser.add_argument("--dry-run", action="store_true", help="Show planned tools and approvals without executing tools.")
    daily_parser.add_argument("--json", action="store_true", help="Print the structured briefing payload.")
    config_parser = subparsers.add_parser("config", help="Show or update Daily Briefing v2 config.")
    config_subparsers = config_parser.add_subparsers(dest="config_command", required=True)
    config_subparsers.add_parser("show", help="Show Daily Briefing v2 config.")
    config_set_parser = config_subparsers.add_parser("set", help="Set config with key=value pairs.")
    config_set_parser.add_argument(
        "assignment",
        nargs="+",
        help="Supported keys: sections, weather_location, web_topics, suggested_actions.",
    )
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    if parsed.command == "config":
        if parsed.config_command == "show":
            print(json.dumps(briefing_config_load(), indent=2, sort_keys=True))
            return 0
        updates: dict[str, object] = {}
        for assignment in parsed.assignment:
            if "=" not in assignment:
                print(f"invalid config assignment: {assignment}; use key=value", file=sys.stderr)
                return 2
            key, value = assignment.split("=", 1)
            updates[key.strip()] = value.strip()
        try:
            print(json.dumps(briefing_config_set(updates), indent=2, sort_keys=True))
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    if parsed.command != "daily":
        parser.error("unsupported briefing command")

    explicit_sections = [item.strip() for item in parsed.sections.split(",")] if parsed.sections else None
    include_weather = parsed.weather is not None or bool(parsed.weather_default)
    legacy_sections = []
    if explicit_sections is None:
        if include_weather:
            legacy_sections.append("weather")
        if parsed.calendar:
            legacy_sections.append("calendar")
        if parsed.email_metadata:
            legacy_sections.append("email")
        if parsed.web_topic:
            legacy_sections.append("web")
    location = " ".join(parsed.weather) if parsed.weather else None
    center = ActionCenter(
        audit_logger=broker.audit_logger,
        session_id=broker.session_id,
        model=broker.model,
        route="briefing_actions",
    )
    try:
        payload = daily_briefing_v2(
            broker,
            sections=explicit_sections if explicit_sections is not None else (legacy_sections or None),
            weather_location=location,
            use_default_weather_location=bool(parsed.weather_default or parsed.weather == []),
            web_topics=parsed.web_topic,
            dry_run=bool(parsed.dry_run),
            action_center=center,
        )
    except AuditLogError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if debug:
        sources = [
            name
            for enabled, name in (
                (include_weather, "weather"),
                ("calendar" in payload.get("configured_sections", []), "calendar"),
                ("email" in payload.get("configured_sections", []), "email"),
                ("tasks" in payload.get("configured_sections", []), "tasks"),
                ("web" in payload.get("configured_sections", []), "web"),
                ("memory" in payload.get("configured_sections", []), "memory"),
                ("suggested_actions" in payload.get("configured_sections", []), "suggested_actions"),
            )
            if enabled
        ]
        print(
            "[debug] "
            f"briefing sources={sources or ['none']} dry_run={payload.get('dry_run')} "
            "writes_or_sends=false memory_writes=false",
            file=sys.stderr,
        )
    if parsed.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("status") in {"ok", "limited", "dry_run"}:
        print(str(payload.get("briefing", "Weather briefing unavailable")))
    else:
        print(str(payload.get("error", "weather briefing failed")), file=sys.stderr)
    return 0 if payload.get("status") in {"ok", "limited", "dry_run"} else 2


def _run_meeting_command(argv: list[str], broker: ToolBroker, *, debug: bool = False) -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py meeting", description="Safety-scoped meeting preparation.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    prep_parser = subparsers.add_parser("prep", help="Prepare for a selected calendar meeting.")
    selector = prep_parser.add_mutually_exclusive_group(required=True)
    selector.add_argument("--event-id", help="Selected event token returned by calendar.read_date_range.")
    selector.add_argument("--date", help="Meeting date, YYYY-MM-DD; requires --title.")
    prep_parser.add_argument("--title", help="Meeting title when using --date.")
    prep_parser.add_argument("--contact", action="append", default=[], help="Optional specific contact query; may be repeated.")
    prep_parser.add_argument("--web-topic", help="Optional public web research topic.")
    prep_parser.add_argument("--dry-run", action="store_true", help="Show planned tools and approvals without executing tools.")
    prep_parser.add_argument("--json", action="store_true", help="Print the structured meeting prep payload.")
    follow_parser = subparsers.add_parser("follow-up", help="Create meeting follow-up drafts and pending actions.")
    follow_selector = follow_parser.add_mutually_exclusive_group(required=False)
    follow_selector.add_argument("--event-id", help="Selected event token returned by calendar.read_date_range.")
    follow_selector.add_argument("--notes-file", help="Workspace-bounded meeting notes file.")
    follow_parser.add_argument("--contact", action="append", default=[], help="Optional selected contact lookup query; may be repeated.")
    follow_parser.add_argument("--dry-run", action="store_true", help="Show planned reads/actions without executing tools or queuing actions.")
    follow_parser.add_argument("--json", action="store_true", help="Print the structured follow-up payload.")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    if parsed.command not in {"prep", "follow-up"}:
        parser.error("unsupported meeting command")
    if parsed.command == "follow-up":
        center = ActionCenter(
            audit_logger=broker.audit_logger,
            session_id=broker.session_id,
            model=broker.model,
            route="meeting_followup_actions",
        )
        try:
            payload = meeting_follow_up(
                broker,
                event_id=parsed.event_id,
                notes_file=parsed.notes_file,
                contact_queries=parsed.contact,
                dry_run=bool(parsed.dry_run),
                action_center=center,
            )
        except AuditLogError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        if debug:
            print(
                "[debug] "
                f"meeting follow-up dry_run={payload.get('dry_run')} "
                "writes_or_sends=false memory_writes=false",
                file=sys.stderr,
            )
        if parsed.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(str(payload.get("briefing", "Meeting follow-up unavailable")))
        return 0 if payload.get("status") in {"ok", "limited", "dry_run"} else 2
    if parsed.date and not parsed.title:
        parser.error("meeting prep --date requires --title")
    try:
        payload = meeting_prep(
            broker,
            event_id=parsed.event_id,
            date=parsed.date,
            title=parsed.title,
            contact_queries=parsed.contact,
            web_topic=parsed.web_topic,
            dry_run=bool(parsed.dry_run),
        )
    except AuditLogError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if debug:
        print(
            "[debug] "
            f"meeting prep dry_run={payload.get('dry_run')} "
            "writes_or_sends=false memory_writes=false",
            file=sys.stderr,
        )
    if parsed.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(str(payload.get("briefing", "Meeting prep unavailable")))
    return 0 if payload.get("status") in {"ok", "limited", "dry_run"} else 2


def _run_files_command(argv: list[str], broker: ToolBroker, *, debug: bool = False) -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py files", description="Workspace-bounded file assistant.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List files inside approved roots.")
    list_parser.add_argument("path", nargs="?", default=".")
    list_parser.add_argument("--recursive", action="store_true")
    list_parser.add_argument("--max-entries", type=int, default=100)

    read_parser = subparsers.add_parser("read", help="Read a UTF-8 file inside approved roots.")
    read_parser.add_argument("path")
    read_parser.add_argument("--max-bytes", type=int, default=100_000)

    summarize_parser = subparsers.add_parser("summarize", help="Summarize a UTF-8 file as untrusted document data.")
    summarize_parser.add_argument("path")
    summarize_parser.add_argument("--max-bytes", type=int, default=100_000)

    search_parser = subparsers.add_parser("search", help="Search UTF-8 files inside approved roots.")
    search_parser.add_argument("query")
    search_parser.add_argument("--path", default=".")
    search_parser.add_argument("--max-files", type=int, default=100)
    search_parser.add_argument("--max-matches", type=int, default=25)
    search_parser.add_argument("--max-bytes", type=int, default=100_000)

    patch_parser = subparsers.add_parser("patch", help="Patch exact text in a file, with backup and diff.")
    patch_parser.add_argument("path")
    patch_parser.add_argument("--old-text", required=True)
    patch_parser.add_argument("--new-text", required=True)
    patch_parser.add_argument("--expected-replacements", type=int, default=1)

    write_parser = subparsers.add_parser("write", help="Write UTF-8 content inside approved roots.")
    write_parser.add_argument("path")
    write_parser.add_argument("--content", required=True)
    write_parser.add_argument("--overwrite", action="store_true")

    diff_parser = subparsers.add_parser("diff", help="Show git diff through the brokered git tool.")
    diff_parser.add_argument("path", nargs="?")
    diff_parser.add_argument("--staged", action="store_true")
    diff_parser.add_argument("--max-chars", type=int, default=20_000)

    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    try:
        if parsed.command == "list":
            payload = files_list(
                broker,
                parsed.path,
                recursive=parsed.recursive,
                max_entries=parsed.max_entries,
            )
        elif parsed.command == "read":
            payload = files_read(broker, parsed.path, max_bytes=parsed.max_bytes)
        elif parsed.command == "summarize":
            payload = files_summarize(broker, parsed.path, max_bytes=parsed.max_bytes)
        elif parsed.command == "search":
            payload = files_search(
                broker,
                parsed.query,
                path=parsed.path,
                max_files=parsed.max_files,
                max_matches=parsed.max_matches,
                max_bytes=parsed.max_bytes,
            )
        elif parsed.command == "patch":
            payload = files_patch(
                broker,
                parsed.path,
                parsed.old_text,
                parsed.new_text,
                expected_replacements=parsed.expected_replacements,
            )
        elif parsed.command == "write":
            payload = files_write(broker, parsed.path, parsed.content, overwrite=parsed.overwrite)
        else:
            payload = files_diff(broker, path=parsed.path, staged=parsed.staged, max_chars=parsed.max_chars)
    except AuditLogError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if debug and isinstance(payload, dict):
        debug_payload = payload.get("debug")
        if debug_payload:
            from agent.core.orchestrator import format_debug_payload

            print("[debug] " + format_debug_payload({"event": "tool_broker", **debug_payload}), file=sys.stderr)
    print(json.dumps(payload, indent=2, sort_keys=True))
    if payload.get("status") == "error":
        return 2
    if "allowed" in payload:
        return 0 if payload.get("allowed") else 2
    return 0


def _run_pdf_command(argv: list[str], broker: ToolBroker, *, debug: bool = False) -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py pdf", description="Workspace-bounded PDF assistant.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common(command_parser: argparse.ArgumentParser) -> None:
        command_parser.add_argument("path")
        command_parser.add_argument("--max-bytes", type=int, default=10_000_000)
        command_parser.add_argument("--max-pages", type=int, default=100)

    info_parser = subparsers.add_parser("info", help="Read PDF metadata and page count inside approved roots.")
    add_common(info_parser)

    text_parser = subparsers.add_parser("extract-text", help="Extract embedded PDF text as untrusted document data.")
    add_common(text_parser)
    text_parser.add_argument("--max-chars", type=int, default=200_000)

    summarize_parser = subparsers.add_parser("summarize", help="Summarize a workspace PDF without storing content in memory.")
    add_common(summarize_parser)
    summarize_parser.add_argument("--max-chars", type=int, default=200_000)

    tables_parser = subparsers.add_parser("extract-tables", help="Extract text-delimited tables from a workspace PDF best-effort.")
    add_common(tables_parser)
    tables_parser.add_argument("--max-chars", type=int, default=200_000)

    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    args: dict[str, object] = {
        "path": parsed.path,
        "max_bytes": parsed.max_bytes,
        "max_pages": parsed.max_pages,
    }
    if hasattr(parsed, "max_chars"):
        args["max_chars"] = parsed.max_chars
    tool_by_command = {
        "info": "documents.pdf.read",
        "extract-text": "documents.pdf.extract_text",
        "summarize": "documents.pdf.summarize",
        "extract-tables": "documents.pdf.extract_tables",
    }
    payload = _execute_cli_tool(
        broker,
        f"cli_pdf_{parsed.command.replace('-', '_')}",
        tool_by_command[parsed.command],
        args,
    )
    if debug and isinstance(payload, dict):
        debug_payload = payload.get("debug")
        if debug_payload:
            from agent.core.orchestrator import format_debug_payload

            print("[debug] " + format_debug_payload({"event": "tool_broker", **debug_payload}), file=sys.stderr)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("allowed") else 2


def _run_skills_command(argv: list[str], broker: ToolBroker, *, debug: bool = False) -> int:
    parser = argparse.ArgumentParser(
        prog="smart_agent.py skills",
        description="Review native skill candidates without installing or executing external code.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List metadata-only native skill manifests.")

    show_parser = subparsers.add_parser("show", help="Show one native skill manifest.")
    show_parser.add_argument("skill_id")

    subparsers.add_parser("validate", help="Validate native skill manifests.")
    subparsers.add_parser("doctor", help="Check native skill discovery and validation status.")

    vet_parser = subparsers.add_parser("vet", help="Vet a workspace SKILL.md file.")
    vet_parser.add_argument("path")

    folder_parser = subparsers.add_parser("vet-folder", help="Vet a workspace skill folder.")
    folder_parser.add_argument("path")

    score_parser = subparsers.add_parser("score", help="Score a workspace skill candidate file.")
    score_parser.add_argument("path")

    find_parser = subparsers.add_parser("find", help="Find local native skills and reviewed candidates for a requested capability.")
    find_parser.add_argument("query")
    find_parser.add_argument("--max-results", type=int, default=5)

    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    if parsed.command in {"list", "show", "validate", "doctor"}:
        registry = NativeSkillRegistry(Path("."))
        if parsed.command == "list":
            payload = {"status": "ok", "skills": registry.list()}
        elif parsed.command == "show":
            skill = registry.show(parsed.skill_id)
            payload = {"status": "ok", "skill": skill} if skill else {"status": "error", "error": "native skill not found", "skill_id": parsed.skill_id}
        elif parsed.command == "validate":
            payload = registry.validate_all()
        else:
            payload = registry.doctor()
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if payload.get("status") == "ok" else 2

    if parsed.command == "vet":
        payload = _execute_cli_tool(broker, "cli_skills_vet", "native_skills.vet_skill_file", {"path": parsed.path})
    elif parsed.command == "vet-folder":
        payload = _execute_cli_tool(broker, "cli_skills_vet_folder", "native_skills.vet_skill_folder", {"path": parsed.path})
    elif parsed.command == "score":
        payload = _execute_cli_tool(broker, "cli_skills_score", "native_skills.score_candidate", {"path": parsed.path})
    else:
        payload = _execute_cli_tool(
            broker,
            "cli_skills_find",
            "native_skills.find_skill",
            {"query": parsed.query, "max_results": parsed.max_results},
        )
    if debug and isinstance(payload, dict) and payload.get("debug"):
        from agent.core.orchestrator import format_debug_payload

        print("[debug] " + format_debug_payload({"event": "tool_broker", **payload["debug"]}), file=sys.stderr)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("allowed") else 2


def _execute_cli_tool(broker: ToolBroker, call_id: str, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    result = broker.execute(
        {
            "id": call_id,
            "type": "function",
            "function": {"name": tool_name, "arguments": json.dumps(arguments)},
        }
    )
    try:
        content = json.loads(result.content)
    except json.JSONDecodeError:
        content = {"raw": result.content}
    return {
        "tool_name": result.tool_name,
        "tool_call_id": result.tool_call_id,
        "allowed": result.allowed,
        "content": content,
        "debug": result.debug,
    }


def _run_memory_command(argv: list[str], broker: ToolBroker, *, debug: bool = False) -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py memory", description="Safe local memory tools.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List memory records for a scope.")
    list_parser.add_argument("--scope", default="default")

    add_parser = subparsers.add_parser("add", help="Store a non-personal preference, project fact, or workflow lesson.")
    add_parser.add_argument("--content", required=True)
    add_parser.add_argument(
        "--category",
        required=True,
        choices=[
            "session_context",
            "user_preference",
            "project_fact",
            "workflow_lesson",
            "temporary_personal_context",
            "personal_data_reference",
        ],
    )
    add_parser.add_argument("--scope", default="default")
    add_parser.add_argument("--source-trust", default="TRUSTED_USER")
    add_parser.add_argument("--personal", action="store_true", help="Use approval-gated personal memory storage.")

    search_parser = subparsers.add_parser("search", help="Search memory within a scope and optional categories.")
    search_parser.add_argument("query")
    search_parser.add_argument("--scope", default="default")
    search_parser.add_argument("--category", action="append", default=[])
    search_parser.add_argument("--limit", type=int, default=10)

    delete_parser = subparsers.add_parser("delete", help="Delete one memory record by id.")
    delete_parser.add_argument("record_id")

    export_parser = subparsers.add_parser("export", help="Export memory records for a scope.")
    export_parser.add_argument("--scope", default="default")

    clear_parser = subparsers.add_parser("clear", help="Clear memory records for a scope.")
    clear_parser.add_argument("--scope", default="default")

    context_parser = subparsers.add_parser("context", help="Build bounded non-personal memory context.")
    context_parser.add_argument("query")
    context_parser.add_argument("--scope", default="default")
    context_parser.add_argument("--category", action="append", default=[])
    context_parser.add_argument("--max-records", type=int, default=5)
    context_parser.add_argument("--max-chars", type=int, default=1200)

    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    if parsed.command == "list":
        tool_name = "memory.export"
        arguments: dict[str, object] = {"scope": parsed.scope}
    elif parsed.command == "add":
        tool_name = "memory.store_personal" if parsed.personal else "memory.store"
        arguments = {
            "content": parsed.content,
            "category": parsed.category,
            "scope": parsed.scope,
            "source_trust": parsed.source_trust,
        }
    elif parsed.command == "search":
        tool_name = "memory.search"
        arguments = {
            "query": parsed.query,
            "scope": parsed.scope,
            "limit": parsed.limit,
            "categories": parsed.category,
        }
    elif parsed.command == "delete":
        tool_name = "memory.delete"
        arguments = {"record_id": parsed.record_id}
    elif parsed.command == "export":
        tool_name = "memory.export"
        arguments = {"scope": parsed.scope}
    elif parsed.command == "clear":
        tool_name = "memory.clear"
        arguments = {"scope": parsed.scope}
    else:
        tool_name = "memory.context"
        arguments = {
            "query": parsed.query,
            "scope": parsed.scope,
            "categories": parsed.category,
            "max_records": parsed.max_records,
            "max_chars": parsed.max_chars,
            "include_personal": False,
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
    for capability_name in ("weather.status", "weather.current", "weather.forecast", "weather.alerts"):
        policy = broker.policy_engine.evaluate(capability_name)
        statuses[capability_name] = {
            "decision": policy.decision.value,
            "risk_level": policy.capability.risk_level.value if policy.capability else "FORBIDDEN",
            "reason": policy.reason,
        }
    return statuses


def _run_calendar_command(argv: list[str], broker: ToolBroker, *, debug: bool = False) -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py calendar", description="Read selected calendar ranges and review approved writes.")
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

    draft_create = subparsers.add_parser("draft-create", help="Draft a calendar create action in Action Center.")
    draft_create.add_argument("--title", required=True)
    draft_create.add_argument("--start", required=True)
    draft_create.add_argument("--end", required=True)
    draft_create.add_argument("--calendar", dest="calendar_name", default="")
    draft_create.add_argument("--attendee", action="append", default=[])
    draft_create.add_argument("--location", default="")
    draft_create.add_argument("--notes", default="")
    draft_create.add_argument("--allow-notes", action="store_true", help="Include notes/body text in the exact preview.")

    create_parser = subparsers.add_parser("create", help="Execute an approved calendar create action once.")
    create_parser.add_argument("--from-action", required=True)

    draft_update = subparsers.add_parser("draft-update", help="Draft a calendar update action in Action Center.")
    draft_update.add_argument("event_id")
    draft_update.add_argument("--title")
    draft_update.add_argument("--start")
    draft_update.add_argument("--end")
    draft_update.add_argument("--calendar", dest="calendar_name")
    draft_update.add_argument("--attendee", action="append", default=None)
    draft_update.add_argument("--location")
    draft_update.add_argument("--notes", default="")
    draft_update.add_argument("--allow-notes", action="store_true", help="Include notes/body text in the exact preview.")

    update_parser = subparsers.add_parser("update", help="Execute an approved calendar update action once.")
    update_parser.add_argument("--from-action", required=True)

    draft_delete = subparsers.add_parser("draft-delete", help="Draft a calendar delete action in Action Center.")
    draft_delete.add_argument("event_id")

    delete_parser = subparsers.add_parser("delete", help="Execute an approved calendar delete action once.")
    delete_parser.add_argument("--from-action", required=True)
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    if parsed.command in {"draft-create", "draft-update", "draft-delete", "create", "update", "delete"}:
        return _run_calendar_write_command(parsed, broker, debug=debug)
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


def _run_calendar_write_command(parsed: argparse.Namespace, broker: ToolBroker, *, debug: bool = False) -> int:
    center = ActionCenter(
        audit_logger=broker.audit_logger,
        session_id=broker.session_id,
        model=broker.model,
        route="calendar_actions",
    )
    try:
        if parsed.command == "draft-create":
            record = draft_calendar_create(
                center,
                title=parsed.title,
                start=parsed.start,
                end=parsed.end,
                calendar_name=parsed.calendar_name,
                attendees=parsed.attendee,
                location=parsed.location,
                notes=parsed.notes,
                allow_notes=parsed.allow_notes,
            )
            print(json.dumps(record.to_dict(), indent=2, sort_keys=True))
            return 0
        if parsed.command == "draft-update":
            changes = _calendar_update_changes(parsed)
            record = draft_calendar_update(center, event_id=parsed.event_id, changes=changes)
            print(json.dumps(record.to_dict(), indent=2, sort_keys=True))
            return 0
        if parsed.command == "draft-delete":
            record = draft_calendar_delete(center, event_id=parsed.event_id)
            print(json.dumps(record.to_dict(), indent=2, sort_keys=True))
            return 0
        expected = {
            "create": CALENDAR_CREATE_ACTION,
            "update": CALENDAR_UPDATE_ACTION,
            "delete": CALENDAR_DELETE_ACTION,
        }[parsed.command]
        report = execute_calendar_action(
            broker,
            center,
            action_id=parsed.from_action,
            expected_action_type=expected,
        )
        if debug and report.get("debug"):
            from agent.core.orchestrator import format_debug_payload

            print("[debug] " + format_debug_payload({"event": "calendar_action", **dict(report["debug"])}), file=sys.stderr)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report.get("status") == "ok" else 2
    except (AuditLogError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


def _calendar_update_changes(parsed: argparse.Namespace) -> dict[str, object]:
    changes: dict[str, object] = {}
    for field in ("title", "start", "end", "calendar_name", "location"):
        value = getattr(parsed, field, None)
        if value is not None:
            changes[field] = value
    if parsed.attendee is not None:
        changes["attendees"] = parsed.attendee
    if parsed.allow_notes and parsed.notes:
        changes["notes"] = parsed.notes
    elif parsed.notes:
        changes["notes_omitted"] = True
    return changes


def _run_contacts_command(argv: list[str], broker: ToolBroker, *, debug: bool = False) -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py contacts", description="Selected-scope contacts.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    search_parser = subparsers.add_parser("search", help="Search compact contact candidates.")
    search_parser.add_argument("query", nargs="?", help="Search query, at least 2 characters.")
    search_parser.add_argument("--query", dest="query_option", default=None, help="Search query, at least 2 characters.")
    search_parser.add_argument("--max-results", type=int, default=None, help="Max candidates, capped by config.")

    read_parser = subparsers.add_parser("read", help="Read one explicitly selected contact.")
    read_parser.add_argument("contact_id", nargs="?", help="Selected contact id/token returned by contacts search.")
    read_parser.add_argument("--token", default=None, help="Selected scope token returned by contacts search.")
    read_parser.add_argument("--field", action="append", default=[], help="Requested field; may be repeated.")

    draft_update_parser = subparsers.add_parser("draft-update", help="Draft a selected contact update in Action Center.")
    draft_update_parser.add_argument("contact_id", help="Selected contact id/token returned by contacts search.")
    draft_update_parser.add_argument("--set", dest="set_fields", action="append", default=[], help="Field change as key=value; may be repeated.")
    draft_update_parser.add_argument("--old", dest="old_fields", action="append", default=[], help="Known old value as key=value; may be repeated.")
    draft_update_parser.add_argument("--source-workflow", default="manual")

    update_parser = subparsers.add_parser("update", help="Execute one approved contact update action.")
    update_parser.add_argument("--from-action", required=True)

    draft_create_parser = subparsers.add_parser("draft-create", help="Draft a contact create action in Action Center.")
    draft_create_parser.add_argument("--display-name", required=True)
    draft_create_parser.add_argument("--field", dest="fields", action="append", default=[], help="Contact field as key=value; may be repeated.")
    draft_create_parser.add_argument("--source-workflow", default="manual")

    create_parser = subparsers.add_parser("create", help="Execute one approved contact create action.")
    create_parser.add_argument("--from-action", required=True)
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    if parsed.command == "draft-update":
        try:
            changes = parse_field_assignments(parsed.set_fields)
            old_values = parse_field_assignments(parsed.old_fields)
            record = draft_contact_update(
                ActionCenter(
                    audit_logger=broker.audit_logger,
                    session_id=broker.session_id,
                    model=broker.model,
                    route="contacts_actions",
                ),
                selected_scope_token=parsed.contact_id,
                changes=changes,
                old_values=old_values,
                source_workflow=parsed.source_workflow,
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(json.dumps(record.to_dict(), indent=2, sort_keys=True))
        return 0
    if parsed.command == "update":
        report = execute_contact_action(
            broker,
            ActionCenter(
                audit_logger=broker.audit_logger,
                session_id=broker.session_id,
                model=broker.model,
                route="contacts_actions",
            ),
            action_id=parsed.from_action,
            expected_action_type=CONTACT_UPDATE_ACTION,
        )
        if debug and report.get("debug"):
            from agent.core.orchestrator import format_debug_payload

            print("[debug] " + format_debug_payload({"event": "contacts_action", **dict(report["debug"])}), file=sys.stderr)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report.get("status") == "ok" else 2
    if parsed.command == "draft-create":
        try:
            fields = parse_field_assignments(parsed.fields)
            record = draft_contact_create(
                ActionCenter(
                    audit_logger=broker.audit_logger,
                    session_id=broker.session_id,
                    model=broker.model,
                    route="contacts_actions",
                ),
                display_name=parsed.display_name,
                fields=fields,
                source_workflow=parsed.source_workflow,
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(json.dumps(record.to_dict(), indent=2, sort_keys=True))
        return 0
    if parsed.command == "create":
        report = execute_contact_action(
            broker,
            ActionCenter(
                audit_logger=broker.audit_logger,
                session_id=broker.session_id,
                model=broker.model,
                route="contacts_actions",
            ),
            action_id=parsed.from_action,
            expected_action_type=CONTACT_CREATE_ACTION,
        )
        if debug and report.get("debug"):
            from agent.core.orchestrator import format_debug_payload

            print("[debug] " + format_debug_payload({"event": "contacts_action", **dict(report["debug"])}), file=sys.stderr)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report.get("status") == "ok" else 2
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

    triage_parser = subparsers.add_parser("triage", help="Triage email metadata and optionally one selected thread.")
    triage_parser.add_argument("--selected-thread", default=None, help="Read, summarize, and draft for one selected thread.")
    triage_parser.add_argument("--max-results", type=int, default=10, help="Max metadata rows, capped by config.")
    triage_parser.add_argument("--dry-run", action="store_true", help="Show planned tools and approvals without executing tools.")
    triage_parser.add_argument("--json", action="store_true", help="Print the structured triage payload.")

    read_parser = subparsers.add_parser("read", help="Read one selected email thread.")
    read_parser.add_argument("thread_id", help="Selected email thread id.")

    summarize_parser = subparsers.add_parser("summarize", help="Summarize one selected email thread.")
    summarize_parser.add_argument("thread_id", help="Selected email thread id.")

    draft_parser = subparsers.add_parser("draft-reply", help="Draft a reply without sending.")
    draft_parser.add_argument("thread_id", help="Selected email thread id.")
    draft_parser.add_argument("--instruction", default="", help="Optional drafting instruction.")
    draft_parser.add_argument("--to", default="", help="Recipient for creating a reviewed send action.")
    draft_parser.add_argument("--subject", default="", help="Subject for creating a reviewed send action.")
    draft_parser.add_argument("--body", default=None, help="Full reviewed body for creating a send action.")
    draft_parser.add_argument("--body-file", default=None, help="UTF-8 file containing the full reviewed body.")
    draft_parser.add_argument("--from-account", default="", help="From account/provider account label for preview.")
    draft_parser.add_argument("--provider", default="", help="Send provider label; use mock only for tests.")
    draft_parser.add_argument("--cc", action="append", default=[])
    draft_parser.add_argument("--bcc", action="append", default=[])
    draft_parser.add_argument("--attachment", action="append", default=[], help="Blocked in email send v1.")

    draft_new_parser = subparsers.add_parser("draft-new", help="Create a reviewed new-email send action.")
    draft_new_parser.add_argument("--to", required=True)
    draft_new_parser.add_argument("--subject", required=True)
    draft_new_parser.add_argument("--body", default=None)
    draft_new_parser.add_argument("--body-file", default=None)
    draft_new_parser.add_argument("--from-account", default="")
    draft_new_parser.add_argument("--provider", default="")
    draft_new_parser.add_argument("--cc", action="append", default=[])
    draft_new_parser.add_argument("--bcc", action="append", default=[])
    draft_new_parser.add_argument("--attachment", action="append", default=[], help="Blocked in email send v1.")
    draft_new_parser.add_argument("--source-workflow", default="manual")

    send_parser = subparsers.add_parser("send", help="Execute one approved email send action.")
    send_parser.add_argument("--from-action", required=True)
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    if parsed.command == "triage":
        try:
            payload = email_triage(
                broker,
                selected_thread=parsed.selected_thread,
                max_results=parsed.max_results,
                dry_run=bool(parsed.dry_run),
            )
        except AuditLogError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        if debug:
            print(
                "[debug] "
                f"email triage dry_run={payload.get('dry_run')} "
                "send=false delete=false move=false archive=false memory_writes=false",
                file=sys.stderr,
            )
        if parsed.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(str(payload.get("briefing", "Email triage unavailable")))
        return 0 if payload.get("status") in {"ok", "limited", "dry_run"} else 2

    if parsed.command == "draft-new":
        try:
            body = read_body_argument(parsed.body, parsed.body_file)
            record = draft_email_new(
                ActionCenter(
                    audit_logger=broker.audit_logger,
                    session_id=broker.session_id,
                    model=broker.model,
                    route="email_actions",
                ),
                to=parsed.to,
                subject=parsed.subject,
                body=body,
                from_account=parsed.from_account,
                provider=parsed.provider,
                cc=parsed.cc,
                bcc=parsed.bcc,
                attachments=parsed.attachment,
                source_workflow=parsed.source_workflow,
            )
        except (OSError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(json.dumps(record.to_dict(), indent=2, sort_keys=True))
        return 0

    if parsed.command == "send":
        report = execute_email_send_action(
            broker,
            ActionCenter(
                audit_logger=broker.audit_logger,
                session_id=broker.session_id,
                model=broker.model,
                route="email_actions",
            ),
            action_id=parsed.from_action,
        )
        if debug and report.get("debug"):
            from agent.core.orchestrator import format_debug_payload

            print("[debug] " + format_debug_payload({"event": "email_send_action", **dict(report["debug"])}), file=sys.stderr)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report.get("status") == "ok" else 2

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
        if parsed.to:
            try:
                body = read_body_argument(parsed.body, parsed.body_file)
                record = draft_email_reply_action(
                    ActionCenter(
                        audit_logger=broker.audit_logger,
                        session_id=broker.session_id,
                        model=broker.model,
                        route="email_actions",
                    ),
                    thread_id=parsed.thread_id,
                    to=parsed.to,
                    subject=parsed.subject or f"Re: {parsed.thread_id}",
                    body=body,
                    from_account=parsed.from_account,
                    provider=parsed.provider,
                    cc=parsed.cc,
                    bcc=parsed.bcc,
                    attachments=parsed.attachment,
                )
            except (OSError, ValueError) as exc:
                print(str(exc), file=sys.stderr)
                return 2
            print(json.dumps(record.to_dict(), indent=2, sort_keys=True))
            return 0
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
    manual_parser.add_argument("--save-path", default="", help="Optional workspace path for the save-draft action.")

    save_parser = subparsers.add_parser("save-draft", help="Save an approved message draft inside ./workspace.")
    save_parser.add_argument("--from-action", required=True)

    copy_parser = subparsers.add_parser("copy-draft", help="Copy an approved message draft to clipboard without sending.")
    copy_parser.add_argument("--from-action", required=True)
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    if parsed.command == "save-draft":
        report = execute_message_handoff_action(
            broker,
            ActionCenter(
                audit_logger=broker.audit_logger,
                session_id=broker.session_id,
                model=broker.model,
                route="messages_actions",
            ),
            action_id=parsed.from_action,
            expected_action_type=MESSAGE_SAVE_DRAFT_ACTION,
        )
        if debug and report.get("debug"):
            from agent.core.orchestrator import format_debug_payload

            print("[debug] " + format_debug_payload({"event": "messages_handoff", **dict(report["debug"])}), file=sys.stderr)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report.get("status") == "ok" else 2
    if parsed.command == "copy-draft":
        report = execute_message_handoff_action(
            broker,
            ActionCenter(
                audit_logger=broker.audit_logger,
                session_id=broker.session_id,
                model=broker.model,
                route="messages_actions",
            ),
            action_id=parsed.from_action,
            expected_action_type=MESSAGE_COPY_DRAFT_ACTION,
        )
        if debug and report.get("debug"):
            from agent.core.orchestrator import format_debug_payload

            print("[debug] " + format_debug_payload({"event": "messages_handoff", **dict(report["debug"])}), file=sys.stderr)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report.get("status") == "ok" else 2
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
        tool_name = "messages.draft_from_text"
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
    payload = json.loads(result.content)
    if parsed.command == "draft-from-text" and result.allowed:
        try:
            actions = draft_message_handoff_actions(
                ActionCenter(
                    audit_logger=broker.audit_logger,
                    session_id=broker.session_id,
                    model=broker.model,
                    route="messages_actions",
                ),
                to=str(payload.get("to") or parsed.to),
                draft=str(payload.get("draft") or ""),
                source_thread_id=str(payload.get("thread_id") or ""),
                save_path=parsed.save_path,
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        payload["handoff_actions"] = {name: record.to_dict() for name, record in actions.items()}
        payload["handoff_instructions"] = [
            "Review and approve either the save or copy action in Action Center.",
            "Use messages save-draft --from-action <action_id> or messages copy-draft --from-action <action_id>.",
            "No automatic message sending is implemented in v1.",
        ]
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if result.allowed else 2


def _run_tasks_command(argv: list[str], broker: ToolBroker, *, debug: bool = False) -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py tasks", description="Selected-scope tasks/reminders.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    list_parser = subparsers.add_parser("list", help="List selected-scope tasks/reminders after approval.")
    list_parser.add_argument("--selected-scope-token", default=None)
    list_parser.add_argument("--max-results", type=int, default=None)

    draft_create = subparsers.add_parser("draft-create", help="Draft a task create action in Action Center.")
    draft_create.add_argument("task", nargs="+")
    draft_create.add_argument("--due", default="")
    draft_create.add_argument("--list", dest="list_name", default="")
    draft_create.add_argument("--notes", default="")
    draft_create.add_argument("--allow-notes", action="store_true")
    draft_create.add_argument(
        "--source-workflow",
        choices=["manual", "daily_briefing", "meeting_prep", "email_triage", "task_extraction"],
        default="manual",
    )

    extract_parser = subparsers.add_parser("extract", help="Extract candidate tasks from approved sources into Action Center drafts.")
    source_group = extract_parser.add_mutually_exclusive_group(required=False)
    source_group.add_argument("--from-notes", dest="from_notes", help="Workspace-bounded notes file.")
    source_group.add_argument("--from-email-thread", dest="from_email_thread", help="Selected email thread id; approval required.")
    source_group.add_argument("--from-meeting", dest="from_meeting", help="Selected calendar event id; approval required.")
    source_group.add_argument("--from-url", dest="from_url", help="Selected URL or web page to fetch through web.fetch_url.")
    source_group.add_argument("--from-capture", dest="from_capture", help="Workspace capture file to read through filesystem.read.")
    extract_parser.add_argument("--dry-run", action="store_true", help="Preview source reads and action drafts without reading sources or queuing actions.")
    extract_parser.add_argument("--json", action="store_true", help="Print structured extraction payload.")

    create_parser = subparsers.add_parser("create", help="Execute an approved task create action once.")
    create_parser.add_argument("--from-action", required=True)

    complete_parser = subparsers.add_parser("complete", help="Complete a selected task/reminder after approval.")
    complete_parser.add_argument("task_id")

    update_parser = subparsers.add_parser("update", help="Update a selected task/reminder after approval.")
    update_parser.add_argument("task_id")
    update_parser.add_argument("--title")
    update_parser.add_argument("--due")
    update_parser.add_argument("--list", dest="list_name")
    update_parser.add_argument("--notes", default="")
    update_parser.add_argument("--allow-notes", action="store_true")

    delete_parser = subparsers.add_parser("delete", help="Delete a selected task/reminder after approval.")
    delete_parser.add_argument("task_id")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    if parsed.command == "extract":
        center = ActionCenter(
            audit_logger=broker.audit_logger,
            session_id=broker.session_id,
            model=broker.model,
            route="task_extraction_actions",
        )
        try:
            payload = extract_personal_tasks(
                broker,
                notes_file=parsed.from_notes,
                email_thread_id=parsed.from_email_thread,
                meeting_event_id=parsed.from_meeting,
                url=parsed.from_url,
                capture_file=parsed.from_capture,
                dry_run=bool(parsed.dry_run),
                action_center=center,
            )
        except AuditLogError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        if debug:
            print(
                "[debug] "
                f"task extraction dry_run={payload.get('dry_run')} "
                "writes_or_sends=false memory_writes=false",
                file=sys.stderr,
            )
        if parsed.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(str(payload.get("briefing", "Task extraction unavailable")))
        return 0 if payload.get("status") in {"ok", "limited", "dry_run"} else 2
    if parsed.command == "draft-create":
        tool_call = {
            "id": "cli_tasks_draft_create",
            "type": "function",
            "function": {
                "name": "tasks.draft_create",
                "arguments": json.dumps(
                    {
                        "title": " ".join(parsed.task),
                        "due": parsed.due,
                        "notes": parsed.notes,
                        "list_name": parsed.list_name,
                        "source_workflow": parsed.source_workflow,
                        "allow_notes": bool(parsed.allow_notes),
                    }
                ),
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
    if parsed.command == "create":
        center = ActionCenter(
            audit_logger=broker.audit_logger,
            session_id=broker.session_id,
            model=broker.model,
            route="tasks_actions",
        )
        report = execute_task_action(broker, center, action_id=parsed.from_action, expected_action_type=TASK_CREATE_ACTION)
        if debug and report.get("debug"):
            from agent.core.orchestrator import format_debug_payload

            print("[debug] " + format_debug_payload({"event": "tasks_action", **dict(report["debug"])}), file=sys.stderr)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report.get("status") == "ok" else 2
    if parsed.command == "list":
        tool_name = "tasks.list"
        arguments: dict[str, object] = {}
        if parsed.selected_scope_token:
            arguments["selected_scope_token"] = parsed.selected_scope_token
        if parsed.max_results is not None:
            arguments["max_results"] = parsed.max_results
    elif parsed.command == "complete":
        tool_name = "tasks.complete"
        arguments = {"task_id": parsed.task_id}
    elif parsed.command == "delete":
        tool_name = "tasks.delete"
        arguments = {"task_id": parsed.task_id}
    else:
        tool_name = "tasks.update"
        changes = _task_update_changes(parsed)
        if not changes:
            parser.error("tasks update requires at least one changed field")
        arguments = {"task_id": parsed.task_id, "changes": changes}
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


def _task_update_changes(parsed: argparse.Namespace) -> dict[str, object]:
    changes: dict[str, object] = {}
    for field in ("title", "due", "list_name"):
        value = getattr(parsed, field, None)
        if value is not None:
            changes[field] = value
    if parsed.allow_notes and parsed.notes:
        changes["notes"] = parsed.notes
    elif parsed.notes:
        changes["notes_omitted"] = True
    return changes


def _run_improve_command(argv: list[str], broker: ToolBroker, *, debug: bool = False) -> int:
    parser = argparse.ArgumentParser(
        prog="smart_agent.py improve",
        description="Controlled self-improvement backlog and implementation commands.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("backlog", "Inspect approved project files and produce a ranked improvement backlog."),
        ("propose", "Inspect approved project files and return the top safe improvement proposal."),
    ):
        command_parser = subparsers.add_parser(name, help=help_text)
        command_parser.add_argument("--dry-run", action="store_true", help="Evaluate planned file reads without reading files.")
        command_parser.add_argument("--json", action="store_true", help="Print the structured payload.")
        command_parser.add_argument("--max-bytes", type=int, default=250_000, help="Maximum bytes to read per approved file.")
    implement_parser = subparsers.add_parser("implement", help="Implement an approved proposal on a codex/ branch.")
    implement_parser.add_argument("proposal_id")
    implement_parser.add_argument("--proposals-path", default=None, help="Approved proposal JSON store.")
    implement_parser.add_argument("--json", action="store_true", help="Print the structured payload.")
    run_tests_parser = subparsers.add_parser("run-tests", help="Run brokered self-improvement tests.")
    run_tests_parser.add_argument("--test-path", default="tests")
    run_tests_parser.add_argument("--timeout", type=int, default=120)
    run_tests_parser.add_argument("--json", action="store_true")
    diff_parser = subparsers.add_parser("show-diff", help="Show brokered git diff for the current implementation.")
    diff_parser.add_argument("--max-chars", type=int, default=50_000)
    diff_parser.add_argument("--json", action="store_true")
    overnight_parser = subparsers.add_parser("overnight-plan", help="Build a safe overnight self-improvement candidate plan.")
    overnight_parser.add_argument("--max-items", type=int, default=8)
    overnight_parser.add_argument("--json", action="store_true")
    create_action_parser = subparsers.add_parser(
        "create-action-for-commit",
        help="Run brokered tests/diff and create a pending Action Center commit action.",
    )
    create_action_parser.add_argument("--message", default="Self-improvement changes")
    create_action_parser.add_argument("--test-path", default="tests/test_self_improvement.py")
    create_action_parser.add_argument("--timeout", type=int, default=120)
    create_action_parser.add_argument("--max-diff-chars", type=int, default=50_000)
    create_action_parser.add_argument("--json", action="store_true")
    commit_parser = subparsers.add_parser("commit", help="Execute an approved self-improvement commit action.")
    commit_parser.add_argument("--from-action", required=True)
    commit_parser.add_argument("--json", action="store_true")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    if parsed.command == "implement":
        center = ActionCenter(
            audit_logger=broker.audit_logger,
            session_id=broker.session_id,
            model=broker.model,
            route="self_improvement_actions",
        )
        try:
            payload = implement_approved_proposal(
                broker,
                center,
                proposal_id=parsed.proposal_id,
                proposals_path=parsed.proposals_path,
            )
        except ToolError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        if debug:
            print(
                "[debug] "
                f"improve implement proposal_id={parsed.proposal_id} status={payload.get('status')} "
                "commit_created=true commit_executed=false",
                file=sys.stderr,
            )
        if parsed.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(_format_improvement_implementation(payload))
        return 0 if payload.get("status") == "ok" else 2
    if parsed.command == "run-tests":
        payload = run_self_improvement_tests(broker, test_path=parsed.test_path, timeout_seconds=parsed.timeout)
        if parsed.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(payload.get("content", {}).get("stdout", ""))
            stderr = payload.get("content", {}).get("stderr", "")
            if stderr:
                print(stderr, file=sys.stderr)
        return 0 if payload.get("allowed") and payload.get("content", {}).get("returncode") == 0 else 2
    if parsed.command == "show-diff":
        payload = show_self_improvement_diff(broker, max_chars=parsed.max_chars)
        if parsed.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(payload.get("content", {}).get("stdout", ""))
        return 0 if payload.get("allowed") else 2
    if parsed.command == "overnight-plan":
        payload = build_overnight_plan(broker, max_items=parsed.max_items)
        if debug:
            print(
                "[debug] "
                f"improve overnight-plan status={payload.get('status')} "
                f"candidates={len(payload.get('candidates', []))} "
                "plan_only=true personal_data=false commits=false",
                file=sys.stderr,
            )
        if parsed.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(_format_overnight_plan(payload))
        return 0 if payload.get("status") == "ok" else 2
    if parsed.command == "create-action-for-commit":
        center = ActionCenter(
            audit_logger=broker.audit_logger,
            session_id=broker.session_id,
            model=broker.model,
            route="self_improvement_actions",
        )
        try:
            payload = create_self_improvement_commit_action(
                broker,
                center,
                message=parsed.message,
                test_path=parsed.test_path,
                timeout_seconds=parsed.timeout,
                max_diff_chars=parsed.max_diff_chars,
            )
        except ToolError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        if debug:
            print(
                "[debug] "
                f"improve create-action-for-commit status={payload.get('status')} "
                f"action_created={payload.get('action_created')} commit_executed=false",
                file=sys.stderr,
            )
        if parsed.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(_format_improvement_commit_action(payload))
        return 0 if payload.get("status") == "ok" else 2
    if parsed.command == "commit":
        center = ActionCenter(
            audit_logger=broker.audit_logger,
            session_id=broker.session_id,
            model=broker.model,
            route="self_improvement_actions",
        )
        payload = execute_self_improvement_commit(broker, center, action_id=parsed.from_action)
        if parsed.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if payload.get("committed") is True else 2
    payload = self_improvement_backlog(
        broker,
        mode=parsed.command,
        dry_run=bool(parsed.dry_run),
        max_bytes_per_file=parsed.max_bytes,
    )
    if debug:
        print(
            "[debug] "
            f"improve mode={parsed.command} dry_run={payload.get('dry_run')} "
            f"files_inspected={len(payload.get('files_inspected', []))} "
            "edits=false commits=false personal_data=false",
            file=sys.stderr,
        )
    if parsed.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(_format_improvement_backlog(payload))
    return 0 if payload.get("status") in {"ok", "dry_run"} else 2


def _format_improvement_commit_action(payload: dict[str, object]) -> str:
    lines = [f"Self-improvement commit action ({payload.get('status')})"]
    if payload.get("status") != "ok":
        lines.append(str(payload.get("error", "commit action was not created")))
        return "\n".join(lines)
    commit_action = payload.get("commit_action")
    if isinstance(commit_action, dict):
        lines.append(f"Action: {commit_action.get('action_id')} ({commit_action.get('status')})")
        preview = commit_action.get("preview")
        if isinstance(preview, dict):
            diff_summary = preview.get("diff_summary")
            if isinstance(diff_summary, dict):
                lines.append(
                    "Diff: "
                    f"{diff_summary.get('files_changed_count', 0)} files, "
                    f"+{diff_summary.get('lines_added', 0)}/-{diff_summary.get('lines_removed', 0)}"
                )
        lines.append("Approve it in Action Center, then run improve commit --from-action <action_id>.")
    return "\n".join(lines)


def _format_improvement_implementation(payload: dict[str, object]) -> str:
    lines = [
        f"Self-improvement implement ({payload.get('status')})",
        f"Proposal: {payload.get('proposal_id')}",
        f"Branch: {payload.get('branch')}",
        "",
        "Files written:",
    ]
    files = payload.get("files_written")
    if isinstance(files, list) and files:
        lines.extend(f"- {item}" for item in files)
    else:
        lines.append("- none")
    commit_action = payload.get("commit_action")
    if isinstance(commit_action, dict):
        lines.extend(["", f"Commit action: {commit_action.get('action_id')} ({commit_action.get('status')})"])
        lines.append("Approve it in Action Center, then run improve commit --from-action <action_id>.")
    return "\n".join(str(line) for line in lines)


def _format_overnight_plan(payload: dict[str, object]) -> str:
    lines = [
        f"Overnight self-improvement plan ({payload.get('status')})",
        "Mode: plan only, safe-mode, no execution",
        f"Sources read: {', '.join(str(path) for path in payload.get('source_files', []))}",
        "",
        "Recommended candidates:",
    ]
    candidates = payload.get("candidates", [])
    if isinstance(candidates, list) and candidates:
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            lines.extend(
                [
                    f"{candidate.get('rank')}. {candidate.get('title')} [{candidate.get('risk_level')}]",
                    f"   Category: {candidate.get('category')}",
                    f"   Why: {candidate.get('why')}",
                    f"   Tests: {', '.join(str(item) for item in candidate.get('tests_needed', []))}",
                    "",
                ]
            )
    else:
        lines.append("- none")
    lines.append("Stop if approval, personal data, package installs, policy changes, or unclear requirements appear.")
    return "\n".join(lines).rstrip()


def _format_improvement_backlog(payload: dict[str, object]) -> str:
    lines = [
        f"Self-improvement {payload.get('mode', 'backlog')} ({payload.get('status')})",
        f"Read-only: {payload.get('read_only')} | dry_run: {payload.get('dry_run')}",
        f"Files inspected: {len(payload.get('files_inspected', []))}",
    ]
    failures = payload.get("read_failures", [])
    if isinstance(failures, list) and failures:
        lines.append(f"Read limitations: {len(failures)} approved files were unavailable or denied.")
    proposal = payload.get("proposal")
    improvements = [proposal] if isinstance(proposal, dict) else payload.get("improvements", [])
    if not isinstance(improvements, list):
        improvements = []
    lines.append("")
    lines.append("Ranked improvements:")
    for item in improvements:
        if not isinstance(item, dict):
            continue
        lines.extend(
            [
                f"{item.get('rank')}. {item.get('title')} [{item.get('risk_level')}]",
                f"   Why: {item.get('why')}",
                f"   Expected files: {', '.join(str(path) for path in item.get('expected_files', []))}",
                f"   Tests: {', '.join(str(test) for test in item.get('tests_needed', []))}",
                f"   Rollback: {item.get('rollback_plan')}",
                f"   Approval: {item.get('approval_requirements')}",
                "",
            ]
        )
    blocked = payload.get("blocked_suggestions", [])
    if isinstance(blocked, list) and blocked:
        lines.append("Blocked safety-weakening suggestions:")
        for item in blocked:
            if isinstance(item, dict):
                lines.append(f"- {item.get('title')}: {item.get('reason')}")
    return "\n".join(lines).rstrip()


def _print_debug_events(result: OrchestratorResult) -> None:
    from agent.core.orchestrator import format_debug_payload

    for event in result.debug_events:
        print("[debug] " + format_debug_payload(event), file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
