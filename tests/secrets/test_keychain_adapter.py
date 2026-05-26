from __future__ import annotations

from agent.secrets.keychain import KeychainAdapter
from agent.ui.cli_commands import dispatch_cli


def test_non_macos_keychain_unsupported() -> None:
    status = KeychainAdapter(platform_name="Linux").status()

    assert status["supported"] is False
    assert status["enabled"] is False
    assert status["real_access_enabled"] is False


def test_macos_status_is_optional_and_no_real_access() -> None:
    status = KeychainAdapter(platform_name="Darwin").status()

    assert status["supported"] is True
    assert status["enabled"] is False
    assert status["real_access_enabled"] is False
    assert "dry-run" in str(status["setup_hint"])


def test_dry_run_get_returns_no_value() -> None:
    payload = KeychainAdapter(platform_name="Darwin").dry_run_get("github_token")

    assert payload["status"] == "requires_setup"
    assert payload["secret_id"] == "github_token"
    assert payload["env_name"] == "GITHUB_TOKEN"
    assert payload["value_returned"] is False
    assert payload["keychain_accessed"] is False
    assert "ghp_" not in str(payload)


def test_dry_run_set_does_not_write() -> None:
    payload = KeychainAdapter(platform_name="Darwin").dry_run_set("github_token")

    assert payload["status"] == "requires_setup"
    assert payload["value_written"] is False
    assert payload["keychain_accessed"] is False


def test_keychain_cli_status_and_dry_runs_are_metadata_only(capsys, tmp_path) -> None:
    assert dispatch_cli(["secrets", "keychain", "status"], project_root=tmp_path) == 0
    status_output = capsys.readouterr().out
    assert '"keychain_accessed": false' in status_output
    assert '"real_access_enabled": false' in status_output

    assert dispatch_cli(["secrets", "keychain", "get", "github_token", "--dry-run"], project_root=tmp_path) == 0
    get_output = capsys.readouterr().out
    assert '"value_returned": false' in get_output
    assert '"keychain_accessed": false' in get_output
    assert "ghp_" not in get_output

    assert dispatch_cli(["secrets", "keychain", "set", "github_token", "--dry-run"], project_root=tmp_path) == 0
    set_output = capsys.readouterr().out
    assert '"value_written": false' in set_output
    assert '"keychain_accessed": false' in set_output


def test_non_dry_run_keychain_get_is_blocked(capsys, tmp_path) -> None:
    assert dispatch_cli(["secrets", "keychain", "get", "github_token"], project_root=tmp_path) == 0
    output = capsys.readouterr().out

    assert '"status": "blocked"' in output
    assert '"value_returned": false' in output
    assert '"keychain_accessed": false' in output
