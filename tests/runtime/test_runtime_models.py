from __future__ import annotations

import pytest

from agent.runtime.models import (
    RuntimeFeatureInfo,
    RuntimeFeatureStatus,
    RuntimeJobInfo,
    RuntimeJobStatus,
    RuntimeMode,
    RuntimeServiceInfo,
    RuntimeServiceStatus,
    RuntimeStateSnapshot,
    RuntimeStatus,
    RuntimeWorkflowInfo,
)


def test_runtime_models_serialize_to_primitives() -> None:
    service = RuntimeServiceInfo("core", "Core", RuntimeServiceStatus.AVAILABLE)
    feature = RuntimeFeatureInfo("runtime.status", "Runtime status", RuntimeFeatureStatus.ENABLED, enabled_by_default=True)
    workflow = RuntimeWorkflowInfo("doctor", "Doctor")
    job = RuntimeJobInfo("job_1", "doctor")
    snapshot = RuntimeStateSnapshot(RuntimeMode.CLI, RuntimeStatus.READY, (service,), (feature,), (workflow,), (job,))

    data = snapshot.to_dict()

    assert data["mode"] == "cli"
    assert data["status"] == "ready"
    assert data["services"][0]["status"] == "available"
    assert data["features"][0]["status"] == "enabled"


def test_personal_feature_cannot_be_enabled_by_default() -> None:
    with pytest.raises(ValueError, match="personal-data"):
        RuntimeFeatureInfo("email.read", "Email read", personal_data=True, enabled_by_default=True)


def test_critical_feature_requires_approval() -> None:
    with pytest.raises(ValueError, match="critical"):
        RuntimeFeatureInfo("email.send", "Email send", critical_action=True, approval_required=False)


def test_critical_job_is_blocked_in_v1() -> None:
    with pytest.raises(ValueError, match="CRITICAL jobs"):
        RuntimeJobInfo("job_1", "email_send", RuntimeJobStatus.QUEUED, risk_level="CRITICAL")

