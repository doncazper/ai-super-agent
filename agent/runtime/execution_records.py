from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from .models import now_iso
from .state import redact_runtime_value


class ExecutionRecordStatus(str, Enum):
    QUEUED = "queued"
    ACTIVE = "active"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    SUPERSEDED = "superseded"
    NEEDS_REVIEW = "needs_review"


class ExecutionRecordType(str, Enum):
    PROMPT_RUN = "prompt_run"
    PROMPT_PACK_RUN = "prompt_pack_run"
    JOB_RUN = "job_run"
    WORKFLOW_RUN = "workflow_run"
    COMMAND_RUN = "command_run"
    APPROVAL_GATED_RESUME = "approval_gated_resume"
    QA_RUN = "qa_run"
    SELF_HEAL_RUN = "self_heal_run"
    MEDIA_GENERATION_RUN = "media_generation_run"
    SECRET_SCAN_RUN = "secret_scan_run"


@dataclass(frozen=True)
class DurableExecutionRecord:
    record_id: str
    record_type: ExecutionRecordType
    status: ExecutionRecordStatus = ExecutionRecordStatus.QUEUED
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)
    started_at: str = ""
    completed_at: str = ""
    branch: str = ""
    commit_hash: str = ""
    prompt_id: str = ""
    prompt_pack_id: str = ""
    command: str = ""
    args_redacted: dict[str, Any] = field(default_factory=dict)
    risk_level: str = "SAFE"
    approval_required: bool = False
    approval_id: str = ""
    toolbroker_required: bool = True
    audit_ids: tuple[str, ...] = ()
    input_hash: str = ""
    output_hash: str = ""
    artifact_hashes: dict[str, str] = field(default_factory=dict)
    checkpoint_ids: tuple[str, ...] = ()
    resume_command: str = ""
    rollback_plan: str = ""
    blocked_reason: str = ""
    evidence_paths: tuple[str, ...] = ()
    test_results: tuple[str, ...] = ()
    docs_updated: tuple[str, ...] = ()
    next_record_id: str = ""

    def __post_init__(self) -> None:
        if not self.record_id:
            raise ValueError("record_id is required")
        if self.risk_level in {"HIGH", "CRITICAL"} and not self.approval_required:
            raise ValueError("HIGH/CRITICAL execution records must require approval")
        if self.record_type == ExecutionRecordType.APPROVAL_GATED_RESUME and not self.approval_required:
            raise ValueError("approval-gated resume records must require approval")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["record_type"] = self.record_type.value
        data["status"] = self.status.value
        for key in ("audit_ids", "checkpoint_ids", "evidence_paths", "test_results", "docs_updated"):
            data[key] = list(data[key])
        return redact_runtime_value(data)


class PromptRunRecord(DurableExecutionRecord):
    pass


class PromptPackRunRecord(DurableExecutionRecord):
    pass


class JobRunRecord(DurableExecutionRecord):
    pass


class WorkflowRunRecord(DurableExecutionRecord):
    pass


class CommandRunRecord(DurableExecutionRecord):
    pass


class ApprovalGatedResumeRecord(DurableExecutionRecord):
    pass


class QARunRecord(DurableExecutionRecord):
    pass


class SelfHealRunRecord(DurableExecutionRecord):
    pass


class MediaGenerationRunRecord(DurableExecutionRecord):
    pass


class SecretScanRunRecord(DurableExecutionRecord):
    pass


def stable_record_hash(payload: Any) -> str:
    safe_payload = redact_runtime_value(payload)
    encoded = json.dumps(safe_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def execution_record_schema() -> dict[str, Any]:
    return {
        "record_types": [item.value for item in ExecutionRecordType],
        "statuses": [item.value for item in ExecutionRecordStatus],
        "required_fields": [
            "record_id",
            "record_type",
            "status",
            "created_at",
            "updated_at",
            "branch",
            "commit_hash",
            "risk_level",
            "approval_required",
            "toolbroker_required",
            "audit_ids",
            "input_hash",
            "output_hash",
            "artifact_hashes",
            "checkpoint_ids",
            "resume_command",
            "rollback_plan",
            "evidence_paths",
            "test_results",
            "docs_updated",
            "next_record_id",
        ],
        "storage_policy": "future writers must store redacted metadata only; raw secrets and personal data are forbidden by default",
    }


def validate_execution_record_dict(record: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    for field_name in execution_record_schema()["required_fields"]:
        if field_name not in record:
            problems.append(f"missing required field: {field_name}")
    if record.get("record_type") not in {item.value for item in ExecutionRecordType}:
        problems.append("invalid record_type")
    if record.get("status") not in {item.value for item in ExecutionRecordStatus}:
        problems.append("invalid status")
    risk = str(record.get("risk_level", ""))
    if risk in {"HIGH", "CRITICAL"} and not bool(record.get("approval_required")):
        problems.append("HIGH/CRITICAL records must require approval")
    if _contains_secret_like_value(record):
        problems.append("record contains secret-like raw value")
    return problems


def load_execution_records(project_root: str | Path = ".") -> list[dict[str, Any]]:
    records_dir = Path(project_root) / "reports" / "runtime" / "records"
    if not records_dir.exists():
        return []
    records: list[dict[str, Any]] = []
    for path in sorted(records_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {"record_id": path.stem, "record_type": "invalid", "status": "needs_review", "load_error": True}
        if isinstance(payload, dict):
            payload.setdefault("evidence_paths", [])
            payload["source_path"] = str(path)
            records.append(redact_runtime_value(payload))
    return records


def list_execution_records(project_root: str | Path = ".") -> dict[str, Any]:
    records = load_execution_records(project_root)
    return {
        "status": "ok",
        "record_count": len(records),
        "records": records,
        "storage_path": "reports/runtime/records",
        "side_effects": "none; read-only record listing",
    }


def latest_execution_record(project_root: str | Path = ".") -> dict[str, Any]:
    records = load_execution_records(project_root)
    if not records:
        return {
            "status": "empty",
            "record": None,
            "storage_path": "reports/runtime/records",
            "side_effects": "none; read-only record lookup",
        }
    return {"status": "ok", "record": records[-1], "side_effects": "none; read-only record lookup"}


def show_execution_record(record_id: str, project_root: str | Path = ".") -> dict[str, Any]:
    for record in load_execution_records(project_root):
        if record.get("record_id") == record_id:
            return {"status": "ok", "record": record, "side_effects": "none; read-only record lookup"}
    return {"status": "not_found", "record_id": record_id, "side_effects": "none; read-only record lookup"}


def validate_execution_records(project_root: str | Path = ".") -> dict[str, Any]:
    invalid: list[dict[str, Any]] = []
    for record in load_execution_records(project_root):
        problems = validate_execution_record_dict(record)
        if problems:
            invalid.append({"record_id": record.get("record_id", "unknown"), "problems": problems})
    return {
        "status": "ok" if not invalid else "needs_review",
        "invalid_records": invalid,
        "schema": execution_record_schema(),
        "side_effects": "none; read-only validation",
    }


def _contains_secret_like_value(value: Any) -> bool:
    if isinstance(value, str):
        lowered = value.lower()
        return any(marker in lowered for marker in ("sk-", "private key", "begin openssh", "password=", "token="))
    if isinstance(value, dict):
        return any(_contains_secret_like_value(k) or _contains_secret_like_value(v) for k, v in value.items())
    if isinstance(value, list | tuple):
        return any(_contains_secret_like_value(item) for item in value)
    return False
