from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from agent.connectors.cost_policy import ProviderCostConfig, select_provider, weather_provider_candidates, web_provider_candidates
from agent.safety.redaction import SecretRedactor


SECRET_STATUS_PROVIDERS = ("serpapi", "weatherapi", "gmail", "telegram")
SECRET_ENV_VARS = (
    "SERPAPI_API_KEY",
    "WEATHERAPI_API_KEY",
    "WEATHER_API_KEY",
    "GMAIL_USER",
    "GMAIL_CLIENT_ID",
    "GMAIL_CLIENT_SECRET",
    "GMAIL_TOKEN_PATH",
    "GMAIL_SCOPES",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_DEFAULT_CHAT_ID",
    "TELEGRAM_ALLOWED_CHAT_IDS",
    "REDDIT_CLIENT_ID",
    "REDDIT_CLIENT_SECRET",
    "REDDIT_REFRESH_TOKEN",
    "REDDIT_ACCESS_TOKEN",
)

SECRET_SCAN_PATTERN = re.compile(
    r"(?i)(api[_-]?key|client[_-]?secret|token|password|authorization)\s*[:=]\s*([^\s,'\";]+)"
)
PLACEHOLDER_VALUES = {"", "none", "null", "todo", "example", "changeme", "your-key", "[redacted]", "<redacted>"}
GMAIL_BROAD_SCOPES = {
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.readonly",
}
GMAIL_SEND_SCOPES = {
    "https://www.googleapis.com/auth/gmail.send",
    "https://mail.google.com/",
}


@dataclass(frozen=True)
class ProviderCredentialStatus:
    name: str
    configured: bool
    allowed: bool
    default: bool
    paid_or_quota_limited: bool
    disabled_by_cost_policy: bool
    setup_hint: str
    required_env: list[str]
    present_env: list[str]
    missing_env: list[str]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return SecretRedactor().redact(
            {
                "name": self.name,
                "configured": self.configured,
                "allowed": self.allowed,
                "default": self.default,
                "paid_or_quota_limited": self.paid_or_quota_limited,
                "disabled_by_cost_policy": self.disabled_by_cost_policy,
                "setup_hint": self.setup_hint,
                "required_env": self.required_env,
                "present_env": self.present_env,
                "missing_env": self.missing_env,
                "metadata": self.metadata,
            }
        )


def secrets_doctor(
    *,
    project_root: str | Path = ".",
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    env = environ or os.environ
    providers = [provider_status(name, project_root=root, environ=env) for name in SECRET_STATUS_PROVIDERS]
    warnings = _repo_warnings(root, env)
    return SecretRedactor().redact(
        {
            "status": "warn" if warnings else "ok",
            "no_api_calls_made": True,
            "no_personal_data_reads": True,
            "cost_policy": _cost_policy_summary(env),
            "providers": [provider.to_dict() for provider in providers],
            "warnings": warnings,
        }
    )


def secrets_status(
    *,
    project_root: str | Path = ".",
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    report = secrets_doctor(project_root=project_root, environ=environ)
    return {
        "status": report["status"],
        "no_api_calls_made": True,
        "provider_count": len(report["providers"]),
        "configured_providers": [
            provider["name"]
            for provider in report["providers"]
            if provider.get("configured")
        ],
        "warnings": report["warnings"],
        "cost_policy": report["cost_policy"],
    }


def provider_status(
    name: str,
    *,
    project_root: str | Path = ".",
    environ: Mapping[str, str] | None = None,
) -> ProviderCredentialStatus:
    env = environ or os.environ
    normalized = name.strip().casefold()
    if normalized == "serpapi":
        return _serpapi_status(env)
    if normalized == "weatherapi":
        return _weatherapi_status(env)
    if normalized == "gmail":
        return _gmail_status(env, Path(project_root).resolve())
    if normalized == "telegram":
        return _telegram_status(env)
    if normalized == "reddit":
        return _reddit_status(env, Path(project_root).resolve())
    raise ValueError(f"unknown secret provider: {name}")


def gmail_doctor(
    *,
    project_root: str | Path = ".",
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    env = environ or os.environ
    status = provider_status("gmail", project_root=root, environ=env).to_dict()
    warnings = [
        warning
        for warning in _repo_warnings(root, env)
        if warning.get("code") in {"token_path_inside_repo", "env_tracked", "possible_secret_in_repo_text"}
    ]
    warnings.extend(gmail_scopes(environ=env)["warnings"])
    return SecretRedactor().redact(
        {
            "connector": "gmail",
            "status": "warn" if warnings or status["missing_env"] else "ok",
            "configured": status["configured"],
            "enabled": False,
            "no_api_calls_made": True,
            "no_inbox_read": True,
            "no_email_sent": True,
            "credential_status": status,
            "scopes": gmail_scopes(environ=env),
            "send_capability": _send_safety_summary("gmail"),
            "warnings": warnings,
            "setup_hint": status["setup_hint"],
        }
    )


def gmail_scopes(*, environ: Mapping[str, str] | None = None) -> dict[str, Any]:
    env = environ or os.environ
    scopes = _parse_scopes(env.get("GMAIL_SCOPES", ""))
    warnings: list[dict[str, Any]] = []
    for scope in scopes:
        if scope in GMAIL_BROAD_SCOPES:
            warnings.append(
                {
                    "code": "gmail_broad_scope",
                    "severity": "medium",
                    "scope": scope,
                    "message": "Gmail scope is broad; prefer the narrowest future OAuth scope that supports the approved workflow.",
                }
            )
        if scope in GMAIL_SEND_SCOPES:
            warnings.append(
                {
                    "code": "gmail_send_scope",
                    "severity": "high",
                    "scope": scope,
                    "message": "Scope can support sending; send remains CRITICAL, disabled by default, and per-action approval-only.",
                }
            )
    return SecretRedactor().redact(
        {
            "connector": "gmail",
            "configured": bool(scopes),
            "scopes": scopes,
            "scope_count": len(scopes),
            "warnings": warnings,
            "recommended_minimum": "Use the narrowest read/draft scope for the specific approved workflow; avoid https://mail.google.com/ unless explicitly justified.",
            "send_capability": _send_safety_summary("gmail"),
        }
    )


def telegram_doctor(
    *,
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    env = environ or os.environ
    status = provider_status("telegram", environ=env).to_dict()
    warnings: list[dict[str, Any]] = []
    if not _present(env, "TELEGRAM_DEFAULT_CHAT_ID"):
        warnings.append(
            {
                "code": "telegram_default_chat_missing",
                "severity": "medium",
                "message": "TELEGRAM_DEFAULT_CHAT_ID is not set; future sends must still use explicit approved chat selection.",
            }
        )
    if not _present(env, "TELEGRAM_ALLOWED_CHAT_IDS"):
        warnings.append(
            {
                "code": "telegram_allowed_chats_missing",
                "severity": "medium",
                "message": "TELEGRAM_ALLOWED_CHAT_IDS is not set; configure an allowlist before any future send-capable connector.",
            }
        )
    return SecretRedactor().redact(
        {
            "connector": "telegram",
            "status": "warn" if warnings or status["missing_env"] else "ok",
            "configured": status["configured"],
            "enabled": False,
            "no_api_calls_made": True,
            "no_chat_reads": True,
            "no_messages_sent": True,
            "credential_status": status,
            "send_capability": _send_safety_summary("telegram"),
            "warnings": warnings,
            "setup_hint": status["setup_hint"],
        }
    )


def telegram_status(*, environ: Mapping[str, str] | None = None) -> dict[str, Any]:
    env = environ or os.environ
    doctor = telegram_doctor(environ=env)
    return {
        "connector": "telegram",
        "status": doctor["status"],
        "configured": doctor["configured"],
        "enabled": False,
        "no_api_calls_made": True,
        "no_chat_reads": True,
        "no_messages_sent": True,
        "present_env": doctor["credential_status"]["present_env"],
        "missing_env": doctor["credential_status"]["missing_env"],
        "default_chat_configured": doctor["credential_status"]["metadata"]["default_chat_configured"],
        "allowed_chat_ids_configured": doctor["credential_status"]["metadata"]["allowed_chat_ids_configured"],
        "send_capability": doctor["send_capability"],
        "warnings": doctor["warnings"],
        "setup_hint": doctor["setup_hint"],
    }


def _serpapi_status(env: Mapping[str, str]) -> ProviderCredentialStatus:
    required = ["SERPAPI_API_KEY"]
    key_present = _present(env, "SERPAPI_API_KEY")
    enabled = (env.get("SERPAPI_ENABLED") or "").strip().casefold() in {"1", "true", "yes", "on"}
    config = ProviderCostConfig.from_env(env)
    decision = select_provider("web", web_provider_candidates(env), config=config, explicit_provider="serpapi" if key_present else None)
    default = config.search_default_provider == "serpapi"
    cost_allowed = config.allow_paid_apis and config.max_paid_api_calls_per_day > 0
    allowed = key_present and enabled and cost_allowed
    return ProviderCredentialStatus(
        name="serpapi",
        configured=key_present,
        allowed=allowed,
        default=default,
        paid_or_quota_limited=True,
        disabled_by_cost_policy=key_present and not cost_allowed,
        setup_hint=(
            "Set SERPAPI_API_KEY, SERPAPI_ENABLED=true, ALLOW_PAID_APIS=true, "
            "and MAX_PAID_API_CALLS_PER_DAY>0 before using SerpAPI."
        ),
        required_env=required,
        present_env=_present_keys(env, required),
        missing_env=_missing_keys(env, required),
        metadata={
            "enabled_by_config": enabled,
            "selected_by_policy": decision.selected_provider == "serpapi",
            "cost_policy_reason": decision.reason,
            "default_provider_env": config.search_default_provider,
            "max_paid_api_calls_per_day": config.max_paid_api_calls_per_day,
        },
    )


def _weatherapi_status(env: Mapping[str, str]) -> ProviderCredentialStatus:
    required_any = ["WEATHERAPI_API_KEY", "WEATHER_API_KEY"]
    configured = any(_present(env, key) for key in required_any)
    config = ProviderCostConfig.from_env(env)
    explicit = "weatherapi" if configured and config.weather_default_provider == "weatherapi" else None
    decision = select_provider("weather", weather_provider_candidates(env), config=config, explicit_provider=explicit)
    default = config.weather_default_provider == "weatherapi"
    allowed = configured and (default or (config.allow_paid_apis and config.max_paid_api_calls_per_day > 0))
    return ProviderCredentialStatus(
        name="weatherapi",
        configured=configured,
        allowed=allowed,
        default=default,
        paid_or_quota_limited=True,
        disabled_by_cost_policy=configured and not allowed,
        setup_hint="Set WEATHERAPI_API_KEY or WEATHER_API_KEY, then explicitly select WeatherAPI or allow paid APIs.",
        required_env=required_any,
        present_env=_present_keys(env, required_any),
        missing_env=[] if configured else required_any,
        metadata={
            "selected_by_policy": decision.selected_provider == "weatherapi",
            "cost_policy_reason": decision.reason,
            "default_provider_env": config.weather_default_provider,
        },
    )


def _gmail_status(env: Mapping[str, str], project_root: Path) -> ProviderCredentialStatus:
    required = ["GMAIL_USER", "GMAIL_CLIENT_ID", "GMAIL_CLIENT_SECRET", "GMAIL_TOKEN_PATH"]
    configured = all(_present(env, key) for key in required)
    token_path = env.get("GMAIL_TOKEN_PATH", "").strip()
    token_inside_repo = _path_inside_repo(token_path, project_root) if token_path else False
    return ProviderCredentialStatus(
        name="gmail",
        configured=configured,
        allowed=False,
        default=False,
        paid_or_quota_limited=False,
        disabled_by_cost_policy=False,
        setup_hint="Set Gmail OAuth env vars for future config checks only; this doctor does not read Gmail inboxes.",
        required_env=required,
        present_env=_present_keys(env, [*required, "GMAIL_SCOPES"]),
        missing_env=_missing_keys(env, required),
        metadata={
            "oauth_file_configured": bool(token_path),
            "oauth_file_inside_repo": token_inside_repo,
            "scopes_configured": _present(env, "GMAIL_SCOPES"),
            "scope_count": len(_parse_scopes(env.get("GMAIL_SCOPES", ""))),
            "reads_inbox": False,
            "sends_email": False,
            "connector_enabled_by_default": False,
            "send_risk_level": "CRITICAL",
            "send_default_enabled": False,
        },
    )


def _telegram_status(env: Mapping[str, str]) -> ProviderCredentialStatus:
    required = ["TELEGRAM_BOT_TOKEN"]
    chat_configured = _present(env, "TELEGRAM_DEFAULT_CHAT_ID") or _present(env, "TELEGRAM_ALLOWED_CHAT_IDS")
    configured = _present(env, "TELEGRAM_BOT_TOKEN") and chat_configured
    return ProviderCredentialStatus(
        name="telegram",
        configured=configured,
        allowed=False,
        default=False,
        paid_or_quota_limited=False,
        disabled_by_cost_policy=False,
        setup_hint="Set TELEGRAM_BOT_TOKEN plus allowed/default chat ids for future config checks only; this doctor sends no messages.",
        required_env=[*required, "TELEGRAM_DEFAULT_CHAT_ID or TELEGRAM_ALLOWED_CHAT_IDS"],
        present_env=_present_keys(env, ["TELEGRAM_BOT_TOKEN", "TELEGRAM_DEFAULT_CHAT_ID", "TELEGRAM_ALLOWED_CHAT_IDS"]),
        missing_env=[] if configured else _telegram_missing(env),
        metadata={
            "default_chat_configured": _present(env, "TELEGRAM_DEFAULT_CHAT_ID"),
            "allowed_chat_ids_configured": _present(env, "TELEGRAM_ALLOWED_CHAT_IDS"),
            "allowed_chat_count": len(_parse_scopes(env.get("TELEGRAM_ALLOWED_CHAT_IDS", ""))),
            "reads_chats": False,
            "sends_messages": False,
            "connector_enabled_by_default": False,
            "send_risk_level": "CRITICAL",
            "send_default_enabled": False,
        },
    )


def _reddit_status(env: Mapping[str, str], project_root: Path) -> ProviderCredentialStatus:
    from agent.forums.reddit.policy import load_reddit_policy_config, reddit_setup_hint

    policy = load_reddit_policy_config(env)
    token_path_inside_repo = any(
        _looks_like_existing_repo_path((env.get(key) or "").strip(), project_root)
        for key in ("REDDIT_REFRESH_TOKEN", "REDDIT_ACCESS_TOKEN")
        if (env.get(key) or "").strip()
    )
    required = [
        "REDDIT_CLIENT_ID",
        "REDDIT_CLIENT_SECRET",
        "REDDIT_USER_AGENT",
        "REDDIT_REFRESH_TOKEN or REDDIT_ACCESS_TOKEN",
    ]
    return ProviderCredentialStatus(
        name="reddit",
        configured=policy.configured,
        allowed=policy.configured,
        default=False,
        paid_or_quota_limited=False,
        disabled_by_cost_policy=False,
        setup_hint=reddit_setup_hint(policy),
        required_env=required,
        present_env=_present_keys(
            env,
            [
                "REDDIT_ENABLED",
                "REDDIT_CLIENT_ID",
                "REDDIT_CLIENT_SECRET",
                "REDDIT_USER_AGENT",
                "REDDIT_REFRESH_TOKEN",
                "REDDIT_ACCESS_TOKEN",
            ],
        ),
        missing_env=policy.missing_oauth_env,
        metadata={
            "enabled_by_config": policy.enabled,
            "oauth_required": policy.oauth_required,
            "unauthenticated_mode_allowed": policy.unauthenticated_mode_allowed,
            "refresh_oauth_configured": policy.refresh_token_configured,
            "access_oauth_configured": policy.access_token_configured,
            "oauth_file_inside_repo": token_path_inside_repo,
            "max_requests_per_minute": policy.max_requests_per_minute,
            "cache_enabled": policy.cache_enabled,
            "cache_ttl_seconds": policy.cache_ttl_seconds,
            "delete_user_content_after_seconds": policy.delete_user_content_after_seconds,
            "store_author_metadata": policy.store_author_metadata,
            "use_for_training": policy.use_for_training,
            "web_scraping_fallback_allowed": policy.allow_web_fallback,
            "post_comment_vote_dm_capabilities_enabled": False,
            "no_api_calls_made": True,
            "no_post_comment_content_fetched": True,
        },
    )


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
    token_path = env.get("GMAIL_TOKEN_PATH", "").strip()
    if token_path and _path_inside_repo(token_path, root):
        warnings.append(
            {
                "code": "token_path_inside_repo",
                "severity": "high",
                "message": "GMAIL_TOKEN_PATH appears to point inside the repo; keep OAuth token files outside the project tree.",
            }
        )
    warnings.extend(_secret_file_warnings(root))
    return warnings


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


def _secret_file_warnings(root: Path) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    for path in _scan_paths(root):
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for line_number, line in enumerate(lines, start=1):
            if _line_has_secret(line):
                warnings.append(
                    {
                        "code": "possible_secret_in_repo_text",
                        "severity": "medium",
                        "message": "Possible secret-looking value found in docs/tests/config; inspect and redact before committing.",
                        "path": str(path.relative_to(root)),
                        "line": line_number,
                    }
                )
                break
    return warnings


def _scan_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for directory in ("docs", "tests", "config"):
        base = root / directory
        if not base.exists():
            continue
        paths.extend(
            path
            for path in base.rglob("*")
            if path.is_file()
            and path.suffix.lower() in {".md", ".py", ".yaml", ".yml", ".json", ".toml", ".txt", ".example"}
            and "__pycache__" not in path.parts
        )
    return paths


def _line_has_secret(line: str) -> bool:
    if "rg -n" in line or "SECRET_SCAN_PATTERN" in line:
        return False
    if any(marker in line for marker in ("write_text(", "monkeypatch.setenv(", "import_from_stdin(", "content=", '"setup_hint":')):
        return False
    match = SECRET_SCAN_PATTERN.search(line)
    if not match:
        return False
    value = match.group(2).strip().strip('"').strip("'").strip()
    lowered = value.casefold()
    if lowered in PLACEHOLDER_VALUES:
        return False
    if any(marker in lowered for marker in ("not-a-real", "supersecret", "sk-secret")):
        return False
    if value.startswith(("<", "{", "$")):
        return False
    return len(value) >= 8 and "[REDACTED]" not in value


def _path_inside_repo(path_text: str, root: Path) -> bool:
    try:
        path = Path(path_text).expanduser()
        resolved = path if path.is_absolute() else root / path
        resolved = resolved.resolve(strict=False)
    except OSError:
        return False
    return resolved == root or root in resolved.parents


def _looks_like_existing_repo_path(path_text: str, root: Path) -> bool:
    if not path_text or not any(marker in path_text for marker in ("/", "\\")):
        return False
    try:
        path = Path(path_text).expanduser()
        resolved = path if path.is_absolute() else root / path
        return resolved.exists() and _path_inside_repo(path_text, root)
    except OSError:
        return False


def _cost_policy_summary(env: Mapping[str, str]) -> dict[str, Any]:
    config = ProviderCostConfig.from_env(env)
    return {
        "mode": config.cost_mode.value,
        "allow_paid_apis": config.allow_paid_apis,
        "max_paid_api_calls_per_day": config.max_paid_api_calls_per_day,
        "search_default_provider": config.search_default_provider,
        "weather_default_provider": config.weather_default_provider,
        "paid_providers_default_disabled": not config.allow_paid_apis or config.max_paid_api_calls_per_day <= 0,
    }


def _present(env: Mapping[str, str], key: str) -> bool:
    return bool((env.get(key) or "").strip())


def _parse_scopes(text: str) -> list[str]:
    return [item for item in re.split(r"[\s,]+", text.strip()) if item]


def _send_safety_summary(provider: str) -> dict[str, Any]:
    capability = "email.send_approved" if provider == "gmail" else "messages.send_approved"
    return {
        "capability": capability,
        "risk_level": "CRITICAL",
        "default_enabled": False,
        "approval_required": "per_action",
        "approval_reuse_allowed": False,
        "implemented_now": False,
        "note": "Doctor commands never send; any future send must be explicitly implemented, disabled by default, and approved per action.",
    }


def _present_keys(env: Mapping[str, str], keys: Sequence[str]) -> list[str]:
    return [key for key in keys if _present(env, key)]


def _missing_keys(env: Mapping[str, str], keys: Sequence[str]) -> list[str]:
    return [key for key in keys if not _present(env, key)]


def _telegram_missing(env: Mapping[str, str]) -> list[str]:
    missing = []
    if not _present(env, "TELEGRAM_BOT_TOKEN"):
        missing.append("TELEGRAM_BOT_TOKEN")
    if not (_present(env, "TELEGRAM_DEFAULT_CHAT_ID") or _present(env, "TELEGRAM_ALLOWED_CHAT_IDS")):
        missing.append("TELEGRAM_DEFAULT_CHAT_ID or TELEGRAM_ALLOWED_CHAT_IDS")
    return missing
