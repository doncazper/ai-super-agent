from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse


TRUST_LEVEL = "UNTRUSTED_WEB"
PROVIDER = "reddit_api"


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def stable_source_id(kind: str, reddit_id: str, permalink: str = "") -> str:
    material = f"{PROVIDER}|{kind}|{reddit_id.strip()}|{permalink.strip()}"
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]
    return f"reddit_{kind}_{digest}"


def reddit_permalink(permalink: str) -> str:
    value = (permalink or "").strip()
    if not value:
        return ""
    if value.startswith("http://") or value.startswith("https://"):
        return value
    return f"https://www.reddit.com{value if value.startswith('/') else '/' + value}"


def reddit_domain(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


@dataclass(frozen=True)
class RedditPost:
    source_id: str
    reddit_id: str
    subreddit: str
    title: str
    url: str
    permalink: str
    body_text: str
    score: int | None = None
    comment_count: int | None = None
    created_at: str = ""
    retrieved_at: str = field(default_factory=utc_now_iso)
    author_display: str | None = None
    trust_level: str = TRUST_LEVEL
    provider: str = PROVIDER
    removed: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.author_display is None:
            payload.pop("author_display", None)
        return payload


@dataclass(frozen=True)
class RedditComment:
    source_id: str
    reddit_id: str
    subreddit: str
    title: str
    url: str
    permalink: str
    body_text: str
    score: int | None = None
    comment_count: int | None = None
    created_at: str = ""
    retrieved_at: str = field(default_factory=utc_now_iso)
    author_display: str | None = None
    trust_level: str = TRUST_LEVEL
    provider: str = PROVIDER
    parent_id: str = ""
    depth: int = 0
    removed: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.author_display is None:
            payload.pop("author_display", None)
        return payload


@dataclass(frozen=True)
class RedditSubreddit:
    source_id: str
    reddit_id: str
    subreddit: str
    title: str
    url: str
    permalink: str
    body_text: str = ""
    score: int | None = None
    comment_count: int | None = None
    created_at: str = ""
    retrieved_at: str = field(default_factory=utc_now_iso)
    author_display: str | None = None
    trust_level: str = TRUST_LEVEL
    provider: str = PROVIDER
    subscribers: int | None = None
    public_description: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.author_display is None:
            payload.pop("author_display", None)
        return payload


@dataclass(frozen=True)
class RedditSearchResult:
    source_id: str
    reddit_id: str
    subreddit: str
    title: str
    url: str
    permalink: str
    body_text: str
    score: int | None = None
    comment_count: int | None = None
    created_at: str = ""
    retrieved_at: str = field(default_factory=utc_now_iso)
    author_display: str | None = None
    trust_level: str = TRUST_LEVEL
    provider: str = PROVIDER
    rank: int = 0
    snippet_only: bool = True
    evidence_type: str = "snippet_only"
    data_state: str = "search_snippet"
    language: str = "unknown"
    removed: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.author_display is None:
            payload.pop("author_display", None)
        return payload


@dataclass(frozen=True)
class RedditThread:
    post: RedditPost
    comments: list[RedditComment]
    comment_tree: list[dict[str, Any]] = field(default_factory=list)
    retrieved_at: str = field(default_factory=utc_now_iso)
    trust_level: str = TRUST_LEVEL
    provider: str = PROVIDER
    fetch_warnings: list[dict[str, Any]] = field(default_factory=list)
    truncation_info: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "post": self.post.to_dict(),
            "comments": [comment.to_dict() for comment in self.comments],
            "comment_tree": [dict(node) for node in self.comment_tree],
            "flattened_comments": [comment.to_dict() for comment in self.comments],
            "retrieved_at": self.retrieved_at,
            "trust_level": self.trust_level,
            "provider": self.provider,
            "fetch_warnings": [dict(warning) for warning in self.fetch_warnings],
            "truncation_info": dict(self.truncation_info),
            "source_references": [
                {
                    "source_id": self.post.source_id,
                    "url": self.post.permalink,
                    "title": self.post.title,
                    "provider": self.provider,
                    "trust_level": self.trust_level,
                    "retrieved_at": self.retrieved_at,
                },
                *[
                    {
                        "source_id": comment.source_id,
                        "url": comment.permalink,
                        "title": comment.title,
                        "provider": self.provider,
                        "trust_level": self.trust_level,
                        "retrieved_at": self.retrieved_at,
                    }
                    for comment in self.comments
                ],
            ],
        }
