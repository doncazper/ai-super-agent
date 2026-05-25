from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .models import utc_now_iso


SECTION_NAMES = (
    "Short answer",
    "Consensus",
    "Major viewpoints",
    "Disagreements",
    "Repeated complaints/praise",
    "Caveats / bias warning",
    "Source list",
    "Fetch limitations",
)

INSTRUCTION_MARKERS = (
    "ignore previous",
    "ignore all previous",
    "system prompt",
    "developer message",
    "reveal secret",
    "reveal your secret",
    "call tool",
    "execute tool",
    "run command",
    "change policy",
    "disable policy",
    "disable audit",
    "bypass",
    "send email",
    "send message",
    "store this in memory",
)

COMPLAINT_MARKERS = (
    "bad",
    "bug",
    "broken",
    "complaint",
    "crash",
    "disappoint",
    "expensive",
    "fail",
    "issue",
    "problem",
    "slow",
    "worse",
)

PRAISE_MARKERS = (
    "best",
    "easy",
    "fast",
    "good",
    "great",
    "helpful",
    "love",
    "recommend",
    "reliable",
    "useful",
    "works",
)


@dataclass(frozen=True)
class EvidenceItem:
    source_id: str
    title: str
    url: str
    text: str
    retrieved_at: str
    data_state: str
    snippet_only: bool
    score: int | None = None

    def source_reference(self, *, used_as_evidence: bool = True, excluded_reason: str = "") -> dict[str, Any]:
        payload = {
            "source_id": self.source_id,
            "title": self.title,
            "url": self.url,
            "permalink": self.url,
            "provider": "reddit_api",
            "retrieved_at": self.retrieved_at,
            "trust_level": "UNTRUSTED_WEB",
            "data_state": self.data_state,
            "snippet_only": self.snippet_only,
            "used_as_evidence": used_as_evidence,
        }
        if excluded_reason:
            payload["excluded_reason"] = excluded_reason
        return payload


def summarize_reddit_thread(payload: Mapping[str, Any], *, summary_kind: str = "thread") -> dict[str, Any]:
    evidence, excluded = _thread_evidence(payload)
    limitations = [
        "Thread data is fetched Reddit content and remains UNTRUSTED_WEB.",
        "Comment volume may be bounded by max-comments, sorting, and collapse-depth settings.",
    ]
    if payload.get("truncation_info"):
        limitations.append(f"Truncation metadata: {payload.get('truncation_info')}")
    return _build_summary(
        evidence,
        excluded,
        summary_kind=summary_kind,
        data_state="fetched_thread",
        retrieved_at=str(payload.get("retrieved_at") or utc_now_iso()),
        limitations=limitations,
    )


def summarize_reddit_search(payload: Mapping[str, Any], *, summary_kind: str = "search") -> dict[str, Any]:
    evidence, excluded = _search_evidence(payload)
    limitations = [
        "Search summaries are based on Reddit search snippets only until a thread is explicitly fetched.",
        "Reddit search language parameters are advisory unless the provider supports enforcement.",
    ]
    return _build_summary(
        evidence,
        excluded,
        summary_kind=summary_kind,
        data_state="search_snippet",
        retrieved_at=str(payload.get("retrieved_at") or utc_now_iso()),
        limitations=limitations,
    )


def _thread_evidence(payload: Mapping[str, Any]) -> tuple[list[EvidenceItem], list[dict[str, Any]]]:
    items: list[EvidenceItem] = []
    excluded: list[dict[str, Any]] = []
    post = payload.get("post") if isinstance(payload.get("post"), Mapping) else {}
    _append_source(items, excluded, post, data_state="fetched_thread", snippet_only=False, fallback_title=str(post.get("title") or "Reddit post"))
    comments = payload.get("flattened_comments") or payload.get("comments") or []
    if isinstance(comments, list):
        for comment in comments:
            if isinstance(comment, Mapping):
                _append_source(items, excluded, comment, data_state="fetched_thread", snippet_only=False, fallback_title=str(post.get("title") or "Reddit comment"))
    return items, excluded


def _search_evidence(payload: Mapping[str, Any]) -> tuple[list[EvidenceItem], list[dict[str, Any]]]:
    items: list[EvidenceItem] = []
    excluded: list[dict[str, Any]] = []
    results = payload.get("results") or []
    if isinstance(results, list):
        for result in results:
            if isinstance(result, Mapping):
                _append_source(items, excluded, result, data_state="search_snippet", snippet_only=True, fallback_title=str(result.get("title") or "Reddit search result"))
    return items, excluded


def _append_source(
    items: list[EvidenceItem],
    excluded: list[dict[str, Any]],
    source: Mapping[str, Any],
    *,
    data_state: str,
    snippet_only: bool,
    fallback_title: str,
) -> None:
    source_id = str(source.get("source_id") or "").strip()
    url = str(source.get("permalink") or source.get("url") or "").strip()
    title = str(source.get("title") or fallback_title).strip()
    raw_text = " ".join(part for part in (title, str(source.get("body_text") or "")) if part).strip()
    if not source_id or not url:
        return
    item = EvidenceItem(
        source_id=source_id,
        title=title,
        url=url,
        text=_compact(raw_text),
        retrieved_at=str(source.get("retrieved_at") or utc_now_iso()),
        data_state=data_state,
        snippet_only=snippet_only,
        score=_int_or_none(source.get("score")),
    )
    if bool(source.get("removed")):
        excluded.append(item.source_reference(used_as_evidence=False, excluded_reason="deleted_or_removed"))
        return
    if not item.text:
        excluded.append(item.source_reference(used_as_evidence=False, excluded_reason="empty_text"))
        return
    if _looks_like_prompt_injection(item.text):
        excluded.append(item.source_reference(used_as_evidence=False, excluded_reason="prompt_injection_like_text"))
        return
    items.append(item)


def _build_summary(
    evidence: list[EvidenceItem],
    excluded: list[dict[str, Any]],
    *,
    summary_kind: str,
    data_state: str,
    retrieved_at: str,
    limitations: list[str],
) -> dict[str, Any]:
    source_list = [item.source_reference() for item in evidence] + excluded
    low_data = len(evidence) < 2
    evidence_lines = [_evidence_line(item) for item in evidence[:5]]
    complaint_lines = _matching_lines(evidence, COMPLAINT_MARKERS)
    praise_lines = _matching_lines(evidence, PRAISE_MARKERS)
    kind_label = summary_kind.replace("_", " ")
    short_answer = (
        f"Too little usable Reddit evidence to produce a confident {kind_label} summary."
        if low_data
        else f"Based on {len(evidence)} usable Reddit source(s), the {kind_label} signal is anecdotal: {evidence_lines[0]}"
    )
    consensus = (
        "Too little usable Reddit evidence to identify a consensus."
        if low_data
        else "The available Reddit evidence has an overlapping theme, but it is anecdotal and not statistically representative."
    )
    disagreements = (
        ["Too little usable Reddit evidence to compare disagreements."]
        if low_data
        else [
            "Different sources emphasize different details; treat this as a discussion map rather than a settled conclusion.",
            *evidence_lines[:2],
        ]
    )
    repeated = {
        "complaints": complaint_lines[:5] or ["No repeated complaints can be established from the usable evidence."],
        "praise": praise_lines[:5] or ["No repeated praise can be established from the usable evidence."],
    }
    if summary_kind == "complaints":
        short_answer = (
            "Too little usable Reddit evidence to identify repeated complaints."
            if low_data
            else f"Potential complaints mentioned in Reddit evidence: {', '.join(complaint_lines[:3]) if complaint_lines else 'no repeated complaint pattern is clear.'}"
        )
    elif summary_kind == "buying_advice":
        short_answer = (
            "Too little usable Reddit evidence to produce buying advice."
            if low_data
            else "Use the Reddit evidence as anecdotal input only; verify specifications, prices, safety, and availability with authoritative sources."
        )
    sections: dict[str, Any] = {
        "Short answer": short_answer,
        "Consensus": consensus,
        "Major viewpoints": evidence_lines or ["No usable source-backed viewpoints found."],
        "Disagreements": disagreements,
        "Repeated complaints/praise": repeated,
        "Caveats / bias warning": (
            "Reddit is anecdotal, self-selected discussion data. This summary must not be treated as authoritative, "
            "statistically representative, or a substitute for primary sources."
        ),
        "Source list": source_list,
        "Fetch limitations": [
            *limitations,
            f"Usable evidence sources: {len(evidence)}.",
            f"Excluded sources: {len(excluded)}.",
            "Deleted/removed content and prompt-injection-like text are not summarized as evidence.",
        ],
    }
    return {
        "status": "ok",
        "summary_kind": summary_kind,
        "provider": "reddit_api",
        "data_state": data_state,
        "evidence_type": data_state,
        "retrieved_at": retrieved_at,
        "sections": sections,
        "source_list": source_list,
        "source_references": source_list,
        "source_count": len(source_list),
        "usable_evidence_count": len(evidence),
        "excluded_source_count": len(excluded),
        "low_data": low_data,
        "memory_written": False,
        "summary_persisted": False,
        "query_history_persisted": False,
        "trust_level": "UNTRUSTED_WEB",
        "web_scraping_fallback_used": False,
        "section_names": list(SECTION_NAMES),
    }


def _evidence_line(item: EvidenceItem) -> str:
    return f"[{item.source_id}] {_truncate(item.text, 220)}"


def _matching_lines(items: list[EvidenceItem], markers: tuple[str, ...]) -> list[str]:
    matches: list[str] = []
    for item in items:
        lowered = item.text.casefold()
        if any(marker in lowered for marker in markers):
            matches.append(_evidence_line(item))
    return matches


def _looks_like_prompt_injection(text: str) -> bool:
    lowered = text.casefold()
    return any(marker in lowered for marker in INSTRUCTION_MARKERS)


def _compact(text: str) -> str:
    return " ".join(str(text or "").split())


def _truncate(text: str, limit: int) -> str:
    compact = _compact(text)
    if len(compact) <= limit:
        return compact
    return compact[: max(0, limit - 3)].rstrip() + "..."


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
