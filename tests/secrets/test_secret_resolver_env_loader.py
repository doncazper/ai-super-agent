from __future__ import annotations

import subprocess

from agent.secrets.env_loader import EnvFileLoader
from agent.secrets.resolver import SecretResolver
from agent.secrets.sources import env_file_tracked, source_statuses
from agent.ui.cli_commands import dispatch_cli


def test_resolves_env_var_over_missing_env_file(tmp_path) -> None:
    resolver = SecretResolver(project_root=tmp_path, environ={"SERPAPI_API_KEY": "fake-serp-secret"})
    result = resolver.resolve("SERPAPI_API_KEY")

    assert result.present is True
    assert result.source == "environment"
    assert "fake-serp-secret" not in str(result.to_dict())


def test_resolves_fake_dotenv(tmp_path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("BRAVE_SEARCH_API_KEY=fake-brave-secret\n", encoding="utf-8")

    resolver = SecretResolver(project_root=tmp_path, environ={}, env_path=env_file)
    result = resolver.resolve("BRAVE_SEARCH_API_KEY")

    assert result.present is True
    assert result.source == "local_env"
    assert "fake-brave-secret" not in str(result.to_dict())


def test_env_var_overrides_dotenv(tmp_path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("WEATHERAPI_API_KEY=fake-file-secret\n", encoding="utf-8")

    resolver = SecretResolver(
        project_root=tmp_path,
        environ={"WEATHERAPI_API_KEY": "fake-env-secret"},
        env_path=env_file,
    )
    result = resolver.resolve("WEATHERAPI_API_KEY")

    assert result.present is True
    assert result.source == "environment"
    assert "fake-file-secret" not in str(result.to_dict())
    assert "fake-env-secret" not in str(result.to_dict())


def test_missing_secret_returns_missing(tmp_path) -> None:
    resolver = SecretResolver(project_root=tmp_path, environ={})

    result = resolver.resolve("GITHUB_TOKEN")

    assert result.present is False
    assert result.source is None
    assert "GITHUB_TOKEN" in result.setup_hint


def test_invalid_dotenv_line_warning_does_not_print_line(tmp_path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("INVALID SECRET VALUE\nSERPAPI_API_KEY=fake-serp-secret\n", encoding="utf-8")

    result = EnvFileLoader().load(env_file)

    assert result.values["SERPAPI_API_KEY"] == "fake-serp-secret"
    assert result.warnings[0]["code"] == "invalid_env_line"
    assert "INVALID SECRET VALUE" not in str(result.redacted_dict())


def test_env_tracked_warning_mocked(tmp_path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, stdout=subprocess.DEVNULL)
    (tmp_path / ".env").write_text("SERPAPI_API_KEY=fake-serp-secret\n", encoding="utf-8")
    subprocess.run(["git", "add", ".env"], cwd=tmp_path, check=True, stdout=subprocess.DEVNULL)

    assert env_file_tracked(tmp_path, tmp_path / ".env") is True
    local_env = [source for source in source_statuses(project_root=tmp_path, environ={}) if source.source_id == "local_env"][0]
    assert any(warning["code"] == "env_tracked" for warning in local_env.warnings)


def test_values_redacted_from_status(tmp_path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("TELEGRAM_BOT_TOKEN=123456:fakefakefakefakefakefake\n", encoding="utf-8")

    status = SecretResolver(project_root=tmp_path, environ={}, env_path=env_file).status()

    assert status["present_count"] >= 1
    assert "123456:fake" not in str(status)


def test_sources_cli_reports_metadata_without_keychain_access(capsys, tmp_path) -> None:
    assert dispatch_cli(["secrets", "sources"], project_root=tmp_path) == 0
    output = capsys.readouterr().out

    assert "macos_keychain" in output
    assert '"keychain_accessed": false' in output
    assert "fake-" not in output
