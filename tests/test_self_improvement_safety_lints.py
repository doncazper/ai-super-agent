from __future__ import annotations

import subprocess
from pathlib import Path

from agent.self_improvement.safety_lints import lint_diff_text, verify_self_heal_artifacts


def diff_with_added(line: str) -> str:
    return f"diff --git a/file.py b/file.py\n--- a/file.py\n+++ b/file.py\n@@ -1 +1 @@\n+{line}\n"


def init_repo(path: Path) -> None:
    path.mkdir()
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    (path / "file.py").write_text("print('ok')\n", encoding="utf-8")
    subprocess.run(["git", "add", "file.py"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-m", "initial"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )


def test_safe_diff_allows_safe_only_self_heal() -> None:
    report = lint_diff_text(diff_with_added("print('safe diagnostic')"))

    assert report["status"] == "ok"
    assert report["safe_only_allowed"] is True
    assert report["finding_count"] == 0


def test_high_risk_findings_block_safe_only_plan() -> None:
    report = lint_diff_text(diff_with_added("# bypass ToolBroker and direct tool execution"))

    assert report["status"] == "blocked"
    assert report["safe_only_allowed"] is False
    assert report["blocker_count"] >= 1
    assert any(item["rule_id"] == "toolbroker_bypass" for item in report["findings"])
    assert "bypass ToolBroker" not in repr(report)


def test_lints_cover_required_safety_rules() -> None:
    examples = {
        "audit_logging_disabled": "# disable audit logging for tests",
        "policy_engine_weakened": "# bypass policy checks",
        "critical_approval_reuse": "CRITICAL actions may reuse previous approval",
        "personal_data_default_enabled": "LOCAL_PRIVATE_DATA default_enabled: true",
        "background_persistence_added": "background service worker",
        "filesystem_scope_expanded": "full disk access outside workspace",
        "redaction_removed": "disable redaction",
        "package_install_without_approval": "pip install surprise",
        "live_provider_default": "LIVE_PROVIDER_ENABLED=true",
        "server_listener_default": "APP_BRIDGE_ENABLED=true",
        "secret_storage": "store_raw_secret(token)",
        "backup_restore_weakened": "restore without verification",
    }
    for expected_rule, line in examples.items():
        report = lint_diff_text(diff_with_added(line))
        assert any(item["rule_id"] == expected_rule for item in report["findings"]), expected_rule
        assert report["safe_only_allowed"] is False


def test_verify_self_heal_artifacts_combines_lints_and_hashes(tmp_path) -> None:
    project = tmp_path / "repo"
    init_repo(project)
    (project / "file.py").write_text("# disable audit logging\n", encoding="utf-8")

    report = verify_self_heal_artifacts(project)

    assert report["status"] == "blocked"
    assert report["safe_only_allowed"] is False
    assert report["lint_report"]["finding_count"] >= 1
    assert report["artifact_hashes"]["status"] == "ok"
    assert report["side_effects"] == "none; verify-only"
