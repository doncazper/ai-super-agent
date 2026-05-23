from __future__ import annotations

import json
import re
from pathlib import Path

AUDIT_ID_RE = re.compile(r'(?:"?(?:audit_id|audit_hash|request_id|approval_request_id|tool_call_id)"?\s*[:=]\s*"?)([A-Za-z0-9_.:-]{6,})')
TOOL_NAME_RE = re.compile(r"\b([a-z][a-z0-9_]+\.[a-z][a-z0-9_]+)\b")


def extract_audit_ids(text: str) -> list[str]:
    return sorted(set(AUDIT_ID_RE.findall(text)))


def detect_tool_calls(text: str) -> list[str]:
    return sorted({match for match in TOOL_NAME_RE.findall(text) if "." in match})


def audit_ids_from_log(audit_log_path: Path, *, max_entries: int = 20) -> list[str]:
    if not audit_log_path.exists():
        return []
    ids: list[str] = []
    try:
        lines = audit_log_path.read_text(encoding="utf-8").splitlines()[-max_entries:]
    except OSError:
        return []
    for line in lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        for key in ("audit_id", "audit_hash", "request_id", "tool_call_id"):
            value = event.get(key)
            if value:
                ids.append(str(value))
    return sorted(set(ids))
