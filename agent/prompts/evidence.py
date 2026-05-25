from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from agent.ui.prompts import PromptRecord, list_prompt_records


CLASSIFICATIONS = {
    "complete_verified",
    "likely_complete",
    "partial",
    "no_evidence",
    "failed",
    "blocked",
    "superseded",
    "stale",
}

EVIDENCE_PATHS = (
    Path("CHANGELOG.md"),
    Path("README.md"),
    Path("docs/COMPLETION_REPORT.md"),
    Path("docs/FEATURE_REGISTRY.md"),
    Path("docs/FEATURE_MATURITY.md"),
    Path("docs/FEATURE_ROADMAP.md"),
    Path("docs/PROJECT_STATE.md"),
    Path("docs/COMMAND_REGISTRY.md"),
    Path("docs/PROMPT_AUDIT.md"),
    Path("docs/PROMPT_LEDGER.md"),
    Path("docs/PROMPT_QUEUE.md"),
)


@dataclass(frozen=True)
class PromptEvidence:
    prompt_id: str
    status: str
    classification: str
    evidence_links: list[str]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompt_id": self.prompt_id,
            "status": self.status,
            "classification": self.classification,
            "evidence_links": self.evidence_links,
            "reason": self.reason,
        }


def audit_prompt_evidence(project_root: str | Path = ".", prompt_id: str | None = None) -> dict[str, Any]:
    root = Path(project_root)
    records = list_prompt_records(root)
    if prompt_id:
        records = [record for record in records if record.prompt_id == prompt_id]
    evidence = [classify_prompt(record, root).to_dict() for record in records]
    counts: dict[str, int] = {name: 0 for name in sorted(CLASSIFICATIONS)}
    for item in evidence:
        counts[str(item["classification"])] = counts.get(str(item["classification"]), 0) + 1
    return {
        "status": "ok",
        "prompt_id": prompt_id,
        "total": len(evidence),
        "counts": counts,
        "evidence": evidence,
    }


def classify_prompt(record: PromptRecord, project_root: str | Path = ".") -> PromptEvidence:
    root = Path(project_root)
    if record.status in {"failed", "blocked", "superseded"}:
        return PromptEvidence(record.prompt_id, record.status, record.status, _record_links(record, root), f"prompt status is {record.status}")

    links = _matching_evidence_links(record, root)
    if record.status == "completed":
        if len(links) >= 2:
            return PromptEvidence(record.prompt_id, record.status, "complete_verified", links, "completed prompt has multiple evidence links")
        if links:
            return PromptEvidence(record.prompt_id, record.status, "likely_complete", links, "completed prompt has at least one evidence link")
        return PromptEvidence(record.prompt_id, record.status, "stale", links, "completed prompt has no supporting evidence in tracked docs")

    if links:
        return PromptEvidence(record.prompt_id, record.status, "partial", links, "prompt has evidence but is not marked completed")
    return PromptEvidence(record.prompt_id, record.status, "no_evidence", links, "no tracked evidence found")


def _matching_evidence_links(record: PromptRecord, root: Path) -> list[str]:
    links: list[str] = []
    for path in _candidate_paths(root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if _has_evidence(record, text):
            links.append(path.relative_to(root).as_posix())
    return links


def _record_links(record: PromptRecord, root: Path) -> list[str]:
    links = []
    if record.path:
        candidate = root / record.path
        if candidate.exists():
            links.append(candidate.relative_to(root).as_posix())
    return links


def _candidate_paths(root: Path) -> Iterable[Path]:
    for path in EVIDENCE_PATHS:
        candidate = root / path
        if candidate.exists():
            yield candidate
    for glob in ("tests/**/*.py", "dogfood_suites/*.yaml", "eval_cases/**/*.json", "docs/prompt_tracker/*.md"):
        yield from sorted(root.glob(glob))


def _has_evidence(record: PromptRecord, text: str) -> bool:
    lowered = text.lower()
    if record.prompt_id.lower() in lowered:
        return True
    terms = [term for term in re.split(r"[\s/_+-]+", record.title.lower()) if len(term) >= 5]
    return bool(terms and sum(1 for term in terms if term in lowered) >= min(2, len(terms)))
