from __future__ import annotations

import json
from pathlib import Path

from agent.autonomy.skill_proposals import (
    CommandObservation,
    approve_proposal_dry_run,
    propose_from_command_observations,
    validate_suggested_manifest,
)
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


def test_repeated_safe_command_pattern_creates_proposal() -> None:
    report = propose_from_command_observations(
        [
            CommandObservation(command="python smart_agent.py skills docs-check", group="Native skills", risk_level="SAFE", source="cmd:1"),
            CommandObservation(command="python smart_agent.py skills catalog", group="Native skills", risk_level="SAFE", source="cmd:2"),
        ]
    )

    assert report["proposal_count"] == 1
    proposal = report["proposals"][0]
    assert proposal["status"] == "candidate_unreviewed"
    assert proposal["creates_enabled_skill"] is False
    assert proposal["skill_vetting_required"] is True


def test_personal_data_pattern_skipped_by_default() -> None:
    report = propose_from_command_observations(
        [
            CommandObservation(command="python smart_agent.py email inbox", group="Email", risk_level="HIGH", trust_level="LOCAL_PRIVATE_DATA", source="cmd:email"),
            CommandObservation(command="python smart_agent.py email draft", group="Email", risk_level="HIGH", trust_level="LOCAL_PRIVATE_DATA", source="cmd:draft"),
        ]
    )

    assert report["proposal_count"] == 0
    assert report["skipped"]
    assert report["skipped"][0]["reason"] == "personal-data pattern skipped by default"


def test_high_risk_non_personal_proposal_marked_review_required() -> None:
    report = propose_from_command_observations(
        [
            CommandObservation(command="python smart_agent.py backup restore", group="Backup restore", risk_level="HIGH", source="cmd:1"),
            CommandObservation(command="python smart_agent.py backup verify", group="Backup restore", risk_level="HIGH", source="cmd:2"),
        ]
    )

    proposal = report["proposals"][0]
    assert proposal["risk_level"] == "HIGH"
    assert proposal["approval_required"] is True
    assert proposal["status"] == "needs_review"


def test_suggested_manifest_includes_required_policy_fields() -> None:
    report = propose_from_command_observations(
        [
            CommandObservation(command="python smart_agent.py quality status", group="Quality", source="cmd:1"),
            CommandObservation(command="python smart_agent.py quality next", group="Quality", source="cmd:2"),
        ]
    )
    manifest = report["proposals"][0]["suggested_manifest"]

    assert validate_suggested_manifest(manifest) == []
    assert manifest["status"] == "candidate_unreviewed"
    assert manifest["default_enabled"] is False
    assert manifest["memory_behavior"] == "no_store"
    assert "audit_fields" in manifest


def test_proposal_dry_run_does_not_enable_skill(tmp_path: Path, monkeypatch) -> None:
    store = tmp_path / "skill_proposals.json"
    monkeypatch.setenv("SKILL_PROPOSAL_STORE_PATH", str(store))
    report = propose_from_command_observations(
        [
            CommandObservation(command="python smart_agent.py quality status", group="Quality", source="cmd:1"),
            CommandObservation(command="python smart_agent.py quality next", group="Quality", source="cmd:2"),
        ]
    )
    store.write_text(json.dumps(report), encoding="utf-8")

    proposal_id = report["proposals"][0]["proposal_id"]
    dry_run = approve_proposal_dry_run(proposal_id, project_root=tmp_path)

    assert dry_run["status"] == "dry_run_only"
    assert dry_run["would_create_enabled_skill"] is False
    assert dry_run["would_import_skill"] is False
    assert dry_run["would_enable_skill"] is False


def test_skill_proposal_tools_are_brokered_and_audited(tmp_path: Path, monkeypatch) -> None:
    store = tmp_path / "skill_proposals.json"
    monkeypatch.setenv("SKILL_PROPOSAL_STORE_PATH", str(store))
    audit_path = tmp_path / "audit.jsonl"
    broker = _broker(ROOT, audit_path)

    code = _run_skills_command(["propose-from-commands"], broker)

    assert code == 0
    assert store.exists()
    payload = json.loads(store.read_text(encoding="utf-8"))
    assert payload["creates_enabled_skills"] is False
    events = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
    assert events[-1]["tool_name"] == "native_skills.propose_from_commands"
    assert events[-1]["files_written"] == [str(store)]


def test_skill_proposal_cli_list_show_and_dry_run(tmp_path: Path, monkeypatch, capsys) -> None:
    store = tmp_path / "skill_proposals.json"
    monkeypatch.setenv("SKILL_PROPOSAL_STORE_PATH", str(store))
    broker = _broker(ROOT, tmp_path / "audit.jsonl")
    assert _run_skills_command(["propose-from-commands"], broker) == 0
    capsys.readouterr()

    assert _run_skills_command(["proposals", "list"], broker) == 0
    list_payload = json.loads(capsys.readouterr().out)
    proposal_id = list_payload["content"]["proposals"][0]["proposal_id"]

    assert _run_skills_command(["proposals", "show", proposal_id], broker) == 0
    show_payload = json.loads(capsys.readouterr().out)
    assert show_payload["content"]["proposal"]["proposal_id"] == proposal_id

    assert _run_skills_command(["proposals", "approve", proposal_id, "--dry-run"], broker) == 0
    approve_payload = json.loads(capsys.readouterr().out)
    assert approve_payload["content"]["status"] == "dry_run_only"
    assert approve_payload["content"]["would_enable_skill"] is False


def test_command_registry_tracks_skill_proposal_commands() -> None:
    command = get_command("CMD-SKILLS-037")

    assert command is not None
    assert command.command == "python smart_agent.py skills propose-from-commands"
    assert command.risk_level == "LOW"
    assert command.toolbroker_path.startswith("yes via native_skills.propose_from_commands")
    assert command.example

