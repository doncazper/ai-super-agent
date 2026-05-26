from __future__ import annotations

import json

from agent.runtime.canonical_dashboard import build_canonical_dashboard, build_handoff
from agent.ui.cli_commands import dispatch_cli
from tests.runtime.test_canonical_runtime_state import _write_minimal_docs


def test_canonical_dashboard_is_json_serializable_and_read_only(tmp_path) -> None:
    _write_minimal_docs(tmp_path)
    active = tmp_path / "prompts" / "active"
    active.mkdir(parents=True)
    (active / "CANON-08.md").write_text("pack_id: canonical-runtime-gateway-hardening-v1\n", encoding="utf-8")

    dashboard = build_canonical_dashboard(tmp_path)

    assert dashboard["status"] == "ok"
    assert dashboard["read_only"] is True
    assert dashboard["active"]["prompt_id"] == "CANON-08"
    assert dashboard["gateway_kernel_status"]["gateway"]["server_started"] is False
    assert dashboard["gateway_kernel_status"]["kernel_contract"]["listeners_started"] is False
    assert dashboard["safety_summary"]["canonical_state_executes_tools"] is False
    assert dashboard["recovery_resume_hints"]["auto_resume"] is False
    json.dumps(dashboard)


def test_handoff_markdown_contains_chatgpt_upload_recommendations(tmp_path) -> None:
    _write_minimal_docs(tmp_path)

    handoff = build_handoff(tmp_path, for_chatgpt=True)

    assert handoff["for_chatgpt"] is True
    assert handoff["read_only"] is True
    assert "docs/HANDOFF_TO_CHATGPT.md" in handoff["markdown"]
    assert "ToolBroker preserved" in handoff["markdown"]
    assert handoff["recommended_uploads"]["primary"] == "docs/HANDOFF_TO_CHATGPT.md"


def test_runtime_canonical_dashboard_cli(capsys) -> None:
    code = dispatch_cli(["runtime", "canonical-dashboard"])
    output = capsys.readouterr().out

    assert code == 0
    assert '"read_only": true' in output
    assert '"canonical_state_summary"' in output
    assert '"gateway_kernel_status"' in output


def test_runtime_handoff_for_chatgpt_cli(capsys) -> None:
    code = dispatch_cli(["runtime", "handoff", "--for-chatgpt"])
    output = capsys.readouterr().out

    assert code == 0
    assert '"for_chatgpt": true' in output
    assert "Canonical Runtime Handoff" in output
    assert "docs/HANDOFF_TO_CHATGPT.md" in output
