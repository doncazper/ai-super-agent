from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_secrets_policy_docs_exist_and_use_correct_redaction_name() -> None:
    expected = [
        "docs/secrets/SECRETS_MANAGEMENT_POLICY.md",
        "docs/secrets/API_KEY_INVENTORY.md",
        "docs/secrets/LOCAL_ENV_SETUP.md",
        "docs/secrets/MACOS_KEYCHAIN_GUIDE.md",
        "docs/secrets/MACOS_KEYCHAIN_INTEGRATION.md",
        "docs/secrets/SECRET_REDACTION_POLICY.md",
        "docs/secrets/SECRET_LEAK_SCANNING.md",
        "docs/secrets/PROVIDER_SECRET_SETUP.md",
        "docs/git/SAFE_GIT_PREFLIGHT.md",
        "docs/decisions/secrets_management_architecture.md",
        "docs/templates/env_template.example",
    ]
    for relative in expected:
        assert (ROOT / relative).is_file(), relative

    assert not (ROOT / "docs/secrets/SECRET_REDATION_POLICY.md").exists()


def test_env_examples_are_placeholder_only_for_known_secret_names() -> None:
    texts = [
        (ROOT / ".env.example").read_text(encoding="utf-8"),
        (ROOT / "docs/templates/env_template.example").read_text(encoding="utf-8"),
    ]
    for text in texts:
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            secret_markers = ("SECRET", "API_KEY", "PASSWORD")
            token_key = key.endswith("_TOKEN") or "_TOKEN_" in key
            if token_key or any(marker in key for marker in secret_markers):
                assert value in {"", "false", "true", "0"}, key


def test_gitignore_covers_common_secret_artifacts() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for pattern in [".env", ".env.*", "*.pem", "*.key", "*token*.json", "*credential*.json"]:
        assert pattern in gitignore


def test_user_docs_link_secret_doctors_and_preflight() -> None:
    user_guide = (ROOT / "docs/USER_GUIDE.md").read_text(encoding="utf-8")
    provider_setup = (ROOT / "docs/secrets/PROVIDER_SECRET_SETUP.md").read_text(encoding="utf-8")

    for expected in [
        "python smart_agent.py secrets doctor",
        "python smart_agent.py secrets scan",
        "python smart_agent.py git preflight",
        "docs/secrets/PROVIDER_SECRET_SETUP.md",
    ]:
        assert expected in user_guide
    for provider in ["reddit", "serpapi", "brave", "weatherapi", "telegram", "gmail", "newsapi", "mediacloud", "microsoft", "github", "media"]:
        assert f"secrets doctor {provider}" in provider_setup
