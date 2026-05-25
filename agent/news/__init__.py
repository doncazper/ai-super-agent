"""News Intelligence policy scaffolding.

This package intentionally contains no provider clients or fetch logic.
"""

from agent.news.config import NewsConfig
from agent.news.provider_policy import (
    NewsProviderCandidate,
    NewsProviderDecision,
    news_provider_candidates,
    select_news_provider,
)

__all__ = [
    "NewsConfig",
    "NewsProviderCandidate",
    "NewsProviderDecision",
    "news_provider_candidates",
    "select_news_provider",
]
