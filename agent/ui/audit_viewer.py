from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def tail_audit(path: str | Path = "logs/audit.jsonl", limit: int = 20) -> list[dict[str, Any]]:
    audit_path = Path(path)
    if not audit_path.exists():
        return []
    lines = [line for line in audit_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [json.loads(line) for line in lines[-limit:]]
