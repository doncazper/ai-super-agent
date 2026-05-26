from __future__ import annotations

from pathlib import Path
from typing import Any

from .canonical_state import build_canonical_runtime_state, build_reconcile_preview
from .state import redact_runtime_value


TRACKER_ROLES: tuple[dict[str, str], ...] = (
    {"tracker": "canonical runtime state", "future_role": "machine-readable active-work truth"},
    {"tracker": "docs/PROMPT_LEDGER.md", "future_role": "historical prompt evidence"},
    {"tracker": "docs/PROMPT_QUEUE.md", "future_role": "planned-order and active/queued view"},
    {"tracker": "docs/PROMPT_AUDIT.md", "future_role": "prompt reconciliation/audit view"},
    {"tracker": "docs/PROJECT_STATE.md", "future_role": "human-readable resume summary"},
    {"tracker": "docs/COMPLETION_REPORT.md", "future_role": "release and validation evidence"},
    {"tracker": "docs/TRACKER_DASHBOARD.md", "future_role": "summary/dashboard only"},
    {"tracker": "docs/HANDOFF_TO_CHATGPT.md", "future_role": "external communication summary"},
)


def build_tracker_sync_preview(project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    state = build_canonical_runtime_state(root).to_dict()
    reconcile = build_reconcile_preview(root)
    preview = {
        "status": "ok",
        "read_only": True,
        "side_effects": "none; tracker sync preview does not write files",
        "auto_overwrite_trackers": False,
        "broad_rewrites_allowed": False,
        "canonical_active_work": {
            "active_prompt_id": state.get("active_prompt_id", "none"),
            "active_prompt_pack": state.get("active_prompt_pack", "none"),
            "active_job_id": state.get("active_job_id", "none"),
            "active_workflow_id": state.get("active_workflow_id", "none"),
            "active_action_id": state.get("active_action_id", "none"),
            "next_prompt_id": state.get("next_prompt_id", "unknown"),
            "current_status": state.get("current_status", "unknown"),
        },
        "tracker_roles": list(TRACKER_ROLES),
        "migration_phases": [
            "Keep existing markdown trackers as source-of-truth records while canonical state matures.",
            "Use canonical state as the machine-readable active-work view for dashboards and handoffs.",
            "Report conflicts before edits; do not auto-overwrite trackers.",
            "Make small anchored tracker edits only when evidence is clear.",
            "Introduce generated summary views only after release-gate validation.",
        ],
        "conflict_count": len(reconcile.get("conflicts", [])),
        "conflicts": reconcile.get("conflicts", []),
        "sync_policy": {
            "small_anchored_edits_only": True,
            "preserve_history": True,
            "completed_prompts_require_evidence": True,
            "active_prompt_singleton": True,
            "summary_dashboards_not_primary_truth": True,
        },
    }
    return redact_runtime_value(preview)


def build_tracker_conflict_report(project_root: str | Path = ".") -> dict[str, Any]:
    reconcile = build_reconcile_preview(project_root)
    conflicts = reconcile.get("conflicts", [])
    return redact_runtime_value(
        {
            "status": "ok" if not conflicts else "needs_reconciliation",
            "read_only": True,
            "side_effects": "none; conflict report does not change trackers",
            "conflict_count": len(conflicts),
            "conflicts": conflicts,
            "recommended_fix_policy": "Use small anchored edits with evidence; do not broadly rewrite dense trackers.",
        }
    )
