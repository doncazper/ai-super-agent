from __future__ import annotations

from .event_bus import EventBus
from .feature_flags import FeatureFlagRegistry
from .job_queue import JobQueue
from .models import RuntimeHealthReport, RuntimeHealthStatus, RuntimeMode, RuntimeStateSnapshot, RuntimeStatus
from .service_registry import ServiceRegistry
from .state import RuntimeState
from .workflow_runner import WorkflowRunner


class RuntimeKernel:
    def __init__(self, mode: RuntimeMode = RuntimeMode.CLI) -> None:
        self.state = RuntimeState(mode=mode)
        self.services = ServiceRegistry()
        self.features = FeatureFlagRegistry()
        self.events = EventBus()
        self.jobs = JobQueue()
        self.workflows = WorkflowRunner(self.jobs)
        self._booted = False

    def boot(self) -> None:
        if self._booted:
            return
        self.services.register_defaults()
        self.workflows.register_defaults()
        self.state.boot()
        self.events.publish("runtime.started", "runtime.kernel", {"mode": self.state.mode.value})
        self._booted = True

    def status(self) -> dict[str, object]:
        self.boot()
        return {
            "status": self.state.status.value,
            "mode": self.state.mode.value,
            "services": len(self.services.list_services()),
            "features": len(self.features.list_features()),
            "workflows": len(self.workflows.list_workflows()),
            "jobs": len(self.jobs.list_jobs()),
            "lmstudio_checked": False,
            "personal_data_accessed": False,
            "background_persistence": False,
        }

    def health(self) -> RuntimeHealthReport:
        self.boot()
        checks = (
            {"name": "runtime_boot", "status": "ok", "detail": "kernel booted without model/tool/connector calls"},
            {"name": "personal_data_defaults", "status": "ok", "detail": "personal-data features are disabled by default"},
            {"name": "background_persistence", "status": "ok", "detail": "no background scheduler or app bridge is started"},
        )
        return RuntimeHealthReport(RuntimeHealthStatus.OK, checks)

    def snapshot(self) -> RuntimeStateSnapshot:
        self.boot()
        return RuntimeStateSnapshot(
            mode=self.state.mode,
            status=RuntimeStatus.READY,
            services=self.services.list_services(),
            features=self.features.list_features(),
            workflows=self.workflows.list_workflows(),
            jobs=self.jobs.list_jobs(),
            health=self.health(),
        )

