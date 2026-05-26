from __future__ import annotations

import json
from pathlib import Path

from agent.autonomy.skill_improvements import ImprovementEvidence, propose_improvements_from_evidence
from agent.config.loader import load_capabilities_config
from agent.core.tool_broker import ToolBroker
from agent.safety.audit import AuditLogger
from agent.safety.policy import PolicyEngine
from agent.tools.registry import default_registry
from agent.ui.command_registry import get_command
from smart_agent import _run_skills_command


ROOT = Path(__file__).resolve().parents[2]


def _broker(project: Path, audit_path: Path) -> ToolBroker:
    return ToolBroker(
        default_registry(project_root=project),
        PolicyEngine.from_config(load_capabilities_config(ROOT / "config/capabilities.yaml")),
        AuditLogger(audit_path),
        session_id="test-session",
        model="test-model",
        route="test",
    )


def test_bug_evidence_creates_improvement_proposal() -> None:
    report = propose_improvements_from_evidence(
        "native_skill_vetter",
        [
            ImprovementEvidence(
                source_type="bug",
                source_id="BUG-SKILL-001",
                skill_id="native_skill_vetter",
                summary="native_skill_vetter docs check failed after catalog update",
                test_hint="add regression for docs-check drift",
            )
        ],
        source_mode="bugs",
    )

    proposal = report["proposals"][0]
    assert report["status"] == "ok"
    assert proposal["skill_id"] == "native_skill_vetter"
    assert proposal["bug_ids"] == ["BUG-SKILL-001"]
    assert "add regression for docs-check drift" in proposal["tests_required"]


def test_dogfood_failure_creates_improvement_proposal() -> None:
    report = propose_improvements_from_evidence(
        "native_skill_vetter",
        [
            {
                "source_type": "dogfood",
                "source_id": "session-1:0",
                "skill_id": "native_skill_vetter",
                "summary": "native_skill_vetter command returned unclear setup hint",
                "risk_level": "MEDIUM",
            }
        ],
        source_mode="dogfood",
    )

    proposal = report["proposals"][0]
    assert proposal["dogfood_failures"] == ["session-1:0"]
    assert proposal["risk_level"] == "MEDIUM"


def test_no_evidence_returns_low_confidence_without_proposal() -> None:
    report = propose_improvements_from_evidence("native_skill_vetter", [], source_mode="bugs")

    assert report["status"] == "no_evidence"
    assert report["proposal_count"] == 0
    assert report["confidence"] == "low"
    assert report["modifies_files"] is False


def test_personal_or_unredacted_evidence_is_skipped() -> None:
    report = propose_improvements_from_evidence(
        "native_skill_vetter",
        [
            ImprovementEvidence(source_type="bug", source_id="raw", skill_id="native_skill_vetter", summary="raw", redacted=False),
            ImprovementEvidence(source_type="bug", source_id="email", skill_id="native_skill_vetter", summary="failed on customer email"),
        ],
    )

    assert report["status"] == "no_evidence"
    assert {item["source_id"] for item in report["skipped"]} == {"raw", "email"}


def test_proposal_includes_tests_rollback_and_lockfile_impact() -> None:
    report = propose_improvements_from_evidence(
        "native_skill_vetter",
        [ImprovementEvidence(source_type="feedback", source_id="FB-1", skill_id="native_skill_vetter", summary="manual QA found stale docs")],
    )
    proposal = report["proposals"][0]

    assert proposal["tests_required"]
    assert proposal["rollback_plan"]
    assert "No lockfile change in proposal phase" in proposal["lockfile_impact"]
    assert proposal["modifies_files"] is False
    assert proposal["updates_lockfile"] is False
    assert proposal["enables_skill"] is False


def test_high_risk_improvement_requires_human_review() -> None:
    report = propose_improvements_from_evidence(
        "native_skill_vetter",
        [
            ImprovementEvidence(
                source_type="bug",
                source_id="BUG-HIGH",
                skill_id="native_skill_vetter",
                summary="sandbox setup changed for skill vetter",
                risk_level="HIGH",
            )
        ],
    )

    proposal = report["proposals"][0]
    assert proposal["risk_level"] == "HIGH"
    assert proposal["human_review_required"] is True
    assert proposal["status"] == "needs_review"


def test_improvement_tools_are_brokered_and_audited(tmp_path: Path, monkeypatch) -> None:
    store = tmp_path / "skill_improvements.json"
    monkeypatch.setenv("SKILL_IMPROVEMENT_STORE_PATH", str(store))
    bug_dir = tmp_path / "bugs"
    bug_dir.mkdir()
    (bug_dir / "BUG-SKILL-001.json").write_text(
        json.dumps(
            {
                "bug_id": "BUG-SKILL-001",
                "title": "native_skill_vetter docs-check drift",
                "summary": "native_skill_vetter failed docs-check after catalog update",
                "severity": "LOW",
                "redacted": True,
            }
        ),
        encoding="utf-8",
    )
    audit_path = tmp_path / "audit.jsonl"
    broker = _broker(tmp_path, audit_path)

    code = _run_skills_command(["improve-from-bugs", "native_skill_vetter"], broker)

    assert code == 0
    assert store.exists()
    payload = json.loads(store.read_text(encoding="utf-8"))
    assert payload["proposal_count"] == 1
    assert payload["proposals"][0]["modifies_files"] is False
    events = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
    assert events[-1]["tool_name"] == "native_skills.improve_from_bugs"
    assert events[-1]["files_written"] == [str(store)]


def test_improvement_cli_list_and_show(tmp_path: Path, monkeypatch, capsys) -> None:
    store = tmp_path / "skill_improvements.json"
    monkeypatch.setenv("SKILL_IMPROVEMENT_STORE_PATH", str(store))
    bug_dir = tmp_path / "bugs"
    bug_dir.mkdir()
    (bug_dir / "BUG-SKILL-001.json").write_text(
        json.dumps({"bug_id": "BUG-SKILL-001", "summary": "native_skill_vetter fixture failed", "redacted": True}),
        encoding="utf-8",
    )
    broker = _broker(tmp_path, tmp_path / "audit.jsonl")
    assert _run_skills_command(["improve-from-bugs", "native_skill_vetter"], broker) == 0
    capsys.readouterr()

    assert _run_skills_command(["improvements", "list"], broker) == 0
    list_payload = json.loads(capsys.readouterr().out)
    improvement_id = list_payload["content"]["improvements"][0]["improvement_id"]

    assert _run_skills_command(["improvements", "show", improvement_id], broker) == 0
    show_payload = json.loads(capsys.readouterr().out)
    assert show_payload["content"]["improvement"]["improvement_id"] == improvement_id


def test_command_registry_tracks_skill_improvement_commands() -> None:
    command = get_command("CMD-SKILLS-041")

    assert command is not None
    assert command.command == "python smart_agent.py skills improve-propose <skill_id>"
    assert command.risk_level == "LOW"
    assert command.toolbroker_path.startswith("yes via native_skills.improve_propose")
    assert command.example
