from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Any
from uuid import uuid4

from agent.config.loader import load_capabilities_config
from agent.safety.action_preview import ActionPreviewError, ActionPreviewFormatter
from agent.safety.approvals import ApprovalRequest, ApprovalStatus, ApprovalStore
from agent.safety.audit import AuditEvent, AuditLogger, new_request_id
from agent.safety.policy import PolicyDecision, RiskLevel
from agent.safety.redaction import SecretRedactor
from agent.safety.trust import TrustLevel


class ActionStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    USED = "used"
    EXPIRED = "expired"


@dataclass(frozen=True)
class ActionSpec:
    action_type: str
    tool_name: str
    capability: str
    fallback_risk_level: RiskLevel
    fallback_trust_level: TrustLevel
    rollback_availability: bool
    approval_required: bool | str
    approval_reuse_allowed: bool
    required_args: tuple[str, ...] = ()
    irreversible: bool = False


ACTION_SPECS: dict[str, ActionSpec] = {
    "calendar.create_event": ActionSpec(
        "calendar.create_event",
        "calendar.create_event",
        "calendar.create_event",
        RiskLevel.CRITICAL,
        TrustLevel.LOCAL_PRIVATE_DATA,
        rollback_availability=True,
        approval_required="per_action",
        approval_reuse_allowed=False,
        required_args=("title", "start", "end"),
    ),
    "calendar.update_event": ActionSpec(
        "calendar.update_event",
        "calendar.update_event",
        "calendar.update_event",
        RiskLevel.CRITICAL,
        TrustLevel.LOCAL_PRIVATE_DATA,
        rollback_availability=False,
        approval_required="per_action",
        approval_reuse_allowed=False,
        required_args=("event_id", "changes"),
    ),
    "calendar.delete_event": ActionSpec(
        "calendar.delete_event",
        "calendar.delete_event",
        "calendar.delete_event",
        RiskLevel.CRITICAL,
        TrustLevel.LOCAL_PRIVATE_DATA,
        rollback_availability=False,
        approval_required="per_action",
        approval_reuse_allowed=False,
        required_args=("event_id",),
        irreversible=True,
    ),
    "contacts.update_selected": ActionSpec(
        "contacts.update_selected",
        "contacts.update_selected",
        "contacts.update_selected",
        RiskLevel.CRITICAL,
        TrustLevel.LOCAL_PRIVATE_DATA,
        rollback_availability=False,
        approval_required="per_action",
        approval_reuse_allowed=False,
        required_args=("selected_scope_token", "changes"),
    ),
    "contacts.create": ActionSpec(
        "contacts.create",
        "contacts.create",
        "contacts.create",
        RiskLevel.CRITICAL,
        TrustLevel.LOCAL_PRIVATE_DATA,
        rollback_availability=False,
        approval_required="per_action",
        approval_reuse_allowed=False,
        required_args=("display_name",),
    ),
    "email.send_approved": ActionSpec(
        "email.send_approved",
        "email.send_approved",
        "email.send_approved",
        RiskLevel.CRITICAL,
        TrustLevel.MODEL_OUTPUT,
        rollback_availability=False,
        approval_required="per_action",
        approval_reuse_allowed=False,
        required_args=("to", "subject", "body"),
        irreversible=True,
    ),
    "messages.send_approved": ActionSpec(
        "messages.send_approved",
        "messages.send_approved",
        "messages.send_approved",
        RiskLevel.CRITICAL,
        TrustLevel.MODEL_OUTPUT,
        rollback_availability=False,
        approval_required="per_action",
        approval_reuse_allowed=False,
        required_args=("to", "body"),
        irreversible=True,
    ),
    "messages.save_draft": ActionSpec(
        "messages.save_draft",
        "messages.save_draft",
        "messages.save_draft",
        RiskLevel.HIGH,
        TrustLevel.UNTRUSTED_MESSAGE,
        rollback_availability=True,
        approval_required=True,
        approval_reuse_allowed=True,
        required_args=("to", "draft"),
    ),
    "messages.copy_draft": ActionSpec(
        "messages.copy_draft",
        "messages.copy_draft",
        "messages.copy_draft",
        RiskLevel.HIGH,
        TrustLevel.UNTRUSTED_MESSAGE,
        rollback_availability=False,
        approval_required=True,
        approval_reuse_allowed=True,
        required_args=("to", "draft"),
    ),
    "memory.write_personal": ActionSpec(
        "memory.write_personal",
        "memory.store_personal",
        "memory.store_personal",
        RiskLevel.HIGH,
        TrustLevel.LOCAL_PRIVATE_DATA,
        rollback_availability=True,
        approval_required=True,
        approval_reuse_allowed=True,
        required_args=("content",),
    ),
    "file.delete": ActionSpec(
        "file.delete",
        "filesystem.delete",
        "filesystem.delete",
        RiskLevel.HIGH,
        TrustLevel.LOCAL_PRIVATE_DATA,
        rollback_availability=False,
        approval_required=True,
        approval_reuse_allowed=True,
        required_args=("path",),
        irreversible=True,
    ),
    "git.commit": ActionSpec(
        "git.commit",
        "git.commit",
        "git.commit",
        RiskLevel.HIGH,
        TrustLevel.LOCAL_PRIVATE_DATA,
        rollback_availability=True,
        approval_required=True,
        approval_reuse_allowed=True,
        required_args=("message",),
    ),
    "self_improvement.commit": ActionSpec(
        "self_improvement.commit",
        "git.commit",
        "git.commit",
        RiskLevel.HIGH,
        TrustLevel.LOCAL_PRIVATE_DATA,
        rollback_availability=True,
        approval_required=True,
        approval_reuse_allowed=True,
        required_args=("message",),
    ),
    "tasks.create": ActionSpec(
        "tasks.create",
        "tasks.create",
        "tasks.create",
        RiskLevel.CRITICAL,
        TrustLevel.LOCAL_PRIVATE_DATA,
        rollback_availability=True,
        approval_required="per_action",
        approval_reuse_allowed=False,
        required_args=("title",),
    ),
    "tasks.update": ActionSpec(
        "tasks.update",
        "tasks.update",
        "tasks.update",
        RiskLevel.CRITICAL,
        TrustLevel.LOCAL_PRIVATE_DATA,
        rollback_availability=False,
        approval_required="per_action",
        approval_reuse_allowed=False,
        required_args=("task_id", "changes"),
    ),
    "tasks.complete": ActionSpec(
        "tasks.complete",
        "tasks.complete",
        "tasks.complete",
        RiskLevel.CRITICAL,
        TrustLevel.LOCAL_PRIVATE_DATA,
        rollback_availability=False,
        approval_required="per_action",
        approval_reuse_allowed=False,
        required_args=("task_id",),
    ),
    "tasks.delete": ActionSpec(
        "tasks.delete",
        "tasks.delete",
        "tasks.delete",
        RiskLevel.CRITICAL,
        TrustLevel.LOCAL_PRIVATE_DATA,
        rollback_availability=False,
        approval_required="per_action",
        approval_reuse_allowed=False,
        required_args=("task_id",),
        irreversible=True,
    ),
}


@dataclass
class ActionRecord:
    action_id: str
    created_at: str
    expires_at: str
    status: ActionStatus
    action_type: str
    tool_name: str
    capability: str
    risk_level: RiskLevel
    trust_level: TrustLevel
    preview: dict[str, Any]
    sanitized_args: dict[str, Any]
    rollback_availability: bool
    source_workflow: str
    approval_required: bool | str
    approval_result: str
    audit_ids: list[str] = field(default_factory=list)
    approval_request_id: str | None = None
    approval_reuse_allowed: bool = True
    irreversible: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        payload["risk_level"] = self.risk_level.value
        payload["trust_level"] = self.trust_level.value
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ActionRecord":
        return cls(
            action_id=str(payload["action_id"]),
            created_at=str(payload["created_at"]),
            expires_at=str(payload["expires_at"]),
            status=ActionStatus(str(payload.get("status") or ActionStatus.PENDING.value)),
            action_type=str(payload["action_type"]),
            tool_name=str(payload["tool_name"]),
            capability=str(payload["capability"]),
            risk_level=RiskLevel(str(payload["risk_level"])),
            trust_level=TrustLevel(str(payload["trust_level"])),
            preview=dict(payload.get("preview") or {}),
            sanitized_args=dict(payload.get("sanitized_args") or {}),
            rollback_availability=bool(payload.get("rollback_availability", False)),
            source_workflow=str(payload.get("source_workflow") or "manual"),
            approval_required=payload.get("approval_required", False),
            approval_result=str(payload.get("approval_result") or "not_required"),
            audit_ids=list(payload.get("audit_ids") or []),
            approval_request_id=payload.get("approval_request_id"),
            approval_reuse_allowed=bool(payload.get("approval_reuse_allowed", True)),
            irreversible=bool(payload.get("irreversible", False)),
        )

    def is_expired(self, now: datetime | None = None) -> bool:
        check_time = now or datetime.now(UTC)
        try:
            expires_at = datetime.fromisoformat(self.expires_at)
        except ValueError:
            return True
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        return check_time >= expires_at


class ActionCenterStore:
    def __init__(self, path: str | Path = "data/actions.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def list(self) -> list[ActionRecord]:
        if not self.path.exists():
            return []
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
        if not isinstance(raw, list):
            return []
        return [ActionRecord.from_dict(item) for item in raw if isinstance(item, dict)]

    def save(self, records: list[ActionRecord]) -> None:
        self.path.write_text(
            json.dumps([record.to_dict() for record in records], indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def add(self, record: ActionRecord) -> None:
        records = [existing for existing in self.list() if existing.action_id != record.action_id]
        records.append(record)
        self.save(records)

    def get(self, action_id: str) -> ActionRecord | None:
        for record in self.list():
            if record.action_id == action_id:
                return record
        return None

    def update(self, record: ActionRecord) -> ActionRecord:
        records = self.list()
        replaced = False
        for index, existing in enumerate(records):
            if existing.action_id == record.action_id:
                records[index] = record
                replaced = True
                break
        if not replaced:
            records.append(record)
        self.save(records)
        return record

    def clear_denied(self) -> int:
        records = self.list()
        kept = [record for record in records if record.status is not ActionStatus.DENIED]
        self.save(kept)
        return len(records) - len(kept)


class ActionCenter:
    """Persisted review queue for risky actions.

    Action Center tracks proposed actions, previews, and approval state. It
    deliberately does not execute tools; any later execution must still enter
    through ToolBroker with the original capability policy checks.
    """

    def __init__(
        self,
        *,
        store: ActionCenterStore | None = None,
        approval_store: ApprovalStore | None = None,
        audit_logger: AuditLogger | None = None,
        session_id: str = "",
        model: str = "",
        route: str = "actions",
        user_id: str = "local-user",
        expires_in_minutes: int = 30,
    ) -> None:
        self.store = store or ActionCenterStore()
        self.approval_store = approval_store or ApprovalStore()
        self.audit_logger = audit_logger
        self.session_id = session_id
        self.model = model
        self.route = route
        self.user_id = user_id
        self.expires_in_minutes = expires_in_minutes
        self.redactor = SecretRedactor()
        self.preview_formatter = ActionPreviewFormatter()
        self._capability_config = _load_capability_entries()

    def create_action(
        self,
        action_type: str,
        args: dict[str, Any],
        *,
        source_workflow: str = "manual",
        action_id: str | None = None,
    ) -> ActionRecord:
        spec = self._spec_for(action_type)
        self._validate_required_args(spec, args)
        risk_level, trust_level, approval_required, approval_reuse_allowed = self._policy_fields(spec)
        try:
            preview = self.preview_formatter.format(spec.tool_name, args, risk_level).to_dict()
        except ActionPreviewError:
            raise
        sanitized_args = self.redactor.redact(args)
        if spec.irreversible:
            preview["irreversible"] = True
            preview["rollback_note"] = "Rollback is not available for this action."
        record = ActionRecord(
            action_id=action_id or f"act_{uuid4()}",
            created_at=datetime.now(UTC).isoformat(),
            expires_at=(datetime.now(UTC) + timedelta(minutes=self.expires_in_minutes)).isoformat(),
            status=ActionStatus.PENDING,
            action_type=spec.action_type,
            tool_name=spec.tool_name,
            capability=spec.capability,
            risk_level=risk_level,
            trust_level=trust_level,
            preview=preview,
            sanitized_args=sanitized_args,
            rollback_availability=bool(preview.get("rollback_available", spec.rollback_availability)),
            source_workflow=source_workflow,
            approval_required=approval_required,
            approval_result="not_required",
            approval_reuse_allowed=approval_reuse_allowed,
            irreversible=spec.irreversible,
        )
        if approval_required:
            approval = self._new_approval_request(record)
            self.approval_store.add(approval)
            record.approval_request_id = approval.request_id
        self._audit(record, "created", "action queued for review", PolicyDecision.ASK)
        self.store.add(record)
        return record

    def list_actions(self) -> list[ActionRecord]:
        return self.store.list()

    def get_action(self, action_id: str) -> ActionRecord | None:
        record = self.store.get(action_id)
        if record is not None and record.is_expired() and record.status is ActionStatus.PENDING:
            record.status = ActionStatus.EXPIRED
            record.approval_result = "expired"
            self._audit(record, "expired", "action expired before approval", PolicyDecision.DENY)
            self.store.update(record)
        return record

    def approve(self, action_id: str) -> ActionRecord | None:
        record = self.get_action(action_id)
        if record is None:
            return None
        if record.is_expired():
            record.status = ActionStatus.EXPIRED
            record.approval_result = "expired"
            self._sync_approval(record, ApprovalStatus.EXPIRED)
            self._audit(record, "expired", "action approval expired", PolicyDecision.DENY)
            self.store.update(record)
            return record
        record.status = ActionStatus.APPROVED
        record.approval_result = "approved"
        self._sync_approval(record, ApprovalStatus.APPROVED)
        self._audit(record, "approved", "action approved for one brokered execution", PolicyDecision.ALLOW)
        self.store.update(record)
        return record

    def deny(self, action_id: str) -> ActionRecord | None:
        record = self.get_action(action_id)
        if record is None:
            return None
        record.status = ActionStatus.DENIED
        record.approval_result = "denied"
        self._sync_approval(record, ApprovalStatus.DENIED)
        self._audit(record, "denied", "action denied", PolicyDecision.DENY)
        self.store.update(record)
        return record

    def edit(self, action_id: str, updates: dict[str, Any]) -> ActionRecord | None:
        record = self.get_action(action_id)
        if record is None:
            return None
        merged_args = dict(record.sanitized_args)
        merged_args.update(updates)
        spec = self._spec_for(record.action_type)
        self._validate_required_args(spec, merged_args)
        preview = self.preview_formatter.format(spec.tool_name, merged_args, record.risk_level).to_dict()
        if spec.irreversible:
            preview["irreversible"] = True
            preview["rollback_note"] = "Rollback is not available for this action."
        record.sanitized_args = self.redactor.redact(merged_args)
        record.preview = preview
        record.status = ActionStatus.PENDING
        record.approval_result = "not_required"
        record.expires_at = (datetime.now(UTC) + timedelta(minutes=self.expires_in_minutes)).isoformat()
        if record.approval_request_id:
            self._sync_approval(record, ApprovalStatus.DENIED)
        if record.approval_required:
            approval = self._new_approval_request(record)
            self.approval_store.add(approval)
            record.approval_request_id = approval.request_id
        self._audit(record, "edited", "action edited; previous approval invalidated", PolicyDecision.ASK)
        self.store.update(record)
        return record

    def consume_approval_once(self, action_id: str) -> bool:
        record = self.get_action(action_id)
        if record is None or record.status is not ActionStatus.APPROVED or record.is_expired():
            return False
        record.status = ActionStatus.USED
        record.approval_result = "approved_used"
        self._sync_approval(record, ApprovalStatus.USED)
        self._audit(record, "used", "one-time approval consumed; execution must be brokered", PolicyDecision.ALLOW)
        self.store.update(record)
        return True

    def execution_gate(self, action_id: str, *, interactive: bool) -> dict[str, Any]:
        record = self.get_action(action_id)
        if record is None:
            return {"allowed": False, "reason": "action not found"}
        if not interactive and record.approval_required:
            self._audit(record, "blocked_non_interactive", "non-interactive mode cannot execute pending actions", PolicyDecision.DENY)
            self.store.update(record)
            return {"allowed": False, "reason": "approval-required action blocked in non-interactive mode"}
        return {
            "allowed": False,
            "reason": "Action Center does not execute actions; use ToolBroker for execution.",
        }

    def record_failure(self, action_id: str, summary: str) -> ActionRecord | None:
        record = self.get_action(action_id)
        if record is None:
            return None
        self._audit(record, "execution_failed", summary, PolicyDecision.DENY)
        self.store.update(record)
        return record

    def clear_denied(self) -> int:
        count = self.store.clear_denied()
        if count:
            self._audit_system("cleared_denied", f"cleared {count} denied action(s)")
        return count

    def export(self) -> dict[str, Any]:
        records = [record.to_dict() for record in self.store.list()]
        self._audit_system("exported", f"exported {len(records)} action record(s)")
        return {"actions": records}

    def _spec_for(self, action_type: str) -> ActionSpec:
        try:
            return ACTION_SPECS[action_type]
        except KeyError as exc:
            raise ValueError(f"unknown action type: {action_type}") from exc

    def _policy_fields(self, spec: ActionSpec) -> tuple[RiskLevel, TrustLevel, bool | str, bool]:
        entry = self._capability_config.get(spec.capability, {})
        risk_level = RiskLevel(str(entry.get("risk_level") or spec.fallback_risk_level.value))
        trust_level = TrustLevel(str(entry.get("trust_level") or spec.fallback_trust_level.value))
        approval_required = entry.get("approval_required", spec.approval_required)
        approval_reuse_allowed = bool(entry.get("approval_reuse_allowed", spec.approval_reuse_allowed))
        if risk_level is RiskLevel.CRITICAL:
            approval_required = "per_action"
            approval_reuse_allowed = False
        if risk_level is RiskLevel.HIGH and not approval_required:
            approval_required = True
        return risk_level, trust_level, approval_required, approval_reuse_allowed

    def _validate_required_args(self, spec: ActionSpec, args: dict[str, Any]) -> None:
        missing = [key for key in spec.required_args if not args.get(key)]
        if missing:
            raise ActionPreviewError(f"action preview missing exact args: {', '.join(missing)}")

    def _new_approval_request(self, record: ActionRecord) -> ApprovalRequest:
        return ApprovalRequest(
            capability=record.capability,
            tool_name=record.tool_name,
            risk_level=record.risk_level,
            summary=str(record.preview.get("summary") or record.action_type),
            per_action=record.risk_level is RiskLevel.CRITICAL or record.approval_required == "per_action",
            request_id=f"apr_{uuid4()}",
            user_id=self.user_id,
            session_id=self.session_id,
            trust_level=record.trust_level,
            args_preview=record.preview,
            rollback_available=record.rollback_availability,
            expires_at=record.expires_at,
            status=ApprovalStatus.PENDING,
        )

    def _sync_approval(self, record: ActionRecord, status: ApprovalStatus) -> None:
        if record.approval_request_id:
            self.approval_store.update_status(record.approval_request_id, status)

    def _audit(
        self,
        record: ActionRecord,
        event_name: str,
        summary: str,
        decision: PolicyDecision,
    ) -> None:
        if self.audit_logger is None:
            return
        payload = self.audit_logger.log(
            AuditEvent(
                session_id=self.session_id,
                request_id=new_request_id(),
                route=self.route,
                model=self.model,
                tool_name=f"action.{event_name}",
                capability=record.capability,
                risk_level=record.risk_level.value,
                trust_level=record.trust_level.value,
                policy_decision=decision.value,
                approval_result=record.approval_result,
                sanitized_args=record.to_dict(),
                result_summary=summary,
            )
        )
        record.audit_ids.append(str(payload.get("hash_current") or ""))

    def _audit_system(self, event_name: str, summary: str) -> None:
        if self.audit_logger is None:
            return
        self.audit_logger.log(
            AuditEvent(
                session_id=self.session_id,
                request_id=new_request_id(),
                route=self.route,
                model=self.model,
                tool_name=f"action.{event_name}",
                capability="actions.review",
                risk_level=RiskLevel.SAFE.value,
                trust_level=TrustLevel.MODEL_OUTPUT.value,
                policy_decision=PolicyDecision.ALLOW.value,
                approval_result="not_required",
                sanitized_args={},
                result_summary=summary,
            )
        )


def _load_capability_entries() -> dict[str, dict[str, Any]]:
    try:
        loaded = load_capabilities_config()
    except Exception:
        return {}
    tools = loaded.get("tools")
    if not isinstance(tools, dict):
        return {}
    return {str(name): dict(entry) for name, entry in tools.items() if isinstance(entry, dict)}
