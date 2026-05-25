from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


REDDIT_READ_CAPABILITIES = frozenset(
    {
        "reddit.status",
        "reddit.auth_check",
        "reddit.search_posts",
        "reddit.search_subreddit",
        "reddit.fetch_post",
        "reddit.fetch_comments",
        "reddit.fetch_thread",
        "reddit.fetch_subreddit_info",
        "reddit.explain_result",
        "reddit.thread_export",
        "reddit.summarize_thread",
        "reddit.summarize_search",
        "reddit.consensus",
        "reddit.pros_cons",
        "reddit.complaints",
        "reddit.buying_advice",
        "reddit.cache_status",
        "reddit.cache_clear",
        "reddit.retention_status",
        "reddit.retention_sweep",
        "reddit.privacy_report",
    }
)

REDDIT_FORBIDDEN_WRITE_CAPABILITIES = frozenset(
    {
        "reddit.post",
        "reddit.comment",
        "reddit.vote",
        "reddit.dm",
        "reddit.moderate",
    }
)

REDDIT_REQUIRED_OAUTH_ENV = (
    "REDDIT_CLIENT_ID",
    "REDDIT_CLIENT_SECRET",
    "REDDIT_USER_AGENT",
)


def _env_bool(env: Mapping[str, str], key: str, default: bool) -> bool:
    value = env.get(key)
    if value is None or value == "":
        return default
    return value.strip().casefold() in {"1", "true", "yes", "on"}


def _env_int(env: Mapping[str, str], key: str, default: int, *, minimum: int = 0) -> int:
    value = env.get(key)
    if value is None or value == "":
        return default
    try:
        parsed = int(value)
    except ValueError:
        return default
    return max(parsed, minimum)


@dataclass(frozen=True)
class RedditPolicyConfig:
    enabled: bool
    client_id_configured: bool
    client_secret_configured: bool
    user_agent_configured: bool
    refresh_token_configured: bool
    access_token_configured: bool
    cache_enabled: bool
    cache_ttl_seconds: int
    delete_user_content_after_seconds: int
    max_requests_per_minute: int
    allow_web_fallback: bool
    web_fallback_env_requested: bool
    store_author_metadata: bool
    use_for_training: bool
    use_for_training_env_requested: bool
    trust_level: str = "UNTRUSTED_WEB"
    oauth_required: bool = True
    unauthenticated_mode_allowed: bool = False
    read_only: bool = True

    @property
    def token_configured(self) -> bool:
        return self.refresh_token_configured or self.access_token_configured

    @property
    def configured(self) -> bool:
        return (
            self.enabled
            and self.client_id_configured
            and self.client_secret_configured
            and self.user_agent_configured
            and self.token_configured
        )

    @property
    def missing_oauth_env(self) -> list[str]:
        missing: list[str] = []
        if not self.client_id_configured:
            missing.append("REDDIT_CLIENT_ID")
        if not self.client_secret_configured:
            missing.append("REDDIT_CLIENT_SECRET")
        if not self.user_agent_configured:
            missing.append("REDDIT_USER_AGENT")
        if not self.token_configured:
            missing.append("REDDIT_REFRESH_TOKEN or REDDIT_ACCESS_TOKEN")
        return missing

    def public_status(self) -> dict[str, object]:
        if not self.enabled:
            status = "disabled"
        elif not self.configured:
            status = "requires_setup"
        else:
            status = "configured_scaffold_only"
        return {
            "provider": "reddit",
            "status": status,
            "enabled": self.enabled,
            "configured": self.configured,
            "oauth_required": self.oauth_required,
            "unauthenticated_mode_allowed": self.unauthenticated_mode_allowed,
            "client_id_configured": self.client_id_configured,
            "client_secret_configured": self.client_secret_configured,
            "user_agent_configured": self.user_agent_configured,
            "token_configured": self.token_configured,
            "missing_oauth_env": self.missing_oauth_env,
            "cache_enabled": self.cache_enabled,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "delete_user_content_after_seconds": self.delete_user_content_after_seconds,
            "max_requests_per_minute": self.max_requests_per_minute,
            "allow_web_fallback": self.allow_web_fallback,
            "web_fallback_env_requested": self.web_fallback_env_requested,
            "store_author_metadata": self.store_author_metadata,
            "use_for_training": self.use_for_training,
            "use_for_training_env_requested": self.use_for_training_env_requested,
            "trust_level": self.trust_level,
            "read_only": self.read_only,
            "write_capabilities_allowed": False,
        }


def load_reddit_policy_config(
    environ: Mapping[str, str] | None = None,
) -> RedditPolicyConfig:
    env = environ or os.environ
    web_fallback_requested = _env_bool(env, "REDDIT_ALLOW_WEB_FALLBACK", False)
    use_for_training_requested = _env_bool(env, "REDDIT_USE_FOR_TRAINING", False)
    return RedditPolicyConfig(
        enabled=_env_bool(env, "REDDIT_ENABLED", False),
        client_id_configured=bool(env.get("REDDIT_CLIENT_ID")),
        client_secret_configured=bool(env.get("REDDIT_CLIENT_SECRET")),
        user_agent_configured=bool(env.get("REDDIT_USER_AGENT")),
        refresh_token_configured=bool(env.get("REDDIT_REFRESH_TOKEN")),
        access_token_configured=bool(env.get("REDDIT_ACCESS_TOKEN")),
        cache_enabled=_env_bool(env, "REDDIT_CACHE_ENABLED", True),
        cache_ttl_seconds=_env_int(env, "REDDIT_CACHE_TTL_SECONDS", 86400, minimum=0),
        delete_user_content_after_seconds=_env_int(
            env,
            "REDDIT_DELETE_USER_CONTENT_AFTER_SECONDS",
            172800,
            minimum=0,
        ),
        max_requests_per_minute=_env_int(env, "REDDIT_MAX_REQUESTS_PER_MINUTE", 60, minimum=1),
        allow_web_fallback=False,
        web_fallback_env_requested=web_fallback_requested,
        store_author_metadata=_env_bool(env, "REDDIT_STORE_AUTHOR_METADATA", False),
        use_for_training=False,
        use_for_training_env_requested=use_for_training_requested,
    )


def reddit_setup_hint(config: RedditPolicyConfig | None = None) -> str:
    policy = config or load_reddit_policy_config()
    if not policy.enabled:
        return (
            "Reddit connector is disabled. Set REDDIT_ENABLED=true only after OAuth "
            "credentials, a specific REDDIT_USER_AGENT, and retention/rate-limit policy "
            "are configured."
        )
    if not policy.configured:
        return (
            "Reddit OAuth setup is incomplete. Configure "
            f"{', '.join(policy.missing_oauth_env)}. Unauthenticated Reddit access and "
            "Reddit web scraping fallback are not allowed."
        )
    return (
        "Reddit policy config is present, but this milestone is scaffold-only: live API "
        "calls remain unavailable until a read-only connector is implemented through "
        "ToolBroker, PolicyEngine, and AuditLogger."
    )


def reddit_compliance_status(
    environ: Mapping[str, str] | None = None,
) -> dict[str, object]:
    config = load_reddit_policy_config(environ)
    status = config.public_status()
    status["setup_hint"] = reddit_setup_hint(config)
    status["declared_read_capabilities"] = sorted(REDDIT_READ_CAPABILITIES)
    status["forbidden_write_capabilities"] = sorted(REDDIT_FORBIDDEN_WRITE_CAPABILITIES)
    status["content_trust_level"] = "UNTRUSTED_WEB"
    status["deleted_removed_content_retained"] = False
    status["permanent_user_content_storage_default"] = False
    status["model_training_allowed"] = False
    return status


def is_reddit_capability_allowed(
    capability_id: str,
    config: RedditPolicyConfig | None = None,
) -> bool:
    policy = config or load_reddit_policy_config()
    if capability_id in REDDIT_FORBIDDEN_WRITE_CAPABILITIES:
        return False
    if capability_id not in REDDIT_READ_CAPABILITIES:
        return False
    if not policy.configured:
        return False
    return True
