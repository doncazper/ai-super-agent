---
prompt_id: SKILL-07
pack_id: native-skill-system-hardening-v1
title: Skill conflict detector
category: native_skills
risk_level: MEDIUM
approval_gate: false
depends_on: ["SKILL-06"]
status: completed
order: 7
created_at: 2026-05-25T09:50:27+00:00
imported_at: 2026-05-25T09:50:27+00:00
source_pack: prompts/packs/native-skill-system-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T10:39:08+00:00
completed_at: 2026-05-25T22:00:03+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: completed prompt file and prompt audit evidence verified during SOURCE-TRUTH-RECONCILE-01
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
notes: Reconciled stale imported row from completed prompt file and prompt audit evidence; no prompt was run by this reconciliation.
---

# Prompt

You are Codex working in this repo.

Task:
Build native skill conflict detector.

Goal:
Detect when skills conflict, shadow each other, claim the same command/capability, require disabled providers, or create unsafe ambiguity.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- docs/native_skills/SKILL_ROOTS_AND_SCOPES.md
- docs/native_skills/SKILL_PRECEDENCE.md
- docs/native_skills/SKILL_MANIFEST_SCHEMA.md
- docs/native_skills/SKILL_COMPATIBILITY_MATRIX.md
- docs/PROJECT_STATE.md
- docs/FEATURE_MATURITY.md
- docs/COMMAND_REGISTRY.md, if present
- docs/COMPLETION_REPORT.md

Scope:
- Conflict detection.
- Reports.
- CLI.
- Tests.
- No skill execution.

Non-goals:
- Do not auto-resolve conflicts unless safe metadata-only updates are explicitly requested.
- Do not delete skills.
- Do not enable/disable skills silently.
- Do not execute skill scripts.
- Do not bypass policy.

Create or update:
- agent/native_skills/conflicts.py
- tests/native_skills/test_skill_conflict_detector.py
- docs/native_skills/SKILL_CONFLICTS.md
- reports/native_skills/.gitkeep

Commands:
- python smart_agent.py skills conflicts
- python smart_agent.py skills conflicts --json
- python smart_agent.py skills explain-conflict <conflict_id>

Conflict types:
- duplicate_skill_id
- same_command
- same_capability_claim
- unsafe_shadowing
- experimental_overrides_native
- unreviewed_overrides_reviewed
- dependency_missing
- provider_disabled
- platform_incompatible
- risk_policy_mismatch
- approval_policy_mismatch
- memory_policy_mismatch
- docs_missing
- tests_missing

Conflict report fields:
- conflict_id
- conflict_type
- severity
- affected_skills
- winning_skill
- shadowed_skills
- risk_level
- reason
- suggested_resolution
- requires_human_review
- safe_to_continue

Rules:
1. Duplicate skill IDs reported.
2. Same command exposed by multiple skills reported.
3. Same capability claimed by multiple skills reported.
4. Experimental/unreviewed skill overriding trusted/native skill is high severity.
5. Skill requiring disabled provider reported.
6. Skill with missing approval policy reported.
7. Conflict detector does not execute skills.
8. Conflict detector does not modify files by default.
9. Reports saved under reports/native_skills if configured.
10. Command registry updated.

Tests:
- duplicate skill ID detected.
- same command detected.
- same capability claim detected.
- experimental overrides native flagged high severity.
- unreviewed overrides reviewed flagged.
- missing dependency reported.
- disabled provider reported.
- no script execution.
- JSON output valid.
- command registry updated.

Update:
- docs/native_skills/SKILL_CONFLICTS.md.
- docs/RISK_REGISTER.md.
- docs/THREAT_MODEL.md.
- docs/COMMAND_REGISTRY.md.
- docs/FEATURE_MATURITY.md.
- docs/PROJECT_STATE.md.
- docs/COMPLETION_REPORT.md.
- CHANGELOG.md.

Run tests/validations.

Final report:
- conflict detector added
- tests run/results
- known conflicts found, if any
- next recommended prompt
