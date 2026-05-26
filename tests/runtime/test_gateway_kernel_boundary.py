from __future__ import annotations

import json
import sys

from agent.runtime.gateway_state import gateway_status, normalize_gateway_request, preview_gateway_request
from agent.runtime.kernel_contract import frontend_contract, kernel_status
from agent.ui.cli_commands import dispatch_cli


def test_gateway_request_cannot_execute_tool_directly() -> None:
    envelope = normalize_gateway_request(requested_action="tool", payload={"execute_tool": "memory.search"})

    response = preview_gateway_request(envelope).to_dict()

    assert response["status"] == "blocked"
    assert response["tool_execution"] is False
    assert response["approved_by_gateway"] is False
    assert "ToolBroker" in response["summary"]


def test_approval_request_returns_requires_review() -> None:
    envelope = normalize_gateway_request(requested_action="send", risk_level="HIGH", approval_required=True)

    response = preview_gateway_request(envelope).to_dict()

    assert response["status"] == "requires_review"
    assert response["requires_review"] is True
    assert response["approved_by_gateway"] is False


def test_gateway_redacts_secrets() -> None:
    envelope = normalize_gateway_request(requested_action="status", payload={"api_key": "sk-testsecret"})

    response = preview_gateway_request(envelope).to_dict()
    dumped = json.dumps(response)

    assert "sk-testsecret" not in dumped
    assert "[REDACTED]" in dumped


def test_gateway_status_json_serializable_and_no_server() -> None:
    payload = gateway_status()

    assert payload["gateway"]["server_started"] is False
    assert payload["gateway"]["listeners_started"] is False
    assert payload["gateway"]["cli_remains_first_frontend"] is True
    json.dumps(payload)


def test_kernel_contract_owns_execution_truth_without_executor() -> None:
    payload = kernel_status()

    assert "canonical runtime state" in payload["kernel_contract"]["kernel_owns"]
    assert payload["kernel_contract"]["server_started"] is False
    assert payload["kernel_contract"]["cli_replaced"] is False
    assert payload["kernel_contract"]["tool_execution_boundary"] == "ToolBroker only"


def test_frontend_contract_keeps_cli_first_and_blocks_self_approval() -> None:
    payload = frontend_contract()

    assert payload["frontends"][0]["frontend"] == "cli"
    assert payload["frontends"][0]["status"] == "current_first_frontend"
    assert all(frontend["can_self_approve"] is False for frontend in payload["frontends"])


def test_runtime_gateway_kernel_cli_commands(capsys) -> None:
    assert dispatch_cli(["runtime", "gateway-status"]) == 0
    gateway_output = capsys.readouterr().out
    assert '"server_started": false' in gateway_output
    assert '"direct_tool_execution_allowed": false' in gateway_output

    assert dispatch_cli(["runtime", "kernel-status"]) == 0
    kernel_output = capsys.readouterr().out
    assert '"tool_execution_boundary": "ToolBroker only"' in kernel_output

    assert dispatch_cli(["runtime", "frontend-contract"]) == 0
    frontend_output = capsys.readouterr().out
    assert '"frontend": "cli"' in frontend_output


def test_no_server_modules_loaded_for_gateway_status() -> None:
    gateway_status()

    assert "fastapi" not in sys.modules
    assert "uvicorn" not in sys.modules
    assert "fastify" not in sys.modules
