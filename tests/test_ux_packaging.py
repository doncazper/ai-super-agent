from __future__ import annotations

import json

import pytest

from agent.config.runtime import RuntimeConfig
from agent.config.schema import CapabilityConfigError, validate_capabilities_config
from agent.safety.approvals import ApprovalRequest
from agent.safety.policy import RiskLevel
from agent.ui.approvals_ui import ConsoleApprovalPrompt
from agent.ui.audit_viewer import tail_audit
from agent.ui.cli_commands import dispatch_cli
from agent.ui.doctor import doctor_exit_code, run_doctor
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


def test_doctor_with_mocked_lmstudio_reachable(tmp_path) -> None:
    config = RuntimeConfig(
        lmstudio_base_url="http://localhost:1234/v1",
        lmstudio_model="qwopus",
        audit_log_path=str(tmp_path / "audit.jsonl"),
    )

    checks = run_doctor(
        config=config,
        get_json=lambda url: {"data": [{"id": "qwopus"}]},
    )

    by_name = {check.name: check for check in checks}
    assert by_name["lmstudio_server"].status == "ok"
    assert by_name["selected_model_available"].status == "ok"
    assert by_name["startup_policy"].status == "ok"
    assert by_name["audit_log_path_writable"].status == "ok"
    assert by_name["personal_tools_disabled"].status == "ok"
    assert doctor_exit_code(checks) == 0


def test_doctor_with_lmstudio_unavailable(tmp_path) -> None:
    config = RuntimeConfig(
        lmstudio_base_url="http://localhost:1234/v1",
        lmstudio_model="qwopus",
        audit_log_path=str(tmp_path / "audit.jsonl"),
    )

    def fail(url: str):
        raise ConnectionError("no server")

    checks = run_doctor(config=config, get_json=fail)
    by_name = {check.name: check for check in checks}

    assert by_name["lmstudio_server"].status == "fail"
    assert doctor_exit_code(checks) == 1


def test_doctor_reports_missing_model(tmp_path) -> None:
    config = RuntimeConfig(
        lmstudio_base_url="http://localhost:1234/v1",
        lmstudio_model="",
        audit_log_path=str(tmp_path / "audit.jsonl"),
    )

    checks = run_doctor(config=config, get_json=lambda url: {"data": []})
    by_name = {check.name: check for check in checks}

    assert by_name["lmstudio_model"].status == "fail"


def test_doctor_command_can_be_dispatched(monkeypatch, capsys) -> None:
    from agent.ui import cli_commands
    from agent.ui.doctor import DoctorCheck

    monkeypatch.setattr(cli_commands, "run_doctor", lambda: [DoctorCheck("config_loaded", "ok", "loaded")])

    assert dispatch_cli(["doctor"]) == 0
    assert "[ok] config_loaded" in capsys.readouterr().out


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
