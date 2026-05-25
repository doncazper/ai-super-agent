from __future__ import annotations

from pathlib import Path

from agent.native_skills.allowlists import allowed_skills_report, skill_visibility, validate_profile_report
from agent.native_skills.manifest import manifest_from_mapping
from agent.native_skills.profiles import default_skill_profiles, profile_by_id
from agent.native_skills.registry import NativeSkillRegistry
from smart_agent import _run_skills_command
from tests.test_native_skill_manifests import manifest_data, write_project


def manifest(**overrides: object):
    return manifest_from_mapping(manifest_data(**overrides))


def test_default_profile_hides_high_risk_skills() -> None:
    profile = profile_by_id("default")
    assert profile is not None
    visible = skill_visibility(profile, manifest(skill_id="safe_doc", risk_level="LOW", category="documents"))
    hidden = skill_visibility(profile, manifest(skill_id="calendar_reader", risk_level="HIGH", category="calendar/scheduling"))

    assert visible.visible is True
    assert hidden.visible is False
    assert "exceeds profile ceiling" in hidden.reason


def test_locked_down_profile_exposes_safe_only() -> None:
    profile = profile_by_id("locked_down")
    assert profile is not None
    low = skill_visibility(profile, manifest(skill_id="low", risk_level="LOW", category="security"))
    safe = skill_visibility(profile, manifest(skill_id="safe", risk_level="SAFE", category="security"))

    assert low.visible is False
    assert safe.visible is True
    assert safe.reason.startswith("visible by profile metadata")


def test_research_and_coding_profiles_expose_expected_categories() -> None:
    research = profile_by_id("research")
    coding = profile_by_id("coding")
    assert research is not None
    assert coding is not None

    assert skill_visibility(research, manifest(skill_id="research_skill", category="research", network_behavior="none")).visible is True
    assert skill_visibility(coding, manifest(skill_id="coding_skill", category="coding")).visible is True
    assert skill_visibility(coding, manifest(skill_id="research_skill", category="research")).visible is False


def test_blocklist_overrides_allowlist() -> None:
    profile = profile_by_id("default")
    assert profile is not None
    blocked_profile = profile.__class__(**{**profile.to_dict(), "allowed_skills": ["demo_skill"], "blocked_skills": ["demo_skill"]})

    visible = skill_visibility(blocked_profile, manifest(skill_id="demo_skill", category="documents"))

    assert visible.visible is False
    assert visible.reason == "blocked by profile skill blocklist"


def test_risk_ceiling_personal_data_and_critical_rules() -> None:
    profile = profile_by_id("personal_assistant")
    assert profile is not None
    personal = manifest(
        skill_id="contacts_search",
        category="contacts",
        trust_level="LOCAL_PRIVATE_DATA",
        required_capabilities=["contacts.search"],
    )
    critical = manifest(
        skill_id="send_message",
        category="communications",
        risk_level="CRITICAL",
        approval_required="per_action",
        approval_reuse_allowed=False,
        required_capabilities=["messages.send"],
    )

    assert skill_visibility(profile, personal).visible is False
    assert skill_visibility(profile, critical).visible is False


def test_experimental_profile_disabled_by_default() -> None:
    experimental = profile_by_id("experimental")
    assert experimental is not None
    visibility = skill_visibility(experimental, manifest(skill_id="experiment", category="experimental", risk_level="LOW"))

    assert visibility.visible is False
    assert visibility.reason == "profile disabled by default"


def test_allowed_report_and_validation_keep_policy_final() -> None:
    manifests = [
        manifest(skill_id="doc", category="documents", risk_level="LOW"),
        manifest(skill_id="calendar", category="calendar/scheduling", risk_level="HIGH"),
    ]

    report = allowed_skills_report("default", manifests)
    validation = validate_profile_report("default", manifests)

    assert report["status"] == "ok"
    assert [item["skill_id"] for item in report["visible_skills"]] == ["doc"]
    assert "ToolBroker/PolicyEngine" in report["policy_note"]
    assert validation["status"] == "ok"


def test_profile_commands(tmp_path: Path, monkeypatch, capsys) -> None:
    write_project(tmp_path, manifest_data(skill_id="doc", category="documents", risk_level="LOW"))
    monkeypatch.chdir(tmp_path)

    assert _run_skills_command(["profiles"], broker=None) == 0  # type: ignore[arg-type]
    assert _run_skills_command(["profile", "show", "default"], broker=None) == 0  # type: ignore[arg-type]
    assert _run_skills_command(["profile", "allowed", "default"], broker=None) == 0  # type: ignore[arg-type]
    assert _run_skills_command(["profile", "validate", "default"], broker=None) == 0  # type: ignore[arg-type]
    output = capsys.readouterr().out
    assert "policy_engine_final" in output


def test_registry_profile_methods(tmp_path: Path) -> None:
    write_project(tmp_path, manifest_data(skill_id="doc", category="documents", risk_level="LOW"))
    registry = NativeSkillRegistry(tmp_path)

    assert len(default_skill_profiles()) == 7
    assert registry.profiles()["status"] == "ok"
    assert registry.profile("default")["status"] == "ok"
    assert registry.profile_allowed("default")["visible_skills"][0]["skill_id"] == "doc"
    assert registry.profile_validate("default")["status"] == "ok"
