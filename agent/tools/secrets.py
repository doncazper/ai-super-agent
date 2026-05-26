from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from agent.secrets.registry import default_secret_registry
from agent.secrets.redaction import SecretRedactor
from agent.secrets.sources import source_statuses
from agent.secrets.keychain import KeychainAdapter
from agent.secrets.scanner import SecretLeakScanner
from agent.secrets.git_preflight import GitPreflight


def _schema(
    name: str,
    description: str,
    properties: dict[str, Any] | None = None,
    required: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties or {},
                "required": required or [],
                "additionalProperties": False,
            },
        },
    }


SECRETS_SCHEMAS: dict[str, dict[str, Any]] = {
    "secrets.list": _schema("secrets.list", "List known secret metadata without reading values."),
    "secrets.redaction_test": _schema("secrets.redaction_test", "Run a local fake-secret redaction self-test without reading real secrets."),
    "secrets.policy": _schema("secrets.policy", "Show secrets management policy docs and safety boundaries."),
    "secrets.sources": _schema("secrets.sources", "Show approved secret sources and local .env hygiene without reading values."),
    "secrets.keychain.status": _schema("secrets.keychain.status", "Show optional macOS Keychain adapter status without accessing Keychain."),
    "secrets.keychain.get": _schema(
        "secrets.keychain.get",
        "Dry-run a future Keychain secret lookup without reading values.",
        {"secret_id": {"type": "string"}, "dry_run": {"type": "boolean"}},
        ["secret_id", "dry_run"],
    ),
    "secrets.keychain.set": _schema(
        "secrets.keychain.set",
        "Dry-run a future Keychain secret write without writing values.",
        {"secret_id": {"type": "string"}, "dry_run": {"type": "boolean"}},
        ["secret_id", "dry_run"],
    ),
    "secrets.scan": _schema(
        "secrets.scan",
        "Run a best-effort redacted secret leak scan.",
        {"staged": {"type": "boolean"}},
        ["staged"],
    ),
    "git.preflight": _schema(
        "git.preflight",
        "Run redacted Git preflight checks before commit/push.",
        {"staged": {"type": "boolean"}},
        ["staged"],
    ),
}


def _with_audit(payload: dict[str, Any], summary: str) -> dict[str, Any]:
    payload["_audit"] = {
        "files_read": [],
        "files_written": [],
        "commands_run": [],
        "network_domains": [],
        "result_summary": summary,
    }
    return payload


def make_secret_tools(project_root: str | Path = ".") -> dict[str, Callable[..., dict[str, Any]]]:
    root = Path(project_root).resolve()

    def list_secrets() -> dict[str, Any]:
        registry = default_secret_registry()
        secrets = registry.as_dicts()
        return _with_audit(
            {
                "status": "ok",
                "secret_count": len(secrets),
                "providers": registry.providers(),
                "secrets": secrets,
                "values_read": False,
                "values_returned": False,
            },
            "Listed secret registry metadata without reading values.",
        )

    def redaction_test() -> dict[str, Any]:
        fake = {
            "api_key": "sk-testtesttesttest123456",
            "nested": [{"GITHUB_TOKEN": "ghp_fake1234567890abcdef1234567890"}],
            "text": "TELEGRAM_BOT_TOKEN=123456:fakefakefakefakefakefake",
        }
        redacted = SecretRedactor().redact(fake)
        raw = str(fake)
        redacted_text = str(redacted)
        passed = "sk-testtest" not in redacted_text and "ghp_" not in redacted_text and "123456:fake" not in redacted_text
        return _with_audit(
            {
                "status": "ok" if passed else "failed",
                "fake_values_only": True,
                "real_values_read": False,
                "raw_fake_values_returned": False,
                "contains_raw_before_redaction": SecretRedactor().contains_secret(raw),
                "redacted_sample": redacted,
                "passed": passed,
            },
            "Ran fake-secret redaction self-test.",
        )

    def policy() -> dict[str, Any]:
        docs = [
            "docs/secrets/SECRETS_MANAGEMENT_POLICY.md",
            "docs/secrets/API_KEY_INVENTORY.md",
            "docs/secrets/LOCAL_ENV_SETUP.md",
            "docs/secrets/SECRET_REDACTION_POLICY.md",
        ]
        return _with_audit(
            {
                "status": "ok",
                "docs": docs,
                "docs_exist": {path: (root / path).exists() for path in docs},
                "real_secrets_allowed_in_repo": False,
                "keychain_required": False,
                "env_supported": True,
                "local_env_supported_when_ignored": True,
                "values_read": False,
                "values_returned": False,
            },
            "Reported secrets policy metadata.",
        )

    def sources() -> dict[str, Any]:
        sources_payload = [source.to_dict() for source in source_statuses(project_root=root)]
        return _with_audit(
            {
                "status": "ok",
                "values_read": False,
                "values_returned": False,
                "source_order": sources_payload,
                "keychain_accessed": False,
            },
            "Reported secret source metadata without reading values.",
        )

    def keychain_status() -> dict[str, Any]:
        return _with_audit(
            KeychainAdapter().status() | {"keychain_accessed": False},
            "Reported Keychain adapter status without accessing Keychain.",
        )

    def keychain_get(secret_id: str, dry_run: bool) -> dict[str, Any]:
        if not dry_run:
            return _with_audit(
                {
                    "status": "blocked",
                    "secret_id": secret_id,
                    "dry_run": False,
                    "value_returned": False,
                    "keychain_accessed": False,
                    "error": "Real Keychain reads are not enabled in v1; rerun with --dry-run.",
                },
                "Blocked real Keychain read.",
            )
        return _with_audit(KeychainAdapter().dry_run_get(secret_id), "Dry-ran Keychain get without reading values.")

    def keychain_set(secret_id: str, dry_run: bool) -> dict[str, Any]:
        if not dry_run:
            return _with_audit(
                {
                    "status": "blocked",
                    "secret_id": secret_id,
                    "dry_run": False,
                    "value_written": False,
                    "keychain_accessed": False,
                    "error": "Real Keychain writes are not enabled in v1; rerun with --dry-run.",
                },
                "Blocked real Keychain write.",
            )
        return _with_audit(KeychainAdapter().dry_run_set(secret_id), "Dry-ran Keychain set without writing values.")

    def secrets_scan(staged: bool) -> dict[str, Any]:
        payload = SecretLeakScanner(root).scan(staged=staged)
        return _with_audit(payload, "Ran redacted secret leak scan.")

    def git_preflight(staged: bool) -> dict[str, Any]:
        payload = GitPreflight(root).run(staged=staged)
        return _with_audit(payload, "Ran redacted Git preflight.")

    return {
        "secrets.list": list_secrets,
        "secrets.redaction_test": redaction_test,
        "secrets.policy": policy,
        "secrets.sources": sources,
        "secrets.keychain.status": keychain_status,
        "secrets.keychain.get": keychain_get,
        "secrets.keychain.set": keychain_set,
        "secrets.scan": secrets_scan,
        "git.preflight": git_preflight,
    }
