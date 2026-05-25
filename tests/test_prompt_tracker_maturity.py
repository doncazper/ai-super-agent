from __future__ import annotations

import json
from pathlib import Path

from agent.prompts.evidence import audit_prompt_evidence
from agent.prompts.recovery import recover_plan
from agent.prompts.prompt_store import import_prompt_pack
from agent.ui import cli_commands
from agent.ui.prompts import add_prompt_record, mark_prompt, next_prompt


ROOT = Path(__file__).resolve().parents[1]


def _pack_text() -> str:
    return """<<<PROMPT_PACK_START>>>
pack_id: tracker-pack-v1
pack_title: Tracker Pack
mode: import_only
default_execution: one_prompt_at_a_time
requires_sdlc: true
requires_prompt_ledger: true
requires_feature_maturity_update: true

<<<PROMPT_START id="TRK-01" order="1">>
title: Tracker first prompt
category: prompt_tracking
risk_level: LOW
approval_gate: false
depends_on: []
status: queued

PROMPT:
Preserve delimiter examples without splitting:
<<<PROMPT_START id="EXAMPLE" order="99">>
<<<PROMPT_PACK_END>>>
<<<PROMPT_END id="TRK-01">>

<<<PROMPT_START id="TRK-02" order="2">>
title: Tracker second prompt
category: prompt_tracking
risk_level: MEDIUM
approval_gate: false
depends_on: ["TRK-01"]
status: queued

PROMPT:
Second body
<<<PROMPT_END id="TRK-02">>

<<<PROMPT_PACK_END>>>
"""


def test_prompt_pack_preserves_embedded_delimiter_examples(tmp_path: Path) -> None:
    pack = tmp_path / "pack.md"
    pack.write_text(_pack_text(), encoding="utf-8")

    result = import_prompt_pack(pack, project_root=tmp_path)

    assert result.prompt_ids == ["TRK-01", "TRK-02"]
    content = (tmp_path / "prompts/queued/TRK-01.md").read_text(encoding="utf-8")
    assert '<<<PROMPT_START id="EXAMPLE" order="99">>' in content
    assert "<<<PROMPT_PACK_END>>>" in content


def test_prompt_status_cli_search_and_evidence(tmp_path: Path, capsys) -> None:
    add_prompt_record("Tracker Demo", tmp_path)
    (tmp_path / "docs").mkdir(exist_ok=True)
    (tmp_path / "docs/COMPLETION_REPORT.md").write_text("Tracker Demo completed as tracker-demo.\n", encoding="utf-8")

    assert cli_commands.dispatch_cli(["prompts", "search", "tracker"], project_root=tmp_path) == 0
    found = json.loads(capsys.readouterr().out)
    assert found["prompts"][0]["prompt_id"] == "tracker-demo"

    assert cli_commands.dispatch_cli(["prompts", "evidence", "tracker-demo"], project_root=tmp_path) == 0
    evidence = json.loads(capsys.readouterr().out)
    assert evidence["evidence"][0]["classification"] == "partial"


def test_one_active_prompt_enforced_and_failed_requires_reason(tmp_path: Path) -> None:
    add_prompt_record("one", tmp_path)
    add_prompt_record("two", tmp_path)
    mark_prompt("one", "active", project_root=tmp_path)

    try:
        mark_prompt("two", "active", project_root=tmp_path)
    except ValueError as exc:
        assert "another prompt is active" in str(exc)
    else:
        raise AssertionError("second active prompt should be rejected")

    try:
        mark_prompt("one", "failed", project_root=tmp_path)
    except ValueError as exc:
        assert "--notes" in str(exc)
    else:
        raise AssertionError("failed prompt should require a reason")


def test_recovery_plan_is_report_only(tmp_path: Path) -> None:
    pack = tmp_path / "pack.md"
    pack.write_text(_pack_text(), encoding="utf-8")
    import_prompt_pack(pack, project_root=tmp_path)
    plan = recover_plan(tmp_path)

    assert plan["auto_run"] is False
    assert plan["missed_prompts"]
    assert next_prompt(tmp_path).prompt_id == "TRK-01"


def test_prompt_tracker_eval_cli_runs(capsys) -> None:
    assert cli_commands.dispatch_cli(["eval", "run", "--prompt-tracker", "--json"], project_root=ROOT) == 0
    payload = json.loads(capsys.readouterr().out)
    assert "prompt_tracker" in payload["selected_categories"]
    assert any(check["name"] == "prompt_tracker.evidence_audit" for check in payload["checks"])
