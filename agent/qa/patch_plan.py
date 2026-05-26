from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from agent.qa.redaction import redact_text


BROAD_REFACTOR_MARKERS = ("broad refactor", "rewrite", "architecture change", "migration", "redesign")
PACKAGE_INSTALL_MARKERS = ("pip install", "npm install", "package install", "add dependency")
POLICY_CHANGE_MARKERS = ("weaken policy", "disable audit", "bypass approval", "bypass toolbroker")


@dataclass(frozen=True)
class PatchPlan:
    patch_id: str
    bug_id: str
    severity: str
    allowed_to_patch: bool
    reason: str
    branch_name: str
    files_expected: list[str]
    tests_required: list[str]
    docs_required: list[str]
    risk: str
    rollback_plan: str
    human_review_required: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _patch_id(bug: dict[str, Any]) -> str:
    seed = f"{bug.get('bug_id', '')}:{bug.get('command_id', '')}:{bug.get('failure_type', '')}"
    return "qa_patch_" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:10]


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in markers)


def build_patch_plan(bug: dict[str, Any]) -> PatchPlan:
    text = redact_text(" ".join(str(bug.get(key, "")) for key in ("actual_behavior", "suggested_fix", "expected_behavior", "failure_type")))
    bug_id = str(bug.get("bug_id", "BUG-UNKNOWN"))
    severity = str(bug.get("severity", "P2"))
    regression = str(bug.get("suggested_regression_test", ""))
    reasons: list[str] = []
    allowed = True
    if severity in {"P0", "P1"}:
        allowed = False
        reasons.append("P0/P1 bugs require human review before patching.")
    if _contains_any(text, BROAD_REFACTOR_MARKERS):
        allowed = False
        reasons.append("Broad refactor/rewrite signal found.")
    if _contains_any(text, PACKAGE_INSTALL_MARKERS):
        allowed = False
        reasons.append("Package installation signal found.")
    if _contains_any(text, POLICY_CHANGE_MARKERS):
        allowed = False
        reasons.append("Policy/approval/audit bypass signal found.")
    if not regression or not regression.startswith("tests/"):
        allowed = False
        reasons.append("A linked regression test under tests/ is required.")
    risk = "MEDIUM" if severity == "P2" else "LOW"
    if severity in {"P0", "P1"}:
        risk = "HIGH"
    return PatchPlan(
        patch_id=_patch_id(bug),
        bug_id=bug_id,
        severity=severity,
        allowed_to_patch=allowed,
        reason=" ".join(reasons) if reasons else "Scoped low/medium-risk local bug with regression evidence.",
        branch_name=f"codex/qa-self-heal-{bug_id.lower()}",
        files_expected=[],
        tests_required=[regression] if regression else [],
        docs_required=["CHANGELOG.md", "docs/PROJECT_STATE.md", "docs/COMPLETION_REPORT.md"],
        risk=risk,
        rollback_plan="Revert the scoped patch before commit; no commit/push is performed by the self-heal loop.",
        human_review_required=True,
    )


def write_patch_plan(project_root: str | Path, plan: PatchPlan) -> Path:
    import json

    reports = Path(project_root) / "reports/qa"
    reports.mkdir(parents=True, exist_ok=True)
    path = reports / f"{plan.patch_id}.json"
    path.write_text(json.dumps(plan.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    (reports / "last_self_heal_plan.json").write_text(json.dumps(plan.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return path

