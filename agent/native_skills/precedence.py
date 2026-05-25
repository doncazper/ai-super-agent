from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from agent.native_skills.roots import SkillCandidate, SkillRoot, default_skill_roots, scan_skill_roots


@dataclass(frozen=True)
class SkillResolution:
    skill_id: str
    winning_skill: SkillCandidate | None
    shadowed_candidates: list[SkillCandidate]
    diagnostics: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "winning_skill": self.winning_skill.to_dict() if self.winning_skill else None,
            "shadowed_candidates": [candidate.to_dict() for candidate in self.shadowed_candidates],
            "diagnostics": list(self.diagnostics),
        }


def resolve_skill(skill_id: str, candidates: list[SkillCandidate], roots: list[SkillRoot]) -> SkillResolution:
    root_by_id = {root.root_id: root for root in roots}
    matches = [candidate for candidate in candidates if candidate.skill_id == skill_id and root_by_id.get(candidate.root_id, None)]
    matches.sort(key=lambda candidate: root_by_id[candidate.root_id].default_precedence)
    diagnostics: list[str] = []
    if not matches:
        return SkillResolution(skill_id=skill_id, winning_skill=None, shadowed_candidates=[], diagnostics=["skill not found"])

    winner: SkillCandidate | None = None
    for index, candidate in enumerate(matches):
        root = root_by_id[candidate.root_id]
        lower = matches[index + 1 :]
        if lower and not root.allow_shadowing:
            diagnostics.append(f"{candidate.root_id} cannot shadow lower-precedence candidates by default")
            continue
        if lower and not candidate.trusted and any(root_by_id[item.root_id].trusted for item in lower):
            diagnostics.append(f"{candidate.root_id} is untrusted and cannot shadow trusted native skills")
            continue
        winner = candidate
        break

    if winner is None:
        winner = matches[-1]
        diagnostics.append(f"falling back to lowest-precedence candidate from {winner.root_id}")

    shadowed = [candidate for candidate in matches if candidate != winner]
    if shadowed:
        diagnostics.append("shadowing visible in diagnostics")
    for candidate in shadowed:
        root = root_by_id[candidate.root_id]
        if not root.trusted:
            diagnostics.append(f"{candidate.root_id} is untrusted and remains shadowed by the winning skill")
    return SkillResolution(skill_id=skill_id, winning_skill=winner, shadowed_candidates=shadowed, diagnostics=diagnostics)


def duplicate_skill_ids(candidates: list[SkillCandidate]) -> dict[str, list[SkillCandidate]]:
    grouped: dict[str, list[SkillCandidate]] = {}
    for candidate in candidates:
        grouped.setdefault(candidate.skill_id, []).append(candidate)
    return {skill_id: items for skill_id, items in grouped.items() if len(items) > 1}


def precedence_report(project_root: str = ".") -> dict[str, Any]:
    roots = default_skill_roots(project_root)
    candidates = scan_skill_roots(roots)
    duplicates = duplicate_skill_ids(candidates)
    resolutions = [resolve_skill(skill_id, candidates, roots).to_dict() for skill_id in sorted(duplicates)]
    return {
        "status": "ok",
        "root_count": len(roots),
        "candidate_count": len(candidates),
        "duplicate_skill_ids": {skill_id: [asdict(item) for item in items] for skill_id, items in duplicates.items()},
        "resolutions": resolutions,
        "scan_behavior": "metadata_only; SKILL.md and manifests are read as UNTRUSTED_DOCUMENT and no scripts are executed",
    }
