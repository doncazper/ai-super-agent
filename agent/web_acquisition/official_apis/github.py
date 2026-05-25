from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from agent.web_acquisition.official_apis.base import OfficialApiProvider
from agent.web_acquisition.official_apis.errors import OfficialApiSetupError
from agent.web_acquisition.official_apis.models import OfficialApiResult


@dataclass
class GitHubOfficialApiProvider(OfficialApiProvider):
    enabled: bool | None = None
    mock_results: list[Mapping[str, Any]] = field(default_factory=list)

    provider_name: str = "github"
    supported_domains: tuple[str, ...] = ("github.com", "api.github.com")
    capabilities: tuple[str, ...] = ("status", "search", "fetch_resource")
    requires_api_key: bool = False
    docs_path: str = "docs/web/providers/github.md"

    def is_configured(self) -> bool:
        return bool(self.mock_results)

    def is_enabled(self) -> bool:
        return bool(self.mock_results)

    def setup_hint(self) -> str:
        return (
            "GitHub official API support is framework/stubbed in v1. "
            "Set GITHUB_OFFICIAL_API_ENABLED=true only after a later live connector implementation is approved; "
            "public/mock normalization is available for tests."
        )

    def rate_limit(self) -> dict[str, Any]:
        return {"enforced_by_toolbroker": True, "provider": "github", "live_calls_default": False}

    def search(self, query: str, max_results: int, locale: str | None = None, safe_search: bool = True) -> list[OfficialApiResult]:
        if self.mock_results:
            return [self.normalize_result(raw, rank=index + 1) for index, raw in enumerate(self.mock_results[:max_results])]
        raise OfficialApiSetupError("GitHub live API search is not implemented in this framework milestone.", setup_hint=self.setup_hint())

    def normalize_result(self, raw: Mapping[str, Any], *, rank: int = 1, retrieved_at: str | None = None) -> OfficialApiResult:
        mapped = {
            "title": raw.get("full_name") or raw.get("name") or raw.get("title"),
            "url": raw.get("html_url") or raw.get("url"),
            "snippet": raw.get("description") or raw.get("snippet") or "",
            "source": "github.com",
            "language": raw.get("language") or "",
            "content_type": raw.get("content_type") or "github_repository",
            "reliability_signals": {"official_api": True, "provider_host": "api.github.com"},
        }
        return super().normalize_result(mapped, rank=rank, retrieved_at=retrieved_at)
