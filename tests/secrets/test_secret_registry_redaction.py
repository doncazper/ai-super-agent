from __future__ import annotations

from agent.secrets.redaction import SecretRedactor
from agent.secrets.registry import default_secret_registry
from agent.ui.cli_commands import dispatch_cli


def test_registry_contains_known_secret_fields() -> None:
    registry = default_secret_registry()
    env_names = registry.known_env_names()

    assert "REDDIT_CLIENT_SECRET" in env_names
    assert "TELEGRAM_BOT_TOKEN" in env_names
    assert "GITHUB_TOKEN" in env_names
    assert registry.get("reddit_client_secret").provider == "reddit"


def test_redacts_fake_api_keys_and_tokens() -> None:
    text = "OPENAI_API_KEY=sk-testtesttesttest123456 and github_pat_1234567890abcdef1234567890"
    redacted = SecretRedactor().redact_text(text)

    assert "sk-testtesttesttest123456" not in redacted
    assert "github_pat_" not in redacted
    assert "[REDACTED]" in redacted


def test_redacts_nested_dicts_and_lists() -> None:
    payload = {
        "normal": "hello",
        "token": "fake-token-value",
        "nested": [{"GMAIL_CLIENT_SECRET": "fake-gmail-secret"}, "safe text"],
    }

    redacted = SecretRedactor().redact(payload)

    assert redacted["normal"] == "hello"
    assert redacted["token"] == "[REDACTED]"
    assert redacted["nested"][0]["GMAIL_CLIENT_SECRET"] == "[REDACTED]"


def test_redacts_known_env_var_values_when_provided() -> None:
    value = "fake-weather-secret-value"
    redacted = SecretRedactor(known_values={"WEATHERAPI_API_KEY": value}).redact_text(f"configured={value}")

    assert value not in redacted
    assert "[REDACTED]" in redacted


def test_does_not_over_redact_normal_text() -> None:
    text = "Set up the provider after reading the docs."

    assert SecretRedactor().redact_text(text) == text


def test_secrets_registry_cli_commands_are_redacted(capsys) -> None:
    assert dispatch_cli(["secrets", "list"]) == 0
    list_output = capsys.readouterr().out
    assert "REDDIT_CLIENT_SECRET" in list_output
    assert "fake-" not in list_output

    assert dispatch_cli(["secrets", "redaction-test"]) == 0
    redaction_output = capsys.readouterr().out
    assert "sk-testtest" not in redaction_output
    assert "ghp_" not in redaction_output
    assert '"passed": true' in redaction_output

    assert dispatch_cli(["secrets", "policy"]) == 0
    policy_output = capsys.readouterr().out
    assert "SECRETS_MANAGEMENT_POLICY.md" in policy_output
