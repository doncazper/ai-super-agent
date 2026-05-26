from __future__ import annotations

import json
import os
import stat
import subprocess
from pathlib import Path

import pytest

from agent.launcher import diagnostics
from agent.launcher.cli import installer_main, launcher_main
from agent.launcher.diagnostics import (
    choose_python,
    default_repo_path,
    diagnose,
    install_dir_in_path,
    is_valid_repo,
    make_default_config,
    repo_candidate_statuses,
    save_config,
    validate_alias,
    verify_repo,
)
from agent.launcher.generator import generate_launcher_script, launcher_path
from agent.launcher.models import RepairLevel, config_path_for_home
from agent.launcher.repair import repair_venv, run_level1_repairs, write_shell_profile_path


def make_repo(path: Path, *, executable_agent: bool = True, with_venv: bool = False) -> Path:
    (path / "scripts").mkdir(parents=True)
    (path / "docs").mkdir(parents=True)
    (path / "smart_agent.py").write_text("print('ok')\n", encoding="utf-8")
    (path / "pyproject.toml").write_text("[project]\nname='fake'\n", encoding="utf-8")
    (path / "AGENTS.md").write_text("# rules\n", encoding="utf-8")
    (path / "docs" / "PROJECT_STATE.md").write_text("# state\n", encoding="utf-8")
    agent = path / "scripts" / "agent"
    agent.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    if executable_agent:
        agent.chmod(agent.stat().st_mode | stat.S_IXUSR)
    if with_venv:
        venv_python = path / ".venv" / "bin" / "python"
        venv_python.parent.mkdir(parents=True)
        venv_python.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
        venv_python.chmod(venv_python.stat().st_mode | stat.S_IXUSR)
    return path


@pytest.mark.parametrize("alias", ["smartagent", "sa", "agent_1", "sam-agent"])
def test_alias_validation_accepts_safe_aliases(alias: str) -> None:
    ok, error = validate_alias(alias)
    assert ok
    assert error == ""


@pytest.mark.parametrize("alias", ["", "1agent", "bad alias", "bad/alias", "bad;alias", "bad$alias"])
def test_alias_validation_rejects_unsafe_aliases(alias: str) -> None:
    ok, error = validate_alias(alias)
    assert not ok
    assert error


def test_generated_launcher_content_passes_args_and_handles_repo(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    config_path = tmp_path / "launcher.json"

    text = generate_launcher_script(repo_path=repo, config_path=config_path)

    assert "SMARTAGENT_REPO=" in text
    assert "valid_repo()" in text
    assert 'exec "$PY" -m agent.launcher.cli' in text
    assert '"$@"' in text
    assert "--repair-path --repo" in text
    assert "brew install python@3.12" in text
    assert "$HOME/Documents/ai-super-agent" in text
    assert "fewer than two" not in text


def test_install_path_calculation() -> None:
    assert launcher_path("/tmp/example", "sa") == Path("/tmp/example/sa")


def test_path_detection() -> None:
    assert install_dir_in_path("/tmp/bin", env_path=f"/usr/bin{os.pathsep}/tmp/bin")
    assert not install_dir_in_path("/tmp/bin", env_path="/usr/bin")


def test_dry_run_install_writes_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(tmp_path / "repo")
    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))

    code = installer_main(
        [
            "--alias",
            "smartagentpytest",
            "--install-dir",
            str(home / "bin"),
            "--repo",
            str(repo),
            "--dry-run",
        ]
    )

    assert code == 0
    assert not (home / "bin" / "smartagentpytest").exists()
    assert not config_path_for_home(home).exists()
    assert "would write" in capsys.readouterr().out


def test_install_from_current_git_repo_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(tmp_path / "ai-super-agent")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.chdir(repo)

    code = installer_main(["--alias", "smartagentpytest", "--install-dir", str(home / "bin"), "--dry-run"])

    assert code == 0
    output = capsys.readouterr().out
    assert "would write" in output


def test_install_from_explicit_repo_path_saves_verified_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = make_repo(tmp_path / "repo")
    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))

    code = installer_main(["--alias", "smartagentpytest", "--install-dir", str(home / "bin"), "--repo", str(repo)])

    assert code == 0
    config = diagnostics.load_config(config_path_for_home(home))
    assert config is not None
    assert config.repo_path == str(repo)
    assert config.last_repo_verification_status == "ok"


def test_launcher_config_read_write(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    config_path = tmp_path / "launcher.json"
    config = make_default_config(repo, alias="sa", install_dir=tmp_path / "bin")

    save_config(config, config_path)
    loaded = diagnostics.load_config(config_path)

    assert loaded is not None
    assert loaded.repo_path == str(repo)
    assert loaded.alias == "sa"
    assert loaded.auto_repair_safe_enabled is True
    assert loaded.venv_repair_requires_explicit is True


def test_repo_detection_and_invalid_path_behavior(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")

    assert is_valid_repo(repo)
    assert not is_valid_repo(tmp_path / "missing")
    assert verify_repo(repo)["valid"] is True


def test_invalid_repo_rejection_requires_strong_markers(tmp_path: Path) -> None:
    path = tmp_path / "weak"
    (path / "scripts").mkdir(parents=True)
    (path / "smart_agent.py").write_text("", encoding="utf-8")
    (path / "scripts" / "agent").write_text("", encoding="utf-8")
    (path / "pyproject.toml").write_text("", encoding="utf-8")

    result = verify_repo(path)

    assert result["valid"] is False
    assert "fewer than two" in str(result["reason"])


def test_one_valid_fallback_repo_auto_repair_behavior(tmp_path: Path) -> None:
    home = tmp_path / "home"
    fallback = make_repo(home / "Documents" / "AI Super Agent")
    config = make_default_config(tmp_path / "moved", install_dir=home / "bin")

    report = diagnose(config=config, home=home, cwd=tmp_path / "elsewhere")

    assert report.repo_path == str(fallback)
    assert any(finding.code == "repo_path_auto_repair" for finding in report.findings)


def test_multiple_valid_repo_candidates_stop_behavior(tmp_path: Path) -> None:
    home = tmp_path / "home"
    make_repo(home / "Documents" / "AI Super Agent")
    make_repo(home / "Desktop" / "AI Super Agent")
    config = make_default_config(tmp_path / "moved", install_dir=home / "bin")

    report = diagnose(config=config, home=home, cwd=tmp_path / "elsewhere")

    assert report.repo_valid is False
    assert any(finding.code == "multiple_repo_candidates" for finding in report.findings)
    assert any(finding.repair_level is RepairLevel.LEVEL_2_COMMAND_REQUIRED for finding in report.findings)


def test_no_repo_found_prints_clone_setup_instructions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setenv("HOME", str(tmp_path / "home"))

    code = installer_main(["--repo", str(tmp_path / "missing"), "--alias", "smartagentpytest"])

    assert code == 2
    err = capsys.readouterr().err
    assert "git clone https://github.com/doncazper/ai-super-agent.git" in err


def test_set_repo_verifies_before_saving(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(tmp_path / "repo")
    config_path = tmp_path / "launcher.json"

    code = launcher_main(["--config", str(config_path), "--set-repo", str(repo)])

    assert code == 0
    config = diagnostics.load_config(config_path)
    assert config is not None
    assert config.repo_path == str(repo)
    assert json.loads(capsys.readouterr().out)["set_repo"]["ok"] is True


def test_set_repo_rejects_invalid_path(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    config_path = tmp_path / "launcher.json"

    code = launcher_main(["--config", str(config_path), "--set-repo", str(tmp_path / "missing")])

    assert code == 2
    assert json.loads(capsys.readouterr().out)["set_repo"]["ok"] is False


def test_repair_path_updates_only_when_exactly_one_valid_repo_found(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    home = tmp_path / "home"
    fallback = make_repo(home / "Documents" / "ai-super-agent")
    config_path = tmp_path / "launcher.json"
    save_config(make_default_config(tmp_path / "moved", install_dir=home / "bin"), config_path)
    monkeypatch.setenv("HOME", str(home))
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)

    code = launcher_main(["--config", str(config_path), "--repair-path"])

    assert code == 0
    config = diagnostics.load_config(config_path)
    assert config is not None
    assert config.repo_path == str(fallback)
    assert "updated launcher config" in capsys.readouterr().out


def test_repair_path_stops_on_multiple_valid_repos(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    home = tmp_path / "home"
    make_repo(home / "Documents" / "AI Super Agent")
    make_repo(home / "Desktop" / "ai-super-agent")
    config_path = tmp_path / "launcher.json"
    save_config(make_default_config(tmp_path / "moved", install_dir=home / "bin"), config_path)
    monkeypatch.setenv("HOME", str(home))
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)

    code = launcher_main(["--config", str(config_path), "--repair-path"])

    assert code == 2
    config = diagnostics.load_config(config_path)
    assert config is not None
    assert config.repo_path == str(tmp_path / "moved")
    output = json.loads(capsys.readouterr().out)
    assert output["repair_path"]["ok"] is False
    assert "multiple valid repo candidates" in output["repair_path"]["reason"]


def test_repo_status_verifies_configured_repo(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(tmp_path / "repo")
    config_path = tmp_path / "launcher.json"
    save_config(make_default_config(repo), config_path)

    code = launcher_main(["--config", str(config_path), "--repo-status"])

    assert code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["configured_repo_path"] == str(repo)
    assert output["valid"] is True
    assert output["reason"] == "ok"


def test_repo_prints_configured_path(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(tmp_path / "repo")
    config_path = tmp_path / "launcher.json"
    save_config(make_default_config(repo), config_path)

    code = launcher_main(["--config", str(config_path), "--repo"])

    assert code == 0
    assert capsys.readouterr().out.strip() == str(repo)


def test_find_repos_does_not_scan_whole_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    home = tmp_path / "home"
    expected = make_repo(home / "Documents" / "ai-super-agent")
    ignored = make_repo(home / "nested" / "random" / "AI Super Agent")
    monkeypatch.setenv("HOME", str(home))
    config_path = tmp_path / "launcher.json"

    code = launcher_main(["--config", str(config_path), "--find-repos"])

    assert code == 0
    output = json.loads(capsys.readouterr().out)
    paths = {candidate["path"] for candidate in output["candidates"] if candidate["valid"]}
    assert str(expected) in paths
    assert str(ignored) not in paths
    assert output["scanned"] == "safe_likely_locations_only"


def test_python_version_selection_prefers_venv(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo", with_venv=True)

    monkeypatch.setattr(diagnostics, "python_candidate_paths", lambda repo_path: [(str(Path(repo_path) / ".venv" / "bin" / "python"), "repo_venv"), ("/usr/bin/python3", "python3")])
    monkeypatch.setattr(diagnostics, "probe_python_version", lambda path: (3, 12, 1) if ".venv" in str(path) else (3, 11, 1))

    candidate = choose_python(repo)

    assert candidate is not None
    assert candidate.source == "repo_venv"
    assert candidate.usable


def test_apple_python_39_rejected_when_better_runtime_exists(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    python312 = tmp_path / "python3.12"
    python312.write_text("", encoding="utf-8")

    monkeypatch.setattr(diagnostics, "python_candidate_paths", lambda repo_path: [("/usr/bin/python3", "python3"), (str(python312), "python3.12")])
    monkeypatch.setattr(diagnostics, "probe_python_version", lambda path: (3, 9, 6) if str(path) == "/usr/bin/python3" else (3, 12, 2))

    candidate = choose_python(repo)

    assert candidate is not None
    assert candidate.executable == str(python312)
    assert candidate.version == (3, 12, 2)


def test_missing_venv_prints_stronger_repair_command(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    config = make_default_config(repo)

    report = diagnose(config=config)

    missing = [finding for finding in report.findings if finding.code == "venv_missing"]
    assert missing
    assert missing[0].repair_level is RepairLevel.LEVEL_2_COMMAND_REQUIRED
    assert missing[0].next_command == "smartagent --repair-venv"


def test_scripts_agent_chmod_repair(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo", executable_agent=False)
    config_path = tmp_path / "launcher.json"
    config = make_default_config(repo, install_dir=tmp_path / "bin")
    report = diagnose(config=config)

    result = run_level1_repairs(report, config=config, config_path=config_path, wrapper_path=None)

    assert result.ok
    assert os.access(repo / "scripts" / "agent", os.X_OK)


def test_repair_venv_dry_run_does_not_install(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")

    result = repair_venv(repo, dry_run=True)

    assert result.ok
    assert any("pip install" in item for item in result.changed)
    assert not (repo / ".venv").exists()


def test_repair_venv_does_not_delete_existing_broken_venv(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    (repo / ".venv").mkdir()

    result = repair_venv(repo, dry_run=False)

    assert result.ok
    assert (repo / ".venv").exists()
    assert any("will not be deleted" in item for item in result.skipped)
    assert any("mv .venv .venv.backup" in item for item in result.next_commands)


def test_shell_profile_write_opt_in_idempotent(tmp_path: Path) -> None:
    profile = tmp_path / ".zshrc"

    first = write_shell_profile_path(profile, tmp_path / "bin")
    second = write_shell_profile_path(profile, tmp_path / "bin")

    assert first.ok
    assert second.ok
    text = profile.read_text(encoding="utf-8")
    assert text.count("export PATH=") == 1


def test_repair_does_not_perform_level2_actions(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    config = make_default_config(repo)
    report = diagnose(config=config)

    result = run_level1_repairs(report, config=config, config_path=tmp_path / "launcher.json")

    assert result.ok
    assert not (repo / ".venv").exists()
    assert "smartagent --repair-venv" in result.next_commands


def test_launcher_doctor_outputs_repair_levels(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    repo = make_repo(tmp_path / "repo")
    config_path = tmp_path / "launcher.json"
    save_config(make_default_config(repo, install_dir=tmp_path / "bin"), config_path)
    monkeypatch.setattr(diagnostics, "python_candidate_paths", lambda repo_path: [])

    code = launcher_main(["--config", str(config_path), "--doctor"])

    output = json.loads(capsys.readouterr().out)
    assert code == 1
    assert any(finding["repair_level"] == "level_3_manual_required" for finding in output["findings"])


def test_launcher_no_args_launches_interactive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = make_repo(tmp_path / "repo")
    config_path = tmp_path / "launcher.json"
    save_config(make_default_config(repo, install_dir=tmp_path / "bin"), config_path)
    calls: list[list[str]] = []
    monkeypatch.setattr(diagnostics, "probe_python_version", lambda path: (3, 12, 1))

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr("agent.launcher.cli.subprocess.run", fake_run)

    code = launcher_main(["--config", str(config_path)])

    assert code == 0
    assert calls
    assert calls[-1][-1] == "--interactive"


def test_launcher_with_args_passes_through_exactly(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = make_repo(tmp_path / "repo")
    config_path = tmp_path / "launcher.json"
    save_config(make_default_config(repo, install_dir=tmp_path / "bin"), config_path)
    calls: list[list[str]] = []
    monkeypatch.setattr(diagnostics, "probe_python_version", lambda path: (3, 12, 1))

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr("agent.launcher.cli.subprocess.run", fake_run)

    code = launcher_main(["--config", str(config_path), "qa", "dashboard"])

    assert code == 0
    assert calls[-1][-2:] == ["qa", "dashboard"]
