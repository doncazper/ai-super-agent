---
prompt_id: SKILL-05
pack_id: native-skill-system-hardening-v1
title: Per-profile skill allowlists
category: native_skills
risk_level: MEDIUM
approval_gate: false
depends_on: ["SKILL-04"]
status: completed
order: 5
created_at: 2026-05-25T09:50:27+00:00
imported_at: 2026-05-25T09:50:27+00:00
source_pack: prompts/packs/native-skill-system-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T10:25:39+00:00
completed_at: 2026-05-25T10:31:05+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: focused profile/allowlist/native-skill manifest/command tests 20 passed; focused profile/inspection/provenance/manifest/native-skill/command tests 37 passed; docs/prompt/release artifact tests 21 passed; profile CLI smokes passed; make policy-check passed; command registry validation passed with 412 commands; full suite passed with 1165 passed, 1 skipped
docs_updated: yes
changelog_updated:
feature_registry_updated:
feature_maturity_updated:
command_registry_updated:
completion_report_updated:
evidence_links:
blockers:
next_prompt_id:
supersedes:
superseded_by:
notes: Added advisory native skill profile and allowlist visibility rules, read-only profile CLI commands, docs, template, command registry/test matrix, feature/risk/threat trackers. Next prompt: SKILL-06.
---

# Prompt

You are Codex working in this repo.

Task:
Build per-profile skill allowlists and skill visibility rules.

Goal:
Allow different agent modes/profiles to expose different skills safely. For example: default, research, coding, personal-assistant, lead-response, locked-down, experimental.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- docs/native_skills/SKILL_ROOTS_AND_SCOPES.md
- docs/native_skills/SKILL_MANIFEST_SCHEMA.md
- docs/native_skills/SKILL_PROVENANCE.md
- docs/PROJECT_STATE.md
- docs/FEATURE_MATURITY.md
- docs/COMMAND_REGISTRY.md, if present
- docs/COMPLETION_REPORT.md

Scope:
- Agent profile model.
- Skill allowlist/blocklist.
- Risk ceiling.
- Tests.
- Docs.

Non-goals:
- Do not add multi-agent execution.
- Do not delegate work to subagents.
- Do not enable personal-data tools.
- Do not run skills automatically.
- Do not bypass PolicyEngine.

Create or update:
- agent/native_skills/profiles.py
- agent/native_skills/allowlists.py
- tests/native_skills/test_skill_profiles_allowlists.py
- docs/native_skills/SKILL_PROFILES.md
- docs/native_skills/SKILL_ALLOWLISTS.md
- docs/templates/skill_profile_template.yaml

Profile fields:
- profile_id
- name
- description
- allowed_skills
- blocked_skills
- allowed_categories
- blocked_categories
- risk_ceiling
- allow_personal_data
- allow_network
- allow_writes
- allow_critical_actions
- default_tools
- memory_policy
- approval_policy
- docs_path

Default profiles:
1. default
2. research
3. coding
4. personal_assistant
5. lead_response
6. locked_down
7. experimental

Suggested defaults:
- default: low/medium safe skills only
- research: web/news/reddit/weather/docs skills, no personal-data writes
- coding: workspace/code/test/git docs skills, no personal-data
- personal_assistant: personal read-only skills disabled unless explicitly enabled
- lead_response: lead draft skills only, no sends by default
- locked_down: no skills or SAFE-only skills
- experimental: disabled by default

Requirements:
1. Skill visibility depends on profile.
2. Blocklist overrides allowlist.
3. Risk ceiling enforced.
4. Personal-data skills hidden unless profile allows and capability policy allows.
5. CRITICAL skills hidden unless explicitly allowed and approval-required.
6. Experimental profile disabled by default.
7. Profile changes do not modify policy directly.
8. ToolBroker/PolicyEngine still final authority.
9. Profile selection does not enable skills by itself.
10. Profile state visible in diagnostics.

Commands if practical:
- python smart_agent.py skills profiles
- python smart_agent.py skills profile show <profile_id>
- python smart_agent.py skills profile allowed <profile_id>
- python smart_agent.py skills profile validate <profile_id>

Tests:
- default profile hides high-risk skills.
- locked_down profile exposes none or safe-only.
- research profile exposes research skills.
- coding profile exposes coding skills.
- blocklist overrides allowlist.
- risk ceiling enforced.
- personal-data hidden by default.
- critical skill not visible by default.
- policy remains final authority.
- command registry updated.

Update:
- docs/COMMAND_REGISTRY.md if commands added.
- docs/FEATURE_REGISTRY.md.
- docs/FEATURE_MATURITY.md.
- docs/PROJECT_STATE.md.
- docs/COMPLETION_REPORT.md.
- CHANGELOG.md.
- docs/RISK_REGISTER.md.
- docs/THREAT_MODEL.md.

Run tests/validations.

Final report:
- profiles added
- allowlist behavior
- tests run/results
- next recommended prompt
