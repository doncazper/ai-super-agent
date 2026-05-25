from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Callable
from urllib.parse import urljoin

import httpx

from agent.tools.errors import ToolError
from agent.tools.web.untrusted_content import UntrustedContentManager
from agent.web_acquisition.extraction import extract_metadata, extract_readable_text
from agent.web_acquisition.url_normalization import DomainRules, normalize_url


TEXT_CONTENT_TYPES = (
    "text/html",
    "text/plain",
    "application/xhtml+xml",
    "application/xml",
    "application/rss+xml",
    "application/atom+xml",
    "application/rdf+xml",
    "text/xml",
)
DEFAULT_MAX_CONTENT_CHARS = 500_000
MAX_REDIRECTS = 5
BLOCK_PAGE_PATTERNS = (
    "captcha",
    "verify you are human",
    "are you a human",
    "unusual traffic",
    "automated queries",
    "access denied",
    "temporarily blocked",
    "cloudflare ray id",
    "enable javascript and cookies",
    "checking your browser",
    "just a moment",
)


@dataclass(frozen=True)
class WebResponse:
    url: str
    status_code: int
    headers: dict[str, str]
    text: str


def default_fetcher(url: str, timeout_seconds: int, domain_rules: DomainRules | None = None) -> WebResponse:
    rules = domain_rules or DomainRules.from_env()
    try:
        with httpx.Client(
            timeout=timeout_seconds,
            follow_redirects=False,
            headers={"User-Agent": "LocalMacAIAgent/0.1"},
            cookies={},
        ) as client:
            current_url = url
            for _ in range(MAX_REDIRECTS + 1):
                with client.stream("GET", current_url) as response:
                    if response.is_redirect:
                        location = response.headers.get("location")
                        if not location:
                            raise ToolError("web fetch redirect missing location")
                        current_url = normalize_url(urljoin(str(response.url), location))
                        rules.validate_url(current_url)
                        continue
                    response.raise_for_status()
                    content_type = response.headers.get("content-type", "").split(";")[0].lower()
                    if content_type and not any(content_type.startswith(allowed) for allowed in TEXT_CONTENT_TYPES):
                        raise ToolError("binary downloads are disabled by default")
                    chunks: list[bytes] = []
                    total = 0
                    max_bytes = int(os.getenv("WEB_FETCH_MAX_BYTES", str(DEFAULT_MAX_CONTENT_CHARS)))
                    for chunk in response.iter_bytes():
                        total += len(chunk)
                        if total > max_bytes:
                            raise ToolError("web fetch content exceeds max content length")
                        chunks.append(chunk)
                    encoding = response.encoding or "utf-8"
                    return WebResponse(
                        url=str(response.url),
                        status_code=response.status_code,
                        headers={key.lower(): value for key, value in response.headers.items()},
                        text=b"".join(chunks).decode(encoding, errors="replace"),
                    )
            raise ToolError("web fetch exceeded redirect limit")
    except httpx.TimeoutException as exc:
        raise ToolError("web fetch timed out") from exc
    except httpx.HTTPError as exc:
        raise ToolError(f"web fetch failed: {type(exc).__name__}") from exc


def build_fetch_payload(
    *,
    requested_url: str,
    normalized_url: str,
    requested_domain: str,
    response: WebResponse,
    domain_rules: DomainRules,
    max_chars: int,
    max_content_chars: int,
    strip_tracking: bool = True,
    untrusted_manager: UntrustedContentManager | None = None,
) -> dict[str, object]:
    final_url = normalize_url(response.url, strip_tracking=strip_tracking)
    final_domain = domain_rules.validate_url(final_url)
    content_type = response.headers.get("content-type", "").split(";")[0].lower()
    if content_type and not any(content_type.startswith(allowed) for allowed in TEXT_CONTENT_TYPES):
        raise ToolError("binary downloads are disabled by default")
    if len(response.text) > max_content_chars:
        raise ToolError("web fetch content exceeds max content length")

    metadata = extract_metadata(response.text, base_url=final_url, content_type=content_type or "text/html")
    extracted = extract_readable_text(response.text, content_type or "text/html")
    text = str(extracted["text"])
    manager = untrusted_manager or UntrustedContentManager(max_chars=max_chars)
    block_reason = detect_block_page(response, text, metadata)
    status = "unavailable" if block_reason else "ok"
    wrapped_text = (
        f"UNTRUSTED_WEB content unavailable: {block_reason}"
        if block_reason
        else manager.wrap_webpage(text)
    )
    title = str(metadata.get("title") or extracted.get("title") or "")
    retrieved_at = datetime.now(UTC).isoformat()
    return {
        "status": status,
        "url": final_url,
        "final_url": final_url,
        "requested_url": requested_url,
        "normalized_url": normalized_url,
        "retrieved_at": retrieved_at,
        "status_code": response.status_code,
        "content_type": content_type or "unknown",
        "title": title,
        "text": "" if block_reason else text[:max_chars],
        "html_sanitized": "" if block_reason else str(extracted.get("html_sanitized") or ""),
        "trust_level": "UNTRUSTED_WEB",
        "blocked_reason": block_reason,
        "extraction_warnings": list(extracted.get("extraction_warnings") or []),
        "source_metadata": {
            "title": title or None,
            "canonical_url": metadata.get("canonical_url"),
            "author": metadata.get("author"),
            "published_at": metadata.get("published_at"),
            "retrieved_at": retrieved_at,
        },
        "content": wrapped_text,
        "content_chars": len(text),
        "truncated_to_chars": max_chars if len(text) > max_chars else None,
        "_audit": {
            "network_domains": sorted({requested_domain, final_domain}),
            "result_summary": f"web fetch {status}",
        },
    }


def make_extract_tools(
    *,
    fetcher: Callable[[str, int], WebResponse] | None = None,
    domain_rules: DomainRules | None = None,
    untrusted_manager: UntrustedContentManager | None = None,
) -> dict[str, Callable[..., dict[str, object]]]:
    rules = domain_rules or DomainRules.from_env()
    active_fetcher = fetcher or (lambda url, timeout_seconds: default_fetcher(url, timeout_seconds, rules))

    def _fetch_payload(url: str, timeout_seconds: int, max_chars: int, strip_tracking: bool) -> dict[str, object]:
        normalized_url = normalize_url(url, strip_tracking=strip_tracking)
        requested_domain = rules.validate_url(normalized_url)
        _validate_fetch_options(timeout_seconds=timeout_seconds, max_chars=max_chars, max_content_chars=DEFAULT_MAX_CONTENT_CHARS)
        try:
            response = active_fetcher(normalized_url, timeout_seconds)
        except httpx.TimeoutException as exc:
            raise ToolError("web fetch timed out") from exc
        return build_fetch_payload(
            requested_url=url,
            normalized_url=normalized_url,
            requested_domain=requested_domain,
            response=response,
            domain_rules=rules,
            max_chars=max_chars,
            max_content_chars=DEFAULT_MAX_CONTENT_CHARS,
            strip_tracking=strip_tracking,
            untrusted_manager=untrusted_manager,
        )

    def extract_readable(url: str, timeout_seconds: int = 10, max_chars: int = 20000, strip_tracking: bool = True) -> dict[str, object]:
        payload = _fetch_payload(url, timeout_seconds, max_chars, strip_tracking)
        return {
            "status": payload["status"],
            "url": payload["url"],
            "final_url": payload["final_url"],
            "title": payload["title"],
            "text": payload["text"],
            "retrieved_at": payload["retrieved_at"],
            "trust_level": "UNTRUSTED_WEB",
            "blocked_reason": payload["blocked_reason"],
            "extraction_warnings": payload["extraction_warnings"],
            "_audit": payload["_audit"],
        }

    def metadata(url: str, timeout_seconds: int = 10, strip_tracking: bool = True) -> dict[str, object]:
        payload = _fetch_payload(url, timeout_seconds, 20000, strip_tracking)
        return {
            "status": payload["status"],
            "url": payload["url"],
            "final_url": payload["final_url"],
            "retrieved_at": payload["retrieved_at"],
            "trust_level": "UNTRUSTED_WEB",
            "blocked_reason": payload["blocked_reason"],
            "source_metadata": payload["source_metadata"],
            "_audit": payload["_audit"],
        }

    return {"web.extract_readable_text": extract_readable, "web.extract_metadata": metadata}


def detect_block_page(response: WebResponse, text: str, metadata: dict[str, object]) -> str | None:
    combined = f"{metadata.get('title') or ''}\n{text}".lower()
    if response.status_code in {401, 403, 407, 429, 451}:
        return f"http_{response.status_code}_blocked_or_unavailable"
    if any(pattern in combined for pattern in BLOCK_PAGE_PATTERNS):
        return "captcha_or_block_page"
    return None


def _validate_fetch_options(*, timeout_seconds: int, max_chars: int, max_content_chars: int) -> None:
    if timeout_seconds <= 0 or timeout_seconds > 60:
        raise ToolError("timeout_seconds must be between 1 and 60")
    if max_chars <= 0 or max_chars > 100000:
        raise ToolError("max_chars must be between 1 and 100000")
    if max_content_chars <= 0 or max_content_chars > 2_000_000:
        raise ToolError("max_content_chars must be between 1 and 2000000")
