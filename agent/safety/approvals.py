from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from agent.safety.audit import AuditEvent, AuditLogger, new_request_id
from agent.safety.policy import PolicyDecision, RiskLevel
from agent.safety.redaction import SecretRedactor
from agent.safety.trust import TrustLevel


class ApprovalResult(StrEnum):
    APPROVED = "approved"
    DENIED = "denied"
    ABORTED = "aborted"
    EXPIRED = "expired"
    NOT_REQUIRED = "not_required"


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    DISPLAYED = "displayed"
    APPROVED = "approved"
    DENIED = "denied"
    ABORTED = "aborted"
    EXPIRED = "expired"
    USED = "used"


@dataclass
class ApprovalRequest:
    capability: str
    tool_name: str
    risk_level: RiskLevel
    summary: str
    per_action: bool = False
    request_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    user_id: str = "local-user"
    session_id: str = ""
    trust_level: TrustLevel = TrustLevel.MODEL_OUTPUT
    args_preview: dict[str, Any] = field(default_factory=dict)
    rollback_available: bool = False
    expires_at: str = field(default_factory=lambda: (datetime.now(UTC) + timedelta(minutes=10)).isoformat())
    status: ApprovalStatus = ApprovalStatus.PENDING

    def is_expired(self, now: datetime | None = None) -> bool:
        check_time = now or datetime.now(UTC)
        try:
            expires_at = datetime.fromisoformat(self.expires_at)
        except ValueError:
            return True
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        return check_time >= expires_at

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["risk_level"] = self.risk_level.value
        payload["trust_level"] = self.trust_level.value
        payload["status"] = self.status.value
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ApprovalRequest":
        return cls(
            capability=str(payload["capability"]),
            tool_name=str(payload["tool_name"]),
            risk_level=RiskLevel(str(payload["risk_level"])),
            summary=str(payload["summary"]),
            per_action=bool(payload.get("per_action", False)),
            request_id=str(payload.get("request_id") or uuid4()),
            timestamp=str(payload.get("timestamp") or datetime.now(UTC).isoformat()),
            user_id=str(payload.get("user_id") or "local-user"),
            session_id=str(payload.get("session_id") or ""),
            trust_level=TrustLevel(str(payload.get("trust_level") or TrustLevel.MODEL_OUTPUT.value)),
            args_preview=dict(payload.get("args_preview") or {}),
            rollback_available=bool(payload.get("rollback_available", False)),
            expires_at=str(payload.get("expires_at") or (datetime.now(UTC) + timedelta(minutes=10)).isoformat()),
            status=ApprovalStatus(str(payload.get("status") or ApprovalStatus.PENDING.value)),
        )


DecisionProvider = Callable[[ApprovalRequest], ApprovalResult]


class ApprovalStore:
    """Small JSON approval queue for local CLI inspection.

    The queue records requests and their statuses. Approving a queued request
    does not replay a tool call; execution still requires a fresh brokered
    action and a matching live approval path.
    """

    def __init__(self, path: str | Path = "data/approvals.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def list(self) -> list[ApprovalRequest]:
        if not self.path.exists():
            return []
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
        if not isinstance(raw, list):
            return []
        return [ApprovalRequest.from_dict(item) for item in raw if isinstance(item, dict)]

    def save(self, requests: list[ApprovalRequest]) -> None:
        self.path.write_text(
            json.dumps([request.to_dict() for request in requests], indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def add(self, request: ApprovalRequest) -> None:
        requests = [existing for existing in self.list() if existing.request_id != request.request_id]
        requests.append(request)
        self.save(requests)

    def get(self, request_id: str) -> ApprovalRequest | None:
        for request in self.list():
            if request.request_id == request_id:
                return request
        return None

    def update_status(self, request_id: str, status: ApprovalStatus) -> ApprovalRequest | None:
        requests = self.list()
        updated: ApprovalRequest | None = None
        for request in requests:
            if request.request_id == request_id:
                request.status = status
                updated = request
                break
        if updated is not None:
            self.save(requests)
        return updated


class ApprovalManager:
    """Approval manager with conservative non-interactive defaults."""

    def __init__(
        self,
        auto_approve: set[str] | None = None,
        *,
        decision_provider: DecisionProvider | None = None,
        store: ApprovalStore | None = None,
        audit_logger: AuditLogger | None = None,
        session_id: str = "",
        user_id: str = "local-user",
        model: str = "",
        route: str = "approval",
    ) -> None:
        self.auto_approve = auto_approve or set()
        self.decision_provider = decision_provider
        self.store = store
        self.audit_logger = audit_logger
        self.session_id = session_id
        self.user_id = user_id
        self.model = model
        self.route = route
        self.requests: list[ApprovalRequest] = []
        self._critical_auto_approved: set[str] = set()

    def configure_audit(
        self,
        audit_logger: AuditLogger,
        *,
        session_id: str,
        model: str = "",
        route: str = "approval",
    ) -> None:
        self.audit_logger = audit_logger
        self.session_id = session_id
        self.model = model
        self.route = route

    def request_approval(self, request: ApprovalRequest) -> ApprovalResult:
        request.session_id = request.session_id or self.session_id
        request.user_id = request.user_id or self.user_id
        self.requests.append(request)
        self._store(request)
        self._audit(request, "requested", "approval requested", ApprovalResult.NOT_REQUIRED, PolicyDecision.ASK)
        if request.is_expired():
            request.status = ApprovalStatus.EXPIRED
            self._store(request)
            self._audit(request, "expired", "approval expired", ApprovalResult.EXPIRED, PolicyDecision.DENY)
            return ApprovalResult.EXPIRED

        decision = self._decision_for(request)
        if decision is ApprovalResult.APPROVED:
            request.status = ApprovalStatus.APPROVED
            self._store(request)
            self._audit(request, "approved", "approval approved", decision, PolicyDecision.ALLOW)
            return ApprovalResult.APPROVED
        if decision is ApprovalResult.ABORTED:
            request.status = ApprovalStatus.ABORTED
            self._store(request)
            self._audit(request, "aborted", "approval aborted", decision, PolicyDecision.DENY)
            return ApprovalResult.ABORTED

        request.status = ApprovalStatus.DENIED
        self._store(request)
        self._audit(request, "denied", "approval denied", ApprovalResult.DENIED, PolicyDecision.DENY)
        return ApprovalResult.DENIED

    def mark_used(self, request: ApprovalRequest) -> None:
        request.status = ApprovalStatus.USED
        self._store(request)
        self._audit(request, "used", "action executed after approval", ApprovalResult.APPROVED, PolicyDecision.ALLOW)

    def _decision_for(self, request: ApprovalRequest) -> ApprovalResult:
        if self.decision_provider is not None:
            request.status = ApprovalStatus.DISPLAYED
            self._store(request)
            self._audit(request, "displayed", "approval displayed", ApprovalResult.NOT_REQUIRED, PolicyDecision.ASK)
            return self.decision_provider(request)
        if request.capability in self.auto_approve:
            if request.risk_level is RiskLevel.CRITICAL:
                if request.capability in self._critical_auto_approved:
                    return ApprovalResult.DENIED
                self._critical_auto_approved.add(request.capability)
            return ApprovalResult.APPROVED
        return ApprovalResult.DENIED

    def _store(self, request: ApprovalRequest) -> None:
        if self.store is not None:
            self.store.add(request)

    def _audit(
        self,
        request: ApprovalRequest,
        event_name: str,
        summary: str,
        approval_result: ApprovalResult,
        decision: PolicyDecision,
    ) -> None:
        if self.audit_logger is None:
            return
        self.audit_logger.log(
            AuditEvent(
                session_id=request.session_id or self.session_id,
                request_id=new_request_id(),
                route=self.route,
                model=self.model,
                tool_name=f"approval.{event_name}",
                capability=request.capability,
                risk_level=request.risk_level.value,
                trust_level=request.trust_level.value,
                policy_decision=decision.value,
                approval_result=approval_result.value,
                sanitized_args=SecretRedactor().redact(request.to_dict()),
                result_summary=summary,
            )
        )
