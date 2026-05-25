from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from agent.web_acquisition.official_apis.base import OfficialApiProvider
from agent.web_acquisition.official_apis.errors import OfficialApiSetupError
from agent.web_acquisition.official_apis.models import OfficialApiResult


@dataclass
class ArxivOfficialApiProvider(OfficialApiProvider):
    enabled: bool | None = None
    mock_results: list[Mapping[str, Any]] = field(default_factory=list)

    provider_name: str = "arxiv"
    supported_domains: tuple[str, ...] = ("arxiv.org", "export.arxiv.org")
    capabilities: tuple[str, ...] = ("status", "search", "fetch_resource")
    requires_api_key: bool = False
    docs_path: str = "docs/web/providers/arxiv.md"

    def is_configured(self) -> bool:
        return bool(self.mock_results)

    def is_enabled(self) -> bool:
        return bool(self.mock_results)

    def setup_hint(self) -> str:
        return (
            "arXiv official API support is framework/stubbed in v1. "
            "Set ARXIV_OFFICIAL_API_ENABLED=true only after a later live connector implementation is approved."
        )

    def rate_limit(self) -> dict[str, Any]:
        return {"enforced_by_toolbroker": True, "provider": "arxiv", "live_calls_default": False}

    def search(self, query: str, max_results: int, locale: str | None = None, safe_search: bool = True) -> list[OfficialApiResult]:
        if self.mock_results:
            return [self.normalize_result(raw, rank=index + 1) for index, raw in enumerate(self.mock_results[:max_results])]
        raise OfficialApiSetupError("arXiv live API search is not implemented in this framework milestone.", setup_hint=self.setup_hint())

    def normalize_result(self, raw: Mapping[str, Any], *, rank: int = 1, retrieved_at: str | None = None) -> OfficialApiResult:
        mapped = {
            "title": raw.get("title") or raw.get("name"),
            "url": raw.get("pdf_url") or raw.get("entry_url") or raw.get("url"),
            "snippet": raw.get("summary") or raw.get("snippet") or "",
            "source": "arxiv.org",
            "published_at": raw.get("published_at") or raw.get("published"),
            "content_type": raw.get("content_type") or "arxiv_paper",
            "reliability_signals": {"official_api": True, "provider_host": "export.arxiv.org"},
        }
        return super().normalize_result(mapped, rank=rank, retrieved_at=retrieved_at)
