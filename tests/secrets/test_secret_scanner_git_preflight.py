from __future__ import annotations

import json
import subprocess

from agent.secrets.git_preflight import GitPreflight
from agent.secrets.scanner import SecretLeakScanner
from agent.ui.cli_commands import dispatch_cli


def _git(cwd, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def test_fake_secret_detected_and_redacted(tmp_path) -> None:
    _git(tmp_path, "init")
    raw = "sk-liveabc1234567890SECRET"
    path = tmp_path / "config.txt"
    path.write_text(f"OPENAI_API_KEY={raw}\n", encoding="utf-8")
    _git(tmp_path, "add", "config.txt")

    result = SecretLeakScanner(tmp_path).scan()
    text = json.dumps(result)

    assert result["status"] == "fail"
    assert result["fail_count"] >= 1
    assert raw not in text
    assert "[REDACTED]" in text


def test_placeholder_ignored(tmp_path) -> None:
    _git(tmp_path, "init")
    path = tmp_path / ".env.example"
    path.write_text("OPENAI_API_KEY=\nGITHUB_TOKEN=<your-token>\n", encoding="utf-8")
    _git(tmp_path, "add", ".env.example")

    result = SecretLeakScanner(tmp_path).scan()

    assert result["status"] == "ok"
    assert result["fail_count"] == 0


def test_tracked_env_flagged(tmp_path) -> None:
    _git(tmp_path, "init")
    path = tmp_path / ".env"
    path.write_text("TOKEN=not-a-real-production-token\n", encoding="utf-8")
    _git(tmp_path, "add", "-f", ".env")

    result = SecretLeakScanner(tmp_path).scan()

    assert result["status"] == "fail"
    assert any(finding["kind"] == "sensitive_path_tracked" for finding in result["findings"])


def test_staged_scan_fixture(tmp_path) -> None:
    _git(tmp_path, "init")
    raw = "ghp_1234567890abcdef1234567890"
    path = tmp_path / "new.txt"
    path.write_text(f"token={raw}\n", encoding="utf-8")
    _git(tmp_path, "add", "new.txt")

    result = SecretLeakScanner(tmp_path).scan(staged=True)
    text = json.dumps(result)

    assert result["status"] == "fail"
    assert raw not in text


def test_private_key_pattern_flagged(tmp_path) -> None:
    _git(tmp_path, "init")
    path = tmp_path / "key.pem"
    path.write_text("-----BEGIN RSA PRIVATE KEY-----\nabc\n-----END RSA PRIVATE KEY-----\n", encoding="utf-8")
    _git(tmp_path, "add", "key.pem")

    result = SecretLeakScanner(tmp_path).scan()

    assert result["status"] == "fail"
    assert any(finding["kind"] in {"private_key", "sensitive_path_tracked"} for finding in result["findings"])


def test_git_preflight_wraps_scan(tmp_path) -> None:
    _git(tmp_path, "init")
    (tmp_path / "README.md").write_text("hello\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")

    result = GitPreflight(tmp_path).run(staged=True)

    assert result["status"] == "ok"
    assert result["safe_to_commit"] is True
    assert result["values_redacted"] is True


def test_cli_secret_scan_and_git_preflight(tmp_path, capsys) -> None:
    _git(tmp_path, "init")
    (tmp_path / "README.md").write_text("hello\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")

    assert dispatch_cli(["secrets", "scan", "--staged"], project_root=tmp_path) == 0
    scan_output = capsys.readouterr().out
    assert '"values_redacted": true' in scan_output

    assert dispatch_cli(["git", "preflight", "--staged"], project_root=tmp_path) == 0
    preflight_output = capsys.readouterr().out
    assert '"safe_to_commit": true' in preflight_output
