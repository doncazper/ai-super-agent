from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from agent.safety.policy import RiskLevel
from agent.safety.trust import TrustLevel


class ForumProviderStatus(StrEnum):
    ACTIVE = "active"
    CONFIGURED = "configured"
    DISABLED = "disabled"
    STUBBED = "stubbed"
    DISCOVERY_ONLY = "discovery_only"
    BLOCKED = "blocked"
    UNSUPPORTED = "unsupported"
    DEPRECATED = "deprecated"


@dataclass(frozen=True)
class ForumProvider:
    provider_id: str
    name: str
    regions: tuple[str, ...]
    languages: tuple[str, ...]
    source_type: str
    official_api_available: bool
    auth_required: bool
    read_capabilities: tuple[str, ...]
    write_capabilities: tuple[str, ...]
    risk_level: RiskLevel
    default_enabled: bool
    setup_hint: str
    access_policy: dict[str, Any]
    rate_limit_policy: dict[str, Any]
    retention_policy: dict[str, Any]
    status: ForumProviderStatus
    trust_level: TrustLevel = TrustLevel.UNTRUSTED_WEB
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "name": self.name,
            "regions": list(self.regions),
            "languages": list(self.languages),
            "source_type": self.source_type,
            "official_api_available": self.official_api_available,
            "auth_required": self.auth_required,
            "read_capabilities": list(self.read_capabilities),
            "write_capabilities": list(self.write_capabilities),
            "risk_level": self.risk_level.value,
            "trust_level": self.trust_level.value,
            "default_enabled": self.default_enabled,
            "status": self.status.value,
            "setup_hint": self.setup_hint,
            "access_policy": dict(self.access_policy),
            "rate_limit_policy": dict(self.rate_limit_policy),
            "retention_policy": dict(self.retention_policy),
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class ForumPost:
    source_id: str
    provider: str
    provider_post_id: str
    title: str
    url: str
    body_text: str = ""
    created_at: str = ""
    retrieved_at: str = ""
    trust_level: str = TrustLevel.UNTRUSTED_WEB.value
    author_display: str | None = None
    language: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "source_id": self.source_id,
            "provider": self.provider,
            "provider_post_id": self.provider_post_id,
            "title": self.title,
            "url": self.url,
            "body_text": self.body_text,
            "created_at": self.created_at,
            "retrieved_at": self.retrieved_at,
            "trust_level": self.trust_level,
            "language": self.language,
            "metadata": dict(self.metadata),
        }
        if self.author_display is not None:
            payload["author_display"] = self.author_display
        return payload


@dataclass(frozen=True)
class ForumComment:
    source_id: str
    provider: str
    provider_comment_id: str
    thread_id: str
    url: str
    body_text: str = ""
    created_at: str = ""
    retrieved_at: str = ""
    trust_level: str = TrustLevel.UNTRUSTED_WEB.value
    author_display: str | None = None
    parent_id: str = ""
    depth: int = 0
    language: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "source_id": self.source_id,
            "provider": self.provider,
            "provider_comment_id": self.provider_comment_id,
            "thread_id": self.thread_id,
            "url": self.url,
            "body_text": self.body_text,
            "created_at": self.created_at,
            "retrieved_at": self.retrieved_at,
            "trust_level": self.trust_level,
            "parent_id": self.parent_id,
            "depth": self.depth,
            "language": self.language,
            "metadata": dict(self.metadata),
        }
        if self.author_display is not None:
            payload["author_display"] = self.author_display
        return payload


@dataclass(frozen=True)
class ForumThread:
    source_id: str
    provider: str
    provider_thread_id: str
    title: str
    url: str
    post: ForumPost
    comments: list[ForumComment] = field(default_factory=list)
    retrieved_at: str = ""
    trust_level: str = TrustLevel.UNTRUSTED_WEB.value
    language: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "provider": self.provider,
            "provider_thread_id": self.provider_thread_id,
            "title": self.title,
            "url": self.url,
            "post": self.post.to_dict(),
            "comments": [comment.to_dict() for comment in self.comments],
            "retrieved_at": self.retrieved_at,
            "trust_level": self.trust_level,
            "language": self.language,
            "metadata": dict(self.metadata),
            "source_references": [
                {
                    "source_id": self.source_id,
                    "title": self.title,
                    "url": self.url,
                    "provider": self.provider,
                    "trust_level": self.trust_level,
                    "retrieved_at": self.retrieved_at,
                },
                *[
                    {
                        "source_id": comment.source_id,
                        "title": f"Reply {comment.provider_comment_id}",
                        "url": comment.url,
                        "provider": self.provider,
                        "trust_level": self.trust_level,
                        "retrieved_at": comment.retrieved_at or self.retrieved_at,
                    }
                    for comment in self.comments
                ],
            ],
        }


def unsupported_provider(provider_id: str, *, known_provider_ids: tuple[str, ...]) -> ForumProvider:
    known = ", ".join(known_provider_ids)
    return ForumProvider(
        provider_id=provider_id,
        name=f"Unknown provider: {provider_id}",
        regions=("unknown",),
        languages=("unknown",),
        source_type="unsupported",
        official_api_available=False,
        auth_required=False,
        read_capabilities=(),
        write_capabilities=(),
        risk_level=RiskLevel.SAFE,
        default_enabled=False,
        setup_hint=f"Unknown forum provider. Known providers: {known}.",
        access_policy={
            "status_reads_personal_data": False,
            "logged_in_reads_allowed": False,
            "scraping_allowed": False,
            "discovery_method": "none",
        },
        rate_limit_policy={"network_call_performed": False},
        retention_policy={"stores_user_content_by_default": False},
        status=ForumProviderStatus.UNSUPPORTED,
        notes=("Unknown providers are never queried.",),
    )
