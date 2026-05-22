from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from time import monotonic


@dataclass
class RateLimiter:
    requests_per_minute: int
    _events: dict[str, deque[float]] = field(default_factory=lambda: defaultdict(deque))

    def allow(self, key: str) -> bool:
        now = monotonic()
        window_start = now - 60
        events = self._events[key]
        while events and events[0] < window_start:
            events.popleft()
        if len(events) >= self.requests_per_minute:
            return False
        events.append(now)
        return True
