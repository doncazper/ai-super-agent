from __future__ import annotations

from agent.runtime.models import RuntimeStatus
from agent.runtime.state import RuntimeState, redact_runtime_value


def test_runtime_state_boot_stop() -> None:
    state = RuntimeState()
    state.boot()
    assert state.status == RuntimeStatus.READY
    assert state.started_at
    state.stop()
    assert state.status == RuntimeStatus.STOPPED


def test_runtime_state_redacts_metadata() -> None:
    state = RuntimeState(metadata={"api_key": "super-secret", "nested": {"token": "abc123"}})
    data = state.to_dict()
    assert data["metadata"]["api_key"] == "[REDACTED]"
    assert data["metadata"]["nested"]["token"] == "[REDACTED]"


def test_redact_runtime_value_redacts_secret_text() -> None:
    assert "[REDACTED]" in redact_runtime_value("token=abc123")

