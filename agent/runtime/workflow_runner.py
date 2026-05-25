from __future__ import annotations

from .errors import RuntimePolicyBlockedError, RuntimeUnavailableError
from .job_queue import JobQueue
from .models import RuntimeJobInfo, RuntimeWorkflowInfo, RuntimeWorkflowStatus


class WorkflowRunner:
    def __init__(self, job_queue: JobQueue | None = None) -> None:
        self._workflows: dict[str, RuntimeWorkflowInfo] = {}
        self.job_queue = job_queue or JobQueue()

    def register(self, workflow: RuntimeWorkflowInfo) -> None:
        self._workflows[workflow.workflow_id] = workflow

    def register_defaults(self) -> None:
        self.register(RuntimeWorkflowInfo("daily_briefing", "Daily briefing", RuntimeWorkflowStatus.READY, "briefing", "LOW"))
        self.register(RuntimeWorkflowInfo("connector_doctor", "Connector doctor", RuntimeWorkflowStatus.READY, "diagnostics", "SAFE"))
        self.register(RuntimeWorkflowInfo("eval_safe", "Safe eval suite", RuntimeWorkflowStatus.READY, "evals", "LOW"))
        self.register(RuntimeWorkflowInfo("audit_summary", "Audit summary", RuntimeWorkflowStatus.READY, "diagnostics", "SAFE"))
        self.register(RuntimeWorkflowInfo("email_send", "Email send", RuntimeWorkflowStatus.BLOCKED, "communications", "CRITICAL", approval_required=True))

    def list_workflows(self) -> tuple[RuntimeWorkflowInfo, ...]:
        return tuple(self._workflows[key] for key in sorted(self._workflows))

    def get(self, workflow_id: str) -> RuntimeWorkflowInfo:
        try:
            return self._workflows[workflow_id]
        except KeyError as exc:
            raise RuntimeUnavailableError(f"unknown workflow: {workflow_id}") from exc

    def start(self, workflow_id: str) -> RuntimeJobInfo:
        workflow = self.get(workflow_id)
        if workflow.risk_level == "CRITICAL":
            return self.job_queue.create_job(workflow.workflow_id, "CRITICAL", True, "CRITICAL workflows are blocked from runtime execution in v1.")
        if workflow.status == RuntimeWorkflowStatus.BLOCKED:
            raise RuntimePolicyBlockedError(f"workflow is blocked: {workflow_id}")
        return self.job_queue.create_job(workflow.workflow_id, workflow.risk_level, workflow.approval_required)

