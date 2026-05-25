from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any, Mapping

from agent.web_acquisition.official_apis.errors import OfficialApiSetupError
from agent.web_acquisition.official_apis.models import (
    OfficialApiProviderStatus,
    OfficialApiResult,
    content_hash,
    source_from_url,
)


class OfficialApiProvider(ABC):
    provider_name: str
    supported_domains: tuple[str, ...]
    capabilities: tuple[str, ...]
    requires_api_key: bool = False
    requires_oauth: bool = False
    authenticated_apis_enabled: bool = False
    default_enabled: bool = False
    docs_path: str = ""
    web_scraping_fallback: bool = False
    personal_data_access: bool = False

    @abstractmethod
    def is_configured(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_enabled(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def setup_hint(self) -> str:
        raise NotImplementedError

    def rate_limit(self) -> dict[str, Any]:
        return {"enforced_by_toolbroker": True}

    def status(self) -> OfficialApiProviderStatus:
        configured = self.is_configured()
        enabled = self.is_enabled()
        if configured and enabled:
            status = "available"
        elif configured:
            status = "disabled"
        else:
            status = "setup_required"
        return OfficialApiProviderStatus(
            provider_name=self.provider_name,
            configured=configured,
            enabled=enabled,
            requires_api_key=self.requires_api_key,
            requires_oauth=self.requires_oauth,
            authenticated_apis_enabled=self.authenticated_apis_enabled,
            supported_domains=self.supported_domains,
            capabilities=self.capabilities,
            rate_limit=self.rate_limit(),
            setup_hint=self.setup_hint(),
            default_enabled=self.default_enabled,
            status=status,
            docs_path=self.docs_path,
            web_scraping_fallback=self.web_scraping_fallback,
            personal_data_access=self.personal_data_access,
        )

    def fetch_resource(self, resource: str, **kwargs: Any) -> OfficialApiResult:
        raise OfficialApiSetupError(
            f"{self.provider_name} official API fetch is a framework stub in this build.",
            setup_hint=self.setup_hint(),
        )

    def search(
        self,
        query: str,
        max_results: int,
        locale: str | None = None,
        safe_search: bool = True,
    ) -> list[OfficialApiResult]:
        raise OfficialApiSetupError(
            f"{self.provider_name} official API search is not configured.",
            setup_hint=self.setup_hint(),
        )

    def normalize_result(self, raw: Mapping[str, Any], *, rank: int = 1, retrieved_at: str | None = None) -> OfficialApiResult:
        url = str(raw.get("url") or raw.get("html_url") or raw.get("link") or "").strip()
        title = str(raw.get("title") or raw.get("name") or raw.get("full_name") or url).strip()
        snippet = str(raw.get("snippet") or raw.get("description") or raw.get("summary") or raw.get("extract") or "").strip()
        resolved_retrieved_at = retrieved_at or datetime.now(UTC).isoformat()
        return OfficialApiResult(
            title=title,
            url=url,
            snippet=snippet,
            source=str(raw.get("source") or "").strip() or source_from_url(url),
            provider=self.provider_name,
            retrieved_at=resolved_retrieved_at,
            rank=rank,
            published_at=str(raw.get("published_at") or raw.get("updated_at") or "").strip() or None,
            language=str(raw.get("language") or "").strip() or None,
            content_type=str(raw.get("content_type") or "official_api_result").strip(),
            reliability_signals={
                "official_api": True,
                "content_hash": content_hash(title, url, snippet, self.provider_name),
                **dict(raw.get("reliability_signals") or {}),
            },
        )
