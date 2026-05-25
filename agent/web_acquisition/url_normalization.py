from __future__ import annotations

import ipaddress
import os
from dataclasses import dataclass
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from agent.tools.errors import ToolError


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
    return urlunparse((scheme, netloc, parsed.path or "/", "", urlencode(query_pairs, doseq=True), ""))


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
