from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any, Mapping
from urllib.parse import quote

import httpx

from agent.forums.v2ex.errors import V2EXApiError, V2EXRateLimitError, V2EXSetupError


V2EX_WEB_DOMAIN = "www.v2ex.com"
V2EX_API_BASE = "https://www.v2ex.com/api"
V2EX_API_V2_BASE = "https://www.v2ex.com/api/v2"


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
        return max(int(value), minimum)
    except ValueError:
        return default


@dataclass(frozen=True)
class V2EXConfig:
    enabled: bool
    token_configured: bool
    timeout_seconds: float
    max_requests_per_hour: int
    cache_enabled: bool
    cache_ttl_seconds: int
    trust_level: str = "UNTRUSTED_WEB"
    read_only: bool = True

    @property
    def configured(self) -> bool:
        return self.enabled

    def public_status(self) -> dict[str, Any]:
        return {
            "provider": "v2ex",
            "status": "configured" if self.configured else "disabled",
            "enabled": self.enabled,
            "configured": self.configured,
            "token_configured": self.token_configured,
            "timeout_seconds": self.timeout_seconds,
            "max_requests_per_hour": self.max_requests_per_hour,
            "cache_enabled": self.cache_enabled,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "read_only": self.read_only,
            "trust_level": self.trust_level,
            "member_profile_access_enabled": False,
            "notification_access_enabled": False,
            "write_capabilities_allowed": False,
        }


def load_v2ex_config(environ: Mapping[str, str] | None = None) -> V2EXConfig:
    env = environ or os.environ
    return V2EXConfig(
        enabled=_env_bool(env, "V2EX_ENABLED", False),
        token_configured=bool((env.get("V2EX_TOKEN") or "").strip()),
        timeout_seconds=float(_env_int(env, "V2EX_TIMEOUT_SECONDS", 10, minimum=1)),
        max_requests_per_hour=_env_int(env, "V2EX_MAX_REQUESTS_PER_HOUR", 600, minimum=1),
        cache_enabled=_env_bool(env, "V2EX_CACHE_ENABLED", True),
        cache_ttl_seconds=_env_int(env, "V2EX_CACHE_TTL_SECONDS", 86400, minimum=0),
    )


def v2ex_setup_hint(config: V2EXConfig | None = None) -> str:
    cfg = config or load_v2ex_config()
    if not cfg.enabled:
        return (
            "V2EX connector is disabled. Set V2EX_ENABLED=true to use read-only documented API endpoints. "
            "V2EX_TOKEN is optional and is never printed."
        )
    return "V2EX read-only connector is enabled. Token-backed API 2.0 endpoints are used only when V2EX_TOKEN is configured."


@dataclass(frozen=True)
class V2EXRateLimitStatus:
    limit: int | None = None
    remaining: int | None = None
    reset: int | None = None
    local_used: int = 0
    local_limit: int = 600
    exceeded: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "limit": self.limit,
            "remaining": self.remaining,
            "reset": self.reset,
            "local_used": self.local_used,
            "local_limit": self.local_limit,
            "exceeded": self.exceeded,
            "headers_respected": True,
        }


@dataclass(frozen=True)
class V2EXApiResponse:
    payload: Any
    status_code: int
    endpoint: str
    endpoint_family: str
    network_domains: list[str]
    rate_limit: V2EXRateLimitStatus = field(default_factory=V2EXRateLimitStatus)


class V2EXLocalRateLimiter:
    def __init__(self, *, max_requests_per_hour: int = 600) -> None:
        self.max_requests_per_hour = max(1, int(max_requests_per_hour))
        self._timestamps: list[float] = []

    def check(self) -> V2EXRateLimitStatus:
        now = time.time()
        cutoff = now - 3600
        self._timestamps = [timestamp for timestamp in self._timestamps if timestamp > cutoff]
        if len(self._timestamps) >= self.max_requests_per_hour:
            return V2EXRateLimitStatus(
                local_used=len(self._timestamps),
                local_limit=self.max_requests_per_hour,
                exceeded=True,
            )
        self._timestamps.append(now)
        return V2EXRateLimitStatus(
            local_used=len(self._timestamps),
            local_limit=self.max_requests_per_hour,
            exceeded=False,
        )


class V2EXApiClient:
    def __init__(
        self,
        *,
        config: V2EXConfig | None = None,
        env: Mapping[str, str] | None = None,
        transport: httpx.BaseTransport | None = None,
        timeout_seconds: float | None = None,
        api_base: str = V2EX_API_BASE,
        api_v2_base: str = V2EX_API_V2_BASE,
        rate_limiter: V2EXLocalRateLimiter | None = None,
    ) -> None:
        self.env = env or os.environ
        self.config = config or load_v2ex_config(self.env)
        self.transport = transport
        self.timeout_seconds = timeout_seconds or self.config.timeout_seconds
        self.api_base = api_base.rstrip("/")
        self.api_v2_base = api_v2_base.rstrip("/")
        self.rate_limiter = rate_limiter or V2EXLocalRateLimiter(max_requests_per_hour=self.config.max_requests_per_hour)

    @classmethod
    def from_env(cls, *, env: Mapping[str, str] | None = None, transport: httpx.BaseTransport | None = None) -> "V2EXApiClient":
        env_map = env or os.environ
        return cls(config=load_v2ex_config(env_map), env=env_map, transport=transport)

    def ensure_configured(self) -> None:
        if not self.config.configured:
            raise V2EXSetupError(v2ex_setup_hint(self.config))

    def nodes(self) -> V2EXApiResponse:
        return self._get_legacy("/nodes/all.json")

    def node_topics(self, node_name: str, *, page: int = 1) -> V2EXApiResponse:
        node = _clean_node_name(node_name)
        if self._token:
            return self._get_v2(f"/nodes/{quote(node)}/topics", params={"p": max(1, int(page))})
        return self._get_legacy("/topics/show.json", params={"node_name": node})

    def topic(self, topic_id: int | str) -> V2EXApiResponse:
        topic = _clean_id(topic_id, "topic_id")
        if self._token:
            return self._get_v2(f"/topics/{topic}")
        return self._get_legacy("/topics/show.json", params={"id": topic})

    def replies(self, topic_id: int | str, *, page: int = 1) -> V2EXApiResponse:
        topic = _clean_id(topic_id, "topic_id")
        if self._token:
            return self._get_v2(f"/topics/{topic}/replies", params={"p": max(1, int(page))})
        return self._get_legacy("/replies/show.json", params={"topic_id": topic})

    def latest(self) -> V2EXApiResponse:
        return self._get_legacy("/topics/latest.json")

    def hot(self) -> V2EXApiResponse:
        return self._get_legacy("/topics/hot.json")

    @property
    def _token(self) -> str:
        return (self.env.get("V2EX_TOKEN") or "").strip()

    def _get_legacy(self, path: str, *, params: Mapping[str, Any] | None = None) -> V2EXApiResponse:
        return self._get(f"{self.api_base}/{path.lstrip('/')}", endpoint=path, endpoint_family="legacy", params=params)

    def _get_v2(self, path: str, *, params: Mapping[str, Any] | None = None) -> V2EXApiResponse:
        return self._get(f"{self.api_v2_base}/{path.lstrip('/')}", endpoint=path, endpoint_family="api_v2", params=params)

    def _get(self, url: str, *, endpoint: str, endpoint_family: str, params: Mapping[str, Any] | None = None) -> V2EXApiResponse:
        self.ensure_configured()
        local_limit = self.rate_limiter.check()
        if local_limit.exceeded:
            raise V2EXRateLimitError("V2EX local request limit exceeded.")
        headers = {"Accept": "application/json", "User-Agent": "AI-Super-Agent V2EX read-only connector"}
        if self._token and endpoint_family == "api_v2":
            headers["Authorization"] = f"Bearer {self._token}"
        try:
            with httpx.Client(timeout=self.timeout_seconds, transport=self.transport, follow_redirects=False) as client:
                response = client.get(url, headers=headers, params=dict(params or {}))
        except httpx.TimeoutException as exc:
            raise V2EXApiError("V2EX API request timed out") from exc
        except httpx.HTTPError as exc:
            raise V2EXApiError(f"V2EX API request failed: {type(exc).__name__}") from exc
        rate_limit = parse_rate_limit_headers(response.headers, local_limit=local_limit)
        if response.status_code == 429:
            raise V2EXRateLimitError("V2EX API rate limit exceeded")
        if response.status_code in {401, 403}:
            raise V2EXApiError(f"V2EX API returned HTTP {response.status_code}; verify token/setup for this endpoint")
        if response.status_code == 404:
            raise V2EXApiError("V2EX API returned HTTP 404")
        if response.status_code >= 400:
            raise V2EXApiError(f"V2EX API returned HTTP {response.status_code}")
        try:
            payload = response.json()
        except ValueError as exc:
            raise V2EXApiError("V2EX API returned malformed JSON") from exc
        return V2EXApiResponse(
            payload=payload,
            status_code=response.status_code,
            endpoint=endpoint,
            endpoint_family=endpoint_family,
            network_domains=[V2EX_WEB_DOMAIN],
            rate_limit=rate_limit,
        )


def parse_rate_limit_headers(headers: Mapping[str, str], *, local_limit: V2EXRateLimitStatus | None = None) -> V2EXRateLimitStatus:
    local = local_limit or V2EXRateLimitStatus()
    remaining = _int_header(headers, "x-rate-limit-remaining")
    return V2EXRateLimitStatus(
        limit=_int_header(headers, "x-rate-limit-limit"),
        remaining=remaining,
        reset=_int_header(headers, "x-rate-limit-reset"),
        local_used=local.local_used,
        local_limit=local.local_limit,
        exceeded=local.exceeded or (remaining is not None and remaining <= 0),
    )


def _int_header(headers: Mapping[str, str], name: str) -> int | None:
    value = None
    for key, item in headers.items():
        if key.casefold() == name:
            value = item
            break
    try:
        return int(float(value)) if value is not None else None
    except (TypeError, ValueError):
        return None


def _clean_node_name(value: str) -> str:
    node = str(value or "").strip().strip("/")
    if node.startswith("go/"):
        node = node[3:]
    if not node:
        raise V2EXSetupError("A V2EX node name is required.")
    return node


def _clean_id(value: int | str, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise V2EXSetupError(f"A V2EX {field_name} is required.")
    return text
