from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from agent.web_acquisition.search.models import SearchCostClass, SearchProviderInfo, SearchResult


class SearchProvider(ABC):
    provider_name: str
    cost_class: SearchCostClass | str
    requires_api_key: bool
    supports_news: bool = False
    supports_images: bool = False
    supports_time_filter: bool = False

    @abstractmethod
    def is_configured(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_enabled(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def setup_hint(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        query: str,
        max_results: int,
        locale: str | None = None,
        safe_search: bool = True,
        freshness: str | None = None,
    ) -> list[SearchResult | dict[str, Any]]:
        raise NotImplementedError

    def rate_limit_status(self) -> dict[str, Any]:
        return {"enforced_by_provider": True}

    def info(self) -> SearchProviderInfo:
        configured = self.is_configured()
        enabled = self.is_enabled()
        if configured and enabled:
            status = "available"
        elif configured:
            status = "disabled"
        else:
            status = "setup_required"
        return SearchProviderInfo(
            provider_name=self.provider_name,
            configured=configured,
            enabled=enabled,
            cost_class=self.cost_class,
            requires_api_key=self.requires_api_key,
            supports_news=self.supports_news,
            supports_images=self.supports_images,
            supports_time_filter=self.supports_time_filter,
            setup_hint=self.setup_hint(),
            status=status,
            rate_limit_status=self.rate_limit_status(),
        )
