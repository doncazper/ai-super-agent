from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent.qa.patch_plan import PatchPlan, build_patch_plan, write_patch_plan
from agent.qa.regression_generator import load_bug


def plan_self_heal(project_root: str | Path = ".", *, bug_id: str | None = None) -> dict[str, Any]:
    if not bug_id:
        return {
            "status": "needs_bug",
            "message": "Provide --bug <bug_id> to build a scoped patch plan.",
            "safe_only": True,
        }
    bug = load_bug(project_root, bug_id)
    plan = build_patch_plan(bug)
    path = write_patch_plan(project_root, plan)
    payload = plan.to_dict()
    payload["status"] = "ok"
    payload["path"] = path.relative_to(Path(project_root)).as_posix()
    return payload


def run_self_heal(project_root: str | Path = ".", *, bug_id: str, safe_only: bool = True) -> dict[str, Any]:
    bug = load_bug(project_root, bug_id)
    plan = build_patch_plan(bug)
    write_patch_plan(project_root, plan)
    status = "blocked" if not plan.allowed_to_patch else "needs_review"
    result = {
        "status": status,
        "patch_id": plan.patch_id,
        "bug_id": bug_id,
        "safe_only": safe_only,
        "patch_applied": False,
        "commit_created": False,
        "push_performed": False,
        "reason": plan.reason if not plan.allowed_to_patch else "Patch application is intentionally conservative in v1; human-reviewed scoped patch required.",
        "plan": plan.to_dict(),
    }
    reports = Path(project_root) / "reports/qa"
    reports.mkdir(parents=True, exist_ok=True)
    path = reports / f"{plan.patch_id}_run.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    (reports / "last_self_heal_run.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    result["path"] = path.relative_to(Path(project_root)).as_posix()
    return result


def read_last_self_heal_report(project_root: str | Path = ".") -> dict[str, Any]:
    path = Path(project_root) / "reports/qa/last_self_heal_run.json"
    if not path.exists():
        return {"status": "not_found", "message": "No self-heal run report exists yet."}
    return json.loads(path.read_text(encoding="utf-8"))

