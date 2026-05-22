from __future__ import annotations

import json
import sys
import argparse
from pathlib import Path

from agent.config.loader import load_capabilities_config
from agent.safety.approvals import ApprovalStatus, ApprovalStore
from agent.tools.registry import default_registry
from agent.ui.approvals_ui import print_request, print_requests
from agent.ui.audit_viewer import tail_audit
from agent.ui.config_viewer import config_as_json
from agent.ui.doctor import doctor_exit_code, format_doctor, run_doctor
from agent.ui.memory_viewer import delete_memory, list_memory
from agent.ui.permissions_dashboard import PermissionStore
from agent.ui.smoke import SmokeOptions, format_smoke, run_smoke, smoke_exit_code


def dispatch_cli(argv: list[str], *, project_root: str | Path = ".") -> int | None:
    if not argv:
        return None
    command = argv[0]
    if command == "tools" and len(argv) >= 2 and argv[1] == "list":
        for schema in default_registry(project_root=project_root).schemas():
            print(schema["function"]["name"])
        return 0
    if command == "permissions":
        return _permissions(argv[1:])
    if command == "approvals":
        return _approvals(argv[1:])
    if command == "audit" and len(argv) >= 2 and argv[1] == "tail":
        limit = int(argv[2]) if len(argv) > 2 else 20
        print(json.dumps(tail_audit(limit=limit), indent=2, sort_keys=True))
        return 0
    if command == "memory":
        return _memory(argv[1:])
    if command == "config":
        return _config(argv[1:])
    if command == "setup":
        print("Set LMSTUDIO_MODEL, start LM Studio at http://localhost:1234/v1, then run tests.")
        return 0
    if command == "doctor":
        checks = run_doctor()
        print(format_doctor(checks))
        return doctor_exit_code(checks)
    if command == "smoke":
        return _smoke(argv[1:])
    return None


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


def _memory(argv: list[str]) -> int:
    if not argv or argv[0] == "list":
        print(json.dumps({"records": list_memory()}, indent=2, sort_keys=True))
        return 0
    if argv[0] == "delete" and len(argv) == 2:
        print(json.dumps(delete_memory(argv[1]), indent=2, sort_keys=True))
        return 0
    print("usage: memory list|delete <record_id>", file=sys.stderr)
    return 2


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
