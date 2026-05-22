from __future__ import annotations

import json

import pytest

from agent.config.schema import CapabilityConfigError, validate_capabilities_config
from agent.safety.approvals import ApprovalRequest
from agent.safety.policy import RiskLevel
from agent.ui.approvals_ui import ConsoleApprovalPrompt
from agent.ui.audit_viewer import tail_audit
from agent.ui.cli_commands import dispatch_cli
from agent.ui.permissions_dashboard import PermissionStore


def test_cli_tools_list_command_works(capsys) -> None:
    result = dispatch_cli(["tools", "list"])

    output = capsys.readouterr().out
    assert result == 0
    assert "time.get_current_time" in output
    assert "web.fetch_url" in output


def test_approval_prompt_blocks_critical_until_approved() -> None:
    prompt = ConsoleApprovalPrompt()
    request = ApprovalRequest(
        capability="email.send_approved",
        tool_name="email.send_approved",
        risk_level=RiskLevel.CRITICAL,
        summary="preflight",
        per_action=True,
    )

    assert prompt.prompt(request).value == "denied"
    assert prompt.prompt(request, response="deny").value == "denied"
    assert prompt.prompt(request, response="approve").value == "approved"


def test_audit_viewer_displays_entries(tmp_path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    audit_path.write_text('{"tool_name": "time.get_current_time"}\n', encoding="utf-8")

    entries = tail_audit(audit_path)

    assert entries == [{"tool_name": "time.get_current_time"}]


def test_permission_grant_revoke_works(tmp_path) -> None:
    store = PermissionStore(tmp_path / "permissions.json")

    assert store.show() == []
    assert store.grant("web.fetch_url") == ["web.fetch_url"]
    assert store.revoke("web.fetch_url") == []


def test_cli_permissions_command_works(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    assert dispatch_cli(["permissions", "grant", "web.fetch_url"]) == 0
    assert dispatch_cli(["permissions", "show"]) == 0

    output = capsys.readouterr().out
    assert "web.fetch_url" in output


def test_config_validator_rejects_dangerous_config() -> None:
    with pytest.raises(CapabilityConfigError):
        validate_capabilities_config(
            {
                "tools": {
                    "email.send_approved": {
                        "risk_level": "CRITICAL",
                        "default_enabled": True,
                        "approval_required": False,
                    }
                }
            }
        )


def test_cli_audit_tail_command_works(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "audit.jsonl").write_text('{"tool_name": "git.status"}\n', encoding="utf-8")

    assert dispatch_cli(["audit", "tail"]) == 0

    output = capsys.readouterr().out
    assert "git.status" in output


def test_cli_memory_list_command_works(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    assert dispatch_cli(["memory", "list"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["records"] == []
