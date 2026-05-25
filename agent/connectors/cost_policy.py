from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

from agent.safety.audit import AuditEvent, AuditLogger
from agent.safety.policy import PolicyDecision, RiskLevel
from agent.safety.redaction import SecretRedactor
from agent.safety.trust import TrustLevel


class ProviderCostMode(str, Enum):
    FREE_FIRST = "free_first"
    BALANCED = "balanced"
    QUALITY_FIRST = "quality_first"
    MANUAL = "manual"


class ProviderDecisionStatus(str, Enum):
    SELECTED = "selected"
    UNAVAILABLE = "unavailable"


WEB_PROVIDER_ORDER = (
    "cache",
    "url",
    "feed",
    "sitemap",
    "official_api",
    "searxng",
    "brave",
    "serpapi",
)
DEFAULT_SEARCH_ALLOWED_PROVIDERS = WEB_PROVIDER_ORDER
PROVIDER_ALIASES = {
    "local_cache": "cache",
    "direct_url": "url",
    "rss": "feed",
    "rss_atom": "feed",
    "atom": "feed",
}

WEATHER_PROVIDER_ORDER = (
    "open_meteo",
    "nws",
    "weatherapi",
)

COMMUNICATION_PROVIDER_ORDER = (
    "local_drafts",
    "handoff",
    "gmail_doctor",
    "telegram_doctor",
    "draft_only",
    "approved_send",
)

DOMAIN_PROVIDER_ORDER = {
    "web": WEB_PROVIDER_ORDER,
    "search": WEB_PROVIDER_ORDER,
    "weather": WEATHER_PROVIDER_ORDER,
    "personal_communications": COMMUNICATION_PROVIDER_ORDER,
}


@dataclass(frozen=True)
class ProviderCostConfig:
    cost_mode: ProviderCostMode = ProviderCostMode.FREE_FIRST
    allow_paid_apis: bool = False
    max_paid_api_calls_per_day: int = 0
    search_default_provider: str = "auto"
    search_allowed_providers: tuple[str, ...] = DEFAULT_SEARCH_ALLOWED_PROVIDERS
    search_store_history: bool = False
    search_cache_enabled: bool = True
    search_cache_ttl_seconds: int = 86400
    weather_default_provider: str = "auto"

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "ProviderCostConfig":
        source = env or os.environ
        mode = _enum_value(
            source.get("PROVIDER_COST_MODE", cls.cost_mode.value),
            ProviderCostMode,
            default=cls.cost_mode,
        )
        return cls(
            cost_mode=mode,
            allow_paid_apis=_bool(source.get("ALLOW_PAID_APIS"), default=cls.allow_paid_apis),
            max_paid_api_calls_per_day=_int(
                source.get("MAX_PAID_API_CALLS_PER_DAY"),
                default=cls.max_paid_api_calls_per_day,
            ),
            search_default_provider=_normalize_provider_name(source.get("SEARCH_DEFAULT_PROVIDER") or "auto") or "auto",
            search_allowed_providers=_parse_provider_list(
                source.get("SEARCH_ALLOWED_PROVIDERS"),
                default=DEFAULT_SEARCH_ALLOWED_PROVIDERS,
            ),
            search_store_history=_bool(source.get("SEARCH_STORE_HISTORY"), default=cls.search_store_history),
            search_cache_enabled=_bool(source.get("SEARCH_CACHE_ENABLED"), default=cls.search_cache_enabled),
            search_cache_ttl_seconds=_int(
                source.get("SEARCH_CACHE_TTL_SECONDS"),
                default=cls.search_cache_ttl_seconds,
            ),
            weather_default_provider=(source.get("WEATHER_DEFAULT_PROVIDER") or "auto").strip().casefold(),
        )

    def default_for_domain(self, domain: str) -> str:
        normalized = domain.strip().casefold()
        if normalized in {"web", "search"}:
            return self.search_default_provider
        if normalized == "weather":
            return self.weather_default_provider
        return "auto"


@dataclass(frozen=True)
class ProviderCandidate:
    name: str
    domain: str
    configured: bool
    setup_hint: str
    no_key_required: bool = False
    official: bool = False
    local: bool = False
    cached: bool = False
    user_provided: bool = False
    paid_api: bool = False
    quota_limited: bool = False
    supports_requested_action: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def requires_paid_opt_in(self) -> bool:
        return self.paid_api or self.quota_limited


@dataclass(frozen=True)
class ProviderDecision:
    status: ProviderDecisionStatus
    domain: str
    selected_provider: str | None
    configured: bool
    reason: str
    setup_hint: str
    explicit_provider: str | None
    cost_mode: str
    skipped_providers: list[dict[str, Any]]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        provider_metadata = self.metadata.get("provider") if isinstance(self.metadata, dict) else None
        paid_api_used = bool(provider_metadata.get("paid_api") or provider_metadata.get("quota_limited")) if isinstance(provider_metadata, dict) else False
        cache_used = self.selected_provider in {"cache", "local_cache"}
        skip_reasons = {
            str(item.get("provider")): str(item.get("reason", ""))
            for item in self.skipped_providers
            if item.get("provider")
        }
        audit_summary = (
            f"provider_decision domain={self.domain} selected={self.selected_provider or 'unavailable'} "
            f"cost_mode={self.cost_mode} paid_api_used={str(paid_api_used).lower()} "
            f"cache_used={str(cache_used).lower()}"
        )
        return {
            "status": self.status.value,
            "domain": self.domain,
            "selected_provider": self.selected_provider,
            "skipped_providers": self.skipped_providers,
            "skip_reasons": skip_reasons,
            "configured": self.configured,
            "reason": self.reason,
            "setup_hint": self.setup_hint,
            "explicit_provider": self.explicit_provider,
            "cost_mode": self.cost_mode,
            "paid_api_used": paid_api_used,
            "cache_used": cache_used,
            "audit_summary": audit_summary,
            "metadata": SecretRedactor().redact(self.metadata),
        }


def select_provider(
    domain: str,
    candidates: Sequence[ProviderCandidate],
    *,
    config: ProviderCostConfig | None = None,
    explicit_provider: str | None = None,
) -> ProviderDecision:
    active_config = config or ProviderCostConfig.from_env()
    normalized_domain = domain.strip().casefold()
    normalized_explicit = _normalize_provider_name(explicit_provider)
    configured_default = _normalize_provider_name(active_config.default_for_domain(normalized_domain))
    requested = normalized_explicit or (configured_default if configured_default != "auto" else None)
    by_name = {_normalize_provider_name(candidate.name): candidate for candidate in candidates}

    if requested:
        candidate = by_name.get(requested)
        if candidate is None:
            return _unavailable(
                normalized_domain,
                active_config,
                normalized_explicit,
                f"requested provider '{requested}' is not supported",
                f"Choose one of: {', '.join(sorted(by_name)) or 'none configured'}.",
                [],
            )
        if not candidate.configured:
            reason = _not_available_reason(candidate)
            return _unavailable(
                normalized_domain,
                active_config,
                normalized_explicit,
                reason,
                candidate.setup_hint,
                [_skip(candidate, reason)],
            )
        allowed, skipped_reason = _candidate_allowed(candidate, active_config, explicit=bool(normalized_explicit))
        if candidate.configured and allowed and candidate.supports_requested_action:
            return _selected(
                normalized_domain,
                candidate,
                active_config,
                normalized_explicit,
                "explicit provider selected" if normalized_explicit else "configured default provider selected",
                [],
            )
        skipped = [_skip(candidate, skipped_reason or _not_available_reason(candidate))]
        return _unavailable(
            normalized_domain,
            active_config,
            normalized_explicit,
            skipped[0]["reason"],
            candidate.setup_hint,
            skipped,
        )

    skipped: list[dict[str, Any]] = []
    for candidate in sorted(candidates, key=lambda item: _rank(normalized_domain, item, active_config)):
        allowed, skipped_reason = _candidate_allowed(candidate, active_config, explicit=False)
        if candidate.configured and allowed and candidate.supports_requested_action:
            return _selected(
                normalized_domain,
                candidate,
                active_config,
                normalized_explicit,
                _selection_reason(candidate, active_config),
                skipped,
            )
        skipped.append(_skip(candidate, skipped_reason or _not_available_reason(candidate)))

    hint = _first_setup_hint(candidates) or "No configured provider is available for this request."
    return _unavailable(
        normalized_domain,
        active_config,
        normalized_explicit,
        "no configured provider is available under the current cost policy",
        hint,
        skipped,
    )


def audit_provider_decision(
    audit_logger: AuditLogger,
    decision: ProviderDecision,
    *,
    request_id: str,
    session_id: str = "provider-policy",
    route: str = "provider_selection",
    model: str = "none",
) -> dict[str, Any]:
    payload = decision.to_dict()
    return audit_logger.log(
        AuditEvent(
            session_id=session_id,
            request_id=request_id,
            route=route,
            model=model,
            tool_name="provider.select",
            capability=f"{decision.domain}.provider_select",
            risk_level=RiskLevel.SAFE.value,
            trust_level=TrustLevel.MODEL_OUTPUT.value,
            policy_decision=PolicyDecision.ALLOW.value,
            sanitized_args={
                "domain": decision.domain,
                "explicit_provider": decision.explicit_provider,
                "cost_mode": decision.cost_mode,
            },
            result_summary=payload["reason"],
            network_domains=[],
            dry_run=True,
        )
    )


def web_provider_candidates(env: Mapping[str, str] | None = None) -> list[ProviderCandidate]:
    source = env or os.environ
    brave_key = bool((source.get("BRAVE_SEARCH_API_KEY") or "").strip())
    serp_key = bool((source.get("SERPAPI_API_KEY") or "").strip())
    searxng_url = bool((source.get("SEARXNG_BASE_URL") or "").strip())
    config = ProviderCostConfig.from_env(source)
    return [
        ProviderCandidate(
            "cache",
            "web",
            False,
            "Enable SEARCH_CACHE_ENABLED=true and populate the local cache before search.",
            local=True,
            cached=True,
            no_key_required=True,
            metadata={"enabled": config.search_cache_enabled, "ttl_seconds": config.search_cache_ttl_seconds},
        ),
        ProviderCandidate(
            "url",
            "web",
            False,
            "Provide a public URL to fetch directly.",
            no_key_required=True,
            user_provided=True,
        ),
        ProviderCandidate("feed", "web", False, "Provide RSS/Atom feeds for the target source.", no_key_required=True),
        ProviderCandidate("sitemap", "web", False, "Use a direct site sitemap when available."),
        ProviderCandidate("official_api", "web", False, "Configure an official source API for this site."),
        ProviderCandidate(
            "searxng",
            "web",
            searxng_url,
            "Set SEARXNG_BASE_URL for self-hosted search.",
            local=True,
            user_provided=True,
        ),
        ProviderCandidate(
            "brave",
            "web",
            brave_key,
            "Set BRAVE_SEARCH_API_KEY, BRAVE_SEARCH_ENABLED=true, ALLOW_PAID_APIS=true, and MAX_PAID_API_CALLS_PER_DAY>0.",
            user_provided=True,
            paid_api=True,
            quota_limited=True,
        ),
        ProviderCandidate(
            "serpapi",
            "web",
            serp_key,
            "Set SERPAPI_API_KEY, SERPAPI_ENABLED=true, ALLOW_PAID_APIS=true, and MAX_PAID_API_CALLS_PER_DAY>0 before using SerpAPI.",
            user_provided=True,
            paid_api=True,
            quota_limited=True,
        ),
    ]


def weather_provider_candidates(env: Mapping[str, str] | None = None) -> list[ProviderCandidate]:
    source = env or os.environ
    weather_api_key = bool((source.get("WEATHER_API_KEY") or source.get("WEATHERAPI_API_KEY") or "").strip())
    return [
        ProviderCandidate(
            "open_meteo",
            "weather",
            True,
            "Open-Meteo is the default no-key weather provider.",
            no_key_required=True,
        ),
        ProviderCandidate(
            "nws",
            "weather",
            True,
            "NOAA/NWS is available for U.S. official weather data.",
            no_key_required=True,
            official=True,
        ),
        ProviderCandidate(
            "weatherapi",
            "weather",
            weather_api_key,
            "Set WEATHER_API_KEY and explicitly select WeatherAPI, or allow paid APIs if making it a default.",
            user_provided=True,
            paid_api=True,
            quota_limited=True,
        ),
    ]


def _candidate_allowed(
    candidate: ProviderCandidate,
    config: ProviderCostConfig,
    *,
    explicit: bool,
) -> tuple[bool, str | None]:
    if not candidate.supports_requested_action:
        return False, f"{candidate.name} does not support the requested action"
    if candidate.domain in {"web", "search"} and _normalize_provider_name(candidate.name) not in config.search_allowed_providers:
        return False, f"{candidate.name} skipped because it is not in SEARCH_ALLOWED_PROVIDERS"
    if candidate.requires_paid_opt_in and not explicit:
        if not config.allow_paid_apis:
            return False, f"{candidate.name} skipped because ALLOW_PAID_APIS=false"
        if config.max_paid_api_calls_per_day <= 0:
            return False, f"{candidate.name} skipped because MAX_PAID_API_CALLS_PER_DAY=0"
    if candidate.name in {"brave", "serpapi"} and explicit:
        if not config.allow_paid_apis:
            return False, f"{candidate.name} requires ALLOW_PAID_APIS=true"
        if config.max_paid_api_calls_per_day <= 0:
            return False, f"{candidate.name} requires MAX_PAID_API_CALLS_PER_DAY>0"
    if candidate.paid_api and explicit and not config.allow_paid_apis and candidate.name != "weatherapi":
        return False, f"{candidate.name} requires ALLOW_PAID_APIS=true"
    return True, None


def _rank(domain: str, candidate: ProviderCandidate, config: ProviderCostConfig) -> tuple[int, int, int, str]:
    order = DOMAIN_PROVIDER_ORDER.get(domain, ())
    try:
        base_rank = order.index(candidate.name)
    except ValueError:
        base_rank = len(order) + 10
    if config.cost_mode == ProviderCostMode.QUALITY_FIRST:
        quality_bonus = 0 if candidate.official else 1
    elif config.cost_mode == ProviderCostMode.BALANCED:
        quality_bonus = 0 if candidate.official or candidate.no_key_required else 1
    else:
        quality_bonus = 0
    cost_penalty = 1 if candidate.requires_paid_opt_in else 0
    return (cost_penalty, base_rank, quality_bonus, candidate.name)


def _selected(
    domain: str,
    candidate: ProviderCandidate,
    config: ProviderCostConfig,
    explicit_provider: str | None,
    reason: str,
    skipped: list[dict[str, Any]],
) -> ProviderDecision:
    return ProviderDecision(
        status=ProviderDecisionStatus.SELECTED,
        domain=domain,
        selected_provider=candidate.name,
        configured=True,
        reason=reason,
        setup_hint=candidate.setup_hint,
        explicit_provider=explicit_provider,
        cost_mode=config.cost_mode.value,
        skipped_providers=skipped,
        metadata={
            "provider": {
                "name": candidate.name,
                "no_key_required": candidate.no_key_required,
                "official": candidate.official,
                "local": candidate.local,
                "cached": candidate.cached,
                "user_provided": candidate.user_provided,
                "paid_api": candidate.paid_api,
                "quota_limited": candidate.quota_limited,
            },
        },
    )


def _unavailable(
    domain: str,
    config: ProviderCostConfig,
    explicit_provider: str | None,
    reason: str,
    setup_hint: str,
    skipped: list[dict[str, Any]],
) -> ProviderDecision:
    return ProviderDecision(
        status=ProviderDecisionStatus.UNAVAILABLE,
        domain=domain,
        selected_provider=None,
        configured=False,
        reason=reason,
        setup_hint=setup_hint,
        explicit_provider=explicit_provider,
        cost_mode=config.cost_mode.value,
        skipped_providers=skipped,
    )


def _skip(candidate: ProviderCandidate, reason: str) -> dict[str, Any]:
    return {
        "provider": candidate.name,
        "configured": candidate.configured,
        "reason": reason,
        "setup_hint": candidate.setup_hint,
    }


def _not_available_reason(candidate: ProviderCandidate) -> str:
    if not candidate.configured:
        return f"{candidate.name} is not configured"
    return f"{candidate.name} is not available"


def _first_setup_hint(candidates: Sequence[ProviderCandidate]) -> str:
    for candidate in candidates:
        if candidate.setup_hint:
            return candidate.setup_hint
    return ""


def _selection_reason(candidate: ProviderCandidate, config: ProviderCostConfig) -> str:
    labels = []
    if candidate.cached:
        labels.append("cached")
    if candidate.local:
        labels.append("local")
    if candidate.no_key_required:
        labels.append("no-key")
    if candidate.official:
        labels.append("official")
    if candidate.user_provided:
        labels.append("user-configured")
    if not labels:
        labels.append("configured")
    return f"{config.cost_mode.value} selected {candidate.name} ({', '.join(labels)})"


def _normalize_provider_name(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().casefold().replace("-", "_")
    normalized = PROVIDER_ALIASES.get(normalized, normalized)
    return normalized or None


def _parse_provider_list(value: str | None, *, default: Sequence[str]) -> tuple[str, ...]:
    if value is None or not value.strip():
        return tuple(_normalize_provider_name(item) or item for item in default)
    providers = []
    for item in value.split(","):
        normalized = _normalize_provider_name(item)
        if normalized and normalized not in providers:
            providers.append(normalized)
    return tuple(providers)


def _bool(value: str | None, *, default: bool) -> bool:
    if value is None or value == "":
        return default
    return value.strip().casefold() in {"1", "true", "yes", "on"}


def _int(value: str | None, *, default: int) -> int:
    if value is None or value == "":
        return default
    try:
        return max(0, int(value))
    except ValueError:
        return default


def _enum_value(value: str, enum_type: type[ProviderCostMode], *, default: ProviderCostMode) -> ProviderCostMode:
    normalized = value.strip().casefold()
    for member in enum_type:
        if member.value == normalized:
            return member
    return default
