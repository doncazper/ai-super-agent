from __future__ import annotations

import os
from dataclasses import dataclass

from agent.config.runtime import env_bool
from agent.web_acquisition.official_apis.base import OfficialApiProvider
from agent.web_acquisition.official_apis.errors import OfficialApiSetupError


@dataclass
class RedditOfficialApiProvider(OfficialApiProvider):
    provider_name: str = "reddit"
    supported_domains: tuple[str, ...] = ("reddit.com", "www.reddit.com", "old.reddit.com", "redd.it", "oauth.reddit.com")
    capabilities: tuple[str, ...] = ("status", "search", "fetch_resource")
    requires_api_key: bool = True
    requires_oauth: bool = True
    authenticated_apis_enabled: bool = False
    docs_path: str = "docs/web/providers/reddit.md"
    web_scraping_fallback: bool = False
    personal_data_access: bool = False

    def is_configured(self) -> bool:
        return all(
            [
                env_bool("REDDIT_ENABLED", default=False),
                bool(os.getenv("REDDIT_CLIENT_ID", "").strip()),
                bool(os.getenv("REDDIT_CLIENT_SECRET", "").strip()),
                bool(os.getenv("REDDIT_USER_AGENT", "").strip()),
                bool(os.getenv("REDDIT_REFRESH_TOKEN", "").strip() or os.getenv("REDDIT_ACCESS_TOKEN", "").strip()),
            ]
        )

    def is_enabled(self) -> bool:
        return self.is_configured()

    def setup_hint(self) -> str:
        return (
            "Reddit official API access is read-only, OAuth-gated, and setup-gated. "
            "Set REDDIT_ENABLED=true plus REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, and a token only after the Reddit connector track is approved. "
            "Reddit web scraping is not used as an API substitute."
        )

    def rate_limit(self) -> dict[str, object]:
        return {
            "enforced_by_toolbroker": True,
            "provider": "reddit",
            "must_respect_provider_headers": True,
            "web_scraping_fallback": False,
        }

    def search(self, query: str, max_results: int, locale: str | None = None, safe_search: bool = True):
        raise OfficialApiSetupError("Reddit official API connector is a read-only setup-gated stub in this build.", setup_hint=self.setup_hint())

    def fetch_resource(self, resource: str, **kwargs):
        raise OfficialApiSetupError("Reddit official API connector is a read-only setup-gated stub in this build.", setup_hint=self.setup_hint())
