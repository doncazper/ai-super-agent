---
prompt_id: SKILL-08
pack_id: native-skill-system-hardening-v1
title: Skill test and dogfood harness
category: native_skills
risk_level: MEDIUM
approval_gate: false
depends_on: ["SKILL-07"]
status: completed
order: 8
created_at: 2026-05-25T09:50:27+00:00
imported_at: 2026-05-25T09:50:27+00:00
source_pack: prompts/packs/native-skill-system-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T10:47:02+00:00
completed_at: 2026-05-25T10:56:02+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: focused harness tests 10 passed; broader harness/conflict/compatibility/dogfood/eval/command-registry tests 63 passed; docs/prompt/release artifact tests 21 passed; startup policy and capability manifest validation passed via make policy-check; command registry validation passed with 424 commands; native skill manifest validation passed with 3 valid; CLI smokes passed for skills test native_skill_vetter, skills test --all-safe, skills dogfood native_skill_vetter, eval run --native-skills --json, and dogfood show native_skills_core; full suite passed with 1197 passed, 1 skipped
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
notes: Completed metadata-only native skill test and dogfood harness. Added harness and dogfood modules, read-only skills test/dogfood commands, fixture-backed native skill evals, native skill dogfood suites, docs, command registry rows, and tracker updates. No untrusted skill execution, external script execution, dependency install, provider/connector call, plugin runtime execution, high/critical or personal-data auto-run, skill enablement, personal-data access, memory write, permission grant, or safety bypass added.
---

# Prompt

You are Codex working in this repo.

Task:
Build native skill test and dogfood harness.

Goal:
Every native skill should have a repeatable way to validate manifest, dependencies, policy behavior, command behavior, prompt-injection resistance, approval gates, and dogfood/manual QA.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- docs/native_skills/SKILL_MANIFEST_SCHEMA.md
- docs/native_skills/SKILL_VETTING.md
- docs/native_skills/SKILL_COMPATIBILITY_MATRIX.md
- docs/native_skills/SKILL_CONFLICTS.md
- docs/PROJECT_STATE.md
- docs/FEATURE_MATURITY.md
- docs/COMMAND_REGISTRY.md, if present
- docs/COMMAND_TEST_MATRIX.md, if present
- docs/COMPLETION_REPORT.md

Scope:
- Skill validation commands.
- Dogfood/eval suite conventions.
- Tests.
- Docs.
- No untrusted skill execution.

Non-goals:
- Do not run external scripts.
- Do not install dependencies.
- Do not run high/critical skills automatically.
- Do not access personal data.
- Do not enable skills.

Create or update:
- agent/native_skills/test_harness.py
- agent/native_skills/dogfood.py
- tests/native_skills/test_skill_test_harness.py
- dogfood_suites/native_skills_core.yaml
- dogfood_suites/native_skill_vetting.yaml
- eval_cases/native_skills/
- docs/native_skills/SKILL_TESTING.md
- docs/native_skills/SKILL_DOGFOOD_RUNBOOK.md

Commands:
- python smart_agent.py skills test <skill_id>
- python smart_agent.py skills test --all-safe
- python smart_agent.py skills dogfood <skill_id>
- python smart_agent.py skills validate <skill_id>
- python smart_agent.py eval run --native-skills
- python smart_agent.py dogfood run native_skills_core --session

Test categories:
- manifest validation
- dependency gating
- provenance/trust validation
- lockfile verification
- conflict detection
- profile allowlist check
- compatibility matrix check
- prompt-injection fixture
- secret fixture
- policy denial fixture
- approval-required fixture
- docs presence
- command registry presence

Rules:
1. Only safe tests run by default.
2. High/critical skills skipped unless explicitly approved.
3. Personal-data skills skipped by default.
4. External scripts never run.
5. Missing dependencies produce skipped/requires_setup, not failure unless expected.
6. Tests should prefer fixtures/mocks.
7. Dogfood should produce clear failure signals.
8. Results should update or inform FEATURE_MATURITY.
9. Command registry updated.

Tests:
- safe skill test passes.
- high-risk skill skipped by default.
- personal-data skill skipped by default.
- missing dependency reported.
- prompt injection fixture caught.
- secret fixture caught.
- dogfood suite YAML validates.
- eval report generated.
- command registry updated.

Update:
- docs/native_skills/SKILL_TESTING.md.
- docs/native_skills/SKILL_DOGFOOD_RUNBOOK.md.
- docs/TEST_PLAN.md.
- docs/COMMAND_REGISTRY.md.
- docs/COMMAND_TEST_MATRIX.md if present.
- docs/FEATURE_MATURITY.md.
- docs/PROJECT_STATE.md.
- docs/COMPLETION_REPORT.md.
- CHANGELOG.md.

Run tests/validations.

Final report:
- skill test harness added
- dogfood/eval suites added
- tests run/results
- next recommended prompt
