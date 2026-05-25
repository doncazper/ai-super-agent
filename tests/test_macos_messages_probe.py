from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Sequence

from agent.config.loader import load_capabilities_config
from agent.core.tool_broker import ToolBroker
from agent.messaging.macos_probe import last_probe_result, run_macos_messages_probe
from agent.safety.approvals import ApprovalManager
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry
from agent.ui.connectors import connector_status


def _completed(command: Sequence[str], stdout: str = "", stderr: str = "", returncode: int = 0) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(list(command), returncode=returncode, stdout=stdout, stderr=stderr)


def _call(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    return {
        "id": f"call_{tool_name}",
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments)},
    }


def _broker(tmp_path: Path) -> ToolBroker:
    capabilities = {"messages.probe": Capability("messages.probe", RiskLevel.LOW, default_enabled=True)}
    return ToolBroker(
        default_registry(project_root=tmp_path),
        PolicyEngine(capabilities),
        AuditLogger(tmp_path / "audit.jsonl"),
        session_id="macos-probe-test",
        model="test-model",
        route="test",
        approval_manager=ApprovalManager(),
    )


def test_non_mac_returns_unsupported(tmp_path: Path) -> None:
    result, path = run_macos_messages_probe(project_root=tmp_path, platform_name="Linux")

    assert result.supported is False
    assert result.platform == "Linux"
    assert result.messages_app_found is False
    assert result.send_executed is False
    assert result.private_messages_db_accessed is False
    assert Path(path).exists()


def test_mac_mock_returns_unknown_with_read_only_metadata(tmp_path: Path, monkeypatch) -> None:
    app_path = tmp_path / "Messages.app"
    app_path.mkdir()
    monkeypatch.setattr("agent.messaging.macos_probe.shutil.which", lambda _: "/usr/bin/osascript")

    def runner(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        script = command[-1]
        if script.startswith("id of application"):
            return _completed(command, stdout="com.apple.MobileSMS\n")
        return _completed(command, stdout="14.0\n")

    result, _ = run_macos_messages_probe(
        project_root=tmp_path,
        platform_name="Darwin",
        app_paths=[str(app_path)],
        runner=runner,
    )

    assert result.supported == "unknown"
    assert result.messages_app_found is True
    assert result.applescript_read_only_probe_ok is True
    assert result.applescript_bundle_id == "com.apple.MobileSMS"
    assert result.send_capability_known is False
    assert result.send_executed is False
    assert result.message_content_read is False


def test_permission_denied_returns_setup_instructions(tmp_path: Path, monkeypatch) -> None:
    app_path = tmp_path / "Messages.app"
    app_path.mkdir()
    monkeypatch.setattr("agent.messaging.macos_probe.shutil.which", lambda _: "/usr/bin/osascript")

    def runner(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        return _completed(command, stderr="Not authorized to send Apple events to Messages. (-1743)", returncode=1)

    result, _ = run_macos_messages_probe(
        project_root=tmp_path,
        platform_name="Darwin",
        app_paths=[str(app_path)],
        runner=runner,
        explain_permissions=True,
    )

    assert result.automation_permission_status == "denied_or_not_granted"
    assert result.requires_user_setup is True
    assert any("Privacy & Security > Automation" in step for step in result.next_steps)
    assert all("Full Disk Access" not in limitation for limitation in result.limitations)


def test_probe_does_not_call_send_or_private_messages_path(tmp_path: Path, monkeypatch) -> None:
    app_path = tmp_path / "Messages.app"
    app_path.mkdir()
    monkeypatch.setattr("agent.messaging.macos_probe.shutil.which", lambda _: "/usr/bin/osascript")
    commands: list[str] = []

    def runner(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        commands.append(" ".join(command))
        return _completed(command, stdout="ok\n")

    result, _ = run_macos_messages_probe(
        project_root=tmp_path,
        platform_name="Darwin",
        app_paths=[str(app_path)],
        runner=runner,
    )

    combined = "\n".join(commands + result.commands_run).lower()
    assert "send" not in combined
    assert "library/messages" not in combined
    assert "~/library/messages" not in combined
    assert result.full_disk_access_required is False
    assert result.private_messages_db_accessed is False


def test_result_serialized_for_connector_status(tmp_path: Path, monkeypatch) -> None:
    app_path = tmp_path / "Messages.app"
    app_path.mkdir()
    monkeypatch.setattr("agent.messaging.macos_probe.shutil.which", lambda _: "/usr/bin/osascript")

    result, path = run_macos_messages_probe(
        project_root=tmp_path,
        platform_name="Darwin",
        app_paths=[str(app_path)],
        runner=lambda command: _completed(command, stdout="ok\n"),
    )

    saved = json.loads(Path(path).read_text(encoding="utf-8"))
    assert saved["send_capability_known"] is False
    assert saved["send_executed"] is False
    assert last_probe_result(tmp_path)["platform"] == result.platform


def test_brokered_probe_writes_audit_log(tmp_path: Path) -> None:
    broker = _broker(tmp_path)
    result = broker.execute(_call("messages.probe", {"explain_permissions": True}))

    payload = json.loads(result.content)
    audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
    assert result.allowed is True
    assert payload["probe"]["send_executed"] is False
    assert payload["probe"]["private_messages_db_accessed"] is False
    assert payload["connector_status_recorded"] is True
    assert "messages.probe" in audit_text
    assert "no private database read and no send executed" in audit_text


def test_capability_manifest_tracks_probe_safety() -> None:
    tool = load_capabilities_config()["tools"]["messages.probe"]

    assert tool["default_enabled"] is True
    assert tool["risk_level"] == "LOW"
    assert tool["approval_required"] is False
    assert tool["sends_message"] is False
    assert tool["reads_private_app_data"] is False


def test_probe_does_not_enable_messages_connector_by_default(tmp_path: Path, monkeypatch) -> None:
    config = load_capabilities_config(Path(__file__).resolve().parents[1] / "config" / "capabilities.yaml")
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "macos_messages_probe.json").write_text(
        json.dumps({"send_capability_known": False, "private_messages_db_accessed": False}),
        encoding="utf-8",
    )

    status = connector_status("messages", config=config)

    assert status["enabled"] is False
    assert status["configured"] is False
    assert status["macos_probe"]["send_capability_known"] is False
