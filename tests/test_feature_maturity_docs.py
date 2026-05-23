from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def table_rows(markdown: str, required_header: str) -> list[dict[str, str]]:
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        if not line.startswith("|") or required_header not in line:
            continue
        headers = [cell.strip() for cell in line.strip("|").split("|")]
        rows: list[dict[str, str]] = []
        for row in lines[index + 2 :]:
            if not row.startswith("|"):
                break
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            if len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))
        return rows
    raise AssertionError(f"table with header {required_header!r} not found")


def test_tracking_docs_exist() -> None:
    for path in (
        "CHANGELOG.md",
        "docs/FEATURE_MATURITY.md",
        "docs/FEATURE_REGISTRY.md",
        "docs/PROJECT_STATE.md",
        "docs/FEATURE_ROADMAP.md",
        "docs/PROMPT_LEDGER.md",
        "docs/PROMPT_QUEUE.md",
        "docs/PROMPT_AUDIT.md",
        "docs/PROMPT_PACK_FORMAT.md",
        "docs/templates/prompt_record_template.md",
        "docs/templates/prompt_pack_template.md",
        "docs/templates/feature_maturity_template.md",
        "docs/templates/feature_record_template.md",
        "docs/templates/changelog_entry_template.md",
        "docs/templates/project_state_update_template.md",
        "docs/templates/native_skill_record_template.md",
    ):
        assert (ROOT / path).exists(), path


def test_feature_registry_has_required_tracking_columns() -> None:
    registry = read("docs/FEATURE_REGISTRY.md")
    header = next(line for line in registry.splitlines() if line.startswith("| Feature ID |"))
    for column in (
        "Feature ID",
        "Feature name",
        "Category",
        "Status",
        "Risk level",
        "Trust level",
        "Capabilities",
        "Commands",
        "ToolBroker path verified",
        "PolicyEngine checked",
        "Approval required",
        "Audit behavior",
        "Memory behavior",
        "Tests",
        "Docs",
        "Dependencies",
        "Release gate status",
        "Last updated",
    ):
        assert column in header


def test_project_state_has_resume_sections() -> None:
    project_state = read("docs/PROJECT_STATE.md")

    for section in (
        "## Purpose",
        "## Current Overall Phase",
        "## Current Batch",
        "## Current Task",
        "## Current Status",
        "## Current Branch",
        "## Last Known Good Commit",
        "## Last Test Result",
        "## Startup Policy Status",
        "## Last Updated Timestamp",
        "## Last Completed Work",
        "## Current Work In Progress",
        "## Files Being Changed",
        "## Commands Run",
        "## Test Status",
        "## Blockers",
        "## Decisions Made During Current Task",
        "## Things To Verify Before Marking Complete",
        "## Next Queue",
        "## Open Decisions",
        "## Known Risks",
        "## Resume Instructions For Codex",
        "## Last Run Summary",
    ):
        assert section in project_state
    assert "Before doing any work:" in project_state
    assert "Before finishing any run:" in project_state


def test_agents_requires_project_tracking_updates() -> None:
    agents = read("AGENTS.md")

    assert "Every Codex run must read `docs/PROJECT_STATE.md` before making changes." in agents
    assert "Every Codex run must update `docs/PROJECT_STATE.md` before finishing." in agents
    assert "Every user-visible feature must update `CHANGELOG.md`." in agents
    assert "Every feature, command, connector, workflow, or policy change must update `docs/FEATURE_REGISTRY.md`." in agents
    assert "Every roadmap status change must update `docs/FEATURE_ROADMAP.md`." in agents
    assert "Every run must update `docs/COMPLETION_REPORT.md`." in agents
    assert "Do not mark a task complete if `docs/PROJECT_STATE.md` still says `in_progress`." in agents
    assert "Before starting feature work, read `docs/FEATURE_MATURITY.md`." in agents
    assert "update `docs/FEATURE_MATURITY.md`" in agents
    assert "Prompt count is useful context but not proof of maturity." in agents
    assert "A feature can be complete but still immature." in agents
    assert "Before starting work, read `docs/PROMPT_QUEUE.md` and `docs/PROMPT_LEDGER.md`." in agents
    assert "Every Codex final report must include the `prompt_id` and `next_prompt_id`." in agents


def test_native_skills_program_docs_exist_and_define_safety_boundary() -> None:
    for path in (
        "docs/native_skills/NATIVE_SKILLS_PROGRAM.md",
        "docs/native_skills/SKILL_INTAKE_PROCESS.md",
        "docs/native_skills/NATIVE_SKILL_CRITERIA.md",
        "docs/native_skills/NATIVE_SKILL_CANDIDATES.md",
        "docs/native_skills/SKILL_RISK_MODEL.md",
        "docs/native_skills/SKILL_MARKETPLACE_SURVEY.md",
        "docs/native_skills/NATIVE_CANDIDATE_MATRIX.md",
        "docs/native_skills/TOP_NATIVE_SKILL_SHORTLIST.md",
        "docs/native_skills/pdf.md",
        "native_skills/native_skill_vetter.yaml",
        "native_skills/native_skill_finder.yaml",
        "native_skills/pdf_workspace.yaml",
    ):
        assert (ROOT / path).exists(), path

    program = read("docs/native_skills/NATIVE_SKILLS_PROGRAM.md")
    criteria = read("docs/native_skills/NATIVE_SKILL_CRITERIA.md")
    risk_model = read("docs/native_skills/SKILL_RISK_MODEL.md")

    assert "maps to existing `ToolBroker` capabilities" in program
    assert "an unreviewed external script" in program
    assert "direct tool access" in program
    assert "automatic installation" in program
    assert "require unrestricted filesystem access" in criteria
    assert "require browser cookies or session tokens" in criteria
    assert "require Keychain or password access" in criteria
    assert "External skill ecosystems" in risk_model
    assert "never run during intake" in risk_model

    survey = read("docs/native_skills/SKILL_MARKETPLACE_SURVEY.md")
    matrix = read("docs/native_skills/NATIVE_CANDIDATE_MATRIX.md")
    shortlist = read("docs/native_skills/TOP_NATIVE_SKILL_SHORTLIST.md")

    assert "does not install, import, run, clone, or execute external skills" in survey
    assert "Skill-vetter native" in shortlist
    assert "Email send" in shortlist
    assert "skill_id: native_skill_vetter" in read("native_skills/native_skill_vetter.yaml")
    assert "skill_id: native_skill_finder" in read("native_skills/native_skill_finder.yaml")
    assert "skill_id: pdf_workspace" in read("native_skills/pdf_workspace.yaml")
    for column in (
        "User Value",
        "Frequency",
        "Safety Concern",
        "Implementation Difficulty",
        "Dependency Risk",
        "Personal-Data Risk",
        "Workspace-Bounded Feasibility",
        "Testability",
        "Native Priority",
    ):
        assert column in matrix


def test_prompt_tracking_docs_are_valid() -> None:
    queue_rows = table_rows(read("docs/PROMPT_QUEUE.md"), "prompt_id")
    ledger_rows = table_rows(read("docs/PROMPT_LEDGER.md"), "prompt_id")
    project_state = read("docs/PROJECT_STATE.md")

    assert queue_rows
    assert ledger_rows
    assert all(row["prompt_id"] for row in queue_rows)
    assert all(row["prompt_id"] for row in ledger_rows)
    assert {row["status"] for row in queue_rows} <= {"queued", "active", "completed", "skipped", "failed", "superseded", "blocked"}
    active_prompt_ids = {row["prompt_id"] for row in ledger_rows + queue_rows if row["status"] == "active"}
    assert len(active_prompt_ids) <= 1
    assert "active_prompt_id" in project_state
    assert "next_prompt_id" in project_state
    assert "prompt_queue_status" in project_state
    assert "last_prompt_audit_result" in project_state


def test_every_registry_feature_has_valid_status_and_safety_fields() -> None:
    rows = table_rows(read("docs/FEATURE_REGISTRY.md"), "Feature ID")

    assert rows
    for row in rows:
        feature = row["Feature name"]
        assert row["Status"] in {"planned", "in_progress", "complete", "blocked", "deferred"}, feature
        assert row["ToolBroker path verified"] in {"yes", "no"}, feature
        assert row["PolicyEngine checked"] in {"yes", "no"}, feature
        assert row["Approval required"], feature
        assert row["Audit behavior"], feature
        assert row["Memory behavior"], feature
        assert row["Release gate status"], feature


def test_changelog_has_keep_a_changelog_sections() -> None:
    changelog = read("CHANGELOG.md")

    assert "## Unreleased" in changelog
    for section in (
        "### Added",
        "### Changed",
        "### Fixed",
        "### Security",
        "### Deprecated",
        "### Removed",
        "### Known Limitations",
    ):
        assert section in changelog


def test_feature_maturity_assessment_covers_registry_features() -> None:
    registry_features = {row["Feature name"] for row in table_rows(read("docs/FEATURE_REGISTRY.md"), "Feature ID")}
    maturity_features = {row["Feature"] for row in table_rows(read("docs/FEATURE_MATURITY.md"), "Maturity Level")}
    aliases = {
        "LM Studio/Qwopus chat": "LM Studio no-tool chat",
        "Memory v2": "Memory",
    }
    normalized_registry_features = {aliases.get(feature, feature) for feature in registry_features}

    # Tracking-only foundation entries do not need maturity rows until they become user-facing runtime features.
    exempt = {"ToolBroker", "PolicyEngine", "PermissionManager", "ApprovalManager", "AuditLogger"}
    assert normalized_registry_features - exempt <= maturity_features
