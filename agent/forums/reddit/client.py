from __future__ import annotations

import base64
import os
from dataclasses import dataclass, field
from typing import Any, Mapping

import httpx

from .errors import RedditApiError, RedditRateLimitError, RedditSetupError
from .policy import RedditPolicyConfig, load_reddit_policy_config, reddit_setup_hint


REDDIT_API_BASE = "https://oauth.reddit.com"
REDDIT_TOKEN_ENDPOINT = "https://www.reddit.com/api/v1/access_token"


@dataclass(frozen=True)
class RedditRateLimitStatus:
    used: float | None = None
    remaining: float | None = None
    reset_seconds: float | None = None
    exceeded: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "used": self.used,
            "remaining": self.remaining,
            "reset_seconds": self.reset_seconds,
            "exceeded": self.exceeded,
            "headers_respected": True,
        }


@dataclass(frozen=True)
class RedditApiResponse:
    payload: Any
    status_code: int
    endpoint: str
    network_domains: list[str]
    rate_limit: RedditRateLimitStatus = field(default_factory=RedditRateLimitStatus)


class RedditApiClient:
    def __init__(
        self,
        *,
        config: RedditPolicyConfig | None = None,
        env: Mapping[str, str] | None = None,
        transport: httpx.BaseTransport | None = None,
        timeout_seconds: float = 10,
        api_base: str = REDDIT_API_BASE,
    ) -> None:
        self.env = env or {}
        self.config = config or load_reddit_policy_config(self.env)
        self.transport = transport
        self.timeout_seconds = timeout_seconds
        self.api_base = api_base.rstrip("/")
        self._access_token: str | None = (self.env.get("REDDIT_ACCESS_TOKEN") or "").strip() or None
        self._last_auth_domains: list[str] = []

    @classmethod
    def from_env(cls, *, env: Mapping[str, str] | None = None, transport: httpx.BaseTransport | None = None) -> "RedditApiClient":
        env_map = env or os.environ
        return cls(config=load_reddit_policy_config(env_map), env=env_map, transport=transport)

    def ensure_configured(self) -> None:
        if not self.config.configured:
            raise RedditSetupError(reddit_setup_hint(self.config))

    def search_posts(
        self,
        query: str,
        *,
        subreddit: str | None = None,
        limit: int = 10,
        sort: str = "relevance",
        time_filter: str = "all",
        language: str = "auto",
    ) -> RedditApiResponse:
        path = f"/r/{_clean_subreddit(subreddit)}/search" if subreddit else "/search"
        params: dict[str, Any] = {
            "q": query,
            "limit": max(1, min(int(limit), 100)),
            "sort": sort,
            "t": time_filter,
            "raw_json": 1,
        }
        # Reddit's Data API does not expose a general language filter for search.
        # Keep the CLI option advisory and avoid sending unsupported parameters.
        _ = language
        if subreddit:
            params["restrict_sr"] = "on"
        return self.get(path, params=params)

    def fetch_subreddit_info(self, subreddit: str) -> RedditApiResponse:
        return self.get(f"/r/{_clean_subreddit(subreddit)}/about", params={"raw_json": 1})

    def fetch_thread(self, post_id_or_url: str, *, sort: str = "confidence", limit: int = 100) -> RedditApiResponse:
        post_id = parse_post_id(post_id_or_url)
        return self.get(f"/comments/{post_id}", params={"sort": sort, "limit": max(1, min(int(limit), 500)), "raw_json": 1})

    def fetch_post(self, post_id_or_url: str) -> RedditApiResponse:
        post_id = parse_post_id(post_id_or_url)
        return self.get(f"/by_id/t3_{post_id}", params={"raw_json": 1})

    def get(self, path: str, *, params: Mapping[str, Any] | None = None) -> RedditApiResponse:
        self.ensure_configured()
        token = self._bearer_token()
        url = f"{self.api_base}/{path.lstrip('/')}"
        headers = {
            "Authorization": f"bearer {token}",
            "User-Agent": (self.env.get("REDDIT_USER_AGENT") or "").strip(),
            "Accept": "application/json",
        }
        try:
            with httpx.Client(timeout=self.timeout_seconds, transport=self.transport, follow_redirects=False) as client:
                response = client.get(url, headers=headers, params=dict(params or {}))
        except httpx.TimeoutException as exc:
            raise RedditApiError("Reddit API request timed out") from exc
        except httpx.HTTPError as exc:
            raise RedditApiError(f"Reddit API request failed: {type(exc).__name__}") from exc
        return self._response_from_httpx(response, endpoint=path, domain="oauth.reddit.com")

    def _bearer_token(self) -> str:
        if self._access_token:
            self._last_auth_domains = []
            return self._access_token
        if not self.config.refresh_token_configured:
            raise RedditSetupError("REDDIT_ACCESS_TOKEN or REDDIT_REFRESH_TOKEN is required for Reddit API calls.")
        client_id = (self.env.get("REDDIT_CLIENT_ID") or "").strip()
        client_secret = (self.env.get("REDDIT_CLIENT_SECRET") or "").strip()
        credentials = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("ascii")
        data = {
            "grant_type": "refresh_token",
            "refresh_token": (self.env.get("REDDIT_REFRESH_TOKEN") or "").strip(),
        }
        headers = {
            "Authorization": f"Basic {credentials}",
            "User-Agent": (self.env.get("REDDIT_USER_AGENT") or "").strip(),
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        try:
            with httpx.Client(timeout=self.timeout_seconds, transport=self.transport, follow_redirects=False) as client:
                response = client.post(REDDIT_TOKEN_ENDPOINT, headers=headers, data=data)
        except httpx.TimeoutException as exc:
            raise RedditApiError("Reddit OAuth token refresh timed out") from exc
        except httpx.HTTPError as exc:
            raise RedditApiError(f"Reddit OAuth token refresh failed: {type(exc).__name__}") from exc
        if response.status_code == 429:
            raise RedditRateLimitError("Reddit OAuth rate limit exceeded")
        if response.status_code >= 400:
            raise RedditApiError(f"Reddit OAuth token endpoint returned HTTP {response.status_code}")
        try:
            payload = response.json()
        except ValueError as exc:
            raise RedditApiError("Reddit OAuth token endpoint returned malformed JSON") from exc
        token = str(payload.get("access_token") or "").strip() if isinstance(payload, Mapping) else ""
        if not token:
            raise RedditApiError("Reddit OAuth token endpoint did not return an access token")
        self._access_token = token
        self._last_auth_domains = ["www.reddit.com"]
        return token

    def _response_from_httpx(self, response: httpx.Response, *, endpoint: str, domain: str) -> RedditApiResponse:
        rate_limit = parse_rate_limit_headers(response.headers)
        if response.status_code == 429:
            raise RedditRateLimitError("Reddit API rate limit exceeded")
        if response.status_code in {401, 403}:
            raise RedditApiError(f"Reddit API returned HTTP {response.status_code}; verify OAuth scopes and credentials")
        if response.status_code == 404:
            raise RedditApiError("Reddit API returned HTTP 404")
        if response.status_code >= 400:
            raise RedditApiError(f"Reddit API returned HTTP {response.status_code}")
        try:
            payload = response.json()
        except ValueError as exc:
            raise RedditApiError("Reddit API returned malformed JSON") from exc
        return RedditApiResponse(
            payload=payload,
            status_code=response.status_code,
            endpoint=endpoint,
            network_domains=[*self._last_auth_domains, domain],
            rate_limit=rate_limit,
        )


def parse_rate_limit_headers(headers: Mapping[str, str]) -> RedditRateLimitStatus:
    remaining = _float_header(headers, "x-ratelimit-remaining")
    return RedditRateLimitStatus(
        used=_float_header(headers, "x-ratelimit-used"),
        remaining=remaining,
        reset_seconds=_float_header(headers, "x-ratelimit-reset"),
        exceeded=remaining is not None and remaining <= 0,
    )


def parse_post_id(value: str) -> str:
    text = str(value or "").strip().strip("/")
    if not text:
        raise RedditSetupError("A Reddit post id or URL is required.")
    if "/comments/" in text:
        after = text.split("/comments/", 1)[1]
        post_id = after.split("/", 1)[0]
    else:
        post_id = text.rsplit("/", 1)[-1]
    return post_id.removeprefix("t3_")


def _float_header(headers: Mapping[str, str], name: str) -> float | None:
    value = None
    for key, item in headers.items():
        if key.casefold() == name:
            value = item
            break
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _clean_subreddit(subreddit: str | None) -> str:
    value = str(subreddit or "").strip().strip("/")
    if value.startswith("r/"):
        value = value[2:]
    if not value:
        raise RedditSetupError("A subreddit name is required.")
    return value
