from __future__ import annotations

import base64
import json
import os
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from agent.safety.redaction import SecretRedactor

from .policy import (
    REDDIT_FORBIDDEN_WRITE_CAPABILITIES,
    RedditPolicyConfig,
    load_reddit_policy_config,
    reddit_setup_hint,
)


REDDIT_TOKEN_ENV = ("REDDIT_REFRESH_TOKEN", "REDDIT_ACCESS_TOKEN")
REDDIT_AUTH_DOMAINS = ("www.reddit.com", "oauth.reddit.com")
GENERIC_USER_AGENT_MARKERS = (
    "change-me",
    "example",
    "generic",
    "python-requests",
    "curl/",
    "smart_agent",
    "ai-super-agent",
    "test",
    "your-app",
)


def reddit_status(
    *,
    project_root: str | Path = ".",
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    env = environ or os.environ
    config = load_reddit_policy_config(env)
    payload = _base_status(config, env)
    payload.update(
        {
            "status": _status_label(config),
            "warnings": _status_warnings(config),
            "no_api_calls_made": True,
            "no_post_comment_content_fetched": True,
            "no_user_content_stored": True,
            "setup_hint": reddit_setup_hint(config),
            "_audit": {
                "network_domains": [],
                "result_summary": f"Reddit status inspected; status={_status_label(config)}.",
            },
        }
    )
    return _redact(payload)


def reddit_doctor(
    *,
    project_root: str | Path = ".",
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    env = environ or os.environ
    config = load_reddit_policy_config(env)
    warnings = [
        *_status_warnings(config),
        *_repo_warnings(root, env),
        *_user_agent_warnings(env),
    ]
    payload = _base_status(config, env)
    payload.update(
        {
            "status": "warn" if warnings or not config.configured else "ok",
            "warnings": warnings,
            "no_api_calls_made": True,
            "no_post_comment_content_fetched": True,
            "no_user_content_stored": True,
            "setup_hint": reddit_setup_hint(config),
            "_audit": {
                "network_domains": [],
                "result_summary": f"Reddit doctor inspected config; status={_status_label(config)}.",
            },
        }
    )
    return _redact(payload)


def reddit_auth_check(
    *,
    project_root: str | Path = ".",
    environ: Mapping[str, str] | None = None,
    auth_client: Callable[[RedditPolicyConfig, Mapping[str, str]], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    env = environ or os.environ
    config = load_reddit_policy_config(env)
    if not config.configured:
        payload = _base_status(config, env)
        payload.update(
            {
                "status": "setup_required",
                "auth_check_attempted": False,
                "live_call_performed": False,
                "no_post_comment_content_fetched": True,
                "no_user_content_stored": True,
                "content_endpoints_called": [],
                "errors": [
                    {
                        "code": "reddit_oauth_setup_incomplete",
                        "message": reddit_setup_hint(config),
                    }
                ],
                "_audit": {
                    "network_domains": [],
                    "result_summary": "Reddit auth-check skipped because OAuth setup is incomplete.",
                },
            }
        )
        return _redact(payload)

    check = auth_client or _perform_reddit_auth_check
    try:
        result = check(config, env)
        status = "ok" if result.get("ok") else "error"
        domains = [domain for domain in result.get("network_domains", []) if domain in REDDIT_AUTH_DOMAINS]
        payload = {
            "connector": "reddit",
            "status": status,
            "enabled": config.enabled,
            "configured": config.configured,
            "auth_check_attempted": True,
            "live_call_performed": True,
            "endpoint_class": result.get("endpoint_class", "oauth_token"),
            "network_domains": domains,
            "http_status": result.get("http_status"),
            "token_valid": bool(result.get("ok")),
            "scope_count": result.get("scope_count"),
            "expires_in_seconds": result.get("expires_in_seconds"),
            "no_post_comment_content_fetched": True,
            "no_user_content_stored": True,
            "content_endpoints_called": [],
            "errors": result.get("errors", []),
            "rate_limit": _rate_limit(config),
            "retention": _retention(config),
            "disabled_write_actions": _disabled_write_actions(),
            "_audit": {
                "network_domains": domains,
                "result_summary": f"Reddit auth-check completed; status={status}; endpoint_class={result.get('endpoint_class', 'oauth_token')}.",
            },
        }
        return _redact(payload)
    except Exception as exc:  # pragma: no cover - defensive normalization
        return _redact(
            {
                "connector": "reddit",
                "status": "error",
                "enabled": config.enabled,
                "configured": config.configured,
                "auth_check_attempted": True,
                "live_call_performed": True,
                "endpoint_class": "oauth_token",
                "network_domains": ["www.reddit.com"],
                "no_post_comment_content_fetched": True,
                "no_user_content_stored": True,
                "content_endpoints_called": [],
                "errors": [{"code": "reddit_auth_check_failed", "message": type(exc).__name__}],
                "_audit": {
                    "network_domains": ["www.reddit.com"],
                    "result_summary": "Reddit auth-check failed with normalized error.",
                },
            }
        )


def _perform_reddit_auth_check(config: RedditPolicyConfig, env: Mapping[str, str]) -> dict[str, Any]:
    user_agent = env.get("REDDIT_USER_AGENT", "").strip()
    timeout = 10
    if config.refresh_token_configured:
        client_id = env.get("REDDIT_CLIENT_ID", "").strip()
        client_secret = env.get("REDDIT_CLIENT_SECRET", "").strip()
        credentials = f"{client_id}:{client_secret}".encode("utf-8")
        auth_header = base64.b64encode(credentials).decode("ascii")
        body = urllib.parse.urlencode(
            {
                "grant_type": "refresh_token",
                "refresh_token": env.get("REDDIT_REFRESH_TOKEN", "").strip(),
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            "https://www.reddit.com/api/v1/access_token",
            data=body,
            headers={
                "Authorization": f"Basic {auth_header}",
                "User-Agent": user_agent,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )
        return _json_request(request, timeout=timeout, endpoint_class="oauth_token", domain="www.reddit.com")

    request = urllib.request.Request(
        "https://oauth.reddit.com/api/v1/scopes",
        headers={
            "Authorization": f"bearer {env.get('REDDIT_ACCESS_TOKEN', '').strip()}",
            "User-Agent": user_agent,
            "Accept": "application/json",
        },
        method="GET",
    )
    return _json_request(request, timeout=timeout, endpoint_class="oauth_scopes", domain="oauth.reddit.com")


def _json_request(
    request: urllib.request.Request,
    *,
    timeout: int,
    endpoint_class: str,
    domain: str,
) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed Reddit OAuth endpoints only.
            status = getattr(response, "status", 200)
            body = response.read(65536)
        payload = json.loads(body.decode("utf-8") or "{}")
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "http_status": exc.code,
            "endpoint_class": endpoint_class,
            "network_domains": [domain],
            "errors": [{"code": "reddit_http_error", "message": f"Reddit OAuth endpoint returned HTTP {exc.code}"}],
        }
    except (urllib.error.URLError, TimeoutError) as exc:
        return {
            "ok": False,
            "http_status": None,
            "endpoint_class": endpoint_class,
            "network_domains": [domain],
            "errors": [{"code": "reddit_network_error", "message": type(exc).__name__}],
        }
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return {
            "ok": False,
            "http_status": None,
            "endpoint_class": endpoint_class,
            "network_domains": [domain],
            "errors": [{"code": "reddit_malformed_json", "message": type(exc).__name__}],
        }

    if endpoint_class == "oauth_token":
        return {
            "ok": bool(isinstance(payload, dict) and payload.get("access_token")),
            "http_status": status,
            "endpoint_class": endpoint_class,
            "network_domains": [domain],
            "scope_count": len(str(payload.get("scope", "")).split()) if isinstance(payload, dict) else None,
            "expires_in_seconds": payload.get("expires_in") if isinstance(payload, dict) else None,
            "errors": [] if isinstance(payload, dict) and payload.get("access_token") else [{"code": "reddit_token_missing", "message": "OAuth token response did not include an access token."}],
        }
    return {
        "ok": isinstance(payload, dict),
        "http_status": status,
        "endpoint_class": endpoint_class,
        "network_domains": [domain],
        "scope_count": len(payload) if isinstance(payload, dict) else None,
        "errors": [] if isinstance(payload, dict) else [{"code": "reddit_scopes_unexpected", "message": "OAuth scopes response was not an object."}],
    }


def _base_status(config: RedditPolicyConfig, env: Mapping[str, str]) -> dict[str, Any]:
    required = [
        "REDDIT_CLIENT_ID",
        "REDDIT_CLIENT_SECRET",
        "REDDIT_USER_AGENT",
        "REDDIT_REFRESH_TOKEN or REDDIT_ACCESS_TOKEN",
    ]
    return {
        "connector": "reddit",
        "provider": "reddit_api",
        "enabled": config.enabled,
        "configured": config.configured,
        "oauth_required": config.oauth_required,
        "unauthenticated_mode_allowed": config.unauthenticated_mode_allowed,
        "credential_status": {
            "required_env": required,
            "present_env": _present_env(env),
            "missing_env": config.missing_oauth_env,
            "client_id_configured": config.client_id_configured,
            "client_secret_configured": config.client_secret_configured,
            "user_agent_configured": config.user_agent_configured,
            "refresh_token_configured": config.refresh_token_configured,
            "access_token_configured": config.access_token_configured,
            "token_configured": config.token_configured,
        },
        "rate_limit": _rate_limit(config),
        "retention": _retention(config),
        "disabled_write_actions": _disabled_write_actions(),
        "web_fallback": {
            "allowed": config.allow_web_fallback,
            "env_requested": config.web_fallback_env_requested,
            "reddit_web_scraping_as_api_substitute": False,
        },
        "privacy": {
            "store_author_metadata": config.store_author_metadata,
            "use_for_training": config.use_for_training,
            "use_for_training_env_requested": config.use_for_training_env_requested,
            "permanent_user_content_storage_default": False,
            "deleted_removed_content_retained": False,
        },
        "trust_level": config.trust_level,
        "read_only": config.read_only,
    }


def _status_label(config: RedditPolicyConfig) -> str:
    if not config.enabled:
        return "disabled"
    if not config.configured:
        return "requires_setup"
    return "configured"


def _status_warnings(config: RedditPolicyConfig) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    if not config.enabled:
        warnings.append(
            {
                "code": "reddit_disabled",
                "severity": "medium",
                "message": "REDDIT_ENABLED=false; Reddit API connector commands remain disabled except config diagnostics.",
            }
        )
    if not config.configured:
        warnings.append(
            {
                "code": "reddit_oauth_incomplete",
                "severity": "medium",
                "message": reddit_setup_hint(config),
                "missing_env": config.missing_oauth_env,
            }
        )
    if config.web_fallback_env_requested and not config.allow_web_fallback:
        warnings.append(
            {
                "code": "reddit_web_fallback_denied",
                "severity": "high",
                "message": "REDDIT_ALLOW_WEB_FALLBACK was requested but Reddit web scraping fallback is denied by policy.",
            }
        )
    if config.use_for_training_env_requested and not config.use_for_training:
        warnings.append(
            {
                "code": "reddit_training_denied",
                "severity": "high",
                "message": "REDDIT_USE_FOR_TRAINING is hard false; Reddit/forum content is not used for model training.",
            }
        )
    return warnings


def _repo_warnings(root: Path, env: Mapping[str, str]) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    if _env_file_tracked(root):
        warnings.append(
            {
                "code": "env_tracked",
                "severity": "high",
                "message": ".env appears to be tracked by git; remove it from version control and rotate exposed credentials.",
            }
        )
    for key in REDDIT_TOKEN_ENV:
        value = (env.get(key) or "").strip()
        if value and _path_inside_repo(value, root):
            warnings.append(
                {
                    "code": "reddit_token_path_inside_repo",
                    "severity": "high",
                    "env_var": key,
                    "message": f"{key} appears to point inside the repo; keep Reddit OAuth token material outside the project tree.",
                }
            )
    return warnings


def _user_agent_warnings(env: Mapping[str, str]) -> list[dict[str, Any]]:
    user_agent = (env.get("REDDIT_USER_AGENT") or "").strip()
    if not user_agent:
        return [
            {
                "code": "reddit_user_agent_missing",
                "severity": "medium",
                "message": "REDDIT_USER_AGENT is missing; Reddit API access requires a specific descriptive user agent.",
            }
        ]
    lowered = user_agent.casefold()
    if len(user_agent) < 12 or any(marker in lowered for marker in GENERIC_USER_AGENT_MARKERS):
        return [
            {
                "code": "reddit_user_agent_generic",
                "severity": "medium",
                "message": "REDDIT_USER_AGENT looks generic; use a specific app/contact string before live Reddit API use.",
            }
        ]
    return []


def _env_file_tracked(root: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", ".env"],
            cwd=root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            text=True,
        )
    except OSError:
        return False
    return result.returncode == 0


def _path_inside_repo(path_text: str, root: Path) -> bool:
    try:
        path = Path(path_text).expanduser()
        resolved = path if path.is_absolute() else root / path
        resolved = resolved.resolve(strict=False)
    except OSError:
        return False
    return resolved.exists() and (resolved == root or root in resolved.parents)


def _present_env(env: Mapping[str, str]) -> list[str]:
    present = [
        key
        for key in (
            "REDDIT_ENABLED",
            "REDDIT_CLIENT_ID",
            "REDDIT_CLIENT_SECRET",
            "REDDIT_USER_AGENT",
            "REDDIT_REFRESH_TOKEN",
            "REDDIT_ACCESS_TOKEN",
        )
        if (env.get(key) or "").strip()
    ]
    return present


def _rate_limit(config: RedditPolicyConfig) -> dict[str, Any]:
    return {
        "max_requests_per_minute": config.max_requests_per_minute,
        "rate_limit_headers_must_be_respected": True,
    }


def _retention(config: RedditPolicyConfig) -> dict[str, Any]:
    return {
        "cache_enabled": config.cache_enabled,
        "cache_ttl_seconds": config.cache_ttl_seconds,
        "delete_user_content_after_seconds": config.delete_user_content_after_seconds,
        "store_author_metadata": config.store_author_metadata,
        "deleted_removed_content_retained": False,
        "query_history_stored": False,
    }


def _disabled_write_actions() -> dict[str, str]:
    return {capability: "disabled" for capability in sorted(REDDIT_FORBIDDEN_WRITE_CAPABILITIES)}


def _redact(payload: dict[str, Any]) -> dict[str, Any]:
    redactor = SecretRedactor()

    def redact_values(value: Any) -> Any:
        if isinstance(value, str):
            return redactor.redact_text(value)
        if isinstance(value, dict):
            return {key: redact_values(item) for key, item in value.items()}
        if isinstance(value, list):
            return [redact_values(item) for item in value]
        return value

    return redact_values(payload)
