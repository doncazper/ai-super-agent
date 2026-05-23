from __future__ import annotations

import json

from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry
from agent.ui.cli_commands import dispatch_cli
from agent.ui.preflight import PreflightOptions, run_preflight


def test_preflight_identifies_high_risk_capability_without_execution(tmp_path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    report = run_preflight(
        PreflightOptions("email.read_selected_thread", project_root=tmp_path),
        registry=default_registry(project_root=tmp_path),
        policy_engine=PolicyEngine(
            {
                "email.read_selected_thread": Capability(
                    "email.read_selected_thread",
                    RiskLevel.HIGH,
                    default_enabled=True,
                    approval_required=True,
                )
            }
        ),
        audit_logger=AuditLogger(audit_path),
    )

    tool = report["tools"][0]
    assert report["dry_run"] is True
    assert tool["tool_name"] == "email.read_selected_thread"
    assert tool["risk_level"] == "HIGH"
    assert tool["approval_required"] is True
    assert tool["would_execute"] is False
    assert tool["arguments_known"] is False
    event = json.loads(audit_path.read_text(encoding="utf-8").splitlines()[0])
    assert event["dry_run"] is True
    assert event["tool_name"] == "email.read_selected_thread"


def test_preflight_blocks_critical_without_exact_args(tmp_path) -> None:
    report = run_preflight(
        PreflightOptions("email.send_approved", project_root=tmp_path),
        registry=default_registry(project_root=tmp_path),
        policy_engine=PolicyEngine(
            {
                "email.send_approved": Capability(
                    "email.send_approved",
                    RiskLevel.CRITICAL,
                    default_enabled=True,
                    approval_required="per_action",
                    approval_reuse_allowed=False,
                )
            }
        ),
        audit_logger=AuditLogger(tmp_path / "audit.jsonl"),
    )

    tool = report["tools"][0]
    assert tool["risk_level"] == "CRITICAL"
    assert tool["approval_required"] is True
    assert tool["approval_type"] == "per_action"
    assert tool["would_execute"] is False
    assert "critical action preview missing exact args" in tool["error"]


def test_preflight_routes_weather_request_with_sanitized_location(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("WEATHER_DEFAULT_LOCATION", "")
    report = run_preflight(
        PreflightOptions("What's the weather in Phoenix?", project_root=tmp_path),
        registry=default_registry(project_root=tmp_path),
        policy_engine=PolicyEngine(
            {
                "weather.current": Capability("weather.current", RiskLevel.LOW, default_enabled=True),
                "weather.forecast": Capability("weather.forecast", RiskLevel.LOW, default_enabled=True),
            }
        ),
        audit_logger=AuditLogger(tmp_path / "audit.jsonl"),
    )

    assert report["route"]["name"] == "tool.weather"
    assert {tool["tool_name"] for tool in report["tools"]} == {"weather.current", "weather.forecast"}
    for tool in report["tools"]:
        assert tool["would_execute"] is True
        assert tool["sanitized_args"]["location"] == "[WEATHER_LOCATION_REDACTED]"


def test_preflight_non_tool_request_attaches_no_tools(tmp_path) -> None:
    report = run_preflight(
        PreflightOptions("Write a poem about rain.", project_root=tmp_path),
        registry=default_registry(project_root=tmp_path),
        policy_engine=PolicyEngine(),
        audit_logger=AuditLogger(tmp_path / "audit.jsonl"),
    )

    assert report["route"]["use_tools"] is False
    assert report["tools"] == []
    assert report["notes"] == ["No tools would be attached for this request."]


def test_preflight_command_dispatches(monkeypatch, capsys) -> None:
    from agent.ui import cli_commands

    monkeypatch.setattr(
        cli_commands,
        "run_preflight",
        lambda options: {"status": "ok", "dry_run": True, "request": options.request, "tools": []},
    )

    assert dispatch_cli(["preflight", "email.read_selected_thread"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["request"] == "email.read_selected_thread"
