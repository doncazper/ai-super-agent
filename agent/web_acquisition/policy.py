from __future__ import annotations

from typing import Mapping

from agent.connectors.cost_policy import ProviderCostConfig, select_provider
from agent.web_acquisition.models import ProviderDecision
from agent.web_acquisition.providers import provider_candidates_for_policy


def decide_provider(
    *,
    env: Mapping[str, str] | None = None,
    explicit_provider: str | None = None,
    cache_available: bool = False,
    url_available: bool = False,
    feed_available: bool = False,
    sitemap_available: bool = False,
    official_api_available: bool = False,
) -> ProviderDecision:
    config = ProviderCostConfig.from_env(env)
    decision = select_provider(
        "web",
        provider_candidates_for_policy(
            env=env,
            cache_available=cache_available,
            url_available=url_available,
            feed_available=feed_available,
            sitemap_available=sitemap_available,
            official_api_available=official_api_available,
        ),
        config=config,
        explicit_provider=explicit_provider if explicit_provider not in {None, "", "auto"} else None,
    )
    return ProviderDecision.from_cost_policy(decision.to_dict())

