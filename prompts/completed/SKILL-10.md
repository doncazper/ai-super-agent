---
prompt_id: SKILL-10
pack_id: native-skill-system-hardening-v1
title: Native skill system release gate
category: release_gate
risk_level: LOW
approval_gate: false
depends_on: ["SKILL-09"]
status: completed
order: 10
created_at: 2026-05-25T09:50:27+00:00
imported_at: 2026-05-25T09:50:27+00:00
source_pack: prompts/packs/native-skill-system-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T11:04:54+00:00
completed_at: 2026-05-25T22:00:04+00:00
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
Run Native Skill System release gate.

Goal:
Validate that the native skill system is safe, trackable, documented, testable, and ready to support future native skills without importing marketplace risk into the agent.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- CHANGELOG.md
- README.md
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/FEATURE_ROADMAP.md
- docs/COMMAND_REGISTRY.md
- docs/COMMAND_TEST_MATRIX.md, if present
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/TEST_PLAN.md
- docs/RELEASE_CHECKLIST.md
- docs/native_skills/
- agent/native_skills/
- dogfood_suites/native_skills_core.yaml, if present
- eval_cases/native_skills/, if present

Scope:
- Validation.
- Small fixes only if needed.
- Maturity review.
- Release gate docs.
- No new major runtime behavior.

Non-goals:
- Do not install external skills.
- Do not enable external skills.
- Do not run external scripts.
- Do not add plugin runtime.
- Do not enable personal-data skills.
- Do not bypass safety controls.

Run:
1. full test suite
2. startup policy validation
3. capability manifest validation
4. docs validation
5. command registry validation
6. native skill manifest validation
7. skill lockfile verification, if implemented
8. skill conflict detection
9. native skill dogfood suite with safe fixtures
10. native skill eval suite with mocks/fixtures
11. skills docs-check, if implemented

Verify:
- skill roots exist and precedence is deterministic.
- experimental/unreviewed skills cannot silently override trusted native skills.
- manifest schema requires risk/trust/memory/audit fields.
- dependency gating does not install packages or execute scripts.
- provenance/trust metadata exists.
- lockfile/pinning exists or documented as future if not implemented.
- inspection/vetting detects scripts, secrets, network, filesystem, browser/session, personal-data, and approval-bypass risks.
- profile allowlists enforce risk ceilings and personal-data defaults.
- compatibility matrix exists.
- conflict detector works.
- test/dogfood harness exists.
- docs generator/catalog exists.
- no external skill execution by default.
- no personal-data skill enabled by default.
- all commands are in COMMAND_REGISTRY.
- feature maturity is conservative.

Create or update:
- docs/native_skills/NATIVE_SKILL_SYSTEM_RELEASE_GATE.md
- docs/native_skills/NATIVE_SKILL_SYSTEM_MATURITY_REVIEW.md

Maturity assessment:
- Skill roots/scopes/precedence
- Manifest schema
- Dependency gating
- Provenance/trust metadata
- Lockfile/pinning
- Inspection/vetting
- Profile allowlists
- Compatibility matrix
- Conflict detector
- Test/dogfood harness
- Docs generator/catalog
- Release gate

Classify each:
- Idea
- Specified
- Scaffolded
- Implemented
- Tested
- Hardened
- Live-Validated
- User-Ready
- Mature Pattern

Update:
- CHANGELOG.md.
- README.md if needed.
- docs/PROJECT_STATE.md.
- docs/FEATURE_REGISTRY.md.
- docs/FEATURE_MATURITY.md.
- docs/FEATURE_ROADMAP.md.
- docs/COMMAND_REGISTRY.md.
- docs/COMMAND_TEST_MATRIX.md if present.
- docs/COMPLETION_REPORT.md.
- docs/RISK_REGISTER.md.
- docs/THREAT_MODEL.md.
- docs/RELEASE_CHECKLIST.md.

Final report:
- tests run/results
- validation results
- dogfood/eval results
- maturity score
- remaining blockers
- whether native skill system is safe to rely on
- next recommended feature track
