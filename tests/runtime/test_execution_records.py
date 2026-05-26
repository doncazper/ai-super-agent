from __future__ import annotations

import json

import pytest

from agent.runtime.execution_records import (
    CommandRunRecord,
    DurableExecutionRecord,
    ExecutionRecordStatus,
    ExecutionRecordType,
    stable_record_hash,
    validate_execution_record_dict,
)
from agent.ui.cli_commands import dispatch_cli


def test_execution_record_serializes_and_redacts() -> None:
    record = CommandRunRecord(
        record_id="rec_001",
        record_type=ExecutionRecordType.COMMAND_RUN,
        status=ExecutionRecordStatus.COMPLETED,
        command="python smart_agent.py runtime records validate",
        args_redacted={"api_key": "sk-example-secret"},
        input_hash=stable_record_hash({"request": "runtime records validate"}),
        output_hash=stable_record_hash({"status": "ok"}),
        evidence_paths=("docs/runtime/DURABLE_EXECUTION_RECORDS.md",),
        test_results=("tests/runtime/test_execution_records.py passed",),
    )

    payload = record.to_dict()

    assert payload["record_type"] == "command_run"
    assert payload["status"] == "completed"
    assert payload["args_redacted"]["api_key"] == "[REDACTED]"
    json.dumps(payload)


def test_high_risk_record_requires_approval() -> None:
    with pytest.raises(ValueError):
        DurableExecutionRecord(
            record_id="rec_high",
            record_type=ExecutionRecordType.WORKFLOW_RUN,
            risk_level="HIGH",
            approval_required=False,
        )


def test_validation_rejects_missing_fields_and_unapproved_high_risk() -> None:
    problems = validate_execution_record_dict(
        {
            "record_id": "rec_bad",
            "record_type": "command_run",
            "status": "completed",
            "risk_level": "HIGH",
            "approval_required": False,
        }
    )

    assert "HIGH/CRITICAL records must require approval" in problems
    assert any(problem.startswith("missing required field") for problem in problems)


def test_validation_rejects_secret_like_raw_values() -> None:
    record = CommandRunRecord(
        record_id="rec_secret",
        record_type=ExecutionRecordType.SECRET_SCAN_RUN,
        status=ExecutionRecordStatus.NEEDS_REVIEW,
        args_redacted={"token": "sk-rawsecretvalue"},
    ).to_dict()

    assert "sk-rawsecretvalue" not in json.dumps(record)


def test_runtime_records_cli_empty_and_validate(capsys) -> None:
    assert dispatch_cli(["runtime", "records", "list"]) == 0
    output = capsys.readouterr().out
    assert '"record_count":' in output
    assert '"side_effects": "none; read-only record listing"' in output

    assert dispatch_cli(["runtime", "records", "latest"]) == 0
    output = capsys.readouterr().out
    assert '"side_effects": "none; read-only record lookup"' in output

    assert dispatch_cli(["runtime", "records", "validate"]) == 0
    output = capsys.readouterr().out
    assert '"required_fields"' in output
    assert '"side_effects": "none; read-only validation"' in output


def test_runtime_records_show_unknown(capsys) -> None:
    assert dispatch_cli(["runtime", "records", "show", "missing"]) == 0
    output = capsys.readouterr().out
    assert '"status": "not_found"' in output
