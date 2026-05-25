from __future__ import annotations

from agent.runtime.scheduler import SchedulerPolicy


def test_scheduler_allows_safe_manual_run_only() -> None:
    decision = SchedulerPolicy().evaluate("diagnostics", "SAFE")
    assert decision.allowed is True
    assert decision.status == "manual_run_only"
    assert decision.background_persistence is False


def test_scheduler_blocks_background_persistence() -> None:
    decision = SchedulerPolicy().evaluate("diagnostics", background_persistence=True)
    assert decision.allowed is False
    assert "persistence" in decision.reason


def test_scheduler_blocks_critical_actions() -> None:
    decision = SchedulerPolicy().evaluate("email_send", "CRITICAL")
    assert decision.allowed is False
    assert decision.approval_required is True


def test_scheduler_requires_approval_for_personal_data() -> None:
    decision = SchedulerPolicy().evaluate("briefing", "HIGH", personal_data=True)
    assert decision.allowed is False
    assert decision.status == "approval_required"

