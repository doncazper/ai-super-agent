from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .errors import UnknownSecretError
from .models import SecretDefinition


DOCS_PATH = "docs/secrets/API_KEY_INVENTORY.md"


def _definition(
    env_name: str,
    provider: str,
    description: str,
    required_for: str,
    sensitivity: str = "secret",
    storage: str = "Keychain/password manager/env; local .env only when ignored and untracked",
    rotation: str = "Rotate or revoke in the provider console if exposed.",
    status: str = "active",
) -> SecretDefinition:
    return SecretDefinition(
        secret_id=env_name.lower(),
        env_name=env_name,
        provider=provider,
        description=description,
        required_for=required_for,
        sensitivity=sensitivity,
        storage_recommendation=storage,
        docs_path=DOCS_PATH,
        rotation_url_or_note=rotation,
        placeholder_value="",
        status=status,
    )


DEFAULT_SECRET_DEFINITIONS: tuple[SecretDefinition, ...] = (
    _definition("REDDIT_CLIENT_ID", "reddit", "OAuth app client id.", "Reddit OAuth", "public_config"),
    _definition("REDDIT_CLIENT_SECRET", "reddit", "OAuth app client secret.", "Reddit OAuth"),
    _definition("REDDIT_REFRESH_TOKEN", "reddit", "OAuth refresh token.", "Reddit API reads"),
    _definition("SERPAPI_API_KEY", "serpapi", "SerpAPI key.", "Optional paid/quota web search"),
    _definition("BRAVE_SEARCH_API_KEY", "brave", "Brave Search API key.", "Optional quota web search"),
    _definition("WEATHERAPI_API_KEY", "weatherapi", "WeatherAPI key.", "Optional WeatherAPI provider"),
    _definition("TELEGRAM_BOT_TOKEN", "telegram", "Telegram bot token.", "Future Telegram scaffolding"),
    _definition("TELEGRAM_ALLOWED_CHAT_IDS", "telegram", "Telegram allowed chat ids.", "Future Telegram allowlist", "sensitive_config"),
    _definition("GMAIL_CLIENT_ID", "gmail", "Gmail OAuth client id.", "Gmail OAuth", "public_config"),
    _definition("GMAIL_CLIENT_SECRET", "gmail", "Gmail OAuth client secret.", "Gmail OAuth"),
    _definition("GMAIL_TOKEN_PATH", "gmail", "Path to Gmail OAuth token cache.", "Gmail OAuth", "sensitive_path", "Outside repo; do not commit token file"),
    _definition("GMAIL_SCOPES", "gmail", "Configured Gmail OAuth scopes.", "Gmail OAuth review", "sensitive_config"),
    _definition("NEWSAPI_API_KEY", "newsapi", "NewsAPI key.", "Optional NewsAPI provider"),
    _definition("MEDIACLOUD_API_KEY", "mediacloud", "Media Cloud key.", "Optional Media Cloud provider"),
    _definition("MICROSOFT_CLIENT_ID", "microsoft", "Microsoft app client id.", "Future Microsoft Graph", "public_config"),
    _definition("MICROSOFT_TENANT_ID", "microsoft", "Microsoft tenant id.", "Future Microsoft Graph", "sensitive_config"),
    _definition("MICROSOFT_CLIENT_SECRET", "microsoft", "Microsoft OAuth client secret.", "Future Microsoft Graph"),
    _definition("GITHUB_TOKEN", "github", "GitHub token.", "Optional future GitHub API access"),
    _definition("MEDIA_PROVIDER_API_KEY", "media", "Future media provider key.", "Future media provider"),
    _definition("OPENAI_API_KEY", "openai", "Optional future OpenAI API key.", "Future cloud provider", status="future"),
    _definition("ANTHROPIC_API_KEY", "anthropic", "Optional future Anthropic API key.", "Future cloud provider", status="future"),
    _definition("OTHER_PROVIDER_API_KEY", "other", "Other future provider key.", "Future provider", status="future"),
)


@dataclass(frozen=True)
class SecretRegistry:
    definitions: tuple[SecretDefinition, ...]

    def list(self) -> list[SecretDefinition]:
        return list(self.definitions)

    def providers(self) -> list[str]:
        return sorted({definition.provider for definition in self.definitions})

    def by_provider(self, provider: str) -> list[SecretDefinition]:
        normalized = provider.strip().casefold()
        return [definition for definition in self.definitions if definition.provider.casefold() == normalized]

    def get(self, secret_id_or_env_name: str) -> SecretDefinition:
        normalized = secret_id_or_env_name.strip().casefold()
        for definition in self.definitions:
            if definition.secret_id.casefold() == normalized or definition.env_name.casefold() == normalized:
                return definition
        raise UnknownSecretError(f"unknown secret: {secret_id_or_env_name}")

    def known_env_names(self) -> set[str]:
        return {definition.env_name for definition in self.definitions}

    def as_dicts(self, definitions: Iterable[SecretDefinition] | None = None) -> list[dict[str, str]]:
        return [definition.to_dict() for definition in (definitions or self.definitions)]


def default_secret_registry() -> SecretRegistry:
    return SecretRegistry(DEFAULT_SECRET_DEFINITIONS)
