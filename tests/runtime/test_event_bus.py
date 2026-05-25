from __future__ import annotations

import pytest

from agent.runtime.errors import RuntimePolicyBlockedError
from agent.runtime.event_bus import EventBus


def test_event_bus_publishes_and_tails_redacted_events() -> None:
    bus = EventBus()
    seen = []
    bus.subscribe(seen.append)

    event = bus.publish("runtime.started", "test", {"api_key": "secret"})

    assert seen == [event]
    assert bus.tail(1)[0].payload["api_key"] == "[REDACTED]"


def test_untrusted_events_cannot_change_policy_or_approvals() -> None:
    bus = EventBus()

    with pytest.raises(RuntimePolicyBlockedError):
        bus.publish("approval.approve", "webpage", {}, trust_level="UNTRUSTED_WEB")

