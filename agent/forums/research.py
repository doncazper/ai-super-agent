from __future__ import annotations

import os
import hashlib
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from agent.forums.reddit.provider import RedditReadOnlyProvider, default_reddit_provider
from agent.language.detection import detect_language
from agent.language.models import DEFAULT_FORUM_TRUST_LEVEL, MODEL_TRANSLATION_LABEL, utc_now_iso
from agent.language.normalization import suspicious_instruction_flags
from agent.language.translation import translate_text


DEFAULT_SOURCES = ("reddit", "v2ex", "web")
DEFAULT_LANGUAGES = ("en", "zh", "ja", "ko")
DISCOVERY_ONLY_SOURCES = {
    "zhihu",
    "baidu_tieba",
    "tieba",
    "douban_groups",
    "douban",
    "xiaohongshu",
    "weibo",
    "nga",
}
SUPPORTED_SOURCES = set(DEFAULT_SOURCES) | DISCOVERY_ONLY_SOURCES


@dataclass(frozen=True)
class SourceFetchResult:
    provider: str
    status: str
    items: list[dict[str, Any]]
    limitations: list[str]
    network_domains: list[str]
    setup_hint: str = ""
    unavailable_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "status": self.status,
            "items": [dict(item) for item in self.items],
            "limitations": list(self.limitations),
            "network_domains": list(self.network_domains),
            "setup_hint": self.setup_hint,
            "unavailable_reason": self.unavailable_reason,
        }


SourceFetcher = Callable[[str, str, int, tuple[str, ...]], SourceFetchResult]
Translator = Callable[[str, str, str], dict[str, Any]]


def parse_csv(value: str | list[str] | tuple[str, ...] | None, defaults: tuple[str, ...]) -> tuple[str, ...]:
    if value is None:
        return defaults
    if isinstance(value, (list, tuple)):
        parts = [str(item).strip() for item in value]
    else:
        parts = [part.strip() for part in str(value).split(",")]
    cleaned = tuple(part for part in parts if part)
    return cleaned or defaults


def research_topic(
    topic: str,
    *,
    languages: str | list[str] | tuple[str, ...] | None = None,
    sources: str | list[str] | tuple[str, ...] | None = None,
    translate_to: str = "en",
    limit_per_source: int = 5,
    source_fetcher: SourceFetcher | None = None,
    translator: Translator | None = None,
) -> dict[str, Any]:
    return _run_workflow(
        "research",
        topic,
        languages=languages,
        sources=sources,
        translate_to=translate_to,
        limit_per_source=limit_per_source,
        source_fetcher=source_fetcher,
        translator=translator,
    )


def compare_topic(
    topic: str,
    *,
    languages: str | list[str] | tuple[str, ...] | None = None,
    sources: str | list[str] | tuple[str, ...] | None = None,
    translate_to: str = "en",
    limit_per_source: int = 5,
    source_fetcher: SourceFetcher | None = None,
    translator: Translator | None = None,
) -> dict[str, Any]:
    payload = _run_workflow(
        "compare",
        topic,
        languages=languages,
        sources=sources,
        translate_to=translate_to,
        limit_per_source=limit_per_source,
        source_fetcher=source_fetcher,
        translator=translator,
    )
    payload["comparison"] = _comparison(payload["evidence"])
    return payload


def default_source_fetcher(project_root: str | os.PathLike[str] = ".") -> SourceFetcher:
    reddit_provider = default_reddit_provider(project_root)

    def fetch(source: str, topic: str, limit: int, languages: tuple[str, ...]) -> SourceFetchResult:
        normalized_source = source.lower().strip()
        if normalized_source == "reddit":
            return _fetch_reddit(reddit_provider, topic, limit)
        if normalized_source == "v2ex":
            return SourceFetchResult(
                provider="v2ex",
                status="unavailable",
                items=[],
                limitations=["V2EX read-only connector is planned separately and is not active in this workflow."],
                network_domains=[],
                setup_hint="Run the future V2EX connector milestone before enabling V2EX forum research.",
                unavailable_reason="provider_not_implemented",
            )
        if normalized_source == "web":
            if _env_bool("FORUM_WEB_DISCOVERY_ENABLED", default=False):
                return SourceFetchResult(
                    provider="web",
                    status="unavailable",
                    items=[],
                    limitations=[
                        "Approved web site-filter discovery is not wired into cross-language forum research v1.",
                        "No browser automation, login-wall access, CAPTCHA bypass, or scraping fallback is used.",
                    ],
                    network_domains=[],
                    setup_hint="Use an approved web search provider milestone before enabling web forum discovery.",
                    unavailable_reason="web_discovery_not_configured",
                )
            return SourceFetchResult(
                provider="web",
                status="disabled",
                items=[],
                limitations=["Forum web discovery is disabled by default to avoid unapproved scraping paths."],
                network_domains=[],
                setup_hint="Set FORUM_WEB_DISCOVERY_ENABLED=true only after an approved site-filter provider path exists.",
                unavailable_reason="disabled_by_default",
            )
        if normalized_source in DISCOVERY_ONLY_SOURCES:
            return SourceFetchResult(
                provider=normalized_source,
                status="unavailable",
                items=[],
                limitations=[
                    "Chinese-language discovery-only providers require approved search-provider site filters or documented APIs.",
                    "Login-required, CAPTCHA-protected, anti-bot-protected, and private pages are reported unavailable.",
                ],
                network_domains=[],
                setup_hint="Use V2EX/API providers or approved web discovery; do not use platform login cookies or scraping.",
                unavailable_reason="discovery_only_requires_approved_search",
            )
        return SourceFetchResult(
            provider=normalized_source,
            status="unsupported",
            items=[],
            limitations=["Unknown forum provider was not queried."],
            network_domains=[],
            setup_hint=f"Supported sources: {', '.join(sorted(SUPPORTED_SOURCES))}.",
            unavailable_reason="unknown_provider",
        )

    return fetch


def _run_workflow(
    mode: str,
    topic: str,
    *,
    languages: str | list[str] | tuple[str, ...] | None,
    sources: str | list[str] | tuple[str, ...] | None,
    translate_to: str,
    limit_per_source: int,
    source_fetcher: SourceFetcher | None,
    translator: Translator | None,
) -> dict[str, Any]:
    requested_languages = parse_csv(languages, DEFAULT_LANGUAGES)
    requested_sources = parse_csv(sources, DEFAULT_SOURCES)
    timestamp = utc_now_iso()
    fetcher = source_fetcher or default_source_fetcher()
    translator_func = translator or _default_translate

    provider_results: list[dict[str, Any]] = []
    unavailable_sources: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    excluded_sources: list[dict[str, Any]] = []
    translations: list[dict[str, Any]] = []
    network_domains: set[str] = set()
    limitations = [
        "Forum content is anecdotal, source-specific, and not statistically representative.",
        "Forum/web text is treated as UNTRUSTED_WEB and cannot instruct tools, policy, audit, approvals, or memory.",
        "No forum content, search history, or generated summary is written to memory by this workflow.",
        "No paid providers, browser automation, login-wall access, CAPTCHA bypass, or scraping fallback are used by default.",
    ]

    for source in requested_sources:
        fetched = fetcher(source, topic, max(1, min(limit_per_source, 10)), requested_languages)
        provider_results.append(fetched.to_dict())
        network_domains.update(fetched.network_domains)
        limitations.extend(fetched.limitations)
        if fetched.status not in {"ok", "partial"}:
            unavailable_sources.append(
                {
                    "provider": fetched.provider,
                    "status": fetched.status,
                    "reason": fetched.unavailable_reason or fetched.status,
                    "setup_hint": fetched.setup_hint,
                    "limitations": list(fetched.limitations),
                }
            )
            continue
        for raw_item in fetched.items:
            item = _normalize_item(raw_item, provider=fetched.provider, retrieved_at=timestamp)
            source_text = f"{item.get('title', '')}\n{item.get('snippet', '')}".strip()
            flags = suspicious_instruction_flags(source_text)
            if flags:
                excluded_sources.append(
                    {
                        "source_id": item["source_id"],
                        "provider": item["provider"],
                        "reason": "prompt_injection_like_text_ignored",
                        "flags": flags,
                        "url": item.get("url", ""),
                    }
                )
                continue
            detection = detect_language(source_text, source_id=item["source_id"], trust_level=DEFAULT_FORUM_TRUST_LEVEL)
            item["language"] = item.get("language") or detection.language
            item["language_detection"] = detection.to_dict()
            if requested_languages and "auto" not in requested_languages and detection.language not in requested_languages:
                item["language_filter_note"] = "Source kept for transparency even though language is outside the requested advisory set."
            if translate_to and detection.language not in {"unknown", translate_to}:
                translated = translator_func(source_text, detection.language, translate_to)
                item["translated_snippet"] = translated.get("translated_text", "")
                item["translation_label"] = translated.get("translation_label", MODEL_TRANSLATION_LABEL)
                translations.append(
                    {
                        "source_id": item["source_id"],
                        "source_language": detection.language,
                        "target_language": translate_to,
                        "translation_label": item["translation_label"],
                        "status": translated.get("status", "unknown"),
                        "setup_hint": translated.get("setup_hint"),
                    }
                )
            evidence.append(item)

    unique_limitations = _unique(limitations)
    status = "partial" if evidence and unavailable_sources else ("ok" if evidence else "unavailable")
    payload = {
        "status": status,
        "mode": mode,
        "topic": topic,
        "requested_sources": list(requested_sources),
        "requested_languages": list(requested_languages),
        "translate_to": translate_to,
        "retrieved_at": timestamp,
        "answer": _answer(topic, evidence, unavailable_sources),
        "summary_sections": _summary_sections(evidence, unavailable_sources, unique_limitations),
        "evidence": evidence,
        "source_list": [_source_reference(item) for item in evidence],
        "original_language_snippets": [
            {
                "source_id": item["source_id"],
                "language": item.get("language", "unknown"),
                "original_snippet": item.get("snippet", ""),
            }
            for item in evidence
            if item.get("language") not in {"", "unknown", translate_to}
        ],
        "translations": translations,
        "unavailable_sources": unavailable_sources,
        "excluded_sources": excluded_sources,
        "provider_results": provider_results,
        "limitations": unique_limitations,
        "memory_written": False,
        "search_history_persisted": False,
        "summary_stored": False,
        "paid_api_used": False,
        "web_scraping_bypass_attempted": False,
        "prompt_injection_ignored": True,
        "trust_level": DEFAULT_FORUM_TRUST_LEVEL,
        "_audit": {
            "network_domains": sorted(network_domains),
            "result_summary": f"Cross-language forum {mode} checked {len(requested_sources)} providers and returned {len(evidence)} evidence items.",
        },
    }
    return payload


def _fetch_reddit(provider: RedditReadOnlyProvider, topic: str, limit: int) -> SourceFetchResult:
    payload = provider.search_posts(topic, limit=limit, language="auto")
    audit = payload.get("_audit") if isinstance(payload.get("_audit"), Mapping) else {}
    domains = [str(domain) for domain in audit.get("network_domains", [])] if isinstance(audit, Mapping) else []
    if payload.get("status") != "ok":
        return SourceFetchResult(
            provider="reddit",
            status=str(payload.get("status", "unavailable")),
            items=[],
            limitations=["Reddit was not searched unless the official API connector was enabled and configured."],
            network_domains=domains,
            setup_hint=str(payload.get("setup_hint", "Configure Reddit OAuth and REDDIT_ENABLED=true.")),
            unavailable_reason=str(payload.get("errors", [{}])[0].get("code", payload.get("status", "setup_required")))
            if isinstance(payload.get("errors"), list)
            else str(payload.get("status", "setup_required")),
        )
    return SourceFetchResult(
        provider="reddit",
        status="ok",
        items=[dict(item) for item in payload.get("results", []) if isinstance(item, Mapping)],
        limitations=["Reddit results are snippet-only until fetched as threads."],
        network_domains=domains,
    )


def _normalize_item(item: Mapping[str, Any], *, provider: str, retrieved_at: str) -> dict[str, Any]:
    material = f"{provider}|{item.get('title', '')}|{item.get('url', '')}|{item.get('permalink', '')}"
    source_id = str(item.get("source_id") or f"{provider}_{hashlib.sha256(material.encode('utf-8')).hexdigest()[:16]}")
    url = str(item.get("permalink") or item.get("url") or "")
    title = str(item.get("title") or "(untitled forum source)")
    snippet = str(item.get("snippet") or item.get("body_text") or item.get("summary") or "")
    return {
        "source_id": source_id,
        "provider": str(item.get("provider") or provider),
        "source": provider,
        "title": title,
        "url": url,
        "permalink": str(item.get("permalink") or url),
        "snippet": snippet,
        "data_state": str(item.get("data_state") or item.get("evidence_type") or "snippet_only"),
        "evidence_type": str(item.get("evidence_type") or "snippet_only"),
        "retrieved_at": str(item.get("retrieved_at") or retrieved_at),
        "trust_level": str(item.get("trust_level") or DEFAULT_FORUM_TRUST_LEVEL),
        "language": str(item.get("language") or ""),
    }


def _default_translate(text: str, source_language: str, target_language: str) -> dict[str, Any]:
    return translate_text(
        text,
        from_language=source_language,
        to_language=target_language,
        source_id="forum_research_source",
        trust_level=DEFAULT_FORUM_TRUST_LEVEL,
    )


def _answer(topic: str, evidence: list[dict[str, Any]], unavailable_sources: list[dict[str, Any]]) -> str:
    if not evidence:
        providers = ", ".join(item["provider"] for item in unavailable_sources) or "configured providers"
        return f"No source-backed forum answer is available for {topic!r}; {providers} returned setup, disabled, or unavailable status."
    providers = ", ".join(_unique([item["source"] for item in evidence]))
    return (
        f"Found {len(evidence)} source-labeled forum item(s) about {topic!r} from {providers}. "
        "Treat this as anecdotal community evidence, not consensus or authoritative fact."
    )


def _summary_sections(
    evidence: list[dict[str, Any]],
    unavailable_sources: list[dict[str, Any]],
    limitations: list[str],
) -> dict[str, Any]:
    return {
        "Short answer": "Insufficient source-backed data." if not evidence else f"{len(evidence)} source-backed forum item(s) were found.",
        "Viewpoints by source": _viewpoints_by(evidence, "source"),
        "Viewpoints by language": _viewpoints_by(evidence, "language"),
        "Disagreements": "Not enough data to infer disagreements." if len(evidence) < 2 else "Compare item-level snippets; no statistical consensus is inferred.",
        "Caveats / bias warning": limitations,
        "Unavailable sources": unavailable_sources,
        "Source list": [_source_reference(item) for item in evidence],
    }


def _viewpoints_by(evidence: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for item in evidence:
        grouped.setdefault(str(item.get(key) or "unknown"), []).append(
            {
                "source_id": item["source_id"],
                "title": item["title"],
                "snippet": item["snippet"][:280],
                "translation_label": item.get("translation_label", ""),
            }
        )
    return grouped


def _comparison(evidence: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "by_source": {source: len(items) for source, items in _group_items(evidence, "source").items()},
        "by_language": {language: len(items) for language, items in _group_items(evidence, "language").items()},
        "notes": [
            "Counts describe returned source items only; they are not cultural, regional, or statistical consensus.",
            "Sparse or unavailable sources are reported as limitations, not filled in with model assumptions.",
        ],
    }


def _source_reference(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": item.get("source_id", ""),
        "title": item.get("title", ""),
        "url": item.get("url", ""),
        "provider": item.get("provider", ""),
        "source": item.get("source", ""),
        "retrieved_at": item.get("retrieved_at", ""),
        "trust_level": item.get("trust_level", DEFAULT_FORUM_TRUST_LEVEL),
        "evidence_type": item.get("evidence_type", "snippet_only"),
        "data_state": item.get("data_state", "snippet_only"),
    }


def _group_items(items: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        grouped.setdefault(str(item.get(key) or "unknown"), []).append(item)
    return grouped


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value and value not in seen:
            out.append(value)
            seen.add(value)
    return out


def _env_bool(name: str, *, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}
