from __future__ import annotations

from agent.runtime.kernel import RuntimeKernel


def test_kernel_boot_is_lightweight_metadata_only() -> None:
    kernel = RuntimeKernel()

    status = kernel.status()

    assert status["status"] == "ready"
    assert status["lmstudio_checked"] is False
    assert status["personal_data_accessed"] is False
    assert status["background_persistence"] is False
    assert status["services"] >= 1


def test_kernel_snapshot_contains_default_runtime_parts() -> None:
    snapshot = RuntimeKernel().snapshot().to_dict()

    service_ids = {service["service_id"] for service in snapshot["services"]}
    feature_ids = {feature["feature_id"] for feature in snapshot["features"]}
    workflow_ids = {workflow["workflow_id"] for workflow in snapshot["workflows"]}
    assert "core" in service_ids
    assert "runtime.status" in feature_ids
    assert "connector_doctor" in workflow_ids
    assert snapshot["health"]["status"] == "ok"

