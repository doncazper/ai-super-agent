from __future__ import annotations

import ipaddress
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Callable
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

import httpx

from agent.tools.errors import ToolError
from agent.tools.web.extraction import extract_readable_text
from agent.tools.web.untrusted_content import UntrustedContentManager


TEXT_CONTENT_TYPES = (
    "text/html",
    "text/plain",
    "application/xhtml+xml",
    "application/xml",
    "text/xml",
)

TRACKING_QUERY_PREFIXES = ("utm_",)
TRACKING_QUERY_KEYS = {
    "fbclid",
    "gclid",
    "dclid",
    "gbraid",
    "wbraid",
    "mc_cid",
    "mc_eid",
    "igshid",
    "msclkid",
    "ref",
}
DEFAULT_MAX_CONTENT_CHARS = 500_000
MAX_REDIRECTS = 5


@dataclass(frozen=True)
class WebResponse:
    url: str
    status_code: int
    headers: dict[str, str]
    text: str


def normalize_url(url: str, *, strip_tracking: bool = True) -> str:
    parsed = urlparse(url.strip())
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    if (scheme == "https" and netloc.endswith(":443")) or (scheme == "http" and netloc.endswith(":80")):
        netloc = netloc.rsplit(":", 1)[0]
    query_pairs = parse_qsl(parsed.query, keep_blank_values=True)
    if strip_tracking:
        query_pairs = [
            (key, value)
            for key, value in query_pairs
            if key.lower() not in TRACKING_QUERY_KEYS
            and not any(key.lower().startswith(prefix) for prefix in TRACKING_QUERY_PREFIXES)
        ]
    return urlunparse(
        (
            scheme,
            netloc,
            parsed.path or "/",
            "",
            urlencode(query_pairs, doseq=True),
            "",
        )
    )


@dataclass(frozen=True)
class DomainRules:
    allowed_domains: frozenset[str] = frozenset()
    blocked_domains: frozenset[str] = frozenset()

    @classmethod
    def from_env(cls) -> "DomainRules":
        return cls(
            allowed_domains=_split_domains(os.getenv("WEB_ALLOWED_DOMAINS", "")),
            blocked_domains=_split_domains(os.getenv("WEB_BLOCKED_DOMAINS", "")),
        )

    def validate_url(self, url: str) -> str:
        normalized = normalize_url(url)
        parsed = urlparse(normalized)
        if parsed.scheme not in {"http", "https"}:
            raise ToolError("only http and https URLs are supported")
        if not parsed.hostname:
            raise ToolError("URL host is required")
        hostname = parsed.hostname.lower()
        if self._is_private_host(hostname):
            raise ToolError("private or local network hosts are blocked")
        if self.blocked_domains and _domain_matches(hostname, self.blocked_domains):
            raise ToolError("blocked domain denied")
        if self.allowed_domains and not _domain_matches(hostname, self.allowed_domains):
            raise ToolError("domain is not on the allow list")
        return hostname

    def _is_private_host(self, hostname: str) -> bool:
        if hostname in {"localhost", "localhost.localdomain"}:
            return True
        try:
            address = ipaddress.ip_address(hostname)
        except ValueError:
            return False
        return address.is_private or address.is_loopback or address.is_link_local


def _split_domains(raw: str) -> frozenset[str]:
    return frozenset(part.strip().lower() for part in raw.split(",") if part.strip())


def _domain_matches(hostname: str, domains: frozenset[str]) -> bool:
    return any(hostname == domain or hostname.endswith(f".{domain}") for domain in domains)


def default_fetcher(url: str, timeout_seconds: int, domain_rules: DomainRules | None = None) -> WebResponse:
    rules = domain_rules or DomainRules.from_env()
    try:
        with httpx.Client(
            timeout=timeout_seconds,
            follow_redirects=False,
            headers={"User-Agent": "LocalMacAIAgent/0.1"},
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


def make_fetch_tool(
    *,
    fetcher: Callable[[str, int], WebResponse] | None = None,
    domain_rules: DomainRules | None = None,
    untrusted_manager: UntrustedContentManager | None = None,
) -> Callable[..., dict[str, object]]:
    rules = domain_rules or DomainRules.from_env()
    active_fetcher = fetcher or (lambda url, timeout_seconds: default_fetcher(url, timeout_seconds, rules))

    def fetch_url(
        url: str,
        timeout_seconds: int = 10,
        max_chars: int = 20000,
        strip_tracking: bool = True,
        max_content_chars: int = DEFAULT_MAX_CONTENT_CHARS,
    ) -> dict[str, object]:
        normalized_url = normalize_url(url, strip_tracking=strip_tracking)
        requested_domain = rules.validate_url(normalized_url)
        if timeout_seconds <= 0 or timeout_seconds > 60:
            raise ToolError("timeout_seconds must be between 1 and 60")
        if max_chars <= 0 or max_chars > 100000:
            raise ToolError("max_chars must be between 1 and 100000")
        if max_content_chars <= 0 or max_content_chars > 2_000_000:
            raise ToolError("max_content_chars must be between 1 and 2000000")
        try:
            response = active_fetcher(normalized_url, timeout_seconds)
        except httpx.TimeoutException as exc:
            raise ToolError("web fetch timed out") from exc
        final_url = normalize_url(response.url, strip_tracking=strip_tracking)
        final_domain = rules.validate_url(final_url)
        content_type = response.headers.get("content-type", "").split(";")[0].lower()
        if content_type and not any(content_type.startswith(allowed) for allowed in TEXT_CONTENT_TYPES):
            raise ToolError("binary downloads are disabled by default")
        if len(response.text) > max_content_chars:
            raise ToolError("web fetch content exceeds max content length")
        extracted = extract_readable_text(response.text, content_type or "text/html")
        manager = untrusted_manager or UntrustedContentManager(max_chars=max_chars)
        wrapped = manager.wrap_webpage(extracted["text"])
        retrieved_at = datetime.now(UTC).isoformat()
        return {
            "url": final_url,
            "requested_url": url,
            "normalized_url": normalized_url,
            "retrieved_at": retrieved_at,
            "status_code": response.status_code,
            "content_type": content_type or "unknown",
            "title": extracted["title"],
            "trust_level": "UNTRUSTED_WEB",
            "content": wrapped,
            "content_chars": len(extracted["text"]),
            "truncated_to_chars": max_chars if len(extracted["text"]) > max_chars else None,
            "_audit": {"network_domains": sorted({requested_domain, final_domain})},
        }

    return fetch_url


WEB_FETCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.fetch_url",
        "description": "Fetch a public webpage as untrusted data, extract readable text, and wrap it with untrusted-content warnings.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 60},
                "max_chars": {"type": "integer", "minimum": 1, "maximum": 100000},
                "strip_tracking": {"type": "boolean"},
                "max_content_chars": {"type": "integer", "minimum": 1, "maximum": 2000000},
            },
            "required": ["url"],
            "additionalProperties": False,
        },
    },
}
