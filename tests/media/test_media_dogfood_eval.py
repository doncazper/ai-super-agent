from __future__ import annotations

from pathlib import Path

from agent.dogfood.suites import load_all_suites, load_suite
from agent.ui import cli_commands
from agent.ui.command_registry import get_command
from agent.ui.evals import EvalOptions, load_eval_cases, run_eval


ROOT = Path(__file__).resolve().parents[2]


def test_media_dogfood_suites_exist_and_validate() -> None:
    required = {
        "media_core",
        "media_safety",
        "media_image_planning",
        "media_video_audio_planning",
    }
    suites = {suite.suite_id: suite for suite in load_all_suites(project_root=ROOT)}

    assert required.issubset(suites)
    for suite_id in required:
        suite = suites[suite_id]
        assert suite.requires_personal_data is False
        assert suite.requires_live_lmstudio is False
        assert suite.requires_web is False
        assert suite.risk_level == "LOW"
        assert suite.default_enabled is True
        for command in suite.commands:
            assert command.command.startswith("python smart_agent.py ")
            assert command.expected_behavior
            assert command.failure_signals
            assert "--dry-run" in command.command or any(
                safe_status in command.command
                for safe_status in (
                    "media providers",
                    "media doctor",
                    "media assets list",
                    "media plan",
                    "media safety-check",
                    "media tts plan",
                    "media creative plan",
                    "media image plan",
                    "media comfyui doctor",
                )
            )


def test_media_core_suite_covers_required_commands() -> None:
    suite = load_suite("media_core", project_root=ROOT)
    commands = "\n".join(command.command for command in suite.commands)

    assert "media providers" in commands
    assert "media doctor" in commands
    assert "media assets list" in commands
    assert "media plan" in commands


def test_media_eval_cases_load() -> None:
    cases = {case.case_id: case for case in load_eval_cases()}

    required = {
        "media.no_real_generation",
        "media.unsafe_prompt_denied",
        "media.voice_clone_denied",
        "media.license_uncertainty_warned",
        "media.assets_bounded_workspace",
        "media.command_registry_complete",
    }
    assert required.issubset(cases)
    for case_id in required:
        assert cases[case_id].category == "media"
        assert cases[case_id].personal_data is False
        assert cases[case_id].live is False


def test_media_eval_runs_with_fixtures(tmp_path: Path) -> None:
    report = run_eval(
        EvalOptions(
            media=True,
            report_path=tmp_path / "docs" / "EVAL_REPORT.md",
            results_path=tmp_path / "logs" / "eval_results.json",
            reports_dir=tmp_path / "reports" / "evals",
        )
    )

    by_name = {check["name"]: check for check in report["checks"]}
    assert report["status"] == "ok"
    assert by_name["media.no_real_generation"]["status"] == "pass"
    assert by_name["media.unsafe_prompt_denied"]["status"] == "pass"
    assert by_name["media.voice_clone_denied"]["status"] == "pass"
    assert by_name["media.license_uncertainty_warned"]["status"] == "pass"
    assert by_name["media.assets_bounded_workspace"]["status"] == "pass"
    assert by_name["media.command_registry_complete"]["status"] == "pass"


def test_media_eval_cli_flag_runs(capsys) -> None:
    assert cli_commands.dispatch_cli(["eval", "run", "--media", "--json"], project_root=ROOT) == 0
    output = capsys.readouterr().out

    assert '"media.no_real_generation"' in output
    assert '"selected_categories": [' in output
    assert '"media"' in output


def test_media_command_registry_entries_exist() -> None:
    for command_id in (
        "CMD-DOGFOOD-MEDIA-001",
        "CMD-DOGFOOD-MEDIA-002",
        "CMD-DOGFOOD-MEDIA-003",
        "CMD-DOGFOOD-MEDIA-004",
        "CMD-EVAL-021",
        "CMD-EVAL-022",
    ):
        record = get_command(command_id)
        assert record is not None
        assert record.status == "active"
        assert record.risk_level in {"SAFE", "LOW"}
