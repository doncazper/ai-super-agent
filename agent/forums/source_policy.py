from __future__ import annotations

from typing import Any


DISCOVERY_SITE_FILTERS: dict[str, str] = {
    "zhihu": "site:zhihu.com",
    "baidu_tieba": "site:tieba.baidu.com",
    "douban_groups": "site:douban.com/group",
    "xiaohongshu": "site:xiaohongshu.com",
    "weibo": "site:weibo.com",
    "nga": "site:bbs.nga.cn",
    "v2ex": "site:v2ex.com",
}

DISCOVERY_ONLY_PROVIDER_IDS = frozenset(
    {"zhihu", "baidu_tieba", "douban_groups", "xiaohongshu", "weibo", "nga"}
)

NO_PERSONAL_READ_FLAGS = {
    "status_reads_personal_data": False,
    "status_uses_login": False,
    "status_uses_cookies": False,
    "logged_in_reads_allowed": False,
    "private_page_reads_allowed": False,
    "scraping_allowed": False,
    "captcha_or_antibot_bypass_allowed": False,
}


def is_discovery_only(provider_id: str) -> bool:
    return provider_id in DISCOVERY_ONLY_PROVIDER_IDS


def discovery_site_filter(provider_id: str) -> str | None:
    return DISCOVERY_SITE_FILTERS.get(provider_id)


def official_api_policy(*, api_name: str, auth_required: bool) -> dict[str, Any]:
    return {
        **NO_PERSONAL_READ_FLAGS,
        "discovery_method": "official_api",
        "api_name": api_name,
        "auth_required": auth_required,
        "web_scraping_fallback_allowed": False,
        "write_actions_allowed": False,
        "network_call_performed_by_status": False,
    }


def stub_policy(*, reason: str, official_api_available: bool) -> dict[str, Any]:
    return {
        **NO_PERSONAL_READ_FLAGS,
        "discovery_method": "stubbed",
        "stub_reason": reason,
        "official_api_available": official_api_available,
        "write_actions_allowed": False,
        "network_call_performed_by_status": False,
    }


def discovery_only_policy(provider_id: str) -> dict[str, Any]:
    return {
        **NO_PERSONAL_READ_FLAGS,
        "discovery_method": "approved_search_site_filter",
        "site_filter": discovery_site_filter(provider_id),
        "direct_fetch_policy": "public_selected_url_only_where_allowed",
        "blocked_or_login_required_behavior": "report_unavailable",
        "write_actions_allowed": False,
        "network_call_performed_by_status": False,
    }


def default_retention_policy(*, cache_ttl_seconds: int | None = None) -> dict[str, Any]:
    return {
        "stores_user_content_by_default": False,
        "stores_author_metadata_by_default": False,
        "stores_query_history_by_default": False,
        "cache_ttl_seconds": cache_ttl_seconds,
        "deleted_removed_content_retained": False,
    }


def default_rate_limit_policy(*, requests_per_minute: int | None = None, notes: str = "") -> dict[str, Any]:
    return {
        "requests_per_minute": requests_per_minute,
        "respect_provider_headers": True,
        "network_call_performed_by_status": False,
        "notes": notes,
    }
