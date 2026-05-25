from __future__ import annotations

import hashlib
import json
import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Callable
from urllib.parse import urljoin, urlparse, urlunparse

import httpx

from agent.connectors.cost_policy import (
    ProviderCandidate,
    ProviderCostConfig,
    select_provider,
    web_provider_candidates,
)
from agent.config.runtime import env_bool, parse_int
from agent.tools.errors import ToolError
from agent.tools.web.extraction import extract_readable_text
from agent.tools.web.fetch import (
    DEFAULT_MAX_CONTENT_CHARS,
    TEXT_CONTENT_TYPES,
    DomainRules,
    WebResponse,
    default_fetcher,
    normalize_url,
)
from agent.tools.web.untrusted_content import UntrustedContentManager
from agent.web_acquisition import AcquisitionRequest, WebAcquisitionRouter
from agent.web_acquisition.errors import WebAcquisitionError
from agent.web_acquisition.feeds import DEFAULT_MAX_FEED_ITEMS, parse_feed_xml
from agent.web_acquisition.robots import RobotsPolicy, RobotsRule, parse_robots_txt
from agent.web_acquisition.sitemaps import DEFAULT_MAX_SITEMAP_URLS, parse_sitemap_xml


DEFAULT_ACQUISITION_TTL_SECONDS = 3600
DEFAULT_MAX_ACQUIRE_CHARS = 20000
BOT_BLOCK_PATTERNS = (
    "captcha",
    "verify you are human",
    "are you a human",
    "unusual traffic",
    "automated queries",
    "access denied",
    "temporarily blocked",
    "cloudflare ray id",
    "enable javascript and cookies",
)


class WebAcquisitionCache:
    def __init__(self, cache_dir: str | Path, *, ttl_seconds: int | None = None, enabled: bool | None = None) -> None:
        self.cache_dir = Path(cache_dir)
        configured_ttl = parse_int(
            "WEB_ACQUISITION_CACHE_TTL_SECONDS",
            os.getenv("WEB_ACQUISITION_CACHE_TTL_SECONDS", str(DEFAULT_ACQUISITION_TTL_SECONDS)),
            minimum=1,
            maximum=86_400,
        )
        self.ttl_seconds = ttl_seconds if ttl_seconds is not None else configured_ttl
        self.enabled = env_bool("WEB_ACQUISITION_CACHE_ENABLED", default=True) if enabled is None else enabled

    def read(self, kind: str, identifier: str) -> dict[str, object] | None:
        if not self.enabled:
            return None
        path = self._path(kind, identifier)
        if not path.exists():
            return None
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        expires_at = _parse_timestamp(str(record.get("expires_at") or ""))
        if expires_at is None or expires_at <= datetime.now(UTC):
            return None
        payload = record.get("payload")
        if not isinstance(payload, dict):
            return None
        cached = dict(payload)
        cached["cache"] = {
            "status": "hit",
            "cache_key": path.name,
            "expires_at": record.get("expires_at"),
            "ttl_seconds": self.ttl_seconds,
        }
        return cached

    def write(self, kind: str, identifier: str, payload: dict[str, object]) -> None:
        if not self.enabled:
            return
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        clean_payload = dict(payload)
        clean_payload.pop("_audit", None)
        clean_payload["cache"] = {
            "status": "miss_stored",
            "ttl_seconds": self.ttl_seconds,
        }
        record = {
            "kind": kind,
            "identifier": identifier,
            "created_at": datetime.now(UTC).isoformat(),
            "expires_at": (datetime.now(UTC) + timedelta(seconds=self.ttl_seconds)).isoformat(),
            "payload": clean_payload,
        }
        self._path(kind, identifier).write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")

    def _path(self, kind: str, identifier: str) -> Path:
        digest = hashlib.sha256(f"{kind}:{identifier}".encode("utf-8")).hexdigest()
        return self.cache_dir / f"{kind}_{digest}.json"


def make_web_acquisition_tools(
    *,
    project_root: str | Path = ".",
    fetcher: Callable[[str, int], WebResponse] | None = None,
    domain_rules: DomainRules | None = None,
    cache: WebAcquisitionCache | None = None,
    untrusted_manager: UntrustedContentManager | None = None,
) -> dict[str, Callable[..., dict[str, object]]]:
    root = Path(project_root).resolve()
    rules = domain_rules or DomainRules.from_env()
    active_fetcher = fetcher or (lambda url, timeout_seconds: default_fetcher(url, timeout_seconds, rules))
    active_cache = cache or WebAcquisitionCache(root / "data" / "web_acquisition_cache")
    manager = untrusted_manager or UntrustedContentManager(max_chars=DEFAULT_MAX_ACQUIRE_CHARS)
    core_router = WebAcquisitionRouter(domain_rules=rules)

    def robots(domain: str, path: str = "/", timeout_seconds: int = 10, no_cache: bool = False) -> dict[str, object]:
        base_url, domain_name = _base_url_for_domain(domain, rules)
        robots_url = urljoin(base_url, "/robots.txt")
        cached = None if no_cache else active_cache.read("robots", robots_url)
        if cached is not None:
            cached["_audit"] = {"network_domains": [domain_name], "result_summary": "Robots policy loaded from cache."}
            return cached
        policy, network_domains = _fetch_robots_policy(
            robots_url,
            active_fetcher,
            rules,
            timeout_seconds=timeout_seconds,
        )
        payload = {
            "status": policy.status,
            "domain": domain_name,
            "provider": "direct_url",
            "source_type": "direct_fetch",
            "source": robots_url,
            "retrieved_at": datetime.now(UTC).isoformat(),
            "trust_level": "UNTRUSTED_WEB",
            "document_trust_level": "UNTRUSTED_DOCUMENT",
            "robots": policy.to_dict(checked_path=path),
            "limitations": _limitations(),
            "cache": {"status": "miss", "ttl_seconds": active_cache.ttl_seconds},
            "_audit": {"network_domains": sorted(network_domains), "result_summary": "Robots policy checked."},
        }
        if policy.status == "ok":
            active_cache.write("robots", robots_url, payload)
        return payload

    def sitemap(domain: str, timeout_seconds: int = 10, max_urls: int = DEFAULT_MAX_SITEMAP_URLS, no_cache: bool = False) -> dict[str, object]:
        if max_urls <= 0 or max_urls > 1000:
            raise ToolError("max_urls must be between 1 and 1000")
        base_url, domain_name = _base_url_for_domain(domain, rules)
        policy, robots_domains = _fetch_robots_policy(
            urljoin(base_url, "/robots.txt"),
            active_fetcher,
            rules,
            timeout_seconds=timeout_seconds,
        )
        sitemap_urls = policy.sitemaps or [urljoin(base_url, "/sitemap.xml")]
        source_url = sitemap_urls[0]
        cached = None if no_cache else active_cache.read("sitemap", source_url)
        if cached is not None:
            cached["_audit"] = {"network_domains": [domain_name], "result_summary": "Sitemap loaded from cache."}
            return cached
        response, fetch_error = _safe_fetch(source_url, active_fetcher, rules, timeout_seconds)
        network_domains = set(robots_domains)
        network_domains.add(domain_name)
        if response is None:
            return _unavailable_payload(
                "sitemap",
                source_url,
                "sitemap unavailable",
                fetch_error or "sitemap fetch failed",
                sorted(network_domains),
            )
        block = _blocked_page_reason(response)
        if block:
            return _blocked_payload("sitemap", source_url, block, sorted(network_domains))
        _ensure_supported_acquisition_content_type(response, source_kind="sitemap")
        urls, child_sitemaps, truncated = _parse_sitemap(response.text, max_urls=max_urls)
        payload = {
            "status": "ok",
            "domain": domain_name,
            "provider": "sitemap",
            "source_type": "sitemap",
            "source": source_url,
            "retrieved_at": datetime.now(UTC).isoformat(),
            "trust_level": "UNTRUSTED_WEB",
            "document_trust_level": "UNTRUSTED_DOCUMENT",
            "urls": urls,
            "child_sitemaps": child_sitemaps,
            "url_count": len(urls),
            "truncated": truncated,
            "provider_decision": _decision_for("sitemap").to_dict(),
            "limitations": _limitations(),
            "cache": {"status": "miss", "ttl_seconds": active_cache.ttl_seconds},
            "_audit": {"network_domains": sorted(network_domains), "result_summary": "Sitemap parsed."},
        }
        active_cache.write("sitemap", source_url, payload)
        return payload

    def feed(url: str, timeout_seconds: int = 10, max_items: int = DEFAULT_MAX_FEED_ITEMS, no_cache: bool = False) -> dict[str, object]:
        if max_items <= 0 or max_items > 100:
            raise ToolError("max_items must be between 1 and 100")
        normalized_url = normalize_url(url)
        domain = rules.validate_url(normalized_url)
        cached = None if no_cache else active_cache.read("feed", normalized_url)
        if cached is not None:
            cached["_audit"] = {"network_domains": [domain], "result_summary": "Feed loaded from cache."}
            return cached
        response, fetch_error = _safe_fetch(normalized_url, active_fetcher, rules, timeout_seconds)
        if response is None:
            return _unavailable_payload("feed", normalized_url, "feed unavailable", fetch_error or "feed fetch failed", [domain])
        block = _blocked_page_reason(response)
        if block:
            return _blocked_payload("feed", normalized_url, block, [domain])
        _ensure_supported_acquisition_content_type(response, source_kind="feed")
        items, truncated = _parse_feed(response.text, source_url=normalized_url, max_items=max_items)
        payload = {
            "status": "ok",
            "provider": "rss_atom",
            "source_type": "rss_feed",
            "source": normalized_url,
            "retrieved_at": datetime.now(UTC).isoformat(),
            "trust_level": "UNTRUSTED_WEB",
            "document_trust_level": "UNTRUSTED_DOCUMENT",
            "items": items,
            "item_count": len(items),
            "truncated": truncated,
            "provider_decision": _decision_for("rss_atom").to_dict(),
            "limitations": _limitations(),
            "cache": {"status": "miss", "ttl_seconds": active_cache.ttl_seconds},
            "_audit": {"network_domains": [domain], "result_summary": "RSS/Atom feed parsed."},
        }
        active_cache.write("feed", normalized_url, payload)
        return payload

    def acquire_url(
        url: str,
        timeout_seconds: int = 10,
        max_chars: int = DEFAULT_MAX_ACQUIRE_CHARS,
        no_cache: bool = False,
        respect_robots: bool = True,
    ) -> dict[str, object]:
        normalized_url = normalize_url(url)
        requested_domain = rules.validate_url(normalized_url)
        if max_chars <= 0 or max_chars > 100000:
            raise ToolError("max_chars must be between 1 and 100000")
        cached = None if no_cache else active_cache.read("acquire_url", normalized_url)
        if cached is not None:
            cached["_audit"] = {"network_domains": [requested_domain], "result_summary": "Public URL acquired from cache."}
            return cached
        robots_payload = None
        if respect_robots:
            parsed = urlparse(normalized_url)
            robots_policy, robots_domains = _fetch_robots_policy(
                f"{parsed.scheme}://{parsed.netloc}/robots.txt",
                active_fetcher,
                rules,
                timeout_seconds=timeout_seconds,
            )
            robots_payload = robots_policy.to_dict(checked_path=parsed.path or "/")
            if robots_policy.status == "ok" and not robots_policy.allowed(parsed.path or "/"):
                return {
                    "status": "unavailable",
                    "error": "robots_disallowed",
                    "provider": "direct_url",
                    "source_type": "blocked",
                    "url": normalized_url,
                    "trust_level": "UNTRUSTED_WEB",
                    "document_trust_level": "UNTRUSTED_DOCUMENT",
                    "robots": robots_payload,
                    "bypass_attempted": False,
                    "limitations": _limitations(),
                    "_audit": {
                        "network_domains": sorted(set(robots_domains) | {requested_domain}),
                        "result_summary": "URL blocked by robots.txt.",
                    },
                }
        response, fetch_error = _safe_fetch(normalized_url, active_fetcher, rules, timeout_seconds)
        if response is None:
            return _unavailable_payload(
                "direct_url",
                normalized_url,
                "direct URL unavailable",
                fetch_error or "URL fetch failed",
                [requested_domain],
                robots=robots_payload,
            )
        final_url = normalize_url(response.url)
        final_domain = rules.validate_url(final_url)
        block = _blocked_page_reason(response)
        if block:
            return _blocked_payload("direct_url", final_url, block, sorted({requested_domain, final_domain}), robots=robots_payload)
        content_type = response.headers.get("content-type", "").split(";")[0].lower()
        if content_type and not any(content_type.startswith(allowed) for allowed in TEXT_CONTENT_TYPES):
            raise ToolError("binary downloads are disabled by default")
        if len(response.text) > DEFAULT_MAX_CONTENT_CHARS:
            raise ToolError("web acquisition content exceeds max content length")
        extracted = extract_readable_text(response.text, content_type or "text/html")
        wrapped = UntrustedContentManager(max_chars=max_chars).wrap_webpage(extracted["text"]) if max_chars != manager.max_chars else manager.wrap_webpage(extracted["text"])
        payload = {
            "status": "ok",
            "provider": "direct_url",
            "source_type": "direct_fetch",
            "requested_url": url,
            "url": final_url,
            "normalized_url": normalized_url,
            "retrieved_at": datetime.now(UTC).isoformat(),
            "status_code": response.status_code,
            "content_type": content_type or "unknown",
            "title": extracted["title"],
            "trust_level": "UNTRUSTED_WEB",
            "document_trust_level": "UNTRUSTED_DOCUMENT",
            "content": wrapped,
            "content_chars": len(extracted["text"]),
            "truncated_to_chars": max_chars if len(extracted["text"]) > max_chars else None,
            "robots": robots_payload,
            "provider_decision": _decision_for("direct_url").to_dict(),
            "limitations": _limitations(),
            "cache": {"status": "miss", "ttl_seconds": active_cache.ttl_seconds},
            "_audit": {
                "network_domains": sorted({requested_domain, final_domain}),
                "result_summary": "Public URL acquired through free-first direct fetch.",
            },
        }
        active_cache.write("acquire_url", normalized_url, payload)
        return payload

    def acquire(query: str, max_results: int = 5, no_cache: bool = False) -> dict[str, object]:
        normalized_query = query.strip()
        if not normalized_query:
            raise ToolError("query is required")
        if max_results <= 0 or max_results > 20:
            raise ToolError("max_results must be between 1 and 20")
        if _looks_like_url(normalized_query):
            return acquire_url(normalized_query, no_cache=no_cache)
        cache_hits = [] if no_cache else _search_cache(active_cache.cache_dir, normalized_query, max_results=max_results)
        decision = _decision_for("local_cache" if cache_hits else None, cache_hit=bool(cache_hits))
        if cache_hits:
            return {
                "status": "ok",
                "query": normalized_query,
                "provider": "local_cache",
                "source_type": "cache",
                "trust_level": "UNTRUSTED_WEB",
                "document_trust_level": "UNTRUSTED_DOCUMENT",
                "results": cache_hits,
                "provider_decision": decision.to_dict(),
                "limitations": _limitations(search_history=False),
                "_audit": {"network_domains": [], "result_summary": "Web acquisition query served from local cache."},
            }
        if _looks_like_domain(normalized_query):
            return sitemap(normalized_query, max_urls=max_results, no_cache=no_cache)
        return {
            "status": "unavailable",
            "query": normalized_query,
            "provider": None,
            "source_type": "blocked",
            "trust_level": "UNTRUSTED_WEB",
            "document_trust_level": "UNTRUSTED_DOCUMENT",
            "error": "no_free_query_provider_available",
            "provider_decision": decision.to_dict(),
            "paid_providers_skipped": [
                item for item in decision.skipped_providers if "ALLOW_PAID_APIS=false" in str(item.get("reason", ""))
            ],
            "setup_hint": "Provide a direct public URL, RSS/Atom feed URL, domain sitemap, local cache hit, or explicitly configure an allowed search provider.",
            "limitations": _limitations(search_history=False),
            "_audit": {"network_domains": [], "result_summary": "Free-first query acquisition unavailable without a free configured provider."},
        }

    def source_status(url: str) -> dict[str, object]:
        result = core_router.source_status(url)
        payload = result.to_dict()
        audit = payload.get("metadata", {}).get("_audit") if isinstance(payload.get("metadata"), dict) else None
        payload["_audit"] = audit or {"network_domains": [], "result_summary": "Source status checked without network fetch."}
        payload["limitations"] = _limitations(search_history=False)
        payload["bypass_attempted"] = False
        return payload

    return {
        "web.robots": robots,
        "web.robots.check": robots,
        "web.sitemap": sitemap,
        "web.sitemap.fetch": sitemap,
        "web.feed": feed,
        "web.feed.fetch": feed,
        "web.acquire_url": acquire_url,
        "web.acquire": acquire,
        "web.source_status": source_status,
    }


def _base_url_for_domain(domain_or_url: str, rules: DomainRules) -> tuple[str, str]:
    raw = domain_or_url.strip()
    candidate = raw if urlparse(raw).scheme else f"https://{raw}"
    parsed = urlparse(candidate)
    if not parsed.netloc:
        raise ToolError("domain is required")
    base = urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), "/", "", "", ""))
    domain = rules.validate_url(base)
    return base, domain


def _fetch_robots_policy(
    robots_url: str,
    fetcher: Callable[[str, int], WebResponse],
    rules: DomainRules,
    *,
    timeout_seconds: int,
) -> tuple[RobotsPolicy, set[str]]:
    domain = rules.validate_url(robots_url)
    response, fetch_error = _safe_fetch(robots_url, fetcher, rules, timeout_seconds)
    if response is None:
        return RobotsPolicy(robots_url, [], [], status="unavailable", error=fetch_error or "robots.txt unavailable"), {domain}
    block = _blocked_page_reason(response)
    if block:
        return RobotsPolicy(robots_url, [], [], status="unavailable", error=block), {domain}
    try:
        _ensure_supported_acquisition_content_type(response, source_kind="robots")
    except ToolError as exc:
        return RobotsPolicy(robots_url, [], [], status="unavailable", error=str(exc)), {domain}
    ruleset, sitemaps = parse_robots_txt(response.text)
    final_domain = rules.validate_url(normalize_url(response.url))
    return RobotsPolicy(robots_url, sitemaps, ruleset), {domain, final_domain}


def _parse_robots(text: str) -> tuple[list[RobotsRule], list[str]]:
    return parse_robots_txt(text)


def _safe_fetch(
    url: str,
    fetcher: Callable[[str, int], WebResponse],
    rules: DomainRules,
    timeout_seconds: int,
) -> tuple[WebResponse | None, str | None]:
    try:
        normalized = normalize_url(url)
        rules.validate_url(normalized)
        return fetcher(normalized, timeout_seconds), None
    except httpx.TimeoutException:
        return None, "web acquisition timed out"
    except ToolError as exc:
        return None, str(exc)


def _blocked_page_reason(response: WebResponse) -> str | None:
    if response.status_code in {401, 403, 429, 503}:
        return f"blocked_or_captcha_page_http_{response.status_code}"
    haystack = response.text[:5000].casefold()
    for pattern in BOT_BLOCK_PATTERNS:
        if pattern in haystack:
            return "blocked_or_captcha_page"
    return None


def _ensure_supported_acquisition_content_type(response: WebResponse, *, source_kind: str) -> None:
    content_type = response.headers.get("content-type", "").split(";")[0].lower()
    if not content_type:
        return
    if any(content_type.startswith(allowed) for allowed in TEXT_CONTENT_TYPES):
        return
    raise ToolError(f"{source_kind} binary downloads are disabled by default")


def _parse_sitemap(text: str, *, max_urls: int) -> tuple[list[dict[str, str]], list[str], bool]:
    try:
        parsed = parse_sitemap_xml(text, max_urls=max_urls)
    except WebAcquisitionError as exc:
        raise ToolError(str(exc)) from exc
    return parsed.urls, parsed.child_sitemaps, parsed.truncated


def _parent_tag(root: ET.Element, target: ET.Element) -> str | None:
    for parent in root.iter():
        if target in list(parent):
            return parent.tag
    return None


def _parse_feed(text: str, *, source_url: str, max_items: int) -> tuple[list[dict[str, str]], bool]:
    try:
        parsed = parse_feed_xml(text, source_url=source_url, max_items=max_items)
    except WebAcquisitionError as exc:
        raise ToolError(str(exc)) from exc
    return parsed.items, parsed.truncated


def _feed_entry(entry: ET.Element, *, source_url: str) -> dict[str, str]:
    title = ""
    link = ""
    updated = ""
    summary = ""
    for child in list(entry):
        name = _local_name(child.tag)
        text = (child.text or "").strip()
        if name == "title" and text:
            title = text
        elif name == "link":
            link = child.attrib.get("href", "").strip() or text
        elif name in {"updated", "published", "pubDate"} and text:
            updated = text
        elif name in {"summary", "description", "content"} and text:
            summary = re.sub(r"<[^>]+>", "", text).strip()
    return {
        "title": title,
        "url": urljoin(source_url, link) if link else "",
        "updated": updated,
        "summary": summary[:500],
        "trust_level": "UNTRUSTED_WEB",
    }


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _unavailable_payload(
    provider: str,
    source: str,
    error: str,
    reason: str,
    network_domains: list[str],
    *,
    robots: dict[str, object] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "status": "unavailable",
        "provider": provider,
        "source_type": "blocked",
        "source": source,
        "error": error,
        "reason": reason,
        "trust_level": "UNTRUSTED_WEB",
        "document_trust_level": "UNTRUSTED_DOCUMENT",
        "bypass_attempted": False,
        "limitations": _limitations(),
        "_audit": {"network_domains": sorted(set(network_domains)), "result_summary": reason},
    }
    if robots is not None:
        payload["robots"] = robots
    return payload


def _blocked_payload(
    provider: str,
    source: str,
    reason: str,
    network_domains: list[str],
    *,
    robots: dict[str, object] | None = None,
) -> dict[str, object]:
    return _unavailable_payload(
        provider,
        source,
        "blocked_or_captcha_page",
        reason,
        network_domains,
        robots=robots,
    )


def _decision_for(selected_provider: str | None, *, cache_hit: bool = False):
    config = ProviderCostConfig.from_env()
    candidates = web_provider_candidates()
    replacements = {
        "cache": ProviderCandidate(
            "cache",
            "web",
            cache_hit or selected_provider in {"cache", "local_cache"},
            "Local cache has no matching acquisition result.",
            local=True,
            cached=True,
            no_key_required=True,
        ),
        "feed": ProviderCandidate(
            "feed",
            "web",
            selected_provider in {"feed", "rss_atom"},
            "Provide an RSS/Atom feed URL.",
            no_key_required=True,
        ),
        "sitemap": ProviderCandidate(
            "sitemap",
            "web",
            selected_provider == "sitemap",
            "Provide a domain with a public sitemap.",
            no_key_required=True,
        ),
        "url": ProviderCandidate(
            "url",
            "web",
            selected_provider in {"url", "direct_url"},
            "Provide a public URL to fetch directly.",
            no_key_required=True,
            user_provided=True,
        ),
    }
    candidates = [replacements.get(candidate.name, candidate) for candidate in candidates]
    selected_aliases = {"local_cache": "cache", "rss_atom": "feed", "direct_url": "url"}
    explicit = selected_aliases.get(selected_provider or "", selected_provider) if selected_provider else None
    if explicit not in replacements:
        explicit = None
    return select_provider("web", candidates, config=config, explicit_provider=explicit)


def _search_cache(cache_dir: Path, query: str, *, max_results: int) -> list[dict[str, str]]:
    if not cache_dir.exists():
        return []
    tokens = [token.casefold() for token in re.findall(r"[A-Za-z0-9]{3,}", query)[:6]]
    if not tokens:
        return []
    hits: list[dict[str, str]] = []
    for path in sorted(cache_dir.glob("acquire_url_*.json"))[:200]:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        payload = record.get("payload")
        if not isinstance(payload, dict):
            continue
        haystack = " ".join(str(payload.get(key) or "") for key in ("title", "url", "content")).casefold()
        if all(token in haystack for token in tokens):
            hits.append(
                {
                    "title": str(payload.get("title") or ""),
                    "url": str(payload.get("url") or payload.get("source") or ""),
                    "source": "local_cache",
                    "trust_level": "UNTRUSTED_WEB",
                }
            )
        if len(hits) >= max_results:
            break
    return hits


def _looks_like_url(value: str) -> bool:
    parsed = urlparse(value if urlparse(value).scheme else f"https://{value}")
    return bool(parsed.netloc and "." in parsed.netloc and (urlparse(value).scheme or "/" in value))


def _looks_like_domain(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}", value.strip()))


def _parse_timestamp(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _limitations(*, search_history: bool = True) -> list[str]:
    limitations = [
        "No CAPTCHA, anti-bot, login, browser-cookie, or session bypass is attempted.",
        "Content is treated as untrusted data and may be incomplete or unavailable.",
        "Paid or quota-limited search providers are skipped unless explicitly allowed by cost policy.",
    ]
    if not search_history:
        limitations.append("Raw query history is not stored by default.")
    return limitations


WEB_ACQUISITION_SCHEMAS = {
    "web.robots": {
        "type": "function",
        "function": {
            "name": "web.robots",
            "description": "Fetch and parse a public robots.txt file for a domain without bypassing restrictions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "path": {"type": "string"},
                    "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 60},
                    "no_cache": {"type": "boolean"},
                },
                "required": ["domain"],
                "additionalProperties": False,
            },
        },
    },
    "web.sitemap": {
        "type": "function",
        "function": {
            "name": "web.sitemap",
            "description": "Fetch a public sitemap URL discovered from robots.txt or /sitemap.xml and extract URLs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 60},
                    "max_urls": {"type": "integer", "minimum": 1, "maximum": 1000},
                    "no_cache": {"type": "boolean"},
                },
                "required": ["domain"],
                "additionalProperties": False,
            },
        },
    },
    "web.feed": {
        "type": "function",
        "function": {
            "name": "web.feed",
            "description": "Fetch a public RSS/Atom feed and extract untrusted feed items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 60},
                    "max_items": {"type": "integer", "minimum": 1, "maximum": 100},
                    "no_cache": {"type": "boolean"},
                },
                "required": ["url"],
                "additionalProperties": False,
            },
        },
    },
    "web.robots.check": {
        "type": "function",
        "function": {
            "name": "web.robots.check",
            "description": "Fetch and parse a public robots.txt file for a domain without bypassing restrictions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "path": {"type": "string"},
                    "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 60},
                    "no_cache": {"type": "boolean"},
                },
                "required": ["domain"],
                "additionalProperties": False,
            },
        },
    },
    "web.sitemap.fetch": {
        "type": "function",
        "function": {
            "name": "web.sitemap.fetch",
            "description": "Fetch a public sitemap URL discovered from robots.txt or /sitemap.xml and extract URLs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 60},
                    "max_urls": {"type": "integer", "minimum": 1, "maximum": 1000},
                    "no_cache": {"type": "boolean"},
                },
                "required": ["domain"],
                "additionalProperties": False,
            },
        },
    },
    "web.feed.fetch": {
        "type": "function",
        "function": {
            "name": "web.feed.fetch",
            "description": "Fetch a public RSS/Atom feed and extract untrusted feed items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 60},
                    "max_items": {"type": "integer", "minimum": 1, "maximum": 100},
                    "no_cache": {"type": "boolean"},
                },
                "required": ["url"],
                "additionalProperties": False,
            },
        },
    },
    "web.acquire_url": {
        "type": "function",
        "function": {
            "name": "web.acquire_url",
            "description": "Acquire a public URL through robots-aware direct fetch, cache, and untrusted-content wrapping.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 60},
                    "max_chars": {"type": "integer", "minimum": 1, "maximum": 100000},
                    "no_cache": {"type": "boolean"},
                    "respect_robots": {"type": "boolean"},
                },
                "required": ["url"],
                "additionalProperties": False,
            },
        },
    },
    "web.acquire": {
        "type": "function",
        "function": {
            "name": "web.acquire",
            "description": "Run the free-first web acquisition ladder for a URL, domain, or query without storing search history by default.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_results": {"type": "integer", "minimum": 1, "maximum": 20},
                    "no_cache": {"type": "boolean"},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    "web.source_status": {
        "type": "function",
        "function": {
            "name": "web.source_status",
            "description": "Inspect how an explicit public URL would be handled by the web acquisition layer without fetching content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                },
                "required": ["url"],
                "additionalProperties": False,
            },
        },
    },
}
