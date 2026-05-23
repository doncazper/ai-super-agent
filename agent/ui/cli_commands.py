from __future__ import annotations

import json
import sys
import argparse
from pathlib import Path

from agent.config.loader import load_capabilities_config
from agent.config.runtime import RuntimeConfig, RuntimeConfigError
from agent.prompts.pack_models import PromptPackError
from agent.prompts.prompt_store import import_prompt_pack, validate_pack_file
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
from agent.safety.actions import ActionCenter, ActionCenterStore
from agent.safety.approvals import ApprovalStatus, ApprovalStore
from agent.safety.audit import AuditLogger
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
from agent.ui.permissions_dashboard import PermissionStore
from agent.ui.preflight import PreflightOptions, format_preflight, run_preflight
from agent.ui.prompts import (
    add_prompt_record,
    audit_prompts,
    format_prompt_record,
    format_prompt_records,
    list_prompt_records,
    mark_prompt,
    missing_prompts,
    next_prompt,
    show_prompt,
)
from agent.ui.smoke import SmokeOptions, format_smoke, run_smoke, smoke_exit_code
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
    if command == "prompts":
        return _prompts(argv[1:], project_root=project_root)
    if command == "work":
        return _work(argv[1:], project_root=project_root)
    if command == "commands":
        return _commands(argv[1:], project_root=project_root)
    if command == "schedule":
        return _schedule(argv[1:], project_root=project_root)
    return None


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
    run_parser.add_argument("--web", action="store_true", help="Run web search/fetch evals if configured.")
    run_parser.add_argument("--weather", action="store_true", help="Run weather current/forecast evals if configured.")
    run_parser.add_argument("--workspace", action="store_true", help="Run workspace read/write evals in ./workspace/eval.")
    run_parser.add_argument("--memory", action="store_true", help="Run non-sensitive memory add/search/delete evals.")
    run_parser.add_argument("--json", action="store_true", help="Print structured JSON instead of a readable summary.")
    subparsers.add_parser("report", help="Print the last generated eval report.")
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
            web=parsed.web,
            weather=parsed.weather,
            workspace=parsed.workspace,
            memory=parsed.memory,
        )
    )
    print(format_eval_json(report) if parsed.json else format_eval_summary(report))
    return eval_exit_code(report)


def _prompts(argv: list[str], *, project_root: str | Path = ".") -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py prompts", description="Inspect and update Codex prompt tracking.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List known prompt records.")
    subparsers.add_parser("next", help="Show the next queued prompt.")
    show_parser = subparsers.add_parser("show", help="Show a prompt record.")
    show_parser.add_argument("prompt_id")
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
    subparsers.add_parser("audit", help="Audit prompt ledger evidence.")
    subparsers.add_parser("missing", help="Show queued prompts with no completion evidence.")
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
        elif parsed.command == "add":
            print(json.dumps(add_prompt_record(parsed.file_or_id, project_root), indent=2, sort_keys=True))
        elif parsed.command == "mark-active":
            print(json.dumps(mark_prompt(parsed.prompt_id, "active", project_root=project_root, notes=parsed.notes), indent=2, sort_keys=True))
        elif parsed.command == "mark-complete":
            print(
                json.dumps(
                    mark_prompt(
                        parsed.prompt_id,
                        "completed",
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
        elif parsed.command == "mark-skipped":
            print(json.dumps(mark_prompt(parsed.prompt_id, "skipped", project_root=project_root, notes=parsed.notes), indent=2, sort_keys=True))
        elif parsed.command == "mark-failed":
            print(json.dumps(mark_prompt(parsed.prompt_id, "failed", project_root=project_root, notes=parsed.notes), indent=2, sort_keys=True))
        elif parsed.command == "mark-superseded":
            print(
                json.dumps(
                    mark_prompt(
                        parsed.prompt_id,
                        "superseded",
                        project_root=project_root,
                        notes=parsed.notes,
                        superseded_by=parsed.replacement_id,
                    ),
                    indent=2,
                    sort_keys=True,
                )
            )
        elif parsed.command == "validate-pack":
            pack = validate_pack_file(parsed.pack_file)
            print(json.dumps({"status": "ok", "pack_id": pack.pack_id, "prompt_count": len(pack.prompts)}, indent=2, sort_keys=True))
        elif parsed.command in {"import", "split"}:
            result = import_prompt_pack(parsed.pack_file, project_root=project_root)
            print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
        elif parsed.command == "audit":
            print(json.dumps(audit_prompts(project_root), indent=2, sort_keys=True))
        elif parsed.command == "missing":
            print(format_prompt_records(missing_prompts(project_root)))
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


def _schedule(argv: list[str], *, project_root: str | Path = ".") -> int:
    parser = argparse.ArgumentParser(prog="smart_agent.py schedule", description="Manual-run opt-in scheduler.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List local schedule records.")
    create_parser = subparsers.add_parser("create", help="Create a local manual-run schedule record.")
    create_parser.add_argument("--workflow", required=True, choices=["daily_briefing", "connector_doctor", "eval_safe", "memory_cleanup", "audit_summary"])
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
