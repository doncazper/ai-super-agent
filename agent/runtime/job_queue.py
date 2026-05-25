from __future__ import annotations

import itertools
from dataclasses import replace

from .errors import RuntimeUnavailableError
from .models import RuntimeJobInfo, RuntimeJobStatus, now_iso


class JobQueue:
    def __init__(self) -> None:
        self._counter = itertools.count(1)
        self._jobs: dict[str, RuntimeJobInfo] = {}

    def create_job(self, workflow_id: str, risk_level: str = "SAFE", approval_required: bool = False, reason: str = "") -> RuntimeJobInfo:
        status = RuntimeJobStatus.QUEUED
        if risk_level == "CRITICAL":
            status = RuntimeJobStatus.BLOCKED
            approval_required = True
            reason = reason or "CRITICAL jobs cannot run automatically in runtime v1."
        elif risk_level == "HIGH" or approval_required:
            status = RuntimeJobStatus.APPROVAL_REQUIRED
            approval_required = True
            reason = reason or "Approval required before this job can run."
        job = RuntimeJobInfo(
            job_id=f"job_{next(self._counter):06d}",
            workflow_id=workflow_id,
            status=status,
            risk_level=risk_level,
            approval_required=approval_required,
            reason=reason,
        )
        self._jobs[job.job_id] = job
        return job

    def list_jobs(self) -> tuple[RuntimeJobInfo, ...]:
        return tuple(self._jobs[key] for key in sorted(self._jobs))

    def get(self, job_id: str) -> RuntimeJobInfo:
        try:
            return self._jobs[job_id]
        except KeyError as exc:
            raise RuntimeUnavailableError(f"unknown job: {job_id}") from exc

    def update_status(self, job_id: str, status: RuntimeJobStatus, result_summary: str = "") -> RuntimeJobInfo:
        current = self.get(job_id)
        if current.risk_level == "CRITICAL" and status == RuntimeJobStatus.RUNNING:
            updated = replace(current, status=RuntimeJobStatus.BLOCKED, reason="CRITICAL jobs cannot run automatically in runtime v1.", updated_at=now_iso())
        else:
            updated = replace(current, status=status, result_summary=result_summary or current.result_summary, updated_at=now_iso())
        self._jobs[job_id] = updated
        return updated

