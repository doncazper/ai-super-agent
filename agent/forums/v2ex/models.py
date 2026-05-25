from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse


PROVIDER = "v2ex_api"
TRUST_LEVEL = "UNTRUSTED_WEB"
V2EX_BASE_URL = "https://www.v2ex.com"


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def stable_source_id(kind: str, item_id: str, url: str = "") -> str:
    material = f"{PROVIDER}|{kind}|{str(item_id).strip()}|{str(url).strip()}"
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]
    return f"v2ex_{kind}_{digest}"


def v2ex_url(path_or_url: str) -> str:
    value = str(path_or_url or "").strip()
    if not value:
        return ""
    if value.startswith(("http://", "https://")):
        return value
    return f"{V2EX_BASE_URL}{value if value.startswith('/') else '/' + value}"


def v2ex_domain(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


@dataclass(frozen=True)
class V2EXNode:
    source_id: str
    node_id: str
    name: str
    title: str
    url: str
    topics: int | None = None
    created_at: str = ""
    retrieved_at: str = field(default_factory=utc_now_iso)
    trust_level: str = TRUST_LEVEL
    provider: str = PROVIDER
    body_text: str = ""
    language: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class V2EXTopic:
    source_id: str
    topic_id: str
    node_name: str
    title: str
    url: str
    body_text: str
    reply_count: int | None = None
    created_at: str = ""
    retrieved_at: str = field(default_factory=utc_now_iso)
    author_display: str | None = None
    trust_level: str = TRUST_LEVEL
    provider: str = PROVIDER
    language: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.author_display is None:
            payload.pop("author_display", None)
        return payload


@dataclass(frozen=True)
class V2EXReply:
    source_id: str
    reply_id: str
    topic_id: str
    url: str
    body_text: str
    created_at: str = ""
    retrieved_at: str = field(default_factory=utc_now_iso)
    author_display: str | None = None
    trust_level: str = TRUST_LEVEL
    provider: str = PROVIDER
    language: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.author_display is None:
            payload.pop("author_display", None)
        return payload
