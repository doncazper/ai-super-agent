from __future__ import annotations

from pathlib import Path
from typing import Any

from .canonical_state import build_canonical_runtime_state, build_reconcile_preview
from .gateway_state import gateway_status
from .kernel_contract import kernel_status
from .recovery import recovery_preview
from .state import redact_runtime_value


def build_canonical_dashboard(project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    state = build_canonical_runtime_state(root).to_dict()
    reconcile = build_reconcile_preview(root)
    gateway = gateway_status()
    kernel = kernel_status()
    recovery = recovery_preview(root)
    dirty = state.get("dirty_worktree_summary", {})
    dashboard = {
        "status": "ok",
        "read_only": True,
        "side_effects": "none; dashboard reads metadata only",
        "canonical_state_summary": {
            "generated_at": state.get("generated_at"),
            "branch": state.get("branch"),
            "last_commit": state.get("last_commit"),
            "current_status": state.get("current_status"),
            "current_phase": state.get("current_phase"),
        },
        "active": {
            "prompt_id": state.get("active_prompt_id", "none"),
            "prompt_pack": state.get("active_prompt_pack", "none"),
            "job_id": state.get("active_job_id", "none"),
            "workflow_id": state.get("active_workflow_id", "none"),
            "action_id": state.get("active_action_id", "none"),
        },
        "next_prompt_id": state.get("next_prompt_id", "unknown"),
        "last_validation": {
            "test_result": state.get("last_test_result", "unknown"),
            "policy_check": state.get("last_policy_check", "unknown"),
            "capability_check": state.get("last_capability_check", "unknown"),
            "command_registry_check": state.get("last_command_registry_check", "unknown"),
            "prompt_audit": state.get("last_prompt_audit", "unknown"),
        },
        "tracker_conflicts": reconcile.get("conflicts", []),
        "dirty_worktree_summary": dirty,
        "safety_summary": state.get("safety_summary", {}),
        "gateway_kernel_status": {
            "gateway": gateway.get("gateway", {}),
            "kernel_contract": kernel.get("kernel_contract", {}),
        },
        "recovery_resume_hints": {
            "auto_resume": recovery.get("auto_resume", False),
            "safe_next_action": recovery.get("report", {}).get("safe_next_action", ""),
            "unsafe_actions_to_avoid": recovery.get("report", {}).get("unsafe_actions_to_avoid", []),
        },
        "handoff_file_recommendation": {
            "primary": "docs/HANDOFF_TO_CHATGPT.md",
            "supporting": [
                "docs/PROJECT_STATE.md",
                "docs/PROMPT_QUEUE.md",
                "docs/PROMPT_LEDGER.md",
                "docs/PROMPT_AUDIT.md",
                "docs/COMPLETION_REPORT.md",
                "CHANGELOG.md",
            ],
        },
    }
    return redact_runtime_value(dashboard)


def build_handoff(project_root: str | Path = ".", *, for_chatgpt: bool = False) -> dict[str, Any]:
    dashboard = build_canonical_dashboard(project_root)
    handoff = {
        "status": "ok",
        "for_chatgpt": bool(for_chatgpt),
        "read_only": True,
        "side_effects": "none; handoff reads metadata only",
        "dashboard": dashboard,
        "recommended_uploads": dashboard["handoff_file_recommendation"],
        "markdown": render_handoff_markdown(dashboard, for_chatgpt=for_chatgpt),
    }
    return redact_runtime_value(handoff)


def render_handoff_markdown(dashboard: dict[str, Any], *, for_chatgpt: bool = False) -> str:
    active = dashboard.get("active", {})
    validation = dashboard.get("last_validation", {})
    dirty = dashboard.get("dirty_worktree_summary", {})
    safety = dashboard.get("safety_summary", {})
    hints = dashboard.get("recovery_resume_hints", {})
    uploads = dashboard.get("handoff_file_recommendation", {})
    lines = [
        "# Canonical Runtime Handoff",
        "",
        f"- Audience: {'ChatGPT upload bundle' if for_chatgpt else 'local operator'}",
        f"- Active prompt: `{active.get('prompt_id', 'none')}`",
        f"- Active pack: `{active.get('prompt_pack', 'none')}`",
        f"- Next prompt: `{dashboard.get('next_prompt_id', 'unknown')}`",
        f"- Dirty worktree entries: `{dirty.get('total_entries', 0)}`",
        f"- Tracker conflicts: `{len(dashboard.get('tracker_conflicts', []))}`",
        f"- Safe next action: {hints.get('safe_next_action', '')}",
        "",
        "## Validation",
        "",
        f"- Tests: {validation.get('test_result', 'unknown')}",
        f"- Policy: {validation.get('policy_check', 'unknown')}",
        f"- Capabilities: {validation.get('capability_check', 'unknown')}",
        f"- Command registry: {validation.get('command_registry_check', 'unknown')}",
        "",
        "## Safety",
        "",
        f"- ToolBroker preserved: `{safety.get('toolbroker_only_execution_preserved')}`",
        f"- PolicyEngine preserved: `{safety.get('policy_engine_final_authority_preserved')}`",
        f"- ApprovalManager for HIGH/CRITICAL: `{safety.get('approval_manager_required_for_high_critical')}`",
        f"- Personal-data tools enabled by default: `{safety.get('personal_data_tools_enabled_by_default')}`",
        "",
        "## Recommended Uploads",
        "",
        f"- Primary: `{uploads.get('primary', 'docs/HANDOFF_TO_CHATGPT.md')}`",
    ]
    for path in uploads.get("supporting", []):
        lines.append(f"- Supporting: `{path}`")
    return "\n".join(lines) + "\n"
