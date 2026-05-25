from __future__ import annotations

import itertools
from collections.abc import Callable
from typing import Any

from .errors import RuntimePolicyBlockedError
from .models import RuntimeEvent, now_iso
from .state import redact_runtime_value


FORBIDDEN_UNTRUSTED_EVENT_PARTS = ("policy", "permission", "approval", "tool.execute", "send")


class EventBus:
    def __init__(self) -> None:
        self._counter = itertools.count(1)
        self._events: list[RuntimeEvent] = []
        self._subscribers: list[Callable[[RuntimeEvent], None]] = []

    def subscribe(self, callback: Callable[[RuntimeEvent], None]) -> None:
        self._subscribers.append(callback)

    def publish(self, event_type: str, source: str, payload: dict[str, Any] | None = None, trust_level: str = "LOCAL_PRIVATE_DATA metadata") -> RuntimeEvent:
        if trust_level.startswith("UNTRUSTED") and any(part in event_type for part in FORBIDDEN_UNTRUSTED_EVENT_PARTS):
            raise RuntimePolicyBlockedError(f"untrusted event cannot control runtime policy or approvals: {event_type}")
        event = RuntimeEvent(
            event_id=f"evt_{next(self._counter):06d}",
            event_type=event_type,
            source=source,
            payload=redact_runtime_value(payload or {}),
            trust_level=trust_level,
            created_at=now_iso(),
        )
        self._events.append(event)
        for callback in list(self._subscribers):
            callback(event)
        return event

    def tail(self, limit: int = 20) -> tuple[RuntimeEvent, ...]:
        return tuple(self._events[-limit:])

