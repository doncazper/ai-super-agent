---
prompt_id: SKILL-09
pack_id: native-skill-system-hardening-v1
title: Skill docs generator
category: native_skills
risk_level: LOW
approval_gate: false
depends_on: ["SKILL-08"]
status: completed
order: 9
created_at: 2026-05-25T09:50:27+00:00
imported_at: 2026-05-25T09:50:27+00:00
source_pack: prompts/packs/native-skill-system-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T10:56:10+00:00
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
Build native skill docs generator.

Goal:
Generate or update skill catalog documentation from manifests, command registry, compatibility matrix, test status, and feature maturity so docs do not drift as the native skill system grows.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- docs/native_skills/
- docs/COMMAND_REGISTRY.md, if present
- docs/COMMAND_TEST_MATRIX.md, if present
- docs/FEATURE_MATURITY.md
- docs/FEATURE_REGISTRY.md
- docs/PROJECT_STATE.md
- docs/COMPLETION_REPORT.md

Scope:
- Docs generator.
- Dry-run support.
- Generated docs.
- Tests.
- No skill execution.

Non-goals:
- Do not execute skills.
- Do not install dependencies.
- Do not overwrite hand-written docs without review.
- Do not mark skills mature automatically.
- Do not hide known limitations.

Create or update:
- agent/native_skills/docs_generator.py
- tests/native_skills/test_skill_docs_generator.py
- docs/native_skills/SKILL_CATALOG.md
- docs/native_skills/SKILL_DOCS_GENERATION.md
- docs/templates/native_skill_doc_template.md

Commands:
- python smart_agent.py skills docs-generate --dry-run
- python smart_agent.py skills docs-generate
- python smart_agent.py skills catalog
- python smart_agent.py skills docs-check

Generated catalog should include:
- skill_id
- name
- description
- category
- status
- maturity
- risk_level
- trust_level
- profile visibility
- dependencies
- setup hints
- compatibility
- test status
- dogfood status
- provenance/trust
- lock status
- docs path
- commands
- known limitations

Rules:
1. Dry-run default if command can change files.
2. Generator must not execute skills.
3. Generator must not invent maturity.
4. Generator must preserve manual notes where possible.
5. Generated sections must be clearly marked.
6. Missing docs should be reported.
7. Deprecated/blocked skills should remain documented.
8. Command registry updated.

Tests:
- dry-run writes no files.
- generate writes catalog from fixture manifests.
- manual notes preserved or not overwritten.
- missing docs reported.
- deprecated skill included.
- maturity copied conservatively.
- command registry updated.

Update:
- docs/native_skills/SKILL_CATALOG.md.
- docs/native_skills/SKILL_DOCS_GENERATION.md.
- docs/COMMAND_REGISTRY.md.
- docs/FEATURE_REGISTRY.md.
- docs/FEATURE_MATURITY.md.
- docs/PROJECT_STATE.md.
- docs/COMPLETION_REPORT.md.
- CHANGELOG.md.

Run tests/validations.

Final report:
- docs generator added
- catalog generated/updated
- tests run/results
- next recommended prompt
