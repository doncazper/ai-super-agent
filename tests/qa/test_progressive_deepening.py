from pathlib import Path

from agent.qa.progressive import daily_dry_run, depth_status, next_batch, weekly_dry_run


def test_next_batch_selects_safe_commands() -> None:
    result = next_batch(Path(__file__).resolve().parents[2], limit=5)
    assert result["status"] == "ok"
    assert result["dry_run"] is True
    assert result["commands"]
    assert all(command["safe_to_auto_run"] for command in result["commands"])


def test_daily_excludes_high_critical(tmp_path: Path) -> None:
    result = daily_dry_run(Path(__file__).resolve().parents[2], limit=50)
    assert result["dry_run"] is True
    assert all(command["qa_tier"] in {0, 1} for command in result["commands"])
    assert all("HIGH" not in command["risk_level"] and "CRITICAL" not in command["risk_level"] for command in result["commands"])


def test_weekly_requires_sandbox_and_excludes_personal_data() -> None:
    result = weekly_dry_run(Path(__file__).resolve().parents[2], limit=50)
    assert result["dry_run"] is True
    assert result["requires_sandbox"] is True
    assert all(command["qa_tier"] == 3 for command in result["commands"])


def test_depth_status_scheduler_disabled() -> None:
    result = depth_status()
    assert result["scheduler_enabled"] is False
    assert result["policy"]["dry_run_default"] is True
    assert 6 in result["policy"]["never_automatic_tiers"]

