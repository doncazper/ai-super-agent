from __future__ import annotations

import os
from collections.abc import Iterable

from agent.forums.models import ForumProvider, ForumProviderStatus, unsupported_provider
from agent.forums.source_policy import (
    default_rate_limit_policy,
    default_retention_policy,
    discovery_only_policy,
    official_api_policy,
    stub_policy,
)
from agent.safety.policy import RiskLevel


def _env_bool(name: str, *, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class ForumProviderRegistry:
    def __init__(self, providers: Iterable[ForumProvider] | None = None) -> None:
        configured = tuple(providers) if providers is not None else tuple(_default_providers())
        self._providers = {provider.provider_id: provider for provider in configured}

    def list_providers(self) -> list[ForumProvider]:
        return sorted(self._providers.values(), key=lambda provider: provider.provider_id)

    def get_provider(self, provider_id: str) -> ForumProvider:
        normalized = provider_id.strip().lower()
        provider = self._providers.get(normalized)
        if provider is not None:
            return provider
        return unsupported_provider(normalized or "unknown", known_provider_ids=tuple(sorted(self._providers)))

    def has_provider(self, provider_id: str) -> bool:
        return provider_id.strip().lower() in self._providers

    def capability_summary(self, provider_id: str) -> dict[str, object]:
        provider = self.get_provider(provider_id)
        return {
            "provider_id": provider.provider_id,
            "status": provider.status.value,
            "read_capabilities": list(provider.read_capabilities),
            "write_capabilities": list(provider.write_capabilities),
            "write_capabilities_deferred": not provider.write_capabilities,
            "risk_level": provider.risk_level.value,
            "trust_level": provider.trust_level.value,
            "default_enabled": provider.default_enabled,
            "setup_hint": provider.setup_hint,
            "access_policy": dict(provider.access_policy),
            "retention_policy": dict(provider.retention_policy),
        }

    def doctor(self) -> dict[str, object]:
        providers = self.list_providers()
        return {
            "status": "ok",
            "provider_count": len(providers),
            "providers": [provider.to_dict() for provider in providers],
            "status_checks_personal_data": False,
            "logged_in_read_performed": False,
            "network_call_performed": False,
            "write_capabilities_enabled": False,
            "discovery_only_uses_site_filters": True,
            "warnings": _registry_warnings(providers),
            "next_setup_steps": [
                "Enable only official/API providers through their dedicated connector milestones.",
                "Use discovery-only providers through approved search-provider site filters or selected public URL fetch where allowed.",
                "Do not use login cookies, private pages, CAPTCHA bypass, anti-bot bypass, or platform-specific scraping.",
            ],
        }


def default_forum_provider_registry() -> ForumProviderRegistry:
    return ForumProviderRegistry()


def _default_providers() -> list[ForumProvider]:
    reddit_enabled = _env_bool("REDDIT_ENABLED", default=False)
    reddit_configured = all(
        os.environ.get(name)
        for name in ("REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT")
    )
    reddit_status = (
        ForumProviderStatus.CONFIGURED if reddit_enabled and reddit_configured else ForumProviderStatus.DISABLED
    )
    v2ex_enabled = _env_bool("V2EX_ENABLED", default=False)

    providers = [
        ForumProvider(
            provider_id="reddit",
            name="Reddit",
            regions=("global",),
            languages=("multi",),
            source_type="official_api",
            official_api_available=True,
            auth_required=True,
            read_capabilities=(
                "reddit.status",
                "reddit.search_posts",
                "reddit.search_subreddit",
                "reddit.fetch_subreddit_info",
                "reddit.fetch_post",
                "reddit.fetch_comments",
                "reddit.fetch_thread",
            ),
            write_capabilities=(),
            risk_level=RiskLevel.MEDIUM,
            default_enabled=False,
            setup_hint="Set REDDIT_ENABLED=true and configure Reddit OAuth/user-agent for official read-only API access.",
            access_policy=official_api_policy(api_name="Reddit Data API", auth_required=True),
            rate_limit_policy=default_rate_limit_policy(
                requests_per_minute=60,
                notes="Respect Reddit API rate-limit headers; no unauthenticated or web-scraping fallback.",
            ),
            retention_policy=default_retention_policy(cache_ttl_seconds=86400),
            status=reddit_status,
            notes=("Read-only only; posting, commenting, voting, DMs, and moderation are absent.",),
        ),
        ForumProvider(
            provider_id="v2ex",
            name="V2EX",
            regions=("China-adjacent", "global"),
            languages=("zh", "en"),
            source_type="documented_api",
            official_api_available=True,
            auth_required=False,
            read_capabilities=("v2ex.nodes.get", "v2ex.node_topics", "v2ex.topic.get", "v2ex.topic_replies", "v2ex.latest", "v2ex.hot"),
            write_capabilities=(),
            risk_level=RiskLevel.MEDIUM,
            default_enabled=False,
            setup_hint="Set V2EX_ENABLED=true for documented read-only V2EX API access. V2EX_TOKEN is optional and redacted.",
            access_policy={
                **official_api_policy(api_name="V2EX documented API", auth_required=False),
                "member_profile_reads_allowed": False,
                "notifications_allowed": False,
                "web_scraping_fallback_allowed": False,
            },
            rate_limit_policy=default_rate_limit_policy(requests_per_minute=10, notes="V2EX documents a 600 requests/hour limit; local limiter defaults to 600/hour."),
            retention_policy=default_retention_policy(cache_ttl_seconds=86400),
            status=ForumProviderStatus.CONFIGURED if v2ex_enabled else ForumProviderStatus.DISABLED,
            notes=("Read-only only; member profile, notification, posting, and modifying endpoints are absent.",),
        ),
        _stubbed_provider("hackernews", "Hacker News", ("global",), ("en",), True, "Public API candidate; connector deferred."),
        _stubbed_provider("stackexchange", "Stack Exchange", ("global",), ("multi",), True, "Official API candidate; connector deferred."),
        _stubbed_provider("lemmy", "Lemmy", ("global",), ("multi",), True, "Federated public API candidate; instance policy needed."),
    ]
    providers.extend(
        _discovery_provider(provider_id, name, regions, languages)
        for provider_id, name, regions, languages in (
            ("zhihu", "Zhihu", ("China",), ("zh",)),
            ("baidu_tieba", "Baidu Tieba", ("China",), ("zh",)),
            ("douban_groups", "Douban Groups", ("China",), ("zh",)),
            ("xiaohongshu", "Xiaohongshu", ("China",), ("zh",)),
            ("weibo", "Weibo", ("China",), ("zh",)),
            ("nga", "NGA", ("China",), ("zh",)),
        )
    )
    return providers


def _stubbed_provider(
    provider_id: str,
    name: str,
    regions: tuple[str, ...],
    languages: tuple[str, ...],
    official_api_available: bool,
    hint: str,
) -> ForumProvider:
    return ForumProvider(
        provider_id=provider_id,
        name=name,
        regions=regions,
        languages=languages,
        source_type="stubbed_official_api",
        official_api_available=official_api_available,
        auth_required=False,
        read_capabilities=(f"{provider_id}.status",),
        write_capabilities=(),
        risk_level=RiskLevel.MEDIUM,
        default_enabled=False,
        setup_hint=hint,
        access_policy=stub_policy(reason="connector_deferred", official_api_available=official_api_available),
        rate_limit_policy=default_rate_limit_policy(notes="Rate policy must be defined before implementation."),
        retention_policy=default_retention_policy(cache_ttl_seconds=None),
        status=ForumProviderStatus.STUBBED,
        notes=("Read-only metadata stub; no provider call is made by registry/status commands.",),
    )


def _discovery_provider(
    provider_id: str,
    name: str,
    regions: tuple[str, ...],
    languages: tuple[str, ...],
) -> ForumProvider:
    return ForumProvider(
        provider_id=provider_id,
        name=name,
        regions=regions,
        languages=languages,
        source_type="discovery_only_search",
        official_api_available=False,
        auth_required=True,
        read_capabilities=("forum.discovery.search", "web.fetch_url.selected_public"),
        write_capabilities=(),
        risk_level=RiskLevel.MEDIUM,
        default_enabled=False,
        setup_hint=(
            "Discovery-only: use approved search-provider site filters and selected public URL fetch where allowed; "
            "login, cookies, CAPTCHA, anti-bot bypass, and scraping are forbidden."
        ),
        access_policy=discovery_only_policy(provider_id),
        rate_limit_policy=default_rate_limit_policy(notes="Provider status performs no network calls."),
        retention_policy=default_retention_policy(cache_ttl_seconds=86400),
        status=ForumProviderStatus.DISCOVERY_ONLY,
        notes=("Search result discovery only; blocked/login/CAPTCHA pages must be reported unavailable.",),
    )


def _registry_warnings(providers: list[ForumProvider]) -> list[str]:
    warnings: list[str] = []
    if any(provider.write_capabilities for provider in providers):
        warnings.append("One or more forum providers unexpectedly declares write capabilities.")
    if not any(provider.provider_id == "reddit" and provider.status is ForumProviderStatus.CONFIGURED for provider in providers):
        warnings.append("Reddit is not fully configured/enabled; official API workflows will return setup guidance.")
    warnings.append("Chinese discovery-only providers are not scrapers; they require approved search site filters or public URL fetch.")
    return warnings
