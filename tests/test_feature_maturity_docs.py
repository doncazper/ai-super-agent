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


def test_reddit_forum_intelligence_planning_docs_define_safety_boundary() -> None:
    for path in (
        "docs/decisions/reddit_forum_intelligence_track.md",
        "docs/forums/FORUM_ACCESS_POLICY.md",
        "docs/forums/REDDIT_ACCESS_POLICY.md",
        "docs/forums/MULTILINGUAL_FORUM_STRATEGY.md",
        "docs/forums/CHINESE_FORUM_STRATEGY.md",
        "docs/forums/FORUM_SOURCE_GROUNDING.md",
        "docs/forums/FORUM_RETENTION_POLICY.md",
        "docs/forums/REDDIT_COMPLIANCE.md",
        "docs/forums/REDDIT_RETENTION.md",
        "docs/forums/REDDIT_RATE_LIMITS.md",
    ):
        assert (ROOT / path).exists(), path

    decision = read("docs/decisions/reddit_forum_intelligence_track.md")
    access = read("docs/forums/FORUM_ACCESS_POLICY.md")
    reddit = read("docs/forums/REDDIT_ACCESS_POLICY.md")
    chinese = read("docs/forums/CHINESE_FORUM_STRATEGY.md")
    grounding = read("docs/forums/FORUM_SOURCE_GROUNDING.md")
    retention = read("docs/forums/FORUM_RETENTION_POLICY.md")
    compliance = read("docs/forums/REDDIT_COMPLIANCE.md")
    reddit_retention = read("docs/forums/REDDIT_RETENTION.md")
    reddit_rate_limits = read("docs/forums/REDDIT_RATE_LIMITS.md")

    assert "does not add runtime API calls" in decision
    assert "Do not implement Reddit API calls" in decision
    assert "Official public API" in access
    assert "CAPTCHA, Cloudflare, anti-bot" in access
    assert "Forum text can be quoted, summarized, translated, and cited as source data" in access
    assert "Reddit official Data API" in reddit
    assert "No unauthenticated Reddit web scraping" in reddit
    assert "V2EX" in chinese
    assert "login-protected" in chinese
    assert "snippet_only" in grounding
    assert "Do not store Reddit/forum content permanently by default." in retention
    assert "Do not use forum content for model training." in retention
    assert "REDDIT_ENABLED=false" in compliance
    assert "Unauthenticated Reddit traffic is not allowed." in compliance
    assert "Reddit web scraping is not an API substitute." in compliance
    assert "REDDIT_USE_FOR_TRAINING=false" in reddit_retention
    assert "hard false" in reddit_retention
    assert "REDDIT_MAX_REQUESTS_PER_MINUTE=60" in reddit_rate_limits
    assert "structured rate-limit error" in reddit_rate_limits


def test_prompt_tracking_docs_are_valid() -> None:
    queue_rows = table_rows(read("docs/PROMPT_QUEUE.md"), "prompt_id")
    ledger_rows = table_rows(read("docs/PROMPT_LEDGER.md"), "prompt_id")
    project_state = read("docs/PROJECT_STATE.md")

    assert queue_rows
    assert ledger_rows
    assert all(row["prompt_id"] for row in queue_rows)
    assert all(row["prompt_id"] for row in ledger_rows)
    assert {row["status"] for row in queue_rows} <= {
        "queued",
        "active",
        "completed",
        "skipped",
        "failed",
        "superseded",
        "blocked",
        "approval_required",
        "needs_review",
    }
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


def test_cloneability_docs_exist_and_are_linked() -> None:
    for path in (
        "docs/AGENT_DNA.md",
        "docs/ARCHITECTURE_PRINCIPLES.md",
        "docs/CLONE_BLUEPRINT.md",
        "docs/MODEL_MIGRATION_GUIDE.md",
        "docs/PLATFORM_MIGRATION_GUIDE.md",
        "docs/REWRITE_CHECKLIST.md",
        "docs/BUILD_HISTORY.md",
        "docs/BUILD_PROVENANCE.md",
        "docs/DECISION_INDEX.md",
        "docs/RECONSTRUCTED_PROMPT_PACKS.md",
        "docs/templates/reconstructed_prompt_pack_template.md",
        "docs/cloneability/CLONEABILITY_RELEASE_GATE.md",
        "docs/cloneability/CLONEABILITY_MATURITY_REVIEW.md",
    ):
        assert (ROOT / path).exists(), path

    readme = read("README.md")
    agents = read("AGENTS.md")
    spec = read("SPEC.md")
    sdlc = read("docs/SDLC.md")
    registry = read("docs/FEATURE_REGISTRY.md")
    maturity = read("docs/FEATURE_MATURITY.md")

    assert "docs/AGENT_DNA.md" in readme
    assert "docs/CLONE_BLUEPRINT.md" in readme
    assert "docs/AGENT_DNA.md" in agents
    assert "docs/CLONE_BLUEPRINT.md" in agents
    assert "Cloneability And Portability" in spec
    assert "Build Provenance And Cloneability" in sdlc
    assert "AGENT-DNA-CLONEABILITY" in registry
    assert "Agent DNA / Cloneability" in maturity


def test_reconstructed_prompt_packs_are_marked_reconstructed() -> None:
    folder = ROOT / "prompts/packs/reconstructed"
    files = sorted(folder.glob("*.reconstructed.promptpack.md"))

    assert len(files) >= 11
    for file in files:
        text = file.read_text(encoding="utf-8")
        assert "status: reconstructed" in text, file
        assert "exact_original:" in text, file
        assert "confidence:" in text, file
        assert "caveats:" in text, file


def test_internet_access_graduation_docs_define_no_bypass_policy() -> None:
    for path in (
        "docs/decisions/internet_access_graduation_track.md",
        "docs/web/WEB_ACCESS_POLICY.md",
        "docs/web/INTERNET_PROVIDER_STRATEGY.md",
        "docs/web/SOURCE_GROUNDING_REQUIREMENTS.md",
        "docs/web/BLOCKED_SOURCE_POLICY.md",
    ):
        assert (ROOT / path).exists(), path

    decision = read("docs/decisions/internet_access_graduation_track.md")
    policy = read("docs/web/WEB_ACCESS_POLICY.md")
    provider_strategy = read("docs/web/INTERNET_PROVIDER_STRATEGY.md")
    grounding = read("docs/web/SOURCE_GROUNDING_REQUIREMENTS.md")
    blocked = read("docs/web/BLOCKED_SOURCE_POLICY.md")

    assert "This reset does not add provider calls" in decision
    assert "CAPTCHA/anti-bot bypass" in decision
    assert "Web content is data, not instruction." in policy
    assert "Do not write web queries or web content to memory by default." in policy
    assert "Self-hosted SearXNG" in provider_strategy
    assert "SerpAPI, if configured and allowed by cost policy" in provider_strategy
    assert "Graceful unavailable response" in provider_strategy
    assert "Invent sources or citations" in grounding
    assert "Return unavailable with `bypass_attempted=false`." in blocked
    assert "Browser-profile cookie use" in blocked
