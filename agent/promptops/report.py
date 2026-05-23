from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agent.promptops.safety import redact_secrets


def write_promptops_report(payload: dict[str, Any], *, project_root: str | Path = ".") -> str:
    root = Path(project_root)
    directory = root / "reports" / "promptops"
    directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = directory / f"promptops_{timestamp}.json"
    text = json.dumps(_redact_payload(payload), indent=2, sort_keys=True)
    path.write_text(text + "\n", encoding="utf-8")
    return path.relative_to(root).as_posix()


def _redact_payload(value: Any) -> Any:
    if isinstance(value, str):
        return redact_secrets(value)
    if isinstance(value, list):
        return [_redact_payload(item) for item in value]
    if isinstance(value, dict):
        return {key: _redact_payload(item) for key, item in value.items()}
    return value

