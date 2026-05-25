from __future__ import annotations

from agent.ui.cli_commands import dispatch_cli


def test_runtime_status_cli_does_not_require_lmstudio(capsys) -> None:
    code = dispatch_cli(["runtime", "status"])
    output = capsys.readouterr().out
    assert code == 0
    assert '"lmstudio_checked": false' in output
    assert '"personal_data_accessed": false' in output


def test_runtime_doctor_cli_reports_no_background(capsys) -> None:
    code = dispatch_cli(["runtime", "doctor"])
    output = capsys.readouterr().out
    assert code == 0
    assert '"background_persistence": false' in output


def test_runtime_services_and_features_cli(capsys) -> None:
    assert dispatch_cli(["runtime", "services"]) == 0
    assert '"service_id": "core"' in capsys.readouterr().out
    assert dispatch_cli(["runtime", "features"]) == 0
    assert '"feature_id": "email.send"' in capsys.readouterr().out


def test_jobs_and_events_cli(capsys) -> None:
    assert dispatch_cli(["jobs", "list"]) == 0
    assert '"jobs": []' in capsys.readouterr().out
    assert dispatch_cli(["events", "tail"]) == 0
    assert '"runtime.started"' in capsys.readouterr().out


def test_workflows_run_safe_only_metadata_job(capsys) -> None:
    assert dispatch_cli(["workflows", "run", "connector_doctor"]) == 0
    output = capsys.readouterr().out
    assert '"tool_execution": false' in output
    assert '"workflow_id": "connector_doctor"' in output


def test_workflows_run_critical_blocked(capsys) -> None:
    code = dispatch_cli(["workflows", "run", "email_send"])
    output = capsys.readouterr().out
    assert code == 2
    assert '"status": "blocked"' in output

