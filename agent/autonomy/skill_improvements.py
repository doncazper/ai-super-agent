from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


RISK_ORDER = {"SAFE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4, "FORBIDDEN": 5}
DEFAULT_STORE = Path("reports/autonomy/skill_improvements.json")
PERSONAL_TERMS = ("email", "gmail", "message", "calendar", "contacts", "phone", "address", "LOCAL_PRIVATE_DATA")


@dataclass(frozen=True)
class ImprovementEvidence:
    source_type: str
    source_id: str
    skill_id: str
    summary: str
    severity: str = "LOW"
    risk_level: str = "LOW"
    redacted: bool = True
    contains_personal_data: bool = False
    test_hint: str = "add regression test for observed failure"
    docs_hint: str = "update skill docs with limitation or behavior change"

    @classmethod
    def from_mapping(cls, raw: dict[str, Any], *, default_skill_id: str) -> "ImprovementEvidence":
        summary = str(raw.get("summary") or raw.get("title") or raw.get("description") or raw.get("reason") or "")
        return cls(
            source_type=str(raw.get("source_type") or raw.get("type") or "metadata"),
            source_id=str(raw.get("source_id") or raw.get("bug_id") or raw.get("id") or _hash_id(summary)),
            skill_id=str(raw.get("skill_id") or default_skill_id),
            summary=_redact(summary),
            severity=str(raw.get("severity") or "LOW").upper(),
            risk_level=str(raw.get("risk_level") or raw.get("risk") or raw.get("severity") or "LOW").upper(),
            redacted=bool(raw.get("redacted", True)),
            contains_personal_data=bool(raw.get("contains_personal_data", False)),
            test_hint=str(raw.get("test_hint") or "add regression test for observed failure"),
            docs_hint=str(raw.get("docs_hint") or "update skill docs with limitation or behavior change"),
        )


@dataclass(frozen=True)
class SkillImprovementProposal:
    improvement_id: str
    skill_id: str
    evidence_sources: list[str]
    bug_ids: list[str]
    dogfood_failures: list[str]
    user_feedback: list[str]
    proposed_change: str
    risk_level: str
    files_expected: list[str]
    tests_required: list[str]
    docs_required: list[str]
    lockfile_impact: str
    rollback_plan: str
    human_review_required: bool
    status: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0).isoformat())
    modifies_files: bool = False
    updates_lockfile: bool = False
    enables_skill: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def improvement_store_path(project_root: str | Path = ".") -> Path:
    override = os.getenv("SKILL_IMPROVEMENT_STORE_PATH")
    if override:
        return Path(override).expanduser().resolve()
    return Path(project_root).resolve() / DEFAULT_STORE


def propose_improvements_from_evidence(
    skill_id: str,
    evidence: Iterable[ImprovementEvidence | dict[str, Any]],
    *,
    source_mode: str = "provided_evidence",
) -> dict[str, Any]:
    records = [item if isinstance(item, ImprovementEvidence) else ImprovementEvidence.from_mapping(item, default_skill_id=skill_id) for item in evidence]
    skipped: list[dict[str, str]] = []
    usable: list[ImprovementEvidence] = []
    for item in records:
        if item.skill_id != skill_id:
            continue
        if not item.redacted:
            skipped.append({"source_id": item.source_id, "reason": "unredacted evidence skipped"})
            continue
        if item.contains_personal_data or _contains_personal(item.summary):
            skipped.append({"source_id": item.source_id, "reason": "personal-data evidence skipped by default"})
            continue
        if not item.summary.strip():
            skipped.append({"source_id": item.source_id, "reason": "empty evidence skipped"})
            continue
        usable.append(item)

    if not usable:
        return {
            "status": "no_evidence",
            "skill_id": skill_id,
            "proposal_count": 0,
            "proposals": [],
            "skipped": skipped,
            "confidence": "low",
            "setup_hint": "Add redacted bug, dogfood, feedback, regression, or command-QA evidence before proposing an improvement.",
            "modifies_files": False,
        }

    proposal = _proposal_for_evidence(skill_id, usable)
    return {
        "status": "ok",
        "skill_id": skill_id,
        "source_mode": source_mode,
        "proposal_count": 1,
        "proposals": [proposal.to_dict()],
        "skipped": skipped,
        "confidence": "medium" if len(usable) == 1 else "high",
        "modifies_files": False,
        "updates_lockfile": False,
        "enables_skill": False,
    }


def propose_from_bugs(skill_id: str, *, project_root: str | Path = ".") -> dict[str, Any]:
    evidence = _bug_evidence(skill_id, Path(project_root))
    report = propose_improvements_from_evidence(skill_id, evidence, source_mode="bugs")
    return _persist_report(report, project_root=project_root)


def propose_from_dogfood(skill_id: str, *, project_root: str | Path = ".") -> dict[str, Any]:
    evidence = _dogfood_evidence(skill_id, Path(project_root))
    report = propose_improvements_from_evidence(skill_id, evidence, source_mode="dogfood")
    return _persist_report(report, project_root=project_root)


def propose_from_all(skill_id: str, *, project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    evidence = _bug_evidence(skill_id, root) + _dogfood_evidence(skill_id, root)
    report = propose_improvements_from_evidence(skill_id, evidence, source_mode="bugs_and_dogfood")
    return _persist_report(report, project_root=project_root)


def list_improvements(project_root: str | Path = ".") -> dict[str, Any]:
    payload = _load_store(project_root)
    proposals = payload.get("proposals", [])
    return {
        "status": "ok",
        "improvement_count": len(proposals),
        "improvements": [
            {
                "improvement_id": proposal.get("improvement_id"),
                "skill_id": proposal.get("skill_id"),
                "risk_level": proposal.get("risk_level"),
                "human_review_required": proposal.get("human_review_required"),
                "status": proposal.get("status"),
            }
            for proposal in proposals
        ],
        "store_path": str(improvement_store_path(project_root)),
        "modifies_files": False,
    }


def show_improvement(improvement_id: str, *, project_root: str | Path = ".") -> dict[str, Any]:
    payload = _load_store(project_root)
    for proposal in payload.get("proposals", []):
        if proposal.get("improvement_id") == improvement_id:
            return {"status": "ok", "improvement": proposal, "modifies_files": False}
    return {"status": "not_found", "improvement_id": improvement_id, "setup_hint": "Run skills improve-propose, improve-from-bugs, or improve-from-dogfood first."}


def _proposal_for_evidence(skill_id: str, evidence: list[ImprovementEvidence]) -> SkillImprovementProposal:
    risk = _max_risk(evidence)
    review_required = RISK_ORDER.get(risk, 1) >= RISK_ORDER["HIGH"]
    bug_ids = [item.source_id for item in evidence if item.source_type == "bug"]
    dogfood = [item.source_id for item in evidence if item.source_type == "dogfood"]
    feedback = [item.source_id for item in evidence if item.source_type == "feedback"]
    summary = "; ".join(item.summary for item in evidence[:3])
    improvement_id = _improvement_id(skill_id, [item.source_id for item in evidence])
    return SkillImprovementProposal(
        improvement_id=improvement_id,
        skill_id=skill_id,
        evidence_sources=sorted({f"{item.source_type}:{item.source_id}" for item in evidence}),
        bug_ids=bug_ids,
        dogfood_failures=dogfood,
        user_feedback=feedback,
        proposed_change=f"Review `{skill_id}` for the observed evidence and prepare a minimal patch addressing: {summary}",
        risk_level=risk,
        files_expected=[f"native_skills/{skill_id}.yaml", f"docs/native_skills/{skill_id}.md", "tests/native_skills/"],
        tests_required=sorted({item.test_hint for item in evidence} | {"prove no external skill scripts execute", "prove skill remains disabled until reviewed"}),
        docs_required=sorted({item.docs_hint for item in evidence} | {"document known limitation and rollback path"}),
        lockfile_impact="No lockfile change in proposal phase; future skill file edits require reviewed lockfile impact and verification.",
        rollback_plan="Do not apply automatically. If a future reviewed patch fails, revert only that patch, restore prior manifest/docs/tests, rerun validation, and keep the proposal as historical evidence.",
        human_review_required=review_required,
        status="needs_review" if review_required else "candidate_unreviewed",
    )


def _persist_report(report: dict[str, Any], *, project_root: str | Path) -> dict[str, Any]:
    payload = {
        **report,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "store_policy": "redacted improvement proposal metadata only; no skill files or lockfiles modified",
    }
    path = improvement_store_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    payload["report_path"] = str(path)
    return payload


def _load_store(project_root: str | Path) -> dict[str, Any]:
    path = improvement_store_path(project_root)
    if not path.exists():
        return {
            "status": "requires_setup",
            "proposal_count": 0,
            "proposals": [],
            "setup_hint": "Run skills improve-propose, improve-from-bugs, or improve-from-dogfood first.",
            "store_path": str(path),
        }
    return json.loads(path.read_text(encoding="utf-8"))


def _bug_evidence(skill_id: str, root: Path) -> list[ImprovementEvidence]:
    bug_dir = root / "bugs"
    evidence: list[ImprovementEvidence] = []
    if not bug_dir.exists():
        return evidence
    for path in sorted(bug_dir.glob("*.json"))[:100]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        text = " ".join(str(payload.get(key, "")) for key in ("bug_id", "id", "title", "summary", "component", "feature", "notes"))
        if skill_id not in text and "native_skill" not in text and "skills" not in text:
            continue
        evidence.append(
            ImprovementEvidence(
                source_type="bug",
                source_id=str(payload.get("bug_id") or payload.get("id") or path.stem),
                skill_id=skill_id,
                summary=_redact(str(payload.get("summary") or payload.get("title") or path.stem)),
                severity=str(payload.get("severity") or "LOW").upper(),
                risk_level=str(payload.get("risk_level") or payload.get("severity") or "LOW").upper(),
            )
        )
    return evidence


def _dogfood_evidence(skill_id: str, root: Path) -> list[ImprovementEvidence]:
    session_dir = root / "reports" / "sessions"
    evidence: list[ImprovementEvidence] = []
    if not session_dir.exists():
        return evidence
    for path in sorted(session_dir.glob("*.json"))[:100]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not _is_redacted(payload):
            continue
        for index, item in enumerate(payload.get("commands", [])):
            if not isinstance(item, dict):
                continue
            status = str(item.get("status") or item.get("result") or "").lower()
            text = " ".join(str(item.get(key, "")) for key in ("command", "command_preview", "summary", "error"))
            if skill_id in text and status in {"failed", "fail", "error"}:
                evidence.append(
                    ImprovementEvidence(
                        source_type="dogfood",
                        source_id=f"{path.stem}:{index}",
                        skill_id=skill_id,
                        summary=_redact(str(item.get("summary") or item.get("error") or "dogfood command failed")),
                        severity="MEDIUM",
                        risk_level="MEDIUM",
                    )
                )
    return evidence


def _is_redacted(payload: dict[str, Any]) -> bool:
    privacy = payload.get("privacy") if isinstance(payload.get("privacy"), dict) else {}
    return bool(payload.get("redacted") or payload.get("is_redacted") or privacy.get("redacted"))


def _max_risk(evidence: Iterable[ImprovementEvidence]) -> str:
    risk = "LOW"
    for item in evidence:
        candidate = item.risk_level.upper().split("/")[0]
        if RISK_ORDER.get(candidate, 1) > RISK_ORDER.get(risk, 1):
            risk = candidate
    return risk


def _improvement_id(skill_id: str, source_ids: list[str]) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", skill_id.casefold()).strip("_")[:36]
    digest = hashlib.sha256((skill_id + "\n" + "\n".join(sorted(source_ids))).encode("utf-8")).hexdigest()[:10]
    return f"improvement_{slug}_{digest}"


def _hash_id(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _redact(text: str) -> str:
    text = re.sub(r"(?i)(api[_-]?key|token|secret|password)=\\S+", r"\1=[REDACTED]", text)
    text = re.sub(r"(?i)(--(?:api-key|token|secret|password))\\s+\\S+", r"\1 [REDACTED]", text)
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+", "[REDACTED_EMAIL]", text)
    return text[:280]


def _contains_personal(text: str) -> bool:
    lowered = text.casefold()
    return any(term.casefold() in lowered for term in PERSONAL_TERMS)

