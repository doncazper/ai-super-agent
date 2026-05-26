from __future__ import annotations

import json

from agent.runtime.tracker_sync import build_tracker_conflict_report, build_tracker_sync_preview
from agent.ui.cli_commands import dispatch_cli
from tests.runtime.test_canonical_runtime_state import _write_minimal_docs


def test_tracker_sync_preview_is_read_only_and_serializable(tmp_path) -> None:
    _write_minimal_docs(tmp_path)
    active = tmp_path / "prompts" / "active"
    active.mkdir(parents=True)
    (active / "CANON-09.md").write_text("pack_id: canonical-runtime-gateway-hardening-v1\n", encoding="utf-8")

    preview = build_tracker_sync_preview(tmp_path)

    assert preview["read_only"] is True
    assert preview["auto_overwrite_trackers"] is False
    assert preview["broad_rewrites_allowed"] is False
    assert preview["canonical_active_work"]["active_prompt_id"] == "CANON-09"
    assert preview["sync_policy"]["small_anchored_edits_only"] is True
    assert any(role["tracker"] == "docs/PROMPT_LEDGER.md" for role in preview["tracker_roles"])
    json.dumps(preview)


def test_tracker_conflict_report_reuses_canonical_conflicts(tmp_path) -> None:
    _write_minimal_docs(tmp_path)
    (tmp_path / "docs" / "PROJECT_STATE.md").write_text("- active_prompt_id: `CANON-01`\n", encoding="utf-8")
    active = tmp_path / "prompts" / "active"
    active.mkdir(parents=True)
    (active / "CANON-09.md").write_text("pack_id: canonical-runtime-gateway-hardening-v1\n", encoding="utf-8")

    report = build_tracker_conflict_report(tmp_path)

    assert report["status"] == "needs_reconciliation"
    assert report["conflict_count"] == 1
    assert report["conflicts"][0]["field"] == "active_prompt_id"
    assert report["side_effects"] == "none; conflict report does not change trackers"


def test_runtime_tracker_sync_preview_cli(capsys) -> None:
    code = dispatch_cli(["runtime", "tracker-sync-preview"])
    output = capsys.readouterr().out

    assert code == 0
    assert '"auto_overwrite_trackers": false' in output
    assert '"tracker_roles"' in output


def test_runtime_tracker_conflicts_cli(capsys) -> None:
    code = dispatch_cli(["runtime", "tracker-conflicts"])
    output = capsys.readouterr().out

    assert code == 0
    assert '"read_only": true' in output
    assert '"conflict_count"' in output
