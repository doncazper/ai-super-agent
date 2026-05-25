from __future__ import annotations

import json
import subprocess

from agent.connectors.secret_doctor import provider_status
from agent.forums.reddit.doctor import reddit_auth_check, reddit_doctor, reddit_status
from agent.ui.cli_commands import dispatch_cli
from agent.ui.command_registry import get_command
from agent.ui.connectors import connector_status, format_connectors_json


REDDIT_SECRET = "reddit-" + "secret-value"


def _configured_env() -> dict[str, str]:
    return {
        "REDDIT_ENABLED": "true",
        "REDDIT_CLIENT_ID": "reddit-client-id",
        "REDDIT_CLIENT_SECRET": REDDIT_SECRET,
        "REDDIT_USER_AGENT": "ai-super-agent:config-doctor:v1 (by /u/local-test)",
        "REDDIT_REFRESH_TOKEN": "refresh-" + "secret-value",
    }


def test_reddit_doctor_missing_config_shows_setup_hints(tmp_path) -> None:
    report = reddit_doctor(project_root=tmp_path, environ={})

    assert report["connector"] == "reddit"
    assert report["enabled"] is False
    assert report["configured"] is False
    assert report["no_api_calls_made"] is True
    assert report["no_post_comment_content_fetched"] is True
    assert "REDDIT_CLIENT_ID" in report["credential_status"]["missing_env"]
    assert any(warning["code"] == "reddit_disabled" for warning in report["warnings"])
    assert "Reddit connector is disabled" in report["setup_hint"]


def test_reddit_doctor_redacts_secrets(tmp_path) -> None:
    env = _configured_env()

    report = reddit_doctor(project_root=tmp_path, environ=env)
    text = json.dumps(report)

    assert REDDIT_SECRET not in text
    assert env["REDDIT_REFRESH_TOKEN"] not in text
    assert report["credential_status"]["client_secret_configured"] is True
    assert report["credential_status"]["refresh_token_configured"] is True


def test_reddit_doctor_warns_token_path_inside_repo(tmp_path) -> None:
    token_path = tmp_path / "reddit-token.json"
    token_path.write_text("{}", encoding="utf-8")
    env = _configured_env() | {"REDDIT_REFRESH_TOKEN": str(token_path)}

    report = reddit_doctor(project_root=tmp_path, environ=env)

    assert any(warning["code"] == "reddit_token_path_inside_repo" for warning in report["warnings"])


def test_reddit_doctor_warns_if_env_is_tracked(tmp_path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, stdout=subprocess.DEVNULL)
    (tmp_path / ".env").write_text("REDDIT_CLIENT_SECRET=not-a-real-secret\n", encoding="utf-8")
    subprocess.run(["git", "add", ".env"], cwd=tmp_path, check=True, stdout=subprocess.DEVNULL)

    report = reddit_doctor(project_root=tmp_path, environ={})

    assert any(warning["code"] == "env_tracked" for warning in report["warnings"])


def test_reddit_doctor_warns_for_generic_user_agent(tmp_path) -> None:
    env = _configured_env() | {"REDDIT_USER_AGENT": "python-requests"}

    report = reddit_doctor(project_root=tmp_path, environ=env)

    assert any(warning["code"] == "reddit_user_agent_generic" for warning in report["warnings"])


def test_reddit_disabled_connector_status_works(tmp_path) -> None:
    status = reddit_status(project_root=tmp_path, environ={})

    assert status["status"] == "disabled"
    assert status["enabled"] is False
    assert status["configured"] is False
    assert status["rate_limit"]["max_requests_per_minute"] == 60
    assert status["retention"]["cache_ttl_seconds"] == 86400
    assert all(value == "disabled" for value in status["disabled_write_actions"].values())


def test_connectors_status_reddit_does_not_reveal_secrets(monkeypatch) -> None:
    env = _configured_env()
    for key, value in env.items():
        monkeypatch.setenv(key, value)

    payload = connector_status("reddit")
    text = format_connectors_json(payload)

    assert payload["name"] == "reddit"
    assert payload["configured"] is True
    assert REDDIT_SECRET not in text
    assert env["REDDIT_REFRESH_TOKEN"] not in text
    assert provider_status("reddit", environ=env).to_dict()["metadata"]["no_post_comment_content_fetched"] is True


def test_reddit_auth_check_mocked_success(tmp_path) -> None:
    def fake_auth(config, env):
        return {
            "ok": True,
            "http_status": 200,
            "endpoint_class": "oauth_token",
            "network_domains": ["www.reddit.com"],
            "scope_count": 1,
            "expires_in_seconds": 3600,
            "errors": [],
        }

    report = reddit_auth_check(project_root=tmp_path, environ=_configured_env(), auth_client=fake_auth)

    assert report["status"] == "ok"
    assert report["auth_check_attempted"] is True
    assert report["token_valid"] is True
    assert report["network_domains"] == ["www.reddit.com"]
    assert report["content_endpoints_called"] == []
    assert report["no_post_comment_content_fetched"] is True


def test_reddit_auth_check_mocked_failure(tmp_path) -> None:
    def fake_auth(config, env):
        return {
            "ok": False,
            "http_status": 401,
            "endpoint_class": "oauth_token",
            "network_domains": ["www.reddit.com"],
            "errors": [{"code": "reddit_http_error", "message": "Reddit OAuth endpoint returned HTTP 401"}],
        }

    report = reddit_auth_check(project_root=tmp_path, environ=_configured_env(), auth_client=fake_auth)

    assert report["status"] == "error"
    assert report["token_valid"] is False
    assert report["errors"][0]["code"] == "reddit_http_error"
    assert report["content_endpoints_called"] == []


def test_reddit_auth_check_audited_and_no_content_fetch(monkeypatch, tmp_path, capsys) -> None:
    def fake_perform(config, env):
        return {
            "ok": True,
            "http_status": 200,
            "endpoint_class": "oauth_token",
            "network_domains": ["www.reddit.com"],
            "scope_count": 1,
            "errors": [],
        }

    for key, value in _configured_env().items():
        monkeypatch.setenv(key, value)
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("AUDIT_LOG_PATH", str(audit_path))
    monkeypatch.setattr("agent.forums.reddit.doctor._perform_reddit_auth_check", fake_perform)

    assert dispatch_cli(["reddit", "auth-check"], project_root=tmp_path) == 0
    output = json.loads(capsys.readouterr().out)
    audit_text = audit_path.read_text(encoding="utf-8")

    assert output["content_endpoints_called"] == []
    assert output["no_post_comment_content_fetched"] is True
    assert "reddit.auth_check" in audit_text
    assert "www.reddit.com" in audit_text
    assert REDDIT_SECRET not in audit_text
    assert "/comments" not in audit_text


def test_reddit_cli_status_and_doctor(monkeypatch, tmp_path, capsys) -> None:
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))

    assert dispatch_cli(["reddit", "status"], project_root=tmp_path) == 0
    status = json.loads(capsys.readouterr().out)
    assert status["no_api_calls_made"] is True

    assert dispatch_cli(["reddit", "doctor"], project_root=tmp_path) == 0
    doctor = json.loads(capsys.readouterr().out)
    assert doctor["no_post_comment_content_fetched"] is True


def test_reddit_commands_registered() -> None:
    for command_id in ("CMD-REDDIT-001", "CMD-REDDIT-002", "CMD-REDDIT-003", "CMD-CONN-010"):
        record = get_command(command_id)
        assert record is not None
        assert record.example
        assert record.risk_level in {"SAFE", "LOW"}
