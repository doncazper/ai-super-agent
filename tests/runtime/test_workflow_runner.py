from __future__ import annotations

import pytest

from agent.runtime.errors import RuntimePolicyBlockedError, RuntimeUnavailableError
from agent.runtime.models import RuntimeJobStatus
from agent.runtime.workflow_runner import WorkflowRunner


def test_workflow_runner_creates_safe_metadata_job_only() -> None:
    runner = WorkflowRunner()
    runner.register_defaults()

    job = runner.start("connector_doctor")

    assert job.status == RuntimeJobStatus.QUEUED
    assert job.workflow_id == "connector_doctor"


def test_critical_workflow_is_blocked_job() -> None:
    runner = WorkflowRunner()
    runner.register_defaults()

    job = runner.start("email_send")

    assert job.status == RuntimeJobStatus.BLOCKED
    assert job.approval_required is True


def test_unknown_workflow_rejected() -> None:
    runner = WorkflowRunner()

    with pytest.raises(RuntimeUnavailableError):
        runner.start("missing")


def test_blocked_noncritical_workflow_rejected() -> None:
    runner = WorkflowRunner()
    runner.register_defaults()
    workflow = runner.get("email_send")
    object.__setattr__(workflow, "risk_level", "HIGH")

    with pytest.raises(RuntimePolicyBlockedError):
        runner.start("email_send")

