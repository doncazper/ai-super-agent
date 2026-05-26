from __future__ import annotations

import json

from agent.runtime.canonical_state import (
    build_canonical_runtime_state,
    build_reconcile_preview,
    source_of_truth_hierarchy,
)
from agent.ui.cli_commands import dispatch_cli


def _write_minimal_docs(root) -> None:
    docs = root / "docs"
    docs.mkdir()
    (docs / "PROJECT_STATE.md").write_text(
        """
- active_prompt_id: `CANON-01`
- active_prompt_pack: `canonical-runtime-gateway-hardening-v1`
- current_phase: `implement`
- current_status: `in_progress`
- next_prompt_id: `CANON-02`
""",
        encoding="utf-8",
    )
    (docs / "COMPLETION_REPORT.md").write_text(
        """
- prompt_id: `PERF-11`
- tests: 1665 passed
- startup policy validation: passed
- capability manifest validation: passed
- command registry validation: passed
""",
        encoding="utf-8",
    )
    (docs / "PROMPT_QUEUE.md").write_text("- next_prompt_id: `CANON-02`\n", encoding="utf-8")
    (docs / "PROMPT_AUDIT.md").write_text("- prompt audit: ok\n", encoding="utf-8")


def test_canonical_state_is_json_serializable(tmp_path) -> None:
    _write_minimal_docs(tmp_path)
    active = tmp_path / "prompts" / "active"
    active.mkdir(parents=True)
    (active / "CANON-01.md").write_text("pack_id: canonical-runtime-gateway-hardening-v1\n", encoding="utf-8")

    state = build_canonical_runtime_state(tmp_path).to_dict()

    assert state["schema_version"] == "1.0"
    assert state["active_prompt_id"] == "CANON-01"
    assert state["active_prompt_pack"] == "canonical-runtime-gateway-hardening-v1"
    assert state["next_prompt_id"] == "CANON-02"
    assert state["safety_summary"]["canonical_state_executes_tools"] is False
    assert state["safety_summary"]["canonical_state_persists_sensitive_values"] is False
    json.dumps(state)


def test_source_of_truth_hierarchy_order_is_canonical() -> None:
    hierarchy = source_of_truth_hierarchy()

    assert [entry["source"] for entry in hierarchy[:6]] == [
        "SPEC.md",
        "docs/SDLC.md",
        "AGENTS.md",
        "config/capabilities.yaml",
        "actual code/tests",
        "canonical runtime state JSON/model",
    ]
    assert hierarchy[-1]["source"] == "summary dashboards"


def test_reconcile_preview_marks_active_prompt_conflict(tmp_path) -> None:
    _write_minimal_docs(tmp_path)
    (tmp_path / "docs" / "PROJECT_STATE.md").write_text("- active_prompt_id: `CANON-02`\n", encoding="utf-8")
    active = tmp_path / "prompts" / "active"
    active.mkdir(parents=True)
    (active / "CANON-01.md").write_text("pack_id: canonical-runtime-gateway-hardening-v1\n", encoding="utf-8")

    preview = build_reconcile_preview(tmp_path)

    assert preview["status"] == "needs_reconciliation"
    assert preview["conflicts"][0]["field"] == "active_prompt_id"
    assert preview["side_effects"] == "none; read-only metadata preview"


def test_canonical_state_redacts_secret_like_fields(tmp_path) -> None:
    _write_minimal_docs(tmp_path)
    (tmp_path / "docs" / "PROJECT_STATE.md").write_text("- active_prompt_id: `none`\n- token: sk-testsecretvalue\n", encoding="utf-8")

    state = build_canonical_runtime_state(tmp_path).to_dict()

    dumped = json.dumps(state)
    assert "sk-testsecretvalue" not in dumped


def test_runtime_canonical_state_cli(capsys) -> None:
    code = dispatch_cli(["runtime", "canonical-state"])
    output = capsys.readouterr().out

    assert code == 0
    assert '"schema_version": "1.0"' in output
    assert '"canonical_state_executes_tools": false' in output
    assert '"canonical_state_persists_sensitive_values": false' in output


def test_runtime_source_of_truth_cli(capsys) -> None:
    code = dispatch_cli(["runtime", "source-of-truth"])
    output = capsys.readouterr().out

    assert code == 0
    assert '"source": "SPEC.md"' in output
    assert '"source": "canonical runtime state JSON/model"' in output


def test_runtime_reconcile_preview_cli(capsys) -> None:
    code = dispatch_cli(["runtime", "reconcile-preview"])
    output = capsys.readouterr().out

    assert code == 0
    assert '"side_effects": "none; read-only metadata preview"' in output
