from __future__ import annotations

import json

from agent.sandbox.models import SandboxRequest
from agent.sandbox.policy import sandbox_policy_summary, validate_sandbox_request
from agent.sandbox.registry import default_sandbox_registry
from agent.tools.registry import default_registry
from smart_agent import main


def test_mock_backend_works() -> None:
    backend = default_sandbox_registry().get("mock")
    result = backend.dry_run(SandboxRequest())

    assert result.status == "dry_run"
    assert result.allowed is True
    assert result.tools_executed == []
    assert result.network_used is False
    assert result.personal_data_accessed is False


def test_unknown_backend_denied() -> None:
    try:
        default_sandbox_registry().get("missing")
    except Exception as exc:
        assert "unknown sandbox backend" in str(exc)
    else:
        raise AssertionError("unknown sandbox backend should be denied")


def test_network_disabled_by_default() -> None:
    allowed, reason = validate_sandbox_request(SandboxRequest(network_allowed=True))
    assert allowed is False
    assert "network is disabled" in reason


def test_personal_data_disabled() -> None:
    allowed, reason = validate_sandbox_request(SandboxRequest(personal_data_allowed=True))
    assert allowed is False
    assert "personal data is disabled" in reason


def test_arbitrary_command_rejected() -> None:
    allowed, reason = validate_sandbox_request(SandboxRequest(command="python untrusted.py"))
    assert allowed is False
    assert "arbitrary command execution is disabled" in reason


def test_planned_backend_returns_setup_stub() -> None:
    backend = default_sandbox_registry().get("docker_rootless")
    result = backend.dry_run(SandboxRequest(sandbox_id="docker_rootless"))

    assert result.allowed is False
    assert result.status == "requires_setup"
    assert "planned" in result.reason


def test_filesystem_roots_workspace_only() -> None:
    allowed, reason = validate_sandbox_request(SandboxRequest(filesystem_roots=["/Users/example"]))
    assert allowed is False
    assert "outside the approved workspace scope" in reason


def test_policy_summary_safe_defaults() -> None:
    summary = sandbox_policy_summary()
    assert summary["default_backend"] == "mock"
    assert summary["execution_enabled"] is False
    assert summary["network_default"] is False
    assert summary["personal_data_default"] is False
    assert summary["toolbroker_required"] is True


def test_sandbox_tools_registered() -> None:
    registry = default_registry(project_root=".")
    for tool_name in ("sandbox.backends", "sandbox.policy", "sandbox.dry_run"):
        spec = registry.get(tool_name)
        assert spec is not None
        assert spec.capability == tool_name


def test_sandbox_cli_smoke(capsys) -> None:
    code = main(["sandbox", "dry-run"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert code == 0
    assert payload["status"] == "dry_run"
    assert payload["command_executed"] is False
    assert payload["toolbroker_required"] is True
