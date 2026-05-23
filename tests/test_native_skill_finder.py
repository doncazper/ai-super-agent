from __future__ import annotations

import json
from pathlib import Path

from agent.config.loader import load_capabilities_config
from agent.core.tool_broker import ToolBroker
from agent.native_skills.finder import find_native_skills
from agent.safety.audit import AuditLogger
from agent.safety.policy import PolicyEngine
from agent.tools.registry import default_registry


ROOT = Path(__file__).resolve().parents[1]


def make_broker(project: Path, audit_path: Path) -> ToolBroker:
    return ToolBroker(
        default_registry(project_root=project),
        PolicyEngine.from_config(load_capabilities_config(ROOT / "config/capabilities.yaml")),
        AuditLogger(audit_path),
        session_id="test-session",
        model="test-model",
        route="test",
    )


def call(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    return {
        "id": f"call_{tool_name}",
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments)},
    }


def write_finder_project(project: Path) -> None:
    (project / "native_skills").mkdir(parents=True)
    (project / "docs/native_skills").mkdir(parents=True)
    (project / "native_skills/native_skill_vetter.yaml").write_text(
        """
skill_id: native_skill_vetter
name: Native Skill Vetter
description: Review candidate skill files for safety before installation or native porting.
category: security
version: "1.0.0"
status: available
maturity_level: "4 Tested"
risk_level: LOW
trust_level: UNTRUSTED_DOCUMENT
allowed_tools:
  - native_skills.vet_skill_file
required_capabilities:
  - native_skills.vet_skill_file
approval_required: false
memory_behavior: no_store
audit_required: true
inputs_schema: {}
outputs_schema: {}
docs_path: docs/native_skills/SKILL_INTAKE_PROCESS.md
tests_path: tests/test_native_skills.py
owner: local-agent
last_reviewed: "2026-05-23"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (project / "docs/native_skills/NATIVE_CANDIDATE_MATRIX.md").write_text(
        """
# Native Candidate Matrix

| Category | Native Priority | Recommended Implementation Path | Required ToolBroker Capabilities | Required Approval Gates | Memory Behavior | Trust Label |
|---|---|---|---|---|---|---|
| PDF/documents | now | Workspace PDF reader and summarizer with page citations | `filesystem.read`, future `document.extract_pdf` | Approval only for files outside standard roots or personal content | no_store | UNTRUSTED_DOCUMENT |
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (project / "docs/FEATURE_REGISTRY.md").write_text(
        """
# Feature Registry

| Feature ID | Feature name | Category | Status | Risk level | Trust level | Capabilities | Commands | ToolBroker path verified: yes/no | PolicyEngine checked: yes/no | Approval required | Audit behavior | Memory behavior | Tests | Docs | Dependencies | Release gate status | Last updated |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| WORKFLOW-MEETING-FOLLOWUP | Meeting follow-up | Workflow | complete | HIGH for selected reads; CRITICAL for queued writes | LOCAL_PRIVATE_DATA / MODEL_OUTPUT | `calendar.read_selected_event`, `contacts.search`, `tasks.create` | `meeting follow-up --event-id` | yes | yes | calendar/contact approval-required; queued writes require later Action Center approval | audited | no memory write | tests pass | README | Action Center | Complete locally; live personal sections require approval | 2026-05-23 |
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (project / "docs/FEATURE_MATURITY.md").write_text(
        """
# Feature Maturity

| Feature | Category | Maturity Level | Readiness Score | Prompt / Iteration Count | Design Completeness | Implementation Completeness | Test Coverage | Policy/Audit Status | Security Hardening Status | Live Validation Status | UX/Docs Status | Known Limitations | Next Work Needed |
|---|---|---:|---:|---:|---|---|---|---|---|---|---|---|---|
| Meeting Follow-Up | Workflow | 4 Tested | 72 | 1 | Complete | Implemented | Tests pass | ToolBroker audited | No writes | Local only | README | Needs live approval smoke | Live-validate with explicit approval |
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_finds_implemented_native_skill(tmp_path: Path) -> None:
    write_finder_project(tmp_path)

    result = find_native_skills("vet a candidate skill for safety", project_root=tmp_path)

    match = result["matches"][0]
    assert match["skill_id"] == "native_skill_vetter"
    assert match["implemented"] is True
    assert match["safe_to_use_now"] is True
    assert match["maturity_level"] == "4 Tested"


def test_finds_planned_candidate_and_next_work(tmp_path: Path) -> None:
    write_finder_project(tmp_path)

    result = find_native_skills("I need to work with PDFs", project_root=tmp_path)

    assert result["external_search_used"] is False
    assert result["external_install_used"] is False
    pdf = result["matches"][0]
    assert pdf["name"] == "PDF/documents"
    assert pdf["implemented"] is False
    assert pdf["safe_to_use_now"] is False
    assert "Workspace PDF reader" in pdf["next_work_needed"]


def test_reports_maturity_and_required_approvals(tmp_path: Path) -> None:
    write_finder_project(tmp_path)

    result = find_native_skills("Can you help with meeting follow-up?", project_root=tmp_path)

    meeting = next(match for match in result["matches"] if match["skill_id"] == "WORKFLOW-MEETING-FOLLOWUP")
    assert meeting["skill_id"] == "WORKFLOW-MEETING-FOLLOWUP"
    assert meeting["implemented"] is True
    assert "approval" in meeting["required_approvals"]
    assert "calendar.read_selected_event" in meeting["required_capabilities"]


def test_suggests_candidate_creation_when_no_match(tmp_path: Path) -> None:
    write_finder_project(tmp_path)

    result = find_native_skills("quantum submarine bakery", project_root=tmp_path)

    assert result["matches"] == []
    assert result["candidate_creation"]["recommended"] is True


def test_find_skill_executes_through_broker_and_audits_docs_read(tmp_path: Path) -> None:
    write_finder_project(tmp_path)
    audit_path = tmp_path / "audit.jsonl"
    broker = make_broker(tmp_path, audit_path)

    result = broker.execute(call("native_skills.find_skill", {"query": "PDF support", "max_results": 3}))

    assert result.allowed is True
    payload = json.loads(result.content)
    assert payload["matches"][0]["name"] == "PDF/documents"
    assert payload["external_install_used"] is False
    events = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
    assert events[-1]["tool_name"] == "native_skills.find_skill"
    assert events[-1]["trust_level"] == "UNTRUSTED_DOCUMENT"
    assert any(path.endswith("NATIVE_CANDIDATE_MATRIX.md") for path in events[-1]["files_read"])
    assert events[-1]["network_domains"] == []
