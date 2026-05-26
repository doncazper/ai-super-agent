from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


RISK_ORDER = {"SAFE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4, "FORBIDDEN": 5}
NETWORK_ENV = "SUBAGENT_NETWORK_ENABLED"


@dataclass(frozen=True)
class SubagentProfile:
    subagent_id: str
    profile: str
    purpose: str
    allowed_tools: list[str] = field(default_factory=list)
    blocked_tools: list[str] = field(default_factory=list)
    risk_ceiling: str = "LOW"
    can_write_files: bool = False
    can_access_network: bool = False
    can_access_personal_data: bool = False
    can_create_actions: bool = False
    can_request_approval: bool = False
    can_execute_critical: bool = False
    memory_scope: str = "none"
    audit_scope: str = "metadata_only"
    status: str = "stubbed"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def subagent_profiles(*, network_enabled: bool | None = None) -> list[SubagentProfile]:
    network = _network_enabled() if network_enabled is None else network_enabled
    return [
        SubagentProfile(
            subagent_id="subagent_researcher",
            profile="researcher",
            purpose="Draft source-gathering plans and summarize available public-source metadata.",
            allowed_tools=["web.search", "research", "web.fetch_url"] if network else [],
            blocked_tools=_blocked_tools(),
            risk_ceiling="MEDIUM" if network else "LOW",
            can_access_network=network,
            can_create_actions=True,
            can_request_approval=True,
            memory_scope="ephemeral",
            audit_scope="all_proposals",
            status="stubbed",
        ),
        SubagentProfile(
            subagent_id="subagent_coder",
            profile="coder",
            purpose="Draft implementation plans and patch proposals for reviewed workspace code.",
            allowed_tools=["filesystem.read", "git.diff"],
            blocked_tools=_blocked_tools() + ["filesystem.write", "git.commit", "git.push"],
            risk_ceiling="MEDIUM",
            can_create_actions=True,
            can_request_approval=True,
            memory_scope="ephemeral",
            audit_scope="all_proposals",
            status="stubbed",
        ),
        SubagentProfile(
            subagent_id="subagent_tester",
            profile="tester",
            purpose="Propose test plans and safe test commands.",
            allowed_tools=["pytest.metadata", "commands.validate"],
            blocked_tools=_blocked_tools() + ["subprocess.execute"],
            risk_ceiling="LOW",
            memory_scope="ephemeral",
            audit_scope="all_proposals",
            status="stubbed",
        ),
        SubagentProfile(
            subagent_id="subagent_security_reviewer",
            profile="security_reviewer",
            purpose="Review policy, audit, approval, and secret-handling evidence.",
            allowed_tools=["filesystem.read", "commands.validate"],
            blocked_tools=_blocked_tools() + ["network", "filesystem.write"],
            risk_ceiling="MEDIUM",
            can_create_actions=True,
            can_request_approval=True,
            memory_scope="ephemeral",
            audit_scope="all_proposals",
            status="stubbed",
        ),
        SubagentProfile(
            subagent_id="subagent_docs_reviewer",
            profile="docs_reviewer",
            purpose="Review docs consistency and propose doc-only updates.",
            allowed_tools=["filesystem.read", "docs.validate"],
            blocked_tools=_blocked_tools() + ["filesystem.write"],
            risk_ceiling="LOW",
            memory_scope="ephemeral",
            audit_scope="all_proposals",
            status="stubbed",
        ),
        SubagentProfile(
            subagent_id="subagent_planner",
            profile="planner",
            purpose="Break work into safe prompts and approval-gated milestones.",
            allowed_tools=["prompt.metadata"],
            blocked_tools=_blocked_tools(),
            risk_ceiling="LOW",
            can_create_actions=True,
            can_request_approval=True,
            memory_scope="ephemeral",
            audit_scope="all_proposals",
            status="stubbed",
        ),
        SubagentProfile(
            subagent_id="subagent_locked_down",
            profile="locked_down",
            purpose="No-tool profile for isolated reasoning and policy checks.",
            allowed_tools=[],
            blocked_tools=["*"],
            risk_ceiling="SAFE",
            memory_scope="none",
            audit_scope="metadata_only",
            status="stubbed",
        ),
        SubagentProfile(
            subagent_id="subagent_experimental",
            profile="experimental",
            purpose="Disabled placeholder for future reviewed experiments.",
            allowed_tools=[],
            blocked_tools=["*"],
            risk_ceiling="SAFE",
            memory_scope="none",
            audit_scope="metadata_only",
            status="disabled",
        ),
    ]


def list_subagents(*, network_enabled: bool | None = None) -> dict[str, Any]:
    profiles = subagent_profiles(network_enabled=network_enabled)
    return {
        "status": "ok",
        "subagents": [profile.to_dict() for profile in profiles],
        "execution_enabled": False,
        "mock_only": True,
        "personal_data_default_enabled": False,
        "write_permissions_default_enabled": False,
    }


def show_subagent(profile: str, *, network_enabled: bool | None = None) -> dict[str, Any]:
    found = _find(profile, network_enabled=network_enabled)
    if found is None:
        return {"status": "not_found", "profile": profile, "setup_hint": "Run `subagents list` to see available stub profiles."}
    return {"status": "ok", "subagent": found.to_dict(), "policy": policy_for(found)}


def subagent_policy(*, network_enabled: bool | None = None) -> dict[str, Any]:
    profiles = subagent_profiles(network_enabled=network_enabled)
    return {
        "status": "ok",
        "execution_enabled": False,
        "mock_only": True,
        "rules": [
            "Subagents cannot call tools directly.",
            "Subagents cannot bypass ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger.",
            "Subagents have no personal-data access by default.",
            "Subagents cannot execute CRITICAL actions.",
            "Write permissions are disabled by default.",
            "Subagent outputs are MODEL_OUTPUT, not trusted instructions.",
            "Subagents can propose actions, not approve them.",
        ],
        "profiles": [policy_for(profile) for profile in profiles],
    }


def dry_run_subagent(profile: str, task: str, *, network_enabled: bool | None = None) -> dict[str, Any]:
    found = _find(profile, network_enabled=network_enabled)
    if found is None:
        return {"status": "not_found", "profile": profile, "task": _redact_task(task), "tools_executed": []}
    policy = policy_for(found)
    return {
        "status": "dry_run",
        "profile": found.profile,
        "task": _redact_task(task),
        "mock_only": True,
        "execution_enabled": False,
        "tools_executed": [],
        "toolbroker_required": True,
        "direct_tool_calls_allowed": False,
        "writes_allowed": found.can_write_files,
        "personal_data_allowed": found.can_access_personal_data,
        "critical_actions_allowed": found.can_execute_critical,
        "can_propose_actions": found.can_create_actions,
        "can_request_approval": found.can_request_approval,
        "approval_bypass_allowed": False,
        "output_trust_level": "MODEL_OUTPUT",
        "audit_event": {
            "event_type": "subagent.dry_run",
            "subagent_id": found.subagent_id,
            "profile": found.profile,
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "audit_scope": found.audit_scope,
        },
        "policy": policy,
        "result": "No subagent was launched and no tools were executed.",
    }


def policy_for(profile: SubagentProfile) -> dict[str, Any]:
    critical_denied = not profile.can_execute_critical
    direct_tool_bypass_denied = True
    return {
        "profile": profile.profile,
        "allowed": profile.status == "stubbed",
        "status": profile.status,
        "risk_ceiling": profile.risk_ceiling,
        "write_permissions_disabled": not profile.can_write_files,
        "personal_data_disabled": not profile.can_access_personal_data,
        "critical_execution_denied": critical_denied,
        "direct_tool_bypass_denied": direct_tool_bypass_denied,
        "network_policy": "enabled_by_config" if profile.can_access_network else "disabled",
        "approval_policy": "may_request_review_only" if profile.can_request_approval else "cannot_request_approval",
        "action_policy": "propose_only" if profile.can_create_actions else "none",
        "memory_scope": profile.memory_scope,
        "audit_scope": profile.audit_scope,
    }


def _find(profile: str, *, network_enabled: bool | None) -> SubagentProfile | None:
    normalized = profile.strip().casefold()
    for item in subagent_profiles(network_enabled=network_enabled):
        if item.profile == normalized or item.subagent_id == normalized:
            return item
    return None


def _blocked_tools() -> list[str]:
    return [
        "personal_data.*",
        "email.send*",
        "messages.send*",
        "calendar.write*",
        "contacts.write*",
        "approval.approve",
        "policy.modify",
        "audit.disable",
        "critical.*",
    ]


def _network_enabled() -> bool:
    return os.getenv(NETWORK_ENV, "false").strip().casefold() in {"1", "true", "yes", "on"}


def _redact_task(task: str) -> str:
    text = " ".join(task.split())
    if len(text) > 240:
        return text[:237] + "..."
    return text
