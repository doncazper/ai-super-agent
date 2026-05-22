from __future__ import annotations

import ipaddress
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Callable
from urllib.parse import urlparse

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


@dataclass(frozen=True)
class WebResponse:
    url: str
    status_code: int
    headers: dict[str, str]
    text: str


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
        parsed = urlparse(url)
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


def default_fetcher(url: str, timeout_seconds: int) -> WebResponse:
    try:
        with httpx.Client(
            timeout=timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": "LocalMacAIAgent/0.1"},
        ) as client:
            response = client.get(url)
            response.raise_for_status()
            return WebResponse(
                url=str(response.url),
                status_code=response.status_code,
                headers={key.lower(): value for key, value in response.headers.items()},
                text=response.text,
            )
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
    active_fetcher = fetcher or default_fetcher
    rules = domain_rules or DomainRules.from_env()

    def fetch_url(url: str, timeout_seconds: int = 10, max_chars: int = 20000) -> dict[str, object]:
        requested_domain = rules.validate_url(url)
        if timeout_seconds <= 0 or timeout_seconds > 60:
            raise ToolError("timeout_seconds must be between 1 and 60")
        try:
            response = active_fetcher(url, timeout_seconds)
        except httpx.TimeoutException as exc:
            raise ToolError("web fetch timed out") from exc
        final_domain = rules.validate_url(response.url)
        content_type = response.headers.get("content-type", "").split(";")[0].lower()
        if content_type and not any(content_type.startswith(allowed) for allowed in TEXT_CONTENT_TYPES):
            raise ToolError("binary downloads are disabled by default")
        extracted = extract_readable_text(response.text, content_type or "text/html")
        manager = untrusted_manager or UntrustedContentManager(max_chars=max_chars)
        wrapped = manager.wrap_webpage(extracted["text"])
        retrieved_at = datetime.now(UTC).isoformat()
        return {
            "url": response.url,
            "requested_url": url,
            "retrieved_at": retrieved_at,
            "status_code": response.status_code,
            "content_type": content_type or "unknown",
            "title": extracted["title"],
            "trust_level": "UNTRUSTED_WEB",
            "content": wrapped,
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
            },
            "required": ["url"],
            "additionalProperties": False,
        },
    },
}
