from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path

from agent.promptops.models import PromptOpsConfig
from agent.promptops.runner import autopilot, run_next
from agent.promptops.workbench import copy_next, import_from_file, import_from_stdin, next_work
from agent.ui import cli_commands
from agent.ui.prompts import mark_prompt, next_prompt


def pack_text(category: str = "docs", risk: str = "LOW", approval_gate: str = "false") -> str:
    return f"""<<<PROMPT_PACK_START>>>
pack_id: workbench-pack-v1
pack_title: Workbench Pack
mode: import_only
default_execution: one_prompt_at_a_time
requires_sdlc: true
requires_prompt_ledger: true
requires_feature_maturity_update: true

<<<PROMPT_START id="WB-01" order="1">>
title: Workbench first prompt
category: {category}
risk_level: {risk}
approval_gate: {approval_gate}
depends_on: []
status: queued

PROMPT:
Preserve this body exactly.
<<<PROMPT_END id="WB-01">>

<<<PROMPT_START id="WB-02" order="2">>
title: Workbench second prompt
category: docs
risk_level: LOW
approval_gate: false
depends_on: ["WB-01"]
status: queued

PROMPT:
Second body
<<<PROMPT_END id="WB-02">>

<<<PROMPT_PACK_END>>>
"""


def write_pack(tmp_path: Path, text: str | None = None) -> Path:
    path = tmp_path / "pack.md"
    path.write_text(text or pack_text(), encoding="utf-8")
    return path


def test_work_import_from_file_splits_and_updates_tracking(tmp_path: Path) -> None:
    result = import_from_file(write_pack(tmp_path), project_root=tmp_path)

    assert result.status == "ok"
    assert result.mode == "pack"
    assert (tmp_path / "prompts/queued/WB-01.md").exists()
    assert "WB-01" in (tmp_path / "docs/PROMPT_LEDGER.md").read_text(encoding="utf-8")
    assert "WB-01" in (tmp_path / "docs/PROMPT_QUEUE.md").read_text(encoding="utf-8")
    assert "active_prompt_pack: workbench-pack-v1" in (tmp_path / "docs/PROJECT_STATE.md").read_text(encoding="utf-8")
    assert "trust_level: UNTRUSTED_DOCUMENT" in (tmp_path / "prompts/queued/WB-01.md").read_text(encoding="utf-8")


def test_work_import_from_stdin_with_cli(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(pack_text()))

    assert cli_commands.dispatch_cli(["work", "import", "--stdin"], project_root=tmp_path) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["prompt_ids"] == ["WB-01", "WB-02"]


def test_work_import_clipboard_mocked(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr("agent.promptops.workbench.read_clipboard", lambda: pack_text())

    assert cli_commands.dispatch_cli(["work", "import-clipboard"], project_root=tmp_path) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["pack_id"] == "workbench-pack-v1"


def test_work_import_raw_single_prompt(tmp_path: Path) -> None:
    result = import_from_stdin("# Quick task\nDo the safe thing.", project_root=tmp_path, pack_id="quick", single=True, prompt_id="QUICK-001")

    assert result.mode == "single"
    content = (tmp_path / "prompts/queued/QUICK-001.md").read_text(encoding="utf-8")
    assert "trust_level: UNTRUSTED_DOCUMENT" in content
    assert "# Quick task\nDo the safe thing." in content


def test_invalid_pack_rejected_by_work_import(tmp_path: Path) -> None:
    bad_pack = write_pack(tmp_path, pack_text(risk="BANANA"))

    assert cli_commands.dispatch_cli(["work", "import", str(bad_pack)], project_root=tmp_path) == 2
    assert not (tmp_path / "prompts/queued/WB-01.md").exists()


def test_next_respects_dependencies_and_skips_blocked(tmp_path: Path) -> None:
    import_from_file(write_pack(tmp_path), project_root=tmp_path)

    assert next_work(project_root=tmp_path).prompt_id == "WB-01"
    mark_prompt("WB-01", "completed", project_root=tmp_path, unknown=True)
    assert next_prompt(tmp_path).prompt_id == "WB-02"

    blocked = write_pack(tmp_path, pack_text().replace("WB-02", "WB-03").replace("depends_on: [\"WB-01\"]", "depends_on: []").replace("status: queued", "status: blocked", 1))
    assert cli_commands.dispatch_cli(["work", "import", str(blocked), "--pack-id", "blocked-pack"], project_root=tmp_path) == 0
    assert next_work(project_root=tmp_path).prompt_id == "WB-02"


def test_copy_next_uses_clipboard_when_available(tmp_path: Path, monkeypatch) -> None:
    import_from_file(write_pack(tmp_path), project_root=tmp_path)
    copied: dict[str, str] = {}
    monkeypatch.setattr("agent.promptops.workbench.write_clipboard", lambda text: copied.setdefault("text", text))

    result = copy_next(project_root=tmp_path)

    assert result["copied"] is True
    assert "Preserve this body exactly." in copied["text"]


def test_run_next_disabled_by_default(tmp_path: Path) -> None:
    import_from_file(write_pack(tmp_path), project_root=tmp_path)

    result = run_next(project_root=tmp_path, config=PromptOpsConfig(runner_enabled=False))

    assert result.status == "runner_disabled"
    assert result.runner_enabled is False
    assert result.report_path


def test_autopilot_rejects_high_risk_prompt(tmp_path: Path) -> None:
    import_from_file(write_pack(tmp_path, pack_text(risk="HIGH")), project_root=tmp_path)

    result = autopilot(project_root=tmp_path, max_prompts=1, safe_only=True, config=PromptOpsConfig(runner_enabled=False))

    assert result.attempted_prompt_ids == []
    assert "risk level HIGH" in result.stopped_reason


def test_autopilot_stops_at_approval_gate(tmp_path: Path) -> None:
    import_from_file(write_pack(tmp_path, pack_text(approval_gate="true")), project_root=tmp_path)

    result = autopilot(project_root=tmp_path, max_prompts=1, safe_only=True, config=PromptOpsConfig(runner_enabled=False))

    assert result.attempted_prompt_ids == []
    assert "approval gate" in result.stopped_reason


def test_run_next_report_redacts_secrets(tmp_path: Path) -> None:
    import_from_stdin("api_key=sk-secretsecretsecret\nDo docs only.", project_root=tmp_path, pack_id="quick", single=True, prompt_id="QUICK-SECRET")

    result = run_next(project_root=tmp_path, config=PromptOpsConfig(runner_enabled=False))

    report = (tmp_path / result.report_path).read_text(encoding="utf-8")
    assert "sk-secretsecretsecret" not in report


def test_work_mark_complete_requires_evidence(tmp_path: Path) -> None:
    import_from_file(write_pack(tmp_path), project_root=tmp_path)

    assert cli_commands.dispatch_cli(["work", "mark-complete", "WB-01"], project_root=tmp_path) == 2
    assert cli_commands.dispatch_cli(["work", "mark-complete", "WB-01", "--unknown"], project_root=tmp_path) == 0


def test_work_next_cli_prints_readable_summary(tmp_path: Path, capsys) -> None:
    import_from_file(write_pack(tmp_path), project_root=tmp_path)

    assert cli_commands.dispatch_cli(["work", "next"], project_root=tmp_path) == 0
    out = capsys.readouterr().out

    assert "Next prompt: WB-01" in out
    assert "Risk: LOW" in out


def capture_cli(tmp_path: Path, argv: list[str]) -> str:
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        assert cli_commands.dispatch_cli(argv, project_root=tmp_path) == 0
    return stream.getvalue()

