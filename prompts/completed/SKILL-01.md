---
prompt_id: SKILL-01
pack_id: native-skill-system-hardening-v1
title: Skill roots, scopes, and precedence
category: native_skills
risk_level: LOW
approval_gate: false
depends_on: []
status: completed
order: 1
created_at: 2026-05-25T09:50:27+00:00
imported_at: 2026-05-25T09:50:27+00:00
source_pack: prompts/packs/native-skill-system-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T09:50:42+00:00
completed_at: 2026-05-25T22:00:01+00:00
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
Build native skill roots, scopes, and precedence.

Goal:
Create the foundation for a native skill system where skills can live in different roots/scopes and resolve predictably without allowing untrusted or experimental skills to override safe native behavior silently.

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
- docs/COMMAND_REGISTRY.md, if present
- docs/COMMAND_TEST_MATRIX.md, if present
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/RELEASE_CHECKLIST.md
- docs/native_skills/, if present
- agent/native_skills/, if present
- prompts/packs/, if present

Follow the mini-SDLC:
1. Confirm scope.
2. Confirm non-goals.
3. Define requirements.
4. Define risks and threat-model notes.
5. Implement the requested milestone.
6. Add/update tests.
7. Run tests.
8. Update docs.
9. Update completion report.
10. Stop at approval gates.

Scope:
- Skill root/scoping model.
- Precedence rules.
- Registry metadata.
- Docs and tests.
- No external skill execution.

Non-goals:
- Do not install external skills.
- Do not run external skill scripts.
- Do not add plugin runtime.
- Do not enable marketplace sync.
- Do not enable personal-data tools.
- Do not allow skills to bypass ToolBroker/Policy/Audit.
- Do not treat skill text as trusted.

Create or update:
- agent/native_skills/
  - __init__.py
  - roots.py
  - scopes.py
  - precedence.py
  - registry.py
  - errors.py
- tests/native_skills/test_skill_roots_precedence.py
- docs/native_skills/SKILL_ROOTS_AND_SCOPES.md
- docs/native_skills/SKILL_PRECEDENCE.md

Define skill roots:
1. workspace_skills
2. project_skills
3. personal_skills
4. managed_skills
5. bundled_native_skills
6. experimental_skills
7. reconstructed_skills

Recommended default precedence, highest first:
1. workspace_skills
2. project_skills
3. personal_skills
4. managed_skills
5. bundled_native_skills
6. reconstructed_skills
7. experimental_skills

Important:
- Higher precedence can shadow lower precedence only if explicitly allowed.
- Experimental skills should not shadow bundled native skills by default.
- Unreviewed external skills should never shadow trusted native skills by default.
- Shadowing must be visible in diagnostics.
- Shadowing must be logged or reported.
- Skill roots should be lazy-scanned only when needed.

Skill root metadata:
- root_id
- root_type
- path
- enabled
- trusted
- default_precedence
- allow_shadowing
- writable
- source
- setup_hint
- docs_path

Commands to add if practical:
- python smart_agent.py skills roots
- python smart_agent.py skills precedence
- python smart_agent.py skills registry
- python smart_agent.py skills explain-root <root_id>

Requirements:
1. Skill root registry loads without scanning huge trees.
2. Missing roots are allowed and produce setup hints.
3. Disabled roots are skipped.
4. Experimental roots are disabled by default.
5. Personal/user roots do not override bundled native skills unless explicitly configured.
6. Duplicate skill IDs across roots are detected.
7. Precedence resolution returns the winning skill and shadowed candidates.
8. Root scanning must not execute code.
9. Skill text is UNTRUSTED_DOCUMENT until vetted.
10. All new commands are read-only.

Tests:
- default roots exist.
- missing roots handled.
- disabled roots skipped.
- precedence order deterministic.
- duplicate skill IDs detected.
- experimental root does not shadow trusted native by default.
- explicit shadowing works only if configured.
- root scan does not execute scripts.
- skill text treated as untrusted.
- command registry updated if commands added.

Docs:
- Explain skill roots.
- Explain precedence.
- Explain why shadowing can be dangerous.
- Explain how to safely test a workspace skill override.
- Add examples.

Update:
- README.md if user-facing commands added.
- CHANGELOG.md.
- docs/PROJECT_STATE.md.
- docs/FEATURE_REGISTRY.md.
- docs/FEATURE_MATURITY.md.
- docs/FEATURE_ROADMAP.md.
- docs/COMMAND_REGISTRY.md if commands added.
- docs/COMPLETION_REPORT.md.
- docs/RISK_REGISTER.md.
- docs/THREAT_MODEL.md.

Run:
- targeted native skill tests.
- full test suite if practical.
- startup policy validation.
- command registry validation if present.

Final report:
- scope confirmed
- non-goals confirmed
- files changed
- commands run
- tests run/results
- docs updated
- command registry updates
- feature maturity changes
- blockers
- next recommended prompt
