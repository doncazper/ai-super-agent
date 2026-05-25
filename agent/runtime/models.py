from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class RuntimeMode(str, Enum):
    CLI = "cli"
    API = "api"
    APP = "app"
    TEST = "test"


class RuntimeStatus(str, Enum):
    CREATED = "created"
    BOOTING = "booting"
    READY = "ready"
    DEGRADED = "degraded"
    STOPPED = "stopped"
    ERROR = "error"


class RuntimeHealthStatus(str, Enum):
    OK = "ok"
    WARN = "warn"
    ERROR = "error"
    UNKNOWN = "unknown"


class RuntimeServiceStatus(str, Enum):
    REGISTERED = "registered"
    AVAILABLE = "available"
    DISABLED = "disabled"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


class RuntimeFeatureStatus(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    PLANNED = "planned"
    BLOCKED = "blocked"


class RuntimeWorkflowStatus(str, Enum):
    REGISTERED = "registered"
    READY = "ready"
    APPROVAL_REQUIRED = "approval_required"
    BLOCKED = "blocked"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RuntimeJobStatus(str, Enum):
    QUEUED = "queued"
    APPROVAL_REQUIRED = "approval_required"
    BLOCKED = "blocked"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RuntimeEventType(str, Enum):
    RUNTIME_STARTED = "runtime.started"
    RUNTIME_STOPPED = "runtime.stopped"
    SERVICE_REGISTERED = "service.registered"
    FEATURE_UPDATED = "feature.updated"
    WORKFLOW_REGISTERED = "workflow.registered"
    JOB_CREATED = "job.created"
    JOB_UPDATED = "job.updated"
    SCHEDULER_EVALUATED = "scheduler.evaluated"
    FRONTEND_REQUEST = "frontend.request"
    FRONTEND_RESPONSE = "frontend.response"


@dataclass(frozen=True)
class RuntimeServiceInfo:
    service_id: str
    name: str
    status: RuntimeServiceStatus = RuntimeServiceStatus.REGISTERED
    description: str = ""
    category: str = "runtime"
    risk_level: str = "SAFE"
    trust_level: str = "LOCAL_PRIVATE_DATA metadata"
    enabled_by_default: bool = True
    lazy_load: bool = True
    owner: str = "core"
    notes: str = ""
    registered_at: str = field(default_factory=now_iso)

    def __post_init__(self) -> None:
        if not self.service_id:
            raise ValueError("service_id is required")
        if not self.name:
            raise ValueError("name is required")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True)
class RuntimeFeatureInfo:
    feature_id: str
    name: str
    status: RuntimeFeatureStatus = RuntimeFeatureStatus.DISABLED
    risk_level: str = "SAFE"
    trust_level: str = "LOCAL_PRIVATE_DATA metadata"
    approval_required: bool = False
    enabled_by_default: bool = False
    personal_data: bool = False
    critical_action: bool = False
    reason: str = ""

    def __post_init__(self) -> None:
        if not self.feature_id:
            raise ValueError("feature_id is required")
        if self.critical_action and not self.approval_required:
            raise ValueError("critical features must require approval")
        if self.personal_data and self.enabled_by_default:
            raise ValueError("personal-data features must be disabled by default")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True)
class RuntimeWorkflowInfo:
    workflow_id: str
    name: str
    status: RuntimeWorkflowStatus = RuntimeWorkflowStatus.REGISTERED
    category: str = "runtime"
    risk_level: str = "SAFE"
    approval_required: bool = False
    tools_required: tuple[str, ...] = ()
    description: str = ""
    registered_at: str = field(default_factory=now_iso)

    def __post_init__(self) -> None:
        if not self.workflow_id:
            raise ValueError("workflow_id is required")
        if self.risk_level in {"HIGH", "CRITICAL"} and not self.approval_required:
            raise ValueError("HIGH/CRITICAL workflows must require approval")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["tools_required"] = list(self.tools_required)
        return data


@dataclass(frozen=True)
class RuntimeJobInfo:
    job_id: str
    workflow_id: str
    status: RuntimeJobStatus = RuntimeJobStatus.QUEUED
    risk_level: str = "SAFE"
    approval_required: bool = False
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)
    reason: str = ""
    result_summary: str = ""

    def __post_init__(self) -> None:
        if not self.job_id:
            raise ValueError("job_id is required")
        if not self.workflow_id:
            raise ValueError("workflow_id is required")
        if self.risk_level == "CRITICAL" and self.status != RuntimeJobStatus.BLOCKED:
            raise ValueError("CRITICAL jobs are blocked in runtime v1")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True)
class RuntimeEvent:
    event_id: str
    event_type: str
    source: str
    payload: dict[str, Any] = field(default_factory=dict)
    trust_level: str = "LOCAL_PRIVATE_DATA metadata"
    created_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RuntimeHealthReport:
    status: RuntimeHealthStatus
    checks: tuple[dict[str, Any], ...] = ()
    generated_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["checks"] = list(self.checks)
        return data


@dataclass(frozen=True)
class RuntimeStateSnapshot:
    mode: RuntimeMode
    status: RuntimeStatus
    services: tuple[RuntimeServiceInfo, ...] = ()
    features: tuple[RuntimeFeatureInfo, ...] = ()
    workflows: tuple[RuntimeWorkflowInfo, ...] = ()
    jobs: tuple[RuntimeJobInfo, ...] = ()
    health: RuntimeHealthReport | None = None
    generated_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode.value,
            "status": self.status.value,
            "services": [item.to_dict() for item in self.services],
            "features": [item.to_dict() for item in self.features],
            "workflows": [item.to_dict() for item in self.workflows],
            "jobs": [item.to_dict() for item in self.jobs],
            "health": self.health.to_dict() if self.health else None,
            "generated_at": self.generated_at,
        }

