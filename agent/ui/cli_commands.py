from __future__ import annotations

import json
import sys
import argparse
from pathlib import Path

from agent.config.loader import load_capabilities_config
from agent.config.runtime import RuntimeConfig, RuntimeConfigError
from agent.core.router import Router
from agent.core.tool_broker import ToolBroker
from agent.dogfood.runner import run_suite as run_dogfood_suite
from agent.dogfood.planner import build_dogfood_plan, dogfood_checklist, dogfood_next
from agent.dogfood.suites import list_suite_summaries, load_all_suites, load_suite
from agent.prompts.pack_models import PromptPackError
from agent.prompts.prompt_store import import_prompt_pack, validate_pack_file
from agent.prompts.evidence import audit_prompt_evidence
from agent.prompts.recovery import (
    missed_prompts as recovery_missed_prompts,
    reconcile as recovery_reconcile,
    recover_plan as recovery_plan,
    stale_prompts as recovery_stale_prompts,
    superseded_prompts as recovery_superseded_prompts,
)
from agent.promptops.state import update_prompt_state
from agent.promptops.clipboard import ClipboardUnavailable
from agent.promptops.runner import autopilot as promptops_autopilot
from agent.promptops.runner import run_next as promptops_run_next
from agent.promptops.workbench import (
    audit as promptops_audit,
    copy_next as promptops_copy_next,
    format_json as promptops_format_json,
    format_readable_next,
    import_from_clipboard as promptops_import_from_clipboard,
    import_from_file as promptops_import_from_file,
    import_from_stdin as promptops_import_from_stdin,
    mark_active as promptops_mark_active,
    mark_complete as promptops_mark_complete,
    mark_failed as promptops_mark_failed,
    next_work as promptops_next,
    resume as promptops_resume,
    review as promptops_review,
    show_next as promptops_show_next,
    status as promptops_status,
)
from agent.runtime.errors import RuntimeErrorBase
from agent.runtime.kernel import RuntimeKernel
from agent.runtime.scheduler import SchedulerPolicy
from agent.session_logs.feedback import FeedbackManager, VALID_FEEDBACK_TAGS, bug_feedback, make_feedback
from agent.session_logs.recorder import SessionRecorder
from agent.session_logs.review import SessionReviewer
from agent.safety.actions import ActionCenter, ActionCenterStore
from agent.safety.approvals import ApprovalManager
from agent.safety.approvals import ApprovalStatus, ApprovalStore
from agent.safety.audit import AuditLogError, AuditLogger
from agent.safety.policy import PolicyEngine
from agent.safety.validation import validate_startup_policy
from agent.tools.registry import default_registry
from agent.ui.approvals_ui import print_request, print_requests
from agent.ui.audit_viewer import tail_audit
from agent.ui.command_registry import (
    deprecated_commands,
    format_command_detail,
    format_command_list,
    get_command,
    legacy_commands,
    list_commands,
    qa_plan,
    qa_run,
    search_commands,
    validate_command_registry_docs,
)
from agent.ui.config_viewer import config_as_json
from agent.ui.connectors import connector_status, connectors_doctor, format_connectors_json, list_connectors
from agent.ui.dashboard import build_dashboard, format_dashboard, format_dashboard_json
from agent.ui.doctor import doctor_exit_code, format_doctor, run_doctor
from agent.ui.evals import EvalOptions, eval_exit_code, format_eval_json, format_eval_list_json, format_eval_summary, read_eval_report, run_eval
from agent.ui.model_quality import (
    format_quality_json,
    format_quality_summary,
    list_models,
    read_prompt_quality_report,
    run_model_benchmark,
    run_prompt_eval,
    run_router_eval,
)
from agent.ui.permissions_dashboard import PermissionStore
from agent.ui.preflight import PreflightOptions, format_preflight, run_preflight
from agent.ui.product_quality import (
    build_quality_dashboard as build_product_quality_dashboard,
    format_quality_dashboard as format_product_quality_dashboard,
    format_quality_json as format_product_quality_json,
    quality_bugs,
    quality_features,
    quality_next,
    quality_regressions,
    quality_sessions,
    quality_status,
)
from agent.ui.prompts import (
    add_prompt_record,
    audit_prompts,
    format_prompt_record,
    format_prompt_records,
    list_prompt_records,
    mark_prompt,
    missing_prompts,
    next_prompt,
    search_prompt_records,
    show_prompt,
)
from agent.ui.smoke import SmokeOptions, format_smoke, run_smoke, smoke_exit_code
from agent.connectors.secret_doctor import (
    gmail_doctor,
    gmail_scopes,
    secrets_doctor,
    secrets_status,
    telegram_doctor,
    telegram_status,
)
from agent.workflows.scheduler import (
    create_schedule,
    delete_schedule,
    list_schedules,
    pause_schedule,
    run_schedule,
)


def dispatch_cli(argv: list[str], *, project_root: str | Path = ".") -> int | None:
    if not argv:
        return None
    command = argv[0]
    if command == "tools" and len(argv) >= 2 and argv[1] == "list":
        for schema in default_registry(project_root=project_root).schemas():
            print(schema["function"]["name"])
        return 0
    if command in {"dashboard", "status"}:
        return _dashboard(argv[1:], project_root=project_root)
    if command == "permissions":
        return _permissions(argv[1:])
    if command == "approvals":
        return _approvals(argv[1:])
    if command == "actions":
        return _actions(argv[1:])
    if command == "audit" and len(argv) >= 2 and argv[1] == "tail":
        limit = int(argv[2]) if len(argv) > 2 else 20
        print(json.dumps(tail_audit(limit=limit), indent=2, sort_keys=True))
        return 0
    if command == "memory":
        return None
    if command == "config":
        return _config(argv[1:])
    if command == "connectors":
        return _connectors(argv[1:])
    if command == "secrets":
        return _secrets(argv[1:], project_root=project_root)
    if command == "gmail":
        return _gmail(argv[1:], project_root=project_root)
    if command == "telegram":
        return _telegram(argv[1:])
    if command == "reddit":
        return _reddit(argv[1:], project_root=project_root)
    if command == "v2ex":
        return _v2ex(argv[1:], project_root=project_root)
    if command == "forums":
        return _forums(argv[1:], project_root=project_root)
    if command == "cn-forums":
        return _cn_forums(argv[1:], project_root=project_root)
    if command == "language":
        return _language(argv[1:], project_root=project_root)
    if command == "platform":
        return _platform(argv[1:], project_root=project_root)
    if command == "setup":
        print("Set LMSTUDIO_MODEL, start LM Studio at http://localhost:1234/v1, then run tests.")
        return 0
    if command == "doctor":
        checks = run_doctor()
        print(format_doctor(checks))
        return doctor_exit_code(checks)
    if command == "preflight":
        return _preflight(argv[1:], project_root=project_root)
    if command == "smoke":
        return _smoke(argv[1:])
    if command == "eval":
        return _eval(argv[1:])
    if command == "models":
        return _models(argv[1:])
    if command == "router":
        return _router(argv[1:])
    if command == "prompts":
        return _prompts(argv[1:], project_root=project_root)
    if command == "work":
        return _work(argv[1:], project_root=project_root)
    if command == "session":
        return _session(argv[1:], project_root=project_root)
    if command == "bugs":
        return _bugs(argv[1:], project_root=project_root)
    if command == "feedback":
        return _feedback(argv[1:], project_root=project_root)
    if command == "dogfood":
        return _dogfood(argv[1:], project_root=project_root)
    if command == "quality":
        return _quality(argv[1:], project_root=project_root)
    if command == "commands":
        return _commands(argv[1:], project_root=project_root)
    if command == "runtime":
        return _runtime(argv[1:])
    if command == "jobs":
        return _runtime_jobs(argv[1:])
    if command == "workflows":
        return _runtime_workflows(argv[1:])
    if command == "events":
        return _runtime_events(argv[1:])
    if command == "schedule":
        return _schedule(argv[1:], project_root=project_root)
    if command == "backup":
        return _backup(argv[1:], project_root=project_root)
    return None


def _platform(argv: list[str], *, project_root: str | Path = ".") -> int:
    parser = argparse.ArgumentParser(
        prog="smart_agent.py platform",
        description="Read-only platform status and capability inspection.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("doctor", help="Show platform detection, bridge readiness, config, warnings, and setup steps.")
    subparsers.add_parser("status", help="Show short platform and bridge status metadata.")
    subparsers.add_parser("capabilities", help="List platform capability metadata.")
    subparsers.add_parser("matrix", help="Show macOS, iOS companion, Windows, and app/web bridge capability matrix.")
    explain_parser = subparsers.add_parser("explain", help="Explain one platform capability.")
    explain_parser.add_argument("capability_id")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    tool_name = f"platform.{parsed.command}"
    arguments: dict[str, object] = {}
    if parsed.command == "explain":
        arguments["capability_id"] = parsed.capability_id

    try:
        payload = _execute_local_tool(
            _local_broker(project_root=project_root, route="platform-cli"),
            f"cli_{tool_name.replace('.', '_')}",
            tool_name,
            arguments,
        )
    except (RuntimeConfigError, AuditLogError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(payload["content"], indent=2, sort_keys=True))
    return 0 if payload.get("allowed") else 2


def _runtime(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py runtime", description="Inspect the lightweight runtime control plane.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status", help="Show runtime status without model/tool/personal-data calls.")
    subparsers.add_parser("doctor", help="Run runtime orchestration checks without LM Studio calls.")
    subparsers.add_parser("services", help="List registered runtime services.")
    subparsers.add_parser("features", help="List runtime feature flags.")
    subparsers.add_parser("health", help="Show runtime health checks.")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    kernel = RuntimeKernel()
    if parsed.command == "status":
        payload = kernel.status()
    elif parsed.command == "doctor":
        health = kernel.health()
        payload = {
            "status": health.status.value,
            "checks": list(health.checks),
            "lmstudio_checked": False,
            "tool_execution": False,
            "personal_data_accessed": False,
            "background_persistence": False,
        }
    elif parsed.command == "services":
        kernel.boot()
        payload = {"services": [service.to_dict() for service in kernel.services.list_services()]}
    elif parsed.command == "features":
        kernel.boot()
        payload = {"features": [feature.to_dict() for feature in kernel.features.list_features()]}
    else:
        payload = kernel.health().to_dict()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _runtime_jobs(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py jobs", description="Inspect runtime job metadata.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List in-process runtime jobs.")
    show_parser = subparsers.add_parser("show", help="Show one in-process runtime job.")
    show_parser.add_argument("job_id")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    kernel = RuntimeKernel()
    kernel.boot()
    if parsed.command == "list":
        print(json.dumps({"jobs": [job.to_dict() for job in kernel.jobs.list_jobs()]}, indent=2, sort_keys=True))
        return 0
    try:
        job = kernel.jobs.get(parsed.job_id)
    except RuntimeErrorBase as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(job.to_dict(), indent=2, sort_keys=True))
    return 0


def _runtime_workflows(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py workflows", description="Inspect or queue runtime workflow metadata.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List registered workflows.")
    run_parser = subparsers.add_parser("run", help="Create a metadata job for a safe workflow; no tools execute.")
    run_parser.add_argument("workflow_id")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    kernel = RuntimeKernel()
    kernel.boot()
    if parsed.command == "list":
        print(json.dumps({"workflows": [workflow.to_dict() for workflow in kernel.workflows.list_workflows()]}, indent=2, sort_keys=True))
        return 0
    try:
        job = kernel.workflows.start(parsed.workflow_id)
    except RuntimeErrorBase as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}, indent=2, sort_keys=True))
        return 2
    print(json.dumps({"status": job.status.value, "job": job.to_dict(), "tool_execution": False}, indent=2, sort_keys=True))
    return 0 if job.status.value == "queued" else 2


def _runtime_events(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py events", description="Inspect in-process runtime events.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    tail_parser = subparsers.add_parser("tail", help="Tail current process runtime events.")
    tail_parser.add_argument("--limit", type=int, default=20)
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    kernel = RuntimeKernel()
    kernel.boot()
    print(json.dumps({"events": [event.to_dict() for event in kernel.events.tail(parsed.limit)]}, indent=2, sort_keys=True))
    return 0


def _dashboard(argv: list[str], *, project_root: str | Path = ".") -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py dashboard", description="Show read-only agent dashboard.")
    parser.add_argument("--json", action="store_true", help="Print structured dashboard JSON.")
    parser.add_argument("--audit-limit", type=int, default=10, help="Recent audit events to include, 1-50.")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    report = build_dashboard(project_root=project_root, audit_limit=parsed.audit_limit)
    print(format_dashboard_json(report) if parsed.json else format_dashboard(report))
    return 0


def _connectors(argv: list[str]) -> int:
    if not argv or argv[0] == "list":
        print(format_connectors_json({"connectors": list_connectors()}))
        return 0
    if argv[0] == "doctor":
        print(format_connectors_json(connectors_doctor()))
        return 0
    if argv[0] == "status" and len(argv) == 2:
        try:
            print(format_connectors_json(connector_status(argv[1])))
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    print("usage: connectors list|doctor|status <connector>", file=sys.stderr)
    return 2


def _secrets(argv: list[str], *, project_root: str | Path = ".") -> int:
    if not argv or argv[0] == "doctor":
        print(json.dumps(secrets_doctor(project_root=project_root), indent=2, sort_keys=True))
        return 0
    if argv[0] == "status":
        print(json.dumps(secrets_status(project_root=project_root), indent=2, sort_keys=True))
        return 0
    print("usage: secrets doctor|status", file=sys.stderr)
    return 2


def _gmail(argv: list[str], *, project_root: str | Path = ".") -> int:
    if not argv or argv[0] == "doctor":
        print(json.dumps(gmail_doctor(project_root=project_root), indent=2, sort_keys=True))
        return 0
    if argv[0] == "scopes":
        print(json.dumps(gmail_scopes(), indent=2, sort_keys=True))
        return 0
    print("usage: gmail doctor|scopes", file=sys.stderr)
    return 2


def _telegram(argv: list[str]) -> int:
    if not argv or argv[0] == "doctor":
        print(json.dumps(telegram_doctor(), indent=2, sort_keys=True))
        return 0
    if argv[0] == "status":
        print(json.dumps(telegram_status(), indent=2, sort_keys=True))
        return 0
    print("usage: telegram doctor|status", file=sys.stderr)
    return 2


def _reddit(argv: list[str], *, project_root: str | Path = ".") -> int:
    if not argv or argv[0] == "doctor":
        tool_name = "reddit.status"
        arguments: dict[str, object] = {"detail": "doctor"}
    elif argv[0] == "status":
        tool_name = "reddit.status"
        arguments = {"detail": "status"}
    elif argv[0] == "auth-check":
        tool_name = "reddit.auth_check"
        arguments = {}
    elif argv[0] == "search" and len(argv) >= 2:
        parser = argparse.ArgumentParser(prog="reddit search")
        parser.add_argument("query")
        parser.add_argument("--subreddit", default="")
        parser.add_argument("--limit", type=int, default=10)
        parser.add_argument("--sort", default="relevance", choices=["relevance", "hot", "top", "new", "comments"])
        parser.add_argument("--time", dest="time_filter", default="all", choices=["hour", "day", "week", "month", "year", "all"])
        parser.add_argument("--language", default="auto", choices=["auto", "en", "es", "zh", "ja", "ko"])
        try:
            ns = parser.parse_args(argv[1:])
        except SystemExit:
            return 2
        tool_name = "reddit.search_posts"
        arguments = {
            "query": ns.query,
            "subreddit": ns.subreddit,
            "limit": ns.limit,
            "sort": ns.sort,
            "time_filter": ns.time_filter,
            "language": ns.language,
        }
    elif argv[0] == "explain-result" and len(argv) == 2:
        tool_name = "reddit.explain_result"
        arguments = {"source_id": argv[1]}
    elif argv[0] == "subreddit" and len(argv) == 2:
        tool_name = "reddit.fetch_subreddit_info"
        arguments = {"subreddit": argv[1]}
    elif argv[0] == "post" and len(argv) == 2:
        tool_name = "reddit.fetch_post"
        arguments = {"post_id_or_url": argv[1]}
    elif argv[0] == "comments" and len(argv) >= 2:
        parser = argparse.ArgumentParser(prog="reddit comments")
        parser.add_argument("post_id_or_url")
        parser.add_argument("--limit", type=int, default=100)
        parser.add_argument("--sort", default="confidence", choices=["confidence", "top", "new", "controversial", "old", "qa"])
        try:
            ns = parser.parse_args(argv[1:])
        except SystemExit:
            return 2
        tool_name = "reddit.fetch_comments"
        arguments = {"post_id_or_url": ns.post_id_or_url, "limit": ns.limit, "sort": ns.sort}
    elif argv[0] == "thread" and len(argv) >= 2:
        parser = argparse.ArgumentParser(prog="reddit thread")
        parser.add_argument("post_id_or_url")
        parser.add_argument("--max-comments", type=int, default=100)
        parser.add_argument("--sort", default="top", choices=["top", "new", "controversial"])
        parser.add_argument("--collapse-depth", type=int, default=3)
        try:
            ns = parser.parse_args(argv[1:])
        except SystemExit:
            return 2
        tool_name = "reddit.fetch_thread"
        arguments = {
            "post_id_or_url": ns.post_id_or_url,
            "max_comments": ns.max_comments,
            "sort": ns.sort,
            "collapse_depth": ns.collapse_depth,
        }
    elif argv[0] == "thread-export" and len(argv) >= 2:
        parser = argparse.ArgumentParser(prog="reddit thread-export")
        parser.add_argument("post_id_or_url")
        parser.add_argument("--format", default="json", choices=["json", "markdown"])
        parser.add_argument("--max-comments", type=int, default=100)
        parser.add_argument("--sort", default="top", choices=["top", "new", "controversial"])
        parser.add_argument("--collapse-depth", type=int, default=3)
        try:
            ns = parser.parse_args(argv[1:])
        except SystemExit:
            return 2
        tool_name = "reddit.thread_export"
        arguments = {
            "post_id_or_url": ns.post_id_or_url,
            "format": ns.format,
            "max_comments": ns.max_comments,
            "sort": ns.sort,
            "collapse_depth": ns.collapse_depth,
        }
    elif argv[0] == "summarize-thread" and len(argv) >= 2:
        parser = argparse.ArgumentParser(prog="reddit summarize-thread")
        parser.add_argument("post_id_or_url")
        parser.add_argument("--max-comments", type=int, default=100)
        parser.add_argument("--sort", default="top", choices=["top", "new", "controversial"])
        parser.add_argument("--collapse-depth", type=int, default=3)
        try:
            ns = parser.parse_args(argv[1:])
        except SystemExit:
            return 2
        tool_name = "reddit.summarize_thread"
        arguments = {
            "post_id_or_url": ns.post_id_or_url,
            "max_comments": ns.max_comments,
            "sort": ns.sort,
            "collapse_depth": ns.collapse_depth,
        }
    elif argv[0] == "summarize-search" and len(argv) >= 2:
        parser = argparse.ArgumentParser(prog="reddit summarize-search")
        parser.add_argument("query")
        parser.add_argument("--limit", type=int, default=10)
        parser.add_argument("--subreddit", default="")
        parser.add_argument("--sort", default="relevance", choices=["relevance", "hot", "top", "new", "comments"])
        parser.add_argument("--time", dest="time_filter", default="all", choices=["hour", "day", "week", "month", "year", "all"])
        parser.add_argument("--language", default="auto", choices=["auto", "en", "es", "zh", "ja", "ko"])
        try:
            ns = parser.parse_args(argv[1:])
        except SystemExit:
            return 2
        tool_name = "reddit.summarize_search"
        arguments = {
            "query": ns.query,
            "limit": ns.limit,
            "subreddit": ns.subreddit,
            "sort": ns.sort,
            "time_filter": ns.time_filter,
            "language": ns.language,
        }
    elif argv[0] in {"consensus", "pros-cons", "complaints", "buying-advice"} and len(argv) >= 2:
        command = argv[0]
        parser = argparse.ArgumentParser(prog=f"reddit {command}")
        parser.add_argument("query")
        parser.add_argument("--limit", type=int, default=10)
        try:
            ns = parser.parse_args(argv[1:])
        except SystemExit:
            return 2
        tool_name = {
            "consensus": "reddit.consensus",
            "pros-cons": "reddit.pros_cons",
            "complaints": "reddit.complaints",
            "buying-advice": "reddit.buying_advice",
        }[command]
        arguments = {"query": ns.query, "limit": ns.limit}
    elif argv[0] == "cache" and len(argv) == 2 and argv[1] in {"status", "clear"}:
        tool_name = {"status": "reddit.cache_status", "clear": "reddit.cache_clear"}[argv[1]]
        arguments = {}
    elif argv[0] == "retention" and len(argv) == 2 and argv[1] in {"status", "sweep"}:
        tool_name = {"status": "reddit.retention_status", "sweep": "reddit.retention_sweep"}[argv[1]]
        arguments = {}
    elif argv[0] == "privacy-report" and len(argv) == 1:
        tool_name = "reddit.privacy_report"
        arguments = {}
    else:
        print(
            "usage: reddit doctor|status|auth-check|search <query>|explain-result <source_id>|subreddit <name>|post <id_or_url>|comments <id_or_url>|thread <id_or_url>|thread-export <id_or_url>|summarize-thread <id_or_url>|summarize-search <query>|consensus <query>|pros-cons <query>|complaints <topic>|buying-advice <topic>|cache status|cache clear|retention status|retention sweep|privacy-report",
            file=sys.stderr,
        )
        return 2
    try:
        broker = _local_broker(project_root=project_root, route="cli:reddit")
        payload = _execute_local_tool(broker, f"cli_{tool_name.replace('.', '_')}", tool_name, arguments)
    except (RuntimeConfigError, AuditLogError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(payload["content"], indent=2, sort_keys=True))
    return 0 if payload.get("allowed") else 2


def _v2ex(argv: list[str], *, project_root: str | Path = ".") -> int:
    if not argv or argv[0] == "doctor":
        tool_name = "v2ex.status"
        arguments: dict[str, object] = {"detail": "doctor"}
    elif argv[0] == "status":
        tool_name = "v2ex.status"
        arguments = {"detail": "status"}
    elif argv[0] == "nodes":
        parser = argparse.ArgumentParser(prog="v2ex nodes")
        parser.add_argument("--limit", type=int, default=500)
        try:
            ns = parser.parse_args(argv[1:])
        except SystemExit:
            return 2
        tool_name = "v2ex.nodes.get"
        arguments = {"limit": ns.limit}
    elif argv[0] == "node" and len(argv) >= 2:
        parser = argparse.ArgumentParser(prog="v2ex node")
        parser.add_argument("node_name")
        parser.add_argument("--limit", type=int, default=10)
        parser.add_argument("--detect-language", action="store_true")
        parser.add_argument("--translate-to", default="")
        try:
            ns = parser.parse_args(argv[1:])
        except SystemExit:
            return 2
        tool_name = "v2ex.node_topics"
        arguments = {
            "node_name": ns.node_name,
            "limit": ns.limit,
            "detect_language": ns.detect_language,
            "translate_to": ns.translate_to,
        }
    elif argv[0] == "topic" and len(argv) >= 2:
        parser = argparse.ArgumentParser(prog="v2ex topic")
        parser.add_argument("topic_id")
        parser.add_argument("--detect-language", action="store_true")
        parser.add_argument("--translate-to", default="")
        try:
            ns = parser.parse_args(argv[1:])
        except SystemExit:
            return 2
        tool_name = "v2ex.topic.get"
        arguments = {"topic_id": ns.topic_id, "detect_language": ns.detect_language, "translate_to": ns.translate_to}
    elif argv[0] == "replies" and len(argv) >= 2:
        parser = argparse.ArgumentParser(prog="v2ex replies")
        parser.add_argument("topic_id")
        parser.add_argument("--limit", type=int, default=100)
        parser.add_argument("--detect-language", action="store_true")
        parser.add_argument("--translate-to", default="")
        try:
            ns = parser.parse_args(argv[1:])
        except SystemExit:
            return 2
        tool_name = "v2ex.topic_replies"
        arguments = {
            "topic_id": ns.topic_id,
            "limit": ns.limit,
            "detect_language": ns.detect_language,
            "translate_to": ns.translate_to,
        }
    elif argv[0] in {"latest", "hot"}:
        parser = argparse.ArgumentParser(prog=f"v2ex {argv[0]}")
        parser.add_argument("--limit", type=int, default=10)
        try:
            ns = parser.parse_args(argv[1:])
        except SystemExit:
            return 2
        tool_name = {"latest": "v2ex.latest", "hot": "v2ex.hot"}[argv[0]]
        arguments = {"limit": ns.limit}
    else:
        print(
            "usage: v2ex doctor|status|nodes|node <node_name>|topic <topic_id>|replies <topic_id>|latest|hot",
            file=sys.stderr,
        )
        return 2
    try:
        broker = _local_broker(project_root=project_root, route="cli:v2ex")
        payload = _execute_local_tool(broker, f"cli_{tool_name.replace('.', '_')}", tool_name, arguments)
    except (RuntimeConfigError, AuditLogError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(payload["content"], indent=2, sort_keys=True))
    return 0 if payload.get("allowed") else 2


def _language(argv: list[str], *, project_root: str | Path = ".") -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py language", description="Detect, translate, and extract terms from untrusted multilingual text.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    detect_parser = subparsers.add_parser("detect", help="Detect language for inline text.")
    detect_parser.add_argument("--text", required=True)
    translate_parser = subparsers.add_parser("translate", help="Translate inline text with the local model by default.")
    translate_parser.add_argument("--from", dest="from_language", default="auto")
    translate_parser.add_argument("--to", dest="to_language", default="en")
    translate_parser.add_argument("--text", required=True)
    translate_file_parser = subparsers.add_parser("translate-file", help="Translate a workspace file with source references.")
    translate_file_parser.add_argument("path")
    translate_file_parser.add_argument("--from", dest="from_language", default="auto")
    translate_file_parser.add_argument("--to", dest="to_language", default="en")
    glossary_parser = subparsers.add_parser("glossary", help="Extract glossary terms from a workspace file.")
    glossary_parser.add_argument("path")
    glossary_parser.add_argument("--max-terms", type=int, default=20)
    try:
        ns = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    try:
        broker = _local_broker(project_root=project_root, route="cli:language")
        if ns.command == "detect":
            payload = _execute_local_tool(
                broker,
                "cli_language_detect",
                "language.detect",
                {"text": ns.text, "source_id": "inline", "trust_level": "UNTRUSTED_WEB"},
            )
        elif ns.command == "translate":
            payload = _execute_local_tool(
                broker,
                "cli_language_translate_text",
                "language.translate_text",
                {
                    "text": ns.text,
                    "from_language": ns.from_language,
                    "to_language": ns.to_language,
                    "source_id": "inline",
                    "trust_level": "UNTRUSTED_WEB",
                },
            )
        else:
            read_payload = _execute_local_tool(
                broker,
                f"cli_language_read_{ns.command.replace('-', '_')}",
                "filesystem.read",
                {"path": ns.path, "max_bytes": 200_000},
            )
            if not read_payload.get("allowed"):
                print(json.dumps(read_payload["content"], indent=2, sort_keys=True))
                return 2
            file_content = str(read_payload["content"].get("content", ""))
            file_trust = str(read_payload["content"].get("trust_level", "UNTRUSTED_DOCUMENT"))
            if ns.command == "translate-file":
                payload = _execute_local_tool(
                    broker,
                    "cli_language_translate_file",
                    "language.translate_text",
                    {
                        "text": file_content,
                        "from_language": ns.from_language,
                        "to_language": ns.to_language,
                        "source_id": ns.path,
                        "trust_level": file_trust,
                    },
                )
            else:
                payload = _execute_local_tool(
                    broker,
                    "cli_language_glossary",
                    "language.extract_terms",
                    {
                        "text": file_content,
                        "source_id": ns.path,
                        "trust_level": file_trust,
                        "max_terms": ns.max_terms,
                    },
                )
    except (RuntimeConfigError, AuditLogError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(payload["content"], indent=2, sort_keys=True))
    return 0 if payload.get("allowed") else 2


def _forums(argv: list[str], *, project_root: str | Path = ".") -> int:
    parser = argparse.ArgumentParser(
        prog="smart_agent.py forums",
        description="Run source-grounded multilingual forum research without scraping or paid providers by default.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("providers", help="List forum provider registry metadata without provider calls.")
    status_parser = subparsers.add_parser("status", help="Show one forum provider status without logged-in reads.")
    status_parser.add_argument("provider")
    subparsers.add_parser("doctor", help="Run read-only forum provider registry diagnostics.")
    capabilities_parser = subparsers.add_parser("capabilities", help="Show read/write capability metadata for a provider.")
    capabilities_parser.add_argument("provider")
    for command in ("research", "compare"):
        subparser = subparsers.add_parser(command, help=f"{command.title()} configured forum sources for a topic.")
        subparser.add_argument("topic")
        subparser.add_argument("--languages", default="en,zh,ja,ko")
        subparser.add_argument("--sources", default="reddit,v2ex,web")
        subparser.add_argument("--translate-to", default="en")
        subparser.add_argument("--limit-per-source", type=int, default=5)
    try:
        ns = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    if ns.command in {"research", "compare"}:
        tool_name = "forums.research" if ns.command == "research" else "forums.compare"
        arguments = {
            "topic": ns.topic,
            "languages": ns.languages,
            "sources": ns.sources,
            "translate_to": ns.translate_to,
            "limit_per_source": ns.limit_per_source,
        }
    elif ns.command == "providers":
        tool_name = "forums.providers"
        arguments = {}
    elif ns.command == "status":
        tool_name = "forums.status"
        arguments = {"provider": ns.provider}
    elif ns.command == "doctor":
        tool_name = "forums.doctor"
        arguments = {}
    else:
        tool_name = "forums.capabilities"
        arguments = {"provider": ns.provider}
    try:
        broker = _local_broker(project_root=project_root, route="cli:forums")
        payload = _execute_local_tool(broker, f"cli_{tool_name.replace('.', '_')}", tool_name, arguments)
    except (RuntimeConfigError, AuditLogError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(payload["content"], indent=2, sort_keys=True))
    return 0 if payload.get("allowed") else 2


def _cn_forums(argv: list[str], *, project_root: str | Path = ".") -> int:
    parser = argparse.ArgumentParser(
        prog="smart_agent.py cn-forums",
        description="Discover public Chinese-language forum discussions through approved search/fetch paths only.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("providers", help="List Chinese/forum discovery site filters and safety limits.")
    search_parser = subparsers.add_parser("search", help="Search approved site filters through configured web search providers.")
    search_parser.add_argument("topic")
    search_parser.add_argument("--sites", default="zhihu,v2ex,tieba")
    search_parser.add_argument("--limit", type=int, default=10)
    fetch_parser = subparsers.add_parser("fetch", help="Fetch one selected public forum URL using safe web fetch policy.")
    fetch_parser.add_argument("url")
    fetch_parser.add_argument("--translate-to", default="")
    research_parser = subparsers.add_parser("research", help="Search, fetch selected public results, and summarize with sources.")
    research_parser.add_argument("topic")
    research_parser.add_argument("--sites", default="zhihu,v2ex,tieba")
    research_parser.add_argument("--translate-to", default="en")
    research_parser.add_argument("--limit", type=int, default=5)
    try:
        ns = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    if ns.command == "providers":
        tool_name = "cn_forums.providers"
        arguments: dict[str, object] = {}
    elif ns.command == "search":
        tool_name = "cn_forums.search"
        arguments = {"topic": ns.topic, "sites": ns.sites, "limit": ns.limit}
    elif ns.command == "fetch":
        tool_name = "cn_forums.fetch"
        arguments = {"url": ns.url, "translate_to": ns.translate_to}
    else:
        tool_name = "cn_forums.research"
        arguments = {"topic": ns.topic, "sites": ns.sites, "translate_to": ns.translate_to, "limit": ns.limit}
    try:
        broker = _local_broker(project_root=project_root, route="cli:cn-forums")
        payload = _execute_local_tool(broker, f"cli_{tool_name.replace('.', '_')}", tool_name, arguments)
    except (RuntimeConfigError, AuditLogError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(payload["content"], indent=2, sort_keys=True))
    return 0 if payload.get("allowed") else 2


def _permissions(argv: list[str]) -> int:
    store = PermissionStore()
    if not argv or argv[0] == "show":
        print(json.dumps({"grants": store.show()}, indent=2))
        return 0
    if argv[0] == "grant" and len(argv) == 2:
        print(json.dumps({"grants": store.grant(argv[1])}, indent=2))
        return 0
    if argv[0] == "revoke" and len(argv) == 2:
        print(json.dumps({"grants": store.revoke(argv[1])}, indent=2))
        return 0
    print("usage: permissions show|grant <capability>|revoke <capability>", file=sys.stderr)
    return 2


def _approvals(argv: list[str]) -> int:
    store = ApprovalStore()
    if not argv or argv[0] == "list":
        print_requests(store.list())
        return 0
    if argv[0] == "show" and len(argv) == 2:
        request = store.get(argv[1])
        if request is None:
            print("approval request not found", file=sys.stderr)
            return 1
        print_request(request)
        return 0
    if argv[0] == "approve" and len(argv) == 2:
        request = store.update_status(argv[1], ApprovalStatus.APPROVED)
        if request is None:
            print("approval request not found", file=sys.stderr)
            return 1
        print(json.dumps({"request_id": request.request_id, "status": request.status.value}, indent=2))
        return 0
    if argv[0] == "deny" and len(argv) == 2:
        request = store.update_status(argv[1], ApprovalStatus.DENIED)
        if request is None:
            print("approval request not found", file=sys.stderr)
            return 1
        print(json.dumps({"request_id": request.request_id, "status": request.status.value}, indent=2))
        return 0
    print("usage: approvals list|show <request_id>|approve <request_id>|deny <request_id>", file=sys.stderr)
    return 2


def _actions(argv: list[str]) -> int:
    center = ActionCenter(
        store=ActionCenterStore(),
        approval_store=ApprovalStore(),
        audit_logger=AuditLogger(),
        route="actions_cli",
    )
    if not argv or argv[0] == "list":
        print(json.dumps({"actions": [record.to_dict() for record in center.list_actions()]}, indent=2, sort_keys=True))
        return 0
    if argv[0] == "show" and len(argv) == 2:
        record = center.get_action(argv[1])
        if record is None:
            print("action not found", file=sys.stderr)
            return 1
        print(json.dumps(record.to_dict(), indent=2, sort_keys=True))
        return 0
    if argv[0] == "approve" and len(argv) == 2:
        record = center.approve(argv[1])
        if record is None:
            print("action not found", file=sys.stderr)
            return 1
        print(json.dumps({"action_id": record.action_id, "status": record.status.value}, indent=2, sort_keys=True))
        return 0
    if argv[0] == "deny" and len(argv) == 2:
        record = center.deny(argv[1])
        if record is None:
            print("action not found", file=sys.stderr)
            return 1
        print(json.dumps({"action_id": record.action_id, "status": record.status.value}, indent=2, sort_keys=True))
        return 0
    if argv[0] == "edit" and len(argv) >= 3:
        action_id = argv[1]
        try:
            updates = _parse_action_edit_args(argv[2:])
            record = center.edit(action_id, updates)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        if record is None:
            print("action not found", file=sys.stderr)
            return 1
        print(json.dumps({"action_id": record.action_id, "status": record.status.value, "preview": record.preview}, indent=2, sort_keys=True))
        return 0
    if argv[0] == "clear-denied" and len(argv) == 1:
        print(json.dumps({"cleared": center.clear_denied()}, indent=2, sort_keys=True))
        return 0
    if argv[0] == "export" and len(argv) == 1:
        print(json.dumps(center.export(), indent=2, sort_keys=True))
        return 0
    print(
        "usage: actions list|show <action_id>|approve <action_id>|deny <action_id>|edit <action_id> key=value [key=value...]|clear-denied|export",
        file=sys.stderr,
    )
    return 2


def _parse_action_edit_args(values: list[str]) -> dict[str, object]:
    updates: dict[str, object] = {}
    for value in values:
        if value == "--set":
            continue
        if "=" not in value:
            raise ValueError("action edits must be key=value pairs")
        key, raw = value.split("=", 1)
        if not key:
            raise ValueError("action edit key cannot be empty")
        try:
            updates[key] = json.loads(raw)
        except json.JSONDecodeError:
            updates[key] = raw
    if not updates:
        raise ValueError("at least one action edit is required")
    return updates


def _config(argv: list[str]) -> int:
    if not argv or argv[0] == "show":
        print(config_as_json())
        return 0
    if argv[0] == "diff":
        current = load_capabilities_config()
        print(json.dumps({"status": "no alternate config supplied", "tools": sorted(current["tools"])}, indent=2))
        return 0
    print("usage: config show|diff", file=sys.stderr)
    return 2


def _smoke(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py smoke", description="Run controlled live smoke checks.")
    parser.add_argument("--lmstudio", action="store_true", help="Run live LM Studio checks if LMSTUDIO_MODEL is set.")
    parser.add_argument("--web", action="store_true", help="Run live web checks if web access/provider config allows it.")
    parser.add_argument("--calendar", action="store_true", help="Dry-run calendar connector checks; no personal data read.")
    parser.add_argument("--contacts", action="store_true", help="Dry-run contacts connector checks; no personal data read.")
    parser.add_argument("--all-safe", action="store_true", help="Run LM Studio/web checks plus dry-run personal connector checks.")
    parser.add_argument("--dry-run", action="store_true", help="Force tool calls into ToolBroker dry-run mode where applicable.")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    checks = run_smoke(
        SmokeOptions(
            lmstudio=parsed.lmstudio,
            web=parsed.web,
            calendar=parsed.calendar,
            contacts=parsed.contacts,
            all_safe=parsed.all_safe,
            dry_run=parsed.dry_run,
        )
    )
    print(format_smoke(checks))
    return smoke_exit_code(checks)


def _eval(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py eval", description="Run controlled live validation evals.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List available eval checks.")
    run_parser = subparsers.add_parser("run", help="Run selected eval checks.")
    run_parser.add_argument("--safe", action="store_true", help="Run all safe evals; personal-data evals remain skipped.")
    run_parser.add_argument("--lmstudio", action="store_true", help="Run live LM Studio evals if configured.")
    run_parser.add_argument("--lmstudio-live", action="store_true", help="Run opt-in live LM Studio smoke evals if configured.")
    run_parser.add_argument("--routing", action="store_true", help="Run deterministic router golden cases.")
    run_parser.add_argument("--policy", action="store_true", help="Run policy allow/ask/deny golden cases.")
    run_parser.add_argument("--tools", action="store_true", help="Run ToolBroker and audit golden cases.")
    run_parser.add_argument("--workflows", action="store_true", help="Run workflow dry-run golden cases.")
    run_parser.add_argument("--prompt-injection", action="store_true", help="Run untrusted-content prompt-injection golden cases.")
    run_parser.add_argument("--internet", action="store_true", help="Run fixture-backed internet/source-grounding evals without live provider calls.")
    run_parser.add_argument("--forums", action="store_true", help="Run fixture-backed forum intelligence evals without live provider calls.")
    run_parser.add_argument("--native-skills", action="store_true", help="Run fixture-backed native skill harness evals without external skill execution.")
    run_parser.add_argument("--web", action="store_true", help="Run web search/fetch evals if configured.")
    run_parser.add_argument("--weather", action="store_true", help="Run weather current/forecast evals if configured.")
    run_parser.add_argument("--workspace", action="store_true", help="Run workspace read/write evals in ./workspace/eval.")
    run_parser.add_argument("--memory", action="store_true", help="Run non-sensitive memory add/search/delete evals.")
    run_parser.add_argument("--prompt-tracker", action="store_true", help="Run prompt tracker queue/evidence integrity evals.")
    run_parser.add_argument("--json", action="store_true", help="Print structured JSON instead of a readable summary.")
    report_parser = subparsers.add_parser("report", help="Print the last generated eval report.")
    report_parser.add_argument("--prompt-tracker", action="store_true", help="Alias for the last eval report; kept for prompt tracker runbooks.")
    report_parser.add_argument("--internet", action="store_true", help="Alias for the last eval report; kept for internet dogfood runbooks.")
    report_parser.add_argument("--forums", action="store_true", help="Alias for the last eval report; kept for forum dogfood runbooks.")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    if parsed.command == "list":
        print(format_eval_list_json())
        return 0
    if parsed.command == "report":
        print(read_eval_report())
        return 0
    report = run_eval(
        EvalOptions(
            safe=parsed.safe,
            lmstudio=parsed.lmstudio,
            lmstudio_live=parsed.lmstudio_live,
            routing=parsed.routing,
            policy=parsed.policy,
            tools=parsed.tools,
            workflows=parsed.workflows,
            prompt_injection=parsed.prompt_injection,
            internet=parsed.internet,
            forums=parsed.forums,
            native_skills=parsed.native_skills,
            web=parsed.web,
            weather=parsed.weather,
            workspace=parsed.workspace,
            memory=parsed.memory,
            prompt_tracker=parsed.prompt_tracker,
        )
    )
    print(format_eval_json(report) if parsed.json else format_eval_summary(report))
    return eval_exit_code(report)


def _models(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py models", description="Inspect model configuration and run safe model benchmarks.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    list_parser = subparsers.add_parser("list", help="List configured model information without sending prompts.")
    list_parser.add_argument("--live", action="store_true", help="Query LM Studio /v1/models without sending prompts.")
    benchmark_parser = subparsers.add_parser("benchmark", help="Run model/router/prompt quality benchmark cases.")
    benchmark_parser.add_argument("--safe", action="store_true", help="Run safe fixture-backed benchmark cases.")
    benchmark_parser.add_argument("--live", action="store_true", help="Include opt-in live LM Studio smoke placeholders.")
    benchmark_parser.add_argument("--json", action="store_true", help="Print JSON instead of a readable summary.")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    if parsed.command == "list":
        print(json.dumps(list_models(live=parsed.live), indent=2, sort_keys=True))
        return 0
    report = run_model_benchmark(safe=parsed.safe, live=parsed.live)
    print(format_quality_json(report) if parsed.json else format_quality_summary(report))
    return 1 if report.get("status") == "fail" else 0


def _router(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py router", description="Evaluate deterministic router behavior.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    eval_parser = subparsers.add_parser("eval", help="Run router quality eval cases.")
    eval_parser.add_argument("--json", action="store_true", help="Print JSON instead of a readable summary.")
    explain_parser = subparsers.add_parser("explain", help="Explain deterministic routing for one request without executing tools.")
    explain_parser.add_argument("query", nargs=argparse.REMAINDER, help="Request text to route.")
    explain_parser.add_argument("--no-tools", action="store_true", help="Force no-tools routing for this explanation.")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    if parsed.command == "explain":
        query = " ".join(parsed.query).strip()
        if not query:
            print('usage: router explain "<query>"', file=sys.stderr)
            return 2
        report = Router().explain(query, force_no_tools=parsed.no_tools)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    report = run_router_eval()
    print(format_quality_json(report) if parsed.json else format_quality_summary(report))
    return 1 if report.get("status") == "fail" else 0


def _prompts(argv: list[str], *, project_root: str | Path = ".") -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py prompts", description="Inspect and update Codex prompt tracking.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List known prompt records.")
    subparsers.add_parser("next", help="Show the next queued prompt.")
    show_parser = subparsers.add_parser("show", help="Show a prompt record.")
    show_parser.add_argument("prompt_id")
    search_parser = subparsers.add_parser("search", help="Search prompt records.")
    search_parser.add_argument("query")
    add_parser = subparsers.add_parser("add", help="Add a queued prompt from a file or id.")
    add_parser.add_argument("file_or_id")
    for command, help_text in (
        ("mark-active", "Mark a prompt active."),
        ("mark-skipped", "Mark a prompt skipped."),
        ("mark-failed", "Mark a prompt failed."),
    ):
        status_parser = subparsers.add_parser(command, help=help_text)
        status_parser.add_argument("prompt_id")
        status_parser.add_argument("--notes", default=None)
    complete_parser = subparsers.add_parser("mark-complete", help="Mark a prompt complete.")
    complete_parser.add_argument("prompt_id")
    complete_parser.add_argument("--test-result", default=None)
    complete_parser.add_argument("--docs-updated", default=None)
    complete_parser.add_argument("--unknown", action="store_true")
    complete_parser.add_argument("--notes", default=None)
    superseded_parser = subparsers.add_parser("mark-superseded", help="Mark a prompt superseded by another prompt.")
    superseded_parser.add_argument("prompt_id")
    superseded_parser.add_argument("--by", required=True, dest="replacement_id")
    superseded_parser.add_argument("--notes", default=None)
    validate_parser = subparsers.add_parser("validate-pack", help="Validate a prompt pack without writing files.")
    validate_parser.add_argument("pack_file")
    import_parser = subparsers.add_parser("import", help="Validate, store, split, and queue a prompt pack.")
    import_parser.add_argument("pack_file")
    split_parser = subparsers.add_parser("split", help="Alias for import: validate, store, split, and queue a prompt pack.")
    split_parser.add_argument("pack_file")
    audit_parser = subparsers.add_parser("audit", help="Audit prompt ledger evidence.")
    audit_parser.add_argument("prompt_id", nargs="?")
    evidence_parser = subparsers.add_parser("evidence", help="Show completion evidence for prompt records.")
    evidence_parser.add_argument("prompt_id", nargs="?")
    subparsers.add_parser("missing", help="Show queued prompts with no completion evidence.")
    subparsers.add_parser("missed", help="Show queued prompts that appear missed or partial.")
    subparsers.add_parser("superseded", help="Show superseded prompt records.")
    subparsers.add_parser("stale", help="Show completed prompts missing evidence.")
    subparsers.add_parser("recover-plan", help="Build a conservative prompt recovery plan.")
    subparsers.add_parser("reconcile", help="Report a conservative prompt reconciliation plan without auto-running prompts.")
    eval_parser = subparsers.add_parser("eval", help="Run prompt/system-prompt quality evals.")
    eval_parser.add_argument("--json", action="store_true", help="Print JSON instead of a readable summary.")
    subparsers.add_parser("report", help="Show latest model-router/prompt quality report.")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    try:
        if parsed.command == "list":
            print(format_prompt_records(list_prompt_records(project_root)))
        elif parsed.command == "next":
            print(format_prompt_record(next_prompt(project_root)))
        elif parsed.command == "show":
            prompt = show_prompt(parsed.prompt_id, project_root)
            if prompt is None:
                print("prompt not found", file=sys.stderr)
                return 1
            print(format_prompt_record(prompt))
        elif parsed.command == "search":
            print(format_prompt_records(search_prompt_records(parsed.query, project_root)))
        elif parsed.command == "add":
            print(json.dumps(add_prompt_record(parsed.file_or_id, project_root), indent=2, sort_keys=True))
        elif parsed.command == "mark-active":
            result = mark_prompt(parsed.prompt_id, "active", project_root=project_root, notes=parsed.notes)
            update_prompt_state(project_root=project_root, active_prompt_id=parsed.prompt_id)
            print(json.dumps(result, indent=2, sort_keys=True))
        elif parsed.command == "mark-complete":
            result = mark_prompt(
                parsed.prompt_id,
                "completed",
                project_root=project_root,
                test_result=parsed.test_result,
                docs_updated=parsed.docs_updated,
                unknown=parsed.unknown,
                notes=parsed.notes,
            )
            next_record = next_prompt(project_root)
            update_prompt_state(project_root=project_root, active_prompt_id="none", next_prompt_id=next_record.prompt_id if next_record else "none")
            print(json.dumps(result, indent=2, sort_keys=True))
        elif parsed.command == "mark-skipped":
            result = mark_prompt(parsed.prompt_id, "skipped", project_root=project_root, notes=parsed.notes)
            next_record = next_prompt(project_root)
            update_prompt_state(project_root=project_root, active_prompt_id="none", next_prompt_id=next_record.prompt_id if next_record else "none")
            print(json.dumps(result, indent=2, sort_keys=True))
        elif parsed.command == "mark-failed":
            result = mark_prompt(parsed.prompt_id, "failed", project_root=project_root, notes=parsed.notes)
            next_record = next_prompt(project_root)
            update_prompt_state(project_root=project_root, active_prompt_id="none", next_prompt_id=next_record.prompt_id if next_record else "none", prompt_blockers=parsed.notes or "failed")
            print(json.dumps(result, indent=2, sort_keys=True))
        elif parsed.command == "mark-superseded":
            result = mark_prompt(
                parsed.prompt_id,
                "superseded",
                project_root=project_root,
                notes=parsed.notes,
                superseded_by=parsed.replacement_id,
            )
            next_record = next_prompt(project_root)
            update_prompt_state(project_root=project_root, active_prompt_id="none", next_prompt_id=next_record.prompt_id if next_record else "none")
            print(json.dumps(result, indent=2, sort_keys=True))
        elif parsed.command == "validate-pack":
            pack = validate_pack_file(parsed.pack_file)
            print(json.dumps({"status": "ok", "pack_id": pack.pack_id, "prompt_count": len(pack.prompts)}, indent=2, sort_keys=True))
        elif parsed.command in {"import", "split"}:
            result = import_prompt_pack(parsed.pack_file, project_root=project_root)
            print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
        elif parsed.command == "audit":
            if parsed.prompt_id:
                print(json.dumps(audit_prompt_evidence(project_root, parsed.prompt_id), indent=2, sort_keys=True))
            else:
                print(json.dumps(audit_prompts(project_root), indent=2, sort_keys=True))
        elif parsed.command == "evidence":
            print(json.dumps(audit_prompt_evidence(project_root, parsed.prompt_id), indent=2, sort_keys=True))
        elif parsed.command == "missing":
            print(format_prompt_records(missing_prompts(project_root)))
        elif parsed.command == "missed":
            print(json.dumps(recovery_missed_prompts(project_root), indent=2, sort_keys=True))
        elif parsed.command == "superseded":
            print(json.dumps(recovery_superseded_prompts(project_root), indent=2, sort_keys=True))
        elif parsed.command == "stale":
            print(json.dumps(recovery_stale_prompts(project_root), indent=2, sort_keys=True))
        elif parsed.command == "recover-plan":
            print(json.dumps(recovery_plan(project_root), indent=2, sort_keys=True))
        elif parsed.command == "reconcile":
            print(json.dumps(recovery_reconcile(project_root), indent=2, sort_keys=True))
        elif parsed.command == "eval":
            report = run_prompt_eval()
            print(format_quality_json(report) if parsed.json else format_quality_summary(report))
            return 1 if report.get("status") == "fail" else 0
        elif parsed.command == "report":
            print(read_prompt_quality_report())
    except (ValueError, PromptPackError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


def _work(argv: list[str], *, project_root: str | Path = ".") -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py work", description="PromptOps workbench for importing, queuing, and safely running Codex prompts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    import_parser = subparsers.add_parser("import", help="Import a prompt pack or raw single prompt from a file or stdin.")
    import_parser.add_argument("file", nargs="?")
    import_parser.add_argument("--stdin", action="store_true")
    import_parser.add_argument("--single", action="store_true")
    import_parser.add_argument("--id", dest="prompt_id")
    import_parser.add_argument("--pack-id")

    clipboard_parser = subparsers.add_parser("import-clipboard", help="Import a prompt pack or raw single prompt from macOS clipboard.")
    clipboard_parser.add_argument("--single", action="store_true")
    clipboard_parser.add_argument("--id", dest="prompt_id")
    clipboard_parser.add_argument("--pack-id")

    subparsers.add_parser("next", help="Show next safe queued prompt metadata.")
    subparsers.add_parser("show-next", help="Show next prompt metadata and body.")
    copy_parser = subparsers.add_parser("copy-next", help="Copy next prompt body to the clipboard.")
    copy_parser.add_argument("--mark-active", action="store_true")

    active_parser = subparsers.add_parser("mark-active", help="Mark a prompt active.")
    active_parser.add_argument("prompt_id")
    complete_parser = subparsers.add_parser("mark-complete", help="Mark a prompt complete.")
    complete_parser.add_argument("prompt_id")
    complete_parser.add_argument("--test-result")
    complete_parser.add_argument("--docs-updated")
    complete_parser.add_argument("--unknown", action="store_true")
    complete_parser.add_argument("--notes")
    failed_parser = subparsers.add_parser("mark-failed", help="Mark a prompt failed.")
    failed_parser.add_argument("prompt_id")
    failed_parser.add_argument("--notes")

    subparsers.add_parser("resume", help="Show active prompt and next safe action.")
    subparsers.add_parser("status", help="Show prompt queue status.")
    subparsers.add_parser("review", help="Review prompt queue, audit evidence, and active state.")
    subparsers.add_parser("run-next", help="Run the next prompt only when CODEX_RUNNER_ENABLED=true; otherwise print a safe fallback.")
    autopilot_parser = subparsers.add_parser("autopilot", help="Run multiple safe prompts only when runner is explicitly enabled.")
    autopilot_parser.add_argument("--safe-only", action="store_true", required=True)
    autopilot_parser.add_argument("--max-prompts", type=int, default=None)
    subparsers.add_parser("audit", help="Audit prompt queue and ledger evidence.")

    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    try:
        if parsed.command == "import":
            if parsed.stdin:
                text = sys.stdin.read()
                result = promptops_import_from_stdin(
                    text,
                    project_root=project_root,
                    pack_id=parsed.pack_id,
                    single=parsed.single,
                    prompt_id=parsed.prompt_id,
                )
            elif parsed.file:
                result = promptops_import_from_file(parsed.file, project_root=project_root, pack_id=parsed.pack_id)
            else:
                print("work import requires <file> or --stdin", file=sys.stderr)
                return 2
            print(promptops_format_json(result))
            return 0
        if parsed.command == "import-clipboard":
            result = promptops_import_from_clipboard(
                project_root=project_root,
                pack_id=parsed.pack_id,
                single=parsed.single,
                prompt_id=parsed.prompt_id,
            )
            print(promptops_format_json(result))
            return 0
        if parsed.command == "next":
            result = promptops_next(project_root=project_root)
            print(format_readable_next(result))
            return 0 if result.status == "ok" else 1
        if parsed.command == "show-next":
            print(promptops_format_json(promptops_show_next(project_root=project_root)))
            return 0
        if parsed.command == "copy-next":
            print(promptops_format_json(promptops_copy_next(project_root=project_root, mark_active=parsed.mark_active)))
            return 0
        if parsed.command == "mark-active":
            print(json.dumps(promptops_mark_active(parsed.prompt_id, project_root=project_root), indent=2, sort_keys=True))
            return 0
        if parsed.command == "mark-complete":
            print(
                json.dumps(
                    promptops_mark_complete(
                        parsed.prompt_id,
                        project_root=project_root,
                        test_result=parsed.test_result,
                        docs_updated=parsed.docs_updated,
                        unknown=parsed.unknown,
                        notes=parsed.notes,
                    ),
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        if parsed.command == "mark-failed":
            print(json.dumps(promptops_mark_failed(parsed.prompt_id, project_root=project_root, notes=parsed.notes), indent=2, sort_keys=True))
            return 0
        if parsed.command == "resume":
            print(promptops_format_json(promptops_resume(project_root=project_root)))
            return 0
        if parsed.command == "status":
            print(promptops_format_json(promptops_status(project_root=project_root)))
            return 0
        if parsed.command == "review":
            print(promptops_format_json(promptops_review(project_root=project_root)))
            return 0
        if parsed.command == "run-next":
            print(promptops_format_json(promptops_run_next(project_root=project_root)))
            return 0
        if parsed.command == "autopilot":
            print(promptops_format_json(promptops_autopilot(project_root=project_root, max_prompts=parsed.max_prompts, safe_only=parsed.safe_only)))
            return 0
        if parsed.command == "audit":
            print(promptops_format_json(promptops_audit(project_root=project_root)))
            return 0
    except (ValueError, PromptPackError, ClipboardUnavailable) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 2


def _session(argv: list[str], *, project_root: str | Path = ".") -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py session", description="Record and replay redacted manual dogfooding sessions.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    start_parser = subparsers.add_parser("start", help="Start a redacted live session log.")
    start_parser.add_argument("--name", required=True)
    start_parser.add_argument("--tag", action="append", default=[])
    subparsers.add_parser("status", help="Show active session status.")
    subparsers.add_parser("end", help="End the active session.")
    subparsers.add_parser("list", help="List session logs.")
    show_parser = subparsers.add_parser("show", help="Show one session as structured JSON.")
    show_parser.add_argument("session_id")
    replay_parser = subparsers.add_parser("replay", help="Render a redacted session replay.")
    replay_parser.add_argument("session_id", nargs="?")
    replay_parser.add_argument("--last", action="store_true")
    review_parser = subparsers.add_parser("review", help="Analyze a session and generate candidate bug reports.")
    review_parser.add_argument("session_id", nargs="?")
    review_parser.add_argument("--last", action="store_true")
    review_parser.add_argument("--create-bugs", action="store_true")
    export_parser = subparsers.add_parser("export", help="Export one redacted session as JSON.")
    export_parser.add_argument("session_id")
    subparsers.add_parser("last", help="Show the last active or ended session.")
    run_parser = subparsers.add_parser("run", help="Run a smart_agent.py command and append redacted output to the active session.")
    run_parser.add_argument("--unsafe-raw", action="store_true", help="Store unredacted command output. Unsafe; off by default.")
    run_parser.add_argument("command_args", nargs=argparse.REMAINDER)
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    recorder = SessionRecorder(project_root=project_root)
    try:
        if parsed.command == "start":
            print(json.dumps(recorder.start(name=parsed.name, tags=parsed.tag).to_dict(), indent=2, sort_keys=True))
            return 0
        if parsed.command == "status":
            print(json.dumps(recorder.status(), indent=2, sort_keys=True))
            return 0
        if parsed.command == "end":
            print(json.dumps(recorder.end().to_dict(), indent=2, sort_keys=True))
            return 0
        if parsed.command == "list":
            print(json.dumps({"sessions": recorder.list()}, indent=2, sort_keys=True))
            return 0
        if parsed.command == "show":
            print(json.dumps(recorder.show(parsed.session_id), indent=2, sort_keys=True))
            return 0
        if parsed.command == "replay":
            session_id = _resolve_session_id(recorder, parsed.session_id, parsed.last)
            print(recorder.replay(session_id))
            return 0
        if parsed.command == "review":
            session_id = _resolve_session_id(recorder, parsed.session_id, parsed.last)
            reviewer = SessionReviewer(
                store=recorder.store,
                project_root=project_root,
                audit_logger=AuditLogger(Path(project_root) / "logs" / "audit.jsonl"),
            )
            print(json.dumps(reviewer.review_session(session_id, create_bugs=parsed.create_bugs), indent=2, sort_keys=True))
            return 0
        if parsed.command == "export":
            print(json.dumps(recorder.export(parsed.session_id), indent=2, sort_keys=True))
            return 0
        if parsed.command == "last":
            last = recorder.last()
            print(json.dumps(last or {"error": "no sessions found"}, indent=2, sort_keys=True))
            return 0 if last else 1
        if parsed.command == "run":
            args = list(parsed.command_args)
            if args and args[0] == "--":
                args = args[1:]
            record = recorder.run_command(args, unsafe_raw=parsed.unsafe_raw)
            print(json.dumps(record.to_dict(), indent=2, sort_keys=True))
            return 0 if record.exit_code == 0 else record.exit_code
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 2


def _bugs(argv: list[str], *, project_root: str | Path = ".") -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py bugs", description="Inspect redacted session-derived bug reports.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List local redacted bug reports.")
    show_parser = subparsers.add_parser("show", help="Show one local redacted bug report.")
    show_parser.add_argument("bug_id")
    subparsers.add_parser("export", help="Export all local redacted bug reports.")
    create_regression_parser = subparsers.add_parser("create-regression", help="Create a sanitized regression test scaffold for one bug.")
    create_regression_parser.add_argument("bug_id")
    create_regressions_parser = subparsers.add_parser("create-regressions", help="Create sanitized regression test scaffolds for bugs in one session.")
    create_regressions_parser.add_argument("--session", required=True, dest="session_id")
    mark_fixed_parser = subparsers.add_parser("mark-fixed", help="Mark a bug fixed after linking a regression test or giving a reason.")
    mark_fixed_parser.add_argument("bug_id")
    mark_fixed_parser.add_argument("--reason", default="")
    mark_wontfix_parser = subparsers.add_parser("mark-wontfix", help="Mark a bug as wontfix.")
    mark_wontfix_parser.add_argument("bug_id")
    mark_wontfix_parser.add_argument("--reason", default="")
    link_test_parser = subparsers.add_parser("link-test", help="Link an existing regression test path to a bug.")
    link_test_parser.add_argument("bug_id")
    link_test_parser.add_argument("test_path")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    reviewer = SessionReviewer(project_root=project_root, audit_logger=AuditLogger(Path(project_root) / "logs" / "audit.jsonl"))
    try:
        if parsed.command == "list":
            print(json.dumps({"bugs": [record.to_dict() for record in reviewer.list_bugs()]}, indent=2, sort_keys=True))
            return 0
        if parsed.command == "show":
            print(json.dumps(reviewer.show_bug(parsed.bug_id).to_dict(), indent=2, sort_keys=True))
            return 0
        if parsed.command == "export":
            print(json.dumps(reviewer.export_bugs(), indent=2, sort_keys=True))
            return 0
        if parsed.command == "create-regression":
            print(json.dumps(reviewer.create_regression(parsed.bug_id).to_dict(), indent=2, sort_keys=True))
            return 0
        if parsed.command == "create-regressions":
            print(json.dumps({"regressions": [result.to_dict() for result in reviewer.create_regressions_for_session(parsed.session_id)]}, indent=2, sort_keys=True))
            return 0
        if parsed.command == "mark-fixed":
            print(json.dumps(reviewer.mark_fixed(parsed.bug_id, reason=parsed.reason).to_dict(), indent=2, sort_keys=True))
            return 0
        if parsed.command == "mark-wontfix":
            print(json.dumps(reviewer.mark_wontfix(parsed.bug_id, reason=parsed.reason).to_dict(), indent=2, sort_keys=True))
            return 0
        if parsed.command == "link-test":
            print(json.dumps(reviewer.link_test(parsed.bug_id, parsed.test_path).to_dict(), indent=2, sort_keys=True))
            return 0
    except (ValueError, AuditLogError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 2


def _resolve_session_id(recorder: SessionRecorder, session_id: str | None, last: bool) -> str:
    if session_id and last:
        raise ValueError("use either <session_id> or --last")
    if session_id:
        return session_id
    if last:
        latest = recorder.last()
        if latest is None:
            raise ValueError("no sessions found")
        return str(latest["session_id"])
    raise ValueError("session replay requires <session_id> or --last")


def _feedback(argv: list[str], *, project_root: str | Path = ".") -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py feedback", description="Attach redacted feedback to session commands.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    good_parser = subparsers.add_parser("good", help="Mark a command as good.")
    _add_last_or_session_args(good_parser)

    bad_parser = subparsers.add_parser("bad", help="Mark a command as bad.")
    _add_last_or_session_args(bad_parser)
    bad_parser.add_argument("--reason", required=True)

    bug_parser = subparsers.add_parser("bug", help="Mark a command as buggy and create a linked bug placeholder.")
    _add_last_or_session_args(bug_parser)
    bug_parser.add_argument("--title", required=True)
    bug_parser.add_argument("--reason", default="")

    confusing_parser = subparsers.add_parser("confusing", help="Mark a command as confusing.")
    _add_last_or_session_args(confusing_parser)
    confusing_parser.add_argument("--reason", required=True)

    slow_parser = subparsers.add_parser("slow", help="Mark a command as slow.")
    _add_last_or_session_args(slow_parser)
    slow_parser.add_argument("--reason", required=True)

    unsafe_parser = subparsers.add_parser("unsafe", help="Mark a command as unsafe.")
    _add_last_or_session_args(unsafe_parser)
    unsafe_parser.add_argument("--reason", required=True)

    rate_parser = subparsers.add_parser("rate", help="Rate a command from 1 to 5.")
    _add_last_or_session_args(rate_parser)
    rate_parser.add_argument("--score", type=int, required=True)

    add_parser = subparsers.add_parser("add", help="Attach custom feedback to a command id.")
    add_parser.add_argument("command_id")
    add_parser.add_argument("--tag", action="append", required=True, choices=sorted(VALID_FEEDBACK_TAGS))
    add_parser.add_argument("--note", default="")
    add_parser.add_argument("--reason", default="")
    add_parser.add_argument("--expected-behavior", default="")
    add_parser.add_argument("--actual-behavior", default="")
    add_parser.add_argument("--severity", default="low", choices=["low", "medium", "high", "critical"])
    add_parser.add_argument("--session", default=None)

    list_parser = subparsers.add_parser("list", help="List feedback for a session.")
    list_parser.add_argument("--session", required=True)

    export_parser = subparsers.add_parser("export", help="Export redacted feedback for a session.")
    export_parser.add_argument("--session", required=True)
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    manager = FeedbackManager(
        store=SessionRecorder(project_root=project_root).store,
        audit_logger=AuditLogger(Path(project_root) / "logs" / "audit.jsonl"),
    )
    try:
        if parsed.command == "good":
            record = manager.add_feedback(None, make_feedback(tags=[], rating=5, user_note="good"), use_last=parsed.last, session_id=parsed.session)
        elif parsed.command == "bad":
            record = manager.add_feedback(None, make_feedback(tags=["poor_response"], rating=1, reason=parsed.reason, severity="medium"), use_last=parsed.last, session_id=parsed.session)
        elif parsed.command == "bug":
            record = manager.add_feedback(None, bug_feedback(parsed.title, reason=parsed.reason), use_last=parsed.last, session_id=parsed.session)
        elif parsed.command == "confusing":
            record = manager.add_feedback(None, make_feedback(tags=["UX_confusing"], reason=parsed.reason, severity="medium"), use_last=parsed.last, session_id=parsed.session)
        elif parsed.command == "slow":
            record = manager.add_feedback(None, make_feedback(tags=["too_slow"], reason=parsed.reason, severity="medium"), use_last=parsed.last, session_id=parsed.session)
        elif parsed.command == "unsafe":
            record = manager.add_feedback(None, make_feedback(tags=["unsafe_behavior"], reason=parsed.reason, severity="high"), use_last=parsed.last, session_id=parsed.session)
        elif parsed.command == "rate":
            record = manager.add_feedback(None, make_feedback(tags=[], rating=parsed.score), use_last=parsed.last, session_id=parsed.session)
        elif parsed.command == "add":
            record = manager.add_feedback(
                parsed.command_id,
                make_feedback(
                    tags=parsed.tag,
                    reason=parsed.reason,
                    expected_behavior=parsed.expected_behavior,
                    actual_behavior=parsed.actual_behavior,
                    user_note=parsed.note,
                    severity=parsed.severity,
                ),
                session_id=parsed.session,
            )
        elif parsed.command == "list":
            print(json.dumps({"feedback": [record.to_dict() for record in manager.list_feedback(session_id=parsed.session)]}, indent=2, sort_keys=True))
            return 0
        elif parsed.command == "export":
            print(json.dumps(manager.export_feedback(session_id=parsed.session), indent=2, sort_keys=True))
            return 0
        else:
            return 2
        print(json.dumps(record.to_dict(), indent=2, sort_keys=True))
        return 0
    except (ValueError, AuditLogError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


def _add_last_or_session_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--last", action="store_true", help="Attach feedback to the last command in the active or latest session.")
    parser.add_argument("--session", default=None, help="Optional session id; defaults to active session, then latest session.")


def _dogfood(argv: list[str], *, project_root: str | Path = ".") -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py dogfood", description="Run curated manual dogfood command suites.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List available dogfood suites.")
    subparsers.add_parser("plan", help="Show the daily and weekly dogfood workflow plan.")
    subparsers.add_parser("next", help="Show the next recommended dogfood step.")
    subparsers.add_parser("checklist", help="Show the daily and weekly dogfood checklists.")
    show_parser = subparsers.add_parser("show", help="Show one suite definition.")
    show_parser.add_argument("suite")
    run_parser = subparsers.add_parser("run", help="Run one dogfood suite and continue through failures.")
    run_parser.add_argument("suite")
    run_parser.add_argument("--session", action="store_true", help="Capture command output into the active session log.")
    run_parser.add_argument("--dry-run", action="store_true", help="Show commands without executing them.")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    try:
        if parsed.command == "list":
            load_all_suites(project_root=project_root)
            print(json.dumps({"suites": list_suite_summaries(project_root=project_root)}, indent=2, sort_keys=True))
            return 0
        if parsed.command == "plan":
            print(json.dumps(build_dogfood_plan(project_root=project_root), indent=2, sort_keys=True))
            return 0
        if parsed.command == "next":
            print(json.dumps(dogfood_next(project_root=project_root), indent=2, sort_keys=True))
            return 0
        if parsed.command == "checklist":
            print(json.dumps(dogfood_checklist(project_root=project_root), indent=2, sort_keys=True))
            return 0
        if parsed.command == "show":
            print(json.dumps(load_suite(parsed.suite, project_root=project_root).to_dict(), indent=2, sort_keys=True))
            return 0
        if parsed.command == "run":
            report = run_dogfood_suite(
                parsed.suite,
                project_root=project_root,
                dry_run=parsed.dry_run,
                use_session=parsed.session,
            )
            print(json.dumps(report, indent=2, sort_keys=True))
            return 0 if report["status"] == "ok" else 1
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 2


def _quality(argv: list[str], *, project_root: str | Path = ".") -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py quality", description="Show read-only product quality health.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("status", "sessions", "bugs", "regressions", "features", "next"):
        subparsers.add_parser(name, help=f"Show quality {name}.")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    if parsed.command == "status":
        payload = quality_status(project_root=project_root)
    elif parsed.command == "sessions":
        payload = quality_sessions(project_root=project_root)
    elif parsed.command == "bugs":
        payload = quality_bugs(project_root=project_root)
    elif parsed.command == "regressions":
        payload = quality_regressions(project_root=project_root)
    elif parsed.command == "features":
        payload = quality_features(project_root=project_root)
    elif parsed.command == "next":
        payload = quality_next(project_root=project_root)
    else:
        return 2
    if parsed.command == "status":
        report = build_product_quality_dashboard(project_root=project_root)
        print(format_product_quality_dashboard(report))
    else:
        print(format_product_quality_json(payload))
    return 0


def _commands(argv: list[str], *, project_root: str | Path = ".") -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py commands", description="Inspect the durable command registry and manual QA plan.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    list_parser = subparsers.add_parser("list", help="List command IDs, command patterns, group, status, and risk.")
    list_parser.add_argument("--status", default=None)
    list_parser.add_argument("--group", default=None)
    show_parser = subparsers.add_parser("show", help="Show one command registry record.")
    show_parser.add_argument("command_id")
    search_parser = subparsers.add_parser("search", help="Search command registry text.")
    search_parser.add_argument("query")
    subparsers.add_parser("legacy", help="List legacy, deprecated, and removed commands.")
    subparsers.add_parser("deprecated", help="List deprecated commands.")
    subparsers.add_parser("validate", help="Validate command registry docs against structured records.")
    subparsers.add_parser("qa-plan", help="List commands that still need manual QA.")
    qa_run_parser = subparsers.add_parser("qa-run", help="Print safe manual QA commands for a group; does not execute them.")
    qa_run_parser.add_argument("group")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    if parsed.command == "list":
        print(format_command_list(list_commands(status=parsed.status, group=parsed.group)))
        return 0
    if parsed.command == "show":
        record = get_command(parsed.command_id)
        if record is None:
            print("command not found", file=sys.stderr)
            return 1
        print(format_command_detail(record))
        return 0
    if parsed.command == "search":
        print(format_command_list(search_commands(parsed.query)))
        return 0
    if parsed.command == "legacy":
        print(format_command_list(legacy_commands()))
        return 0
    if parsed.command == "deprecated":
        print(format_command_list(deprecated_commands()))
        return 0
    if parsed.command == "validate":
        report = validate_command_registry_docs(project_root)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["status"] == "ok" else 2
    if parsed.command == "qa-plan":
        print(format_command_list(qa_plan()))
        return 0
    if parsed.command == "qa-run":
        print(json.dumps({"group": parsed.group, "commands": qa_run(parsed.group)}, indent=2, sort_keys=True))
        return 0
    return 2


def _backup(argv: list[str], *, project_root: str | Path = ".") -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py backup", description="Create, inspect, verify, and approval-gate local redacted backups.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    create_parser = subparsers.add_parser("create", help="Create a redacted local backup archive.")
    create_parser.add_argument("--backup-dir", default="")
    create_parser.add_argument("--include-captures", action="store_true")
    create_parser.add_argument("--include-audit-metadata", action="store_true")

    list_parser = subparsers.add_parser("list", help="List local backup archives.")
    list_parser.add_argument("--backup-dir", default="")

    inspect_parser = subparsers.add_parser("inspect", help="Inspect one backup manifest and restore preview.")
    inspect_parser.add_argument("backup_id")
    inspect_parser.add_argument("--backup-dir", default="")

    restore_parser = subparsers.add_parser("restore", help="Restore one backup after approval.")
    restore_parser.add_argument("backup_id")
    restore_parser.add_argument("--backup-dir", default="")

    export_parser = subparsers.add_parser("export", help="Create a portable redacted backup export.")
    export_parser.add_argument("--redacted", action="store_true", default=True)
    export_parser.add_argument("--backup-dir", default="")
    export_parser.add_argument("--include-captures", action="store_true")
    export_parser.add_argument("--include-audit-metadata", action="store_true")

    verify_parser = subparsers.add_parser("verify", help="Verify backup integrity.")
    verify_parser.add_argument("backup_id")
    verify_parser.add_argument("--backup-dir", default="")

    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    try:
        broker = _local_broker(project_root=project_root, route="backup_cli")
        if parsed.command == "create":
            tool_name = "backup.create"
            arguments = {
                "backup_dir": parsed.backup_dir,
                "include_captures": parsed.include_captures,
                "include_audit_metadata": parsed.include_audit_metadata,
                "redacted": True,
            }
        elif parsed.command == "list":
            tool_name = "backup.list"
            arguments = {"backup_dir": parsed.backup_dir}
        elif parsed.command == "inspect":
            tool_name = "backup.inspect"
            arguments = {"backup_id": parsed.backup_id, "backup_dir": parsed.backup_dir}
        elif parsed.command == "restore":
            tool_name = "backup.restore"
            arguments = {"backup_id": parsed.backup_id, "backup_dir": parsed.backup_dir}
        elif parsed.command == "export":
            tool_name = "backup.export"
            arguments = {
                "backup_dir": parsed.backup_dir,
                "include_captures": parsed.include_captures,
                "include_audit_metadata": parsed.include_audit_metadata,
                "redacted": bool(parsed.redacted),
            }
        else:
            tool_name = "backup.verify"
            arguments = {"backup_id": parsed.backup_id, "backup_dir": parsed.backup_dir}
        payload = _execute_local_tool(broker, f"cli_{tool_name.replace('.', '_')}", tool_name, arguments)
    except (RuntimeConfigError, AuditLogError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(payload["content"], indent=2, sort_keys=True))
    return 0 if payload.get("allowed") else 2


def _local_broker(*, project_root: str | Path = ".", route: str = "cli") -> ToolBroker:
    runtime = RuntimeConfig.from_env()
    validate_startup_policy(runtime.capabilities_path)
    policy_engine = PolicyEngine.from_config(load_capabilities_config(runtime.capabilities_path))
    audit_logger = AuditLogger(runtime.audit_log_path)
    registry = default_registry(project_root=project_root, memory_path=Path(project_root) / "data" / "memory.sqlite3")
    return ToolBroker(
        registry,
        policy_engine,
        audit_logger,
        session_id="cli-session",
        model=runtime.lmstudio_model,
        route=route,
        approval_manager=ApprovalManager(store=ApprovalStore(), audit_logger=audit_logger, route=route),
    )


def _execute_local_tool(broker: ToolBroker, call_id: str, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
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


def _schedule(argv: list[str], *, project_root: str | Path = ".") -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py schedule", description="Manual-run opt-in scheduler.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List local schedule records.")
    create_parser = subparsers.add_parser("create", help="Create a local manual-run schedule record.")
    create_parser.add_argument(
        "--workflow",
        required=True,
        choices=["daily_briefing", "connector_doctor", "eval_safe", "memory_cleanup", "audit_summary", "backup_create"],
    )
    create_parser.add_argument("--name")
    create_parser.add_argument("--schedule", default="manual", help="Human schedule hint, such as daily@08:00. V1 does not install a background runner.")
    create_parser.add_argument("--arg", action="append", default=[], help="Workflow arg as key=value. Repeat as needed.")
    create_parser.add_argument("--json-args", default=None, help="Workflow args as a JSON object.")
    run_parser = subparsers.add_parser("run", help="Run one schedule now.")
    run_parser.add_argument("schedule_id")
    pause_parser = subparsers.add_parser("pause", help="Pause a schedule.")
    pause_parser.add_argument("schedule_id")
    delete_parser = subparsers.add_parser("delete", help="Delete a schedule.")
    delete_parser.add_argument("schedule_id")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    try:
        runtime = RuntimeConfig.from_env()
        audit_logger = AuditLogger(runtime.audit_log_path)
        if parsed.command == "list":
            payload = list_schedules()
        elif parsed.command == "create":
            payload = create_schedule(
                workflow=parsed.workflow,
                name=parsed.name,
                schedule=parsed.schedule,
                args=_parse_schedule_args(parsed.arg, parsed.json_args),
                audit_logger=audit_logger,
            )
        elif parsed.command == "run":
            payload = run_schedule(parsed.schedule_id, runtime=runtime, audit_logger=audit_logger)
        elif parsed.command == "pause":
            payload = pause_schedule(parsed.schedule_id, audit_logger=audit_logger)
        else:
            payload = delete_schedule(parsed.schedule_id, audit_logger=audit_logger)
    except (RuntimeConfigError, AuditLogError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("status") in {"ok", "limited", "dry_run", "skipped"} else 2


def _parse_schedule_args(pairs: list[str], json_args: str | None) -> dict[str, object]:
    args: dict[str, object] = {}
    if json_args:
        try:
            parsed = json.loads(json_args)
        except json.JSONDecodeError as exc:
            raise ValueError(f"--json-args must be a JSON object: {exc.msg}") from exc
        if not isinstance(parsed, dict):
            raise ValueError("--json-args must be a JSON object")
        args.update(parsed)
    for pair in pairs:
        if "=" not in pair:
            raise ValueError("schedule args must be key=value")
        key, raw = pair.split("=", 1)
        if not key.strip():
            raise ValueError("schedule arg key cannot be empty")
        try:
            args[key.strip()] = json.loads(raw)
        except json.JSONDecodeError:
            args[key.strip()] = raw
    return args


def _preflight(argv: list[str], *, project_root: str | Path = ".") -> int:
    request = " ".join(argv).strip()
    if not request:
        print('usage: preflight "<request>"', file=sys.stderr)
        return 2
    try:
        report = run_preflight(PreflightOptions(request=request, project_root=project_root))
    except Exception as exc:
        print(f"preflight failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(format_preflight(report))
    return 0
