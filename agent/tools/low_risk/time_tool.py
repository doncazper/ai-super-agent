from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo


TOOL_NAME = "time.get_current_time"


def get_current_time(timezone: str = "UTC") -> dict[str, str]:
    tz = ZoneInfo(timezone) if timezone else UTC
    now = datetime.now(tz)
    return {
        "timezone": timezone or "UTC",
        "iso_time": now.isoformat(),
    }


OPENAI_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": TOOL_NAME,
        "description": "Get the current time in an IANA timezone. Defaults to UTC.",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "IANA timezone such as America/Los_Angeles or UTC.",
                }
            },
            "additionalProperties": False,
        },
    },
}
