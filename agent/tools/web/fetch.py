from __future__ import annotations

import httpx
from typing import Callable

from agent.tools.errors import ToolError
from agent.tools.web.untrusted_content import UntrustedContentManager
from agent.web_acquisition.fetch import (
    DEFAULT_MAX_CONTENT_CHARS,
    MAX_REDIRECTS,
    TEXT_CONTENT_TYPES,
    WebResponse,
    build_fetch_payload,
    default_fetcher,
    make_extract_tools,
)
from agent.web_acquisition.url_normalization import (
    TRACKING_QUERY_KEYS,
    TRACKING_QUERY_PREFIXES,
    DomainRules,
    normalize_url,
)


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
        _validate_fetch_options(timeout_seconds=timeout_seconds, max_chars=max_chars, max_content_chars=max_content_chars)
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
            max_content_chars=max_content_chars,
            strip_tracking=strip_tracking,
            untrusted_manager=untrusted_manager,
        )

    return fetch_url


def _validate_fetch_options(*, timeout_seconds: int, max_chars: int, max_content_chars: int) -> None:
    if timeout_seconds <= 0 or timeout_seconds > 60:
        raise ToolError("timeout_seconds must be between 1 and 60")
    if max_chars <= 0 or max_chars > 100000:
        raise ToolError("max_chars must be between 1 and 100000")
    if max_content_chars <= 0 or max_content_chars > 2_000_000:
        raise ToolError("max_content_chars must be between 1 and 2000000")


WEB_FETCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.fetch_url",
        "description": "Fetch a public webpage as untrusted data, sanitize it, extract readable text and metadata, and wrap it with untrusted-content warnings.",
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


WEB_EXTRACT_READABLE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.extract_readable_text",
        "description": "Fetch a public webpage and return sanitized readable text as untrusted web data.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 60},
                "max_chars": {"type": "integer", "minimum": 1, "maximum": 100000},
                "strip_tracking": {"type": "boolean"},
            },
            "required": ["url"],
            "additionalProperties": False,
        },
    },
}


WEB_EXTRACT_METADATA_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web.extract_metadata",
        "description": "Fetch a public webpage and return source metadata as untrusted web data.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 60},
                "strip_tracking": {"type": "boolean"},
            },
            "required": ["url"],
            "additionalProperties": False,
        },
    },
}
