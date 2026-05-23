from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent.native_skills.registry import NativeSkillRegistry
from agent.tools.errors import ToolError


STOPWORDS = {
    "a",
    "about",
    "an",
    "and",
    "can",
    "for",
    "help",
    "i",
    "in",
    "need",
    "of",
    "the",
    "to",
    "with",
    "work",
    "you",
}

SYNONYMS = {
    "pdf": {"pdf", "pdfs", "document", "documents"},
    "pdfs": {"pdf", "pdfs", "document", "documents"},
    "doc": {"doc", "docx", "document", "documents", "office"},
    "docx": {"doc", "docx", "document", "documents", "office"},
    "ppt": {"ppt", "pptx", "presentation", "presentations", "office"},
    "pptx": {"ppt", "pptx", "presentation", "presentations", "office"},
    "xlsx": {"xlsx", "spreadsheet", "spreadsheets", "office"},
    "sheet": {"xlsx", "spreadsheet", "spreadsheets", "office"},
    "meeting": {"meeting", "meetings", "calendar", "follow", "followup", "follow-up"},
    "follow": {"follow", "followup", "follow-up", "meeting"},
    "followup": {"follow", "followup", "follow-up", "meeting"},
    "email": {"email", "emails", "draft", "triage"},
    "message": {"message", "messages", "text", "draft"},
    "skill": {"skill", "skills", "native"},
    "vet": {"vet", "vetter", "review", "safety"},
}


@dataclass(frozen=True)
class SkillSearchRecord:
    skill_id: str
    name: str
    source: str
    source_path: str
    searchable_text: str
    maturity_level: str
    readiness_score: int | None
    implemented: bool
    safe_to_use_now: bool
    required_approvals: str
    required_capabilities: list[str]
    next_work_needed: str
    docs_path: str


def find_native_skills(query: str, *, project_root: str | Path = ".", max_results: int = 5) -> dict[str, Any]:
    normalized_query = " ".join(str(query or "").split())
    if not normalized_query:
        raise ToolError("query is required")
    if max_results < 1 or max_results > 20:
        raise ToolError("max_results must be between 1 and 20")

    root = Path(project_root).resolve()
    files_read: set[str] = set()
    records = _manifest_records(root, files_read)
    records.extend(_feature_registry_records(root, files_read))
    records.extend(_feature_maturity_records(root, files_read))
    records.extend(_native_candidate_records(root, files_read))

    query_tokens = _expand_tokens(_tokens(normalized_query))
    ranked: list[tuple[int, SkillSearchRecord]] = []
    for record in records:
        score = _match_score(query_tokens, normalized_query, record)
        if score > 0:
            ranked.append((score, record))
    ranked.sort(key=lambda item: (-item[0], item[1].source, item[1].name.casefold()))

    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for score, record in ranked:
        key = _dedupe_key(record)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(_record_to_match(record, score))
        if len(deduped) >= max_results:
            break

    return {
        "status": "ok",
        "query": normalized_query,
        "matches": deduped,
        "candidate_creation": {
            "recommended": not deduped,
            "path": "docs/native_skills/NATIVE_SKILL_CANDIDATES.md",
            "next_steps": [
                "Create a native skill candidate record with requirements, risks, ToolBroker capabilities, approvals, memory behavior, and tests.",
                "Run the native skill vetter before any implementation.",
                "Add a metadata-only manifest only after the candidate maps to known capabilities.",
            ],
        },
        "searched_sources": sorted(files_read),
        "external_search_used": False,
        "external_install_used": False,
        "content_handling": "local native skill metadata and candidate docs were searched as data only; no external code was installed or executed",
        "_audit": {
            "files_read": sorted(files_read),
            "result_summary": f"Native skill finder returned {len(deduped)} match(es).",
        },
    }


def _manifest_records(root: Path, files_read: set[str]) -> list[SkillSearchRecord]:
    records: list[SkillSearchRecord] = []
    for manifest in NativeSkillRegistry(root).manifests():
        if manifest.source_path:
            files_read.add(str(Path(manifest.source_path).resolve()))
        status = manifest.status.casefold()
        implemented = status in {"available", "implemented", "active"}
        records.append(
            SkillSearchRecord(
                skill_id=manifest.skill_id,
                name=manifest.name,
                source="native_skill_manifest",
                source_path=manifest.source_path,
                searchable_text=" ".join(
                    [
                        manifest.skill_id,
                        manifest.name,
                        manifest.description,
                        manifest.category,
                        manifest.status,
                        manifest.maturity_level,
                        " ".join(manifest.allowed_tools),
                        " ".join(manifest.required_capabilities),
                    ]
                ),
                maturity_level=manifest.maturity_level,
                readiness_score=_score_from_maturity(manifest.maturity_level),
                implemented=implemented,
                safe_to_use_now=implemented and manifest.risk_level in {"SAFE", "LOW", "MEDIUM"} and not bool(manifest.approval_required),
                required_approvals=_approval_text(manifest.approval_required),
                required_capabilities=list(manifest.required_capabilities),
                next_work_needed="Use the listed command/docs if available; keep all tool calls through ToolBroker." if implemented else "Finish implementation and tests before use.",
                docs_path=manifest.docs_path,
            )
        )
    return records


def _feature_registry_records(root: Path, files_read: set[str]) -> list[SkillSearchRecord]:
    path = root / "docs/FEATURE_REGISTRY.md"
    rows = _markdown_table_rows(path, files_read)
    records: list[SkillSearchRecord] = []
    for row in rows:
        feature_id = row.get("Feature ID", "")
        name = row.get("Feature name", "")
        if not feature_id or not name:
            continue
        status = row.get("Status: planned, in_progress, complete, blocked, deferred") or row.get("Status", "")
        capabilities = _split_inline_values(row.get("Capabilities", ""))
        approval = row.get("Approval required", "")
        risk = row.get("Risk level", "")
        records.append(
            SkillSearchRecord(
                skill_id=feature_id,
                name=name,
                source="feature_registry",
                source_path=str(path),
                searchable_text=" ".join(row.values()),
                maturity_level=_registry_maturity_hint(status),
                readiness_score=None,
                implemented=status.casefold() == "complete",
                safe_to_use_now=status.casefold() == "complete" and "CRITICAL" not in risk and "blocked" not in row.get("Release gate status", "").casefold(),
                required_approvals=approval or "none recorded",
                required_capabilities=capabilities,
                next_work_needed=row.get("Release gate status", "") or "Check feature registry and maturity tracker.",
                docs_path=row.get("Docs", ""),
            )
        )
    return records


def _feature_maturity_records(root: Path, files_read: set[str]) -> list[SkillSearchRecord]:
    path = root / "docs/FEATURE_MATURITY.md"
    rows = _markdown_table_rows(path, files_read)
    records: list[SkillSearchRecord] = []
    for row in rows:
        feature = row.get("Feature", "")
        if not feature or feature == "Level":
            continue
        maturity = row.get("Maturity Level", "")
        readiness = _parse_int(row.get("Readiness Score", ""))
        implemented = _maturity_number(maturity) >= 3
        records.append(
            SkillSearchRecord(
                skill_id=_slug(feature),
                name=feature,
                source="feature_maturity",
                source_path=str(path),
                searchable_text=" ".join(row.values()),
                maturity_level=maturity or "unknown",
                readiness_score=readiness,
                implemented=implemented,
                safe_to_use_now=_maturity_number(maturity) >= 4 and "not implemented" not in " ".join(row.values()).casefold(),
                required_approvals=_infer_approvals(" ".join(row.values())),
                required_capabilities=_extract_capability_names(" ".join(row.values())),
                next_work_needed=row.get("Next Work Needed", "") or row.get("Known Limitations", "") or "Check maturity tracker.",
                docs_path="docs/FEATURE_MATURITY.md",
            )
        )
    return records


def _native_candidate_records(root: Path, files_read: set[str]) -> list[SkillSearchRecord]:
    paths = [
        root / "docs/native_skills/NATIVE_CANDIDATE_MATRIX.md",
        root / "docs/native_skills/TOP_NATIVE_SKILL_SHORTLIST.md",
        root / "docs/native_skills/NATIVE_SKILL_CANDIDATES.md",
    ]
    records: list[SkillSearchRecord] = []
    for path in paths:
        for row in _markdown_table_rows(path, files_read):
            name = row.get("Candidate") or row.get("Category") or row.get("Name") or row.get("Skill ID") or ""
            if not name:
                continue
            skill_id = row.get("Skill ID") or row.get("Feature ID") or _slug(name)
            priority = row.get("Native Priority") or row.get("Priority") or row.get("Status") or "candidate"
            implemented = priority.casefold() in {"implemented", "complete", "available"}
            records.append(
                SkillSearchRecord(
                    skill_id=skill_id,
                    name=name,
                    source="native_candidate_docs",
                    source_path=str(path),
                    searchable_text=" ".join(row.values()),
                    maturity_level="1 Specified" if not implemented else "3 Implemented",
                    readiness_score=44 if not implemented else 60,
                    implemented=implemented,
                    safe_to_use_now=False if not implemented else True,
                    required_approvals=row.get("Required Approval Gates", "") or row.get("Approval Gates", "") or "none recorded",
                    required_capabilities=_split_inline_values(row.get("Required ToolBroker Capabilities", "") or row.get("Required capabilities", "")),
                    next_work_needed=row.get("Recommended Implementation Path", "") or row.get("First Implementation Boundary", "") or row.get("Notes", "") or "Create a native skill implementation prompt and tests.",
                    docs_path=str(path.relative_to(root)) if path.exists() else str(path),
                )
            )
    return records


def _markdown_table_rows(path: Path, files_read: set[str]) -> list[dict[str, str]]:
    if not path.exists():
        return []
    files_read.add(str(path.resolve()))
    lines = path.read_text(encoding="utf-8").splitlines()
    rows: list[dict[str, str]] = []
    headers: list[str] | None = None
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            headers = None
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells:
            continue
        if all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells):
            continue
        if headers is None:
            headers = cells
            continue
        if len(cells) != len(headers):
            continue
        rows.append(dict(zip(headers, cells)))
    return rows


def _tokens(text: str) -> set[str]:
    raw = {match.group(0).casefold() for match in re.finditer(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", text)}
    tokens = {token for token in raw if token not in STOPWORDS and len(token) > 1}
    tokens.update(token[:-1] for token in list(tokens) if token.endswith("s") and len(token) > 3)
    return tokens


def _expand_tokens(tokens: set[str]) -> set[str]:
    expanded = set(tokens)
    for token in list(tokens):
        expanded.update(SYNONYMS.get(token, set()))
    return expanded


def _match_score(query_tokens: set[str], query: str, record: SkillSearchRecord) -> int:
    record_tokens = _expand_tokens(_tokens(record.searchable_text))
    overlap = query_tokens & record_tokens
    score = len(overlap) * 10
    query_phrase = query.casefold()
    searchable = record.searchable_text.casefold()
    if query_phrase and query_phrase in searchable:
        score += 35
    for token in query_tokens:
        if token in record.name.casefold():
            score += 8
        if token in record.skill_id.casefold():
            score += 4
    if score > 0 and record.implemented:
        score += 3
    return score


def _record_to_match(record: SkillSearchRecord, score: int) -> dict[str, Any]:
    return {
        "skill_id": record.skill_id,
        "name": record.name,
        "source": record.source,
        "maturity_level": record.maturity_level,
        "readiness_score": record.readiness_score,
        "implemented": record.implemented,
        "safe_to_use_now": record.safe_to_use_now,
        "required_approvals": record.required_approvals,
        "required_capabilities": record.required_capabilities,
        "next_work_needed": record.next_work_needed,
        "docs_path": record.docs_path,
        "match_score": score,
    }


def _dedupe_key(record: SkillSearchRecord) -> str:
    if record.skill_id:
        return record.skill_id.casefold()
    return _slug(record.name)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-") or "unknown"


def _score_from_maturity(maturity: str) -> int | None:
    level = _maturity_number(maturity)
    if level < 0:
        return None
    return {0: 10, 1: 35, 2: 48, 3: 60, 4: 72, 5: 82, 6: 88, 7: 92, 8: 95}.get(level)


def _maturity_number(maturity: str) -> int:
    match = re.search(r"\b([0-8])\b", maturity or "")
    return int(match.group(1)) if match else -1


def _parse_int(value: str) -> int | None:
    match = re.search(r"\d+", value or "")
    return int(match.group(0)) if match else None


def _approval_text(value: bool | str) -> str:
    if value is True:
        return "approval required"
    if value is False:
        return "none"
    return str(value)


def _registry_maturity_hint(status: str) -> str:
    return "4 Tested" if status.casefold() == "complete" else "1 Specified"


def _infer_approvals(text: str) -> str:
    lowered = text.casefold()
    if "critical" in lowered or "per-action" in lowered:
        return "CRITICAL per-action approval where write/send actions are involved"
    if "approval" in lowered or "high" in lowered:
        return "approval required for HIGH-risk or personal-data steps"
    return "none recorded"


def _split_inline_values(value: str) -> list[str]:
    return sorted(set(_extract_capability_names(value) or [item.strip(" `") for item in re.split(r",|;", value) if item.strip(" `")]))


def _extract_capability_names(text: str) -> list[str]:
    return sorted(set(re.findall(r"\b[a-z_]+(?:\.[a-zA-Z_][\w-]*)+\b", text or "")))
