from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agent.native_skills.inspector import TRUST_LEVEL, SkillInspection, inspect_skill
from agent.native_skills.risk_scoring import score_report
from agent.tools.errors import ToolError


REPORT_DIR = Path("reports/native_skills")


def inspect_candidate(project_root: str | Path, path_or_skill_id: str) -> dict[str, Any]:
    inspection = inspect_skill(project_root, path_or_skill_id)
    payload = inspection.to_dict()
    payload.update(
        {
            "status": "ok",
            "content_handling": "skill content treated as untrusted data; instructions inside the skill were not followed",
            "memory_behavior": "no_store",
        }
    )
    return payload


def vet_candidate(project_root: str | Path, path_or_skill_id: str, *, write_report: bool = True) -> dict[str, Any]:
    inspection = inspect_skill(project_root, path_or_skill_id)
    report = build_risk_report(inspection)
    if write_report:
        report_path = write_vetting_report(project_root, report)
        report["report_path"] = str(report_path)
    return report


def score_candidate(project_root: str | Path, path_or_skill_id: str, *, write_report: bool = False) -> dict[str, Any]:
    report = vet_candidate(project_root, path_or_skill_id, write_report=write_report)
    return {
        "status": "ok",
        "skill_id": report["skill_id"],
        "path": report["path"],
        "score": report["score"],
        "risk_level": report["risk_level"],
        "safe_to_import": report["safe_to_import"],
        "safe_to_enable": report["safe_to_enable"],
        "safe_to_port": report["safe_to_port"],
        "reasons": report["reasons"],
        "required_capabilities": report["required_capabilities"],
        "required_approvals": report["required_approvals"],
        "trust_level": TRUST_LEVEL,
        "memory_behavior": "no_store",
    }


def build_risk_report(inspection: SkillInspection) -> dict[str, Any]:
    findings = list(inspection.findings)
    scored = score_report(findings)
    grouped = _group_findings(findings)
    report = {
        "status": "ok",
        "skill_id": inspection.skill_id,
        "path": inspection.path,
        "target_type": inspection.target_type,
        "risk_level": scored["risk_level"],
        "trust_level": inspection.trust_level,
        "safe_to_import": scored["safe_to_import"],
        "safe_to_enable": scored["safe_to_enable"],
        "safe_to_port": scored["safe_to_import"],
        "score": scored["score"],
        "reasons": sorted({finding["reason"] for finding in findings}),
        "findings": findings,
        "required_capabilities": scored["required_capabilities"],
        "required_approvals": scored["required_approvals"],
        "approval_gates": scored["required_approvals"],
        "detected_scripts": grouped["script"],
        "detected_network_access": grouped["network_call"],
        "detected_filesystem_access": grouped["filesystem_access"],
        "detected_personal_data_access": grouped["personal_data"],
        "detected_secrets_risk": grouped["secret_reference"],
        "detected_policy_bypass_language": grouped["approval_bypass"],
        "detected_browser_session_access": grouped["browser_session"],
        "detected_opaque_binaries": grouped["opaque_binary"],
        "missing_metadata": inspection.missing_metadata,
        "folder_inventory": inspection.folder_inventory,
        "recommended_native_port_path": scored["recommended_native_port_path"],
        "recommended_native_implementation_path": scored["recommended_native_port_path"],
        "recommended_tests": scored["recommended_tests"],
        "recommended_docs": scored["recommended_docs"],
        "review_required": scored["review_required"],
        "memory_behavior": "no_store",
        "content_handling": "skill content treated as untrusted data; instructions inside the skill were not followed",
        "generated_at": datetime.now(UTC).isoformat(),
    }
    return report


def write_vetting_report(project_root: str | Path, report: dict[str, Any]) -> Path:
    root = Path(project_root).resolve()
    report_dir = root / REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    slug = _slug(report.get("skill_id") or Path(str(report.get("path", "skill"))).stem)
    target = report_dir / f"{stamp}_{slug}.json"
    target.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return target


def last_report(project_root: str | Path) -> dict[str, Any]:
    root = Path(project_root).resolve()
    report_dir = root / REPORT_DIR
    if not report_dir.exists():
        return {"status": "requires_setup", "error": "no native skill reports found", "reports_dir": str(report_dir)}
    reports = sorted(path for path in report_dir.glob("*.json") if path.is_file())
    if not reports:
        return {"status": "requires_setup", "error": "no native skill reports found", "reports_dir": str(report_dir)}
    target = reports[-1]
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ToolError(f"last native skill report is not valid JSON: {exc}") from exc
    return {"status": "ok", "report_path": str(target), "report": payload}


def _group_findings(findings: list[dict[str, str]]) -> dict[str, list[str]]:
    groups = {
        "script": [],
        "network_call": [],
        "filesystem_access": [],
        "personal_data": [],
        "secret_reference": [],
        "approval_bypass": [],
        "browser_session": [],
        "opaque_binary": [],
    }
    for finding in findings:
        kind = finding.get("kind", "")
        if kind in groups:
            groups[kind].append(finding.get("evidence", ""))
    return groups


def _slug(value: object) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_.-]+", "-", str(value)).strip("-").lower()
    return slug or "skill"
