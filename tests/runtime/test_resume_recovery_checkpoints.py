from __future__ import annotations

import json

import pytest

from agent.runtime.checkpoints import RuntimeCheckpoint, list_checkpoints, show_checkpoint
from agent.runtime.recovery import recovery_preview
from agent.ui.cli_commands import dispatch_cli


def test_checkpoint_serializes_and_redacts() -> None:
    checkpoint = RuntimeCheckpoint(
        checkpoint_id="chk_001",
        record_id="rec_001",
        current_step="CANON-04",
        completed_steps=("CANON-01", "CANON-02", "CANON-03"),
        remaining_steps=("CANON-04",),
        notes="token=supersecret",
        safe_to_resume=False,
    )

    payload = checkpoint.to_dict()

    assert payload["checkpoint_id"] == "chk_001"
    assert payload["completed_steps"] == ["CANON-01", "CANON-02", "CANON-03"]
    assert "supersecret" not in json.dumps(payload)


def test_critical_checkpoint_cannot_be_safe_to_resume() -> None:
    with pytest.raises(ValueError):
        RuntimeCheckpoint(
            checkpoint_id="chk_critical",
            record_id="rec_critical",
            approval_state="critical_action_pending",
            safe_to_resume=True,
        )


def test_checkpoint_listing_and_show(tmp_path) -> None:
    checkpoints_dir = tmp_path / "reports" / "runtime" / "checkpoints"
    checkpoints_dir.mkdir(parents=True)
    (checkpoints_dir / "chk_001.json").write_text(
        json.dumps(RuntimeCheckpoint(checkpoint_id="chk_001", record_id="rec_001").to_dict()),
        encoding="utf-8",
    )

    listing = list_checkpoints(tmp_path)
    shown = show_checkpoint("chk_001", tmp_path)

    assert listing["checkpoint_count"] == 1
    assert shown["status"] == "ok"
    assert shown["checkpoint"]["checkpoint_id"] == "chk_001"
    assert show_checkpoint("missing", tmp_path)["status"] == "not_found"


def test_recovery_preview_interrupted_prompt_pack(tmp_path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "PROJECT_STATE.md").write_text(
        """
- active_prompt_id: `CANON-04`
- active_prompt_pack: `canonical-runtime-gateway-hardening-v1`
- current_status: `in_progress`
- next_prompt_id: `CANON-05`
""",
        encoding="utf-8",
    )
    (docs / "COMPLETION_REPORT.md").write_text("- tests: runtime passed\n", encoding="utf-8")
    active = tmp_path / "prompts" / "active"
    active.mkdir(parents=True)
    (active / "CANON-04.md").write_text("pack_id: canonical-runtime-gateway-hardening-v1\n", encoding="utf-8")

    preview = recovery_preview(tmp_path)

    assert preview["status"] == "preview_only"
    assert preview["auto_resume"] is False
    assert preview["critical_resume_requires_fresh_approval"] is True
    assert "CANON-04" in preview["report"]["safe_next_action"]
    assert any("Do not resume automatically" in item for item in preview["report"]["unsafe_actions_to_avoid"])


def test_runtime_recovery_and_checkpoint_cli(capsys) -> None:
    assert dispatch_cli(["runtime", "recovery-preview"]) == 0
    output = capsys.readouterr().out
    assert '"auto_resume": false' in output
    assert '"critical_resume_requires_fresh_approval": true' in output

    assert dispatch_cli(["runtime", "checkpoints", "list"]) == 0
    output = capsys.readouterr().out
    assert '"side_effects": "none; read-only checkpoint listing"' in output

    assert dispatch_cli(["runtime", "checkpoints", "show", "missing"]) == 0
    output = capsys.readouterr().out
    assert '"status": "not_found"' in output
