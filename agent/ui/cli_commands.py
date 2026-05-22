from __future__ import annotations

import json
import sys
from pathlib import Path

from agent.config.loader import load_capabilities_config
from agent.tools.registry import default_registry
from agent.ui.audit_viewer import tail_audit
from agent.ui.config_viewer import config_as_json
from agent.ui.doctor import doctor_exit_code, format_doctor, run_doctor
from agent.ui.memory_viewer import delete_memory, list_memory
from agent.ui.permissions_dashboard import PermissionStore


def dispatch_cli(argv: list[str], *, project_root: str | Path = ".") -> int | None:
    if not argv:
        return None
    command = argv[0]
    if command == "--interactive":
        print("Interactive mode is available. Type 'exit' to quit.")
        return 0
    if command == "tools" and len(argv) >= 2 and argv[1] == "list":
        for schema in default_registry(project_root=project_root).schemas():
            print(schema["function"]["name"])
        return 0
    if command == "permissions":
        return _permissions(argv[1:])
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
