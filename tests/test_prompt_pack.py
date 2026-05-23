from __future__ import annotations

import json
from pathlib import Path

from agent.prompts.pack_models import PromptPackError
from agent.prompts.pack_parser import parse_prompt_pack
from agent.prompts.pack_validator import validate_prompt_pack
from agent.prompts.prompt_store import import_prompt_pack, validate_pack_file
from agent.ui import cli_commands
from agent.ui.prompts import next_prompt, show_prompt


def pack_text(*, first_body: str = "First body line\nSecond body line\n", second_approval: str = "false") -> str:
    return f"""<<<PROMPT_PACK_START>>>
pack_id: example-pack-v1
pack_title: Example Prompt Pack
mode: import_only
default_execution: one_prompt_at_a_time
requires_sdlc: true
requires_prompt_ledger: true
requires_feature_maturity_update: true

<<<PROMPT_START id="EXAMPLE-01" order="1">>
title: Example first prompt
category: docs
risk_level: LOW
approval_gate: false
depends_on: []
status: queued

PROMPT:
{first_body}<<<PROMPT_END id="EXAMPLE-01">>

<<<PROMPT_START id="EXAMPLE-02" order="2">>
title: Example second prompt
category: runtime
risk_level: MEDIUM
approval_gate: {second_approval}
depends_on: ["EXAMPLE-01"]
status: queued

PROMPT:
Second body
<<<PROMPT_END id="EXAMPLE-02">>

<<<PROMPT_PACK_END>>>
"""


def write_pack(tmp_path: Path, text: str | None = None) -> Path:
    path = tmp_path / "pack.md"
    path.write_text(text or pack_text(), encoding="utf-8")
    return path


def test_valid_pack_parses() -> None:
    pack = parse_prompt_pack(pack_text())
    validate_prompt_pack(pack)
    assert pack.pack_id == "example-pack-v1"
    assert [prompt.prompt_id for prompt in pack.prompts] == ["EXAMPLE-01", "EXAMPLE-02"]
    assert pack.prompts[1].depends_on == ["EXAMPLE-01"]


def test_duplicate_prompt_ids_rejected() -> None:
    text = pack_text().replace('id="EXAMPLE-02" order="2"', 'id="EXAMPLE-01" order="2"')
    pack = parse_prompt_pack(text.replace('<<<PROMPT_END id="EXAMPLE-02">>', '<<<PROMPT_END id="EXAMPLE-01">>'))
    try:
        validate_prompt_pack(pack)
    except PromptPackError as exc:
        assert "unique" in str(exc)
    else:
        raise AssertionError("duplicate prompt ids should be rejected")


def test_duplicate_order_rejected() -> None:
    pack = parse_prompt_pack(pack_text().replace('id="EXAMPLE-02" order="2"', 'id="EXAMPLE-02" order="1"'))
    try:
        validate_prompt_pack(pack)
    except PromptPackError as exc:
        assert "order values" in str(exc)
    else:
        raise AssertionError("duplicate order should be rejected")


def test_missing_prompt_end_rejected() -> None:
    try:
        parse_prompt_pack(pack_text().replace('<<<PROMPT_END id="EXAMPLE-02">>', ""))
    except PromptPackError as exc:
        assert "missing matching PROMPT_END" in str(exc)
    else:
        raise AssertionError("missing prompt end should be rejected")


def test_missing_metadata_rejected() -> None:
    try:
        parse_prompt_pack(pack_text().replace("title: Example first prompt\n", ""))
    except PromptPackError as exc:
        assert "title" in str(exc)
    else:
        raise AssertionError("missing metadata should be rejected")


def test_invalid_risk_level_rejected() -> None:
    pack = parse_prompt_pack(pack_text().replace("risk_level: MEDIUM", "risk_level: WILD"))
    try:
        validate_prompt_pack(pack)
    except PromptPackError as exc:
        assert "invalid risk_level" in str(exc)
    else:
        raise AssertionError("invalid risk level should be rejected")


def test_dependency_on_missing_prompt_rejected() -> None:
    pack = parse_prompt_pack(pack_text().replace('depends_on: ["EXAMPLE-01"]', 'depends_on: ["MISSING"]'))
    try:
        validate_prompt_pack(pack)
    except PromptPackError as exc:
        assert "missing prompt" in str(exc)
    else:
        raise AssertionError("missing dependency should be rejected")


def test_circular_dependencies_rejected() -> None:
    text = pack_text().replace("depends_on: []", 'depends_on: ["EXAMPLE-02"]')
    pack = parse_prompt_pack(text)
    try:
        validate_prompt_pack(pack)
    except PromptPackError as exc:
        assert "circular" in str(exc)
    else:
        raise AssertionError("cycle should be rejected")


def test_validate_pack_does_not_write_files(tmp_path, capsys) -> None:
    pack = write_pack(tmp_path)
    assert cli_commands.dispatch_cli(["prompts", "validate-pack", str(pack)], project_root=tmp_path) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["pack_id"] == "example-pack-v1"
    assert not (tmp_path / "prompts" / "packs").exists()


def test_import_writes_pack_prompt_files_and_updates_queue(tmp_path) -> None:
    pack = write_pack(tmp_path)
    result = import_prompt_pack(pack, project_root=tmp_path)

    assert result.pack_path == "prompts/packs/example-pack-v1.md"
    assert (tmp_path / "prompts/packs/example-pack-v1.md").exists()
    assert (tmp_path / "prompts/queued/EXAMPLE-01.md").exists()
    assert "EXAMPLE-01" in (tmp_path / "docs/PROMPT_QUEUE.md").read_text(encoding="utf-8")
    assert "EXAMPLE-01" in (tmp_path / "docs/PROMPT_LEDGER.md").read_text(encoding="utf-8")
    assert "example-pack-v1" in (tmp_path / "docs/PROMPT_AUDIT.md").read_text(encoding="utf-8")


def test_next_prompt_respects_dependencies(tmp_path) -> None:
    pack = write_pack(tmp_path)
    import_prompt_pack(pack, project_root=tmp_path)

    assert next_prompt(tmp_path).prompt_id == "EXAMPLE-01"
    assert cli_commands.dispatch_cli(["prompts", "mark-complete", "EXAMPLE-01", "--unknown"], project_root=tmp_path) == 0
    assert next_prompt(tmp_path).prompt_id == "EXAMPLE-02"


def test_approval_gated_prompt_not_returned_as_next(tmp_path) -> None:
    text = pack_text(second_approval="true").replace('depends_on: ["EXAMPLE-01"]', "depends_on: []")
    pack = write_pack(tmp_path, text)
    import_prompt_pack(pack, project_root=tmp_path)

    assert next_prompt(tmp_path).prompt_id == "EXAMPLE-01"
    cli_commands.dispatch_cli(["prompts", "mark-complete", "EXAMPLE-01", "--unknown"], project_root=tmp_path)
    assert next_prompt(tmp_path) is None


def test_prompt_body_preserved_exactly(tmp_path) -> None:
    body = "Keep this EXACT line.\n\n  Preserve indentation.\n"
    pack = write_pack(tmp_path, pack_text(first_body=body))
    import_prompt_pack(pack, project_root=tmp_path)

    content = (tmp_path / "prompts/queued/EXAMPLE-01.md").read_text(encoding="utf-8")
    assert content.split("# Prompt\n\n", 1)[1] == body


def test_prompt_audit_detects_missing_completion_evidence(tmp_path) -> None:
    pack = write_pack(tmp_path)
    import_prompt_pack(pack, project_root=tmp_path)
    missing = json.loads(_capture_cli(tmp_path, ["prompts", "missing"]))
    assert {record["prompt_id"] for record in missing["prompts"]} == {"EXAMPLE-01", "EXAMPLE-02"}


def test_import_rejects_execute_all_mode(tmp_path) -> None:
    pack = write_pack(tmp_path, pack_text().replace("mode: import_only", "mode: execute_all"))
    try:
        validate_pack_file(pack)
    except PromptPackError as exc:
        assert "import_only" in str(exc)
    else:
        raise AssertionError("execute_all should be rejected")


def _capture_cli(tmp_path: Path, argv: list[str]) -> str:
    import contextlib
    import io

    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        assert cli_commands.dispatch_cli(argv, project_root=tmp_path) == 0
    return stream.getvalue()
