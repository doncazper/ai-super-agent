from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from typing import Any, Mapping

TRUE_VALUES = {"1", "true", "yes", "on"}


def _enabled(env: Mapping[str, str], key: str) -> bool:
    return (env.get(key) or "").strip().casefold() in TRUE_VALUES


def _present(env: Mapping[str, str], key: str) -> bool:
    return bool((env.get(key) or "").strip())


def _parse_chat_ids(value: str) -> list[str]:
    return [item.strip() for item in value.replace(";", ",").split(",") if item.strip()]


@dataclass(frozen=True)
class TelegramAccessConfig:
    enabled: bool
    bot_token_present: bool
    default_chat_configured: bool
    allowed_chat_ids_configured: bool
    allowed_chat_count: int
    allow_send: bool
    allow_polling: bool
    allow_webhook: bool

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "TelegramAccessConfig":
        env = environ or os.environ
        allowed_ids = _parse_chat_ids(env.get("TELEGRAM_ALLOWED_CHAT_IDS", ""))
        return cls(
            enabled=_enabled(env, "TELEGRAM_ENABLED"),
            bot_token_present=_present(env, "TELEGRAM_BOT_TOKEN"),
            default_chat_configured=_present(env, "TELEGRAM_DEFAULT_CHAT_ID"),
            allowed_chat_ids_configured=bool(allowed_ids),
            allowed_chat_count=len(allowed_ids),
            allow_send=_enabled(env, "TELEGRAM_ALLOW_SEND"),
            allow_polling=_enabled(env, "TELEGRAM_ALLOW_POLLING"),
            allow_webhook=_enabled(env, "TELEGRAM_ALLOW_WEBHOOK"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def telegram_access_status(environ: Mapping[str, str] | None = None) -> dict[str, Any]:
    config = TelegramAccessConfig.from_env(environ)
    warnings: list[dict[str, str]] = []
    if not config.bot_token_present:
        warnings.append(
            {
                "code": "telegram_token_missing",
                "severity": "medium",
                "message": "TELEGRAM_BOT_TOKEN is not set; Telegram remains setup-only.",
            }
        )
    if not config.allowed_chat_ids_configured:
        warnings.append(
            {
                "code": "telegram_allowed_chats_missing",
                "severity": "medium",
                "message": "TELEGRAM_ALLOWED_CHAT_IDS is required before any future send-capable connector.",
            }
        )
    if config.allow_polling:
        warnings.append(
            {
                "code": "telegram_polling_requested",
                "severity": "high",
                "message": "Polling is requested by config but no polling loop is implemented or started.",
            }
        )
    if config.allow_webhook:
        warnings.append(
            {
                "code": "telegram_webhook_requested",
                "severity": "high",
                "message": "Webhook is requested by config but no webhook server is implemented or started.",
            }
        )
    send_ready = config.enabled and config.bot_token_present and config.allowed_chat_ids_configured and config.allow_send
    payload = {
        "connector": "telegram",
        "status": "warn" if warnings else "ok",
        "enabled": config.enabled,
        "configured": config.bot_token_present and config.allowed_chat_ids_configured,
        "token_present": config.bot_token_present,
        "token_value": "[REDACTED]" if config.bot_token_present else "",
        "default_chat_configured": config.default_chat_configured,
        "allowed_chat_ids_configured": config.allowed_chat_ids_configured,
        "allowed_chat_count": config.allowed_chat_count,
        "allow_send": config.allow_send,
        "allow_polling": config.allow_polling,
        "allow_webhook": config.allow_webhook,
        "future_send_ready": send_ready,
        "send_enabled_now": False,
        "polling_started": False,
        "webhook_server_started": False,
        "no_network_calls_made": True,
        "no_chat_reads": True,
        "no_messages_sent": True,
        "no_background_service": True,
        "trust_level": "UNTRUSTED_MESSAGE",
        "requires_approval_manager_for_future_send": True,
        "warnings": warnings,
        "setup_hint": "Set TELEGRAM_ENABLED=true, TELEGRAM_BOT_TOKEN, and TELEGRAM_ALLOWED_CHAT_IDS for future setup checks only; this scaffold still sends nothing.",
    }
    return payload
