---
prompt_id: SKILL-02
pack_id: native-skill-system-hardening-v1
title: Skill manifest schema and dependency gating
category: native_skills
risk_level: MEDIUM
approval_gate: false
depends_on: ["SKILL-01"]
status: completed
order: 2
created_at: 2026-05-25T09:50:27+00:00
imported_at: 2026-05-25T09:50:27+00:00
source_pack: prompts/packs/native-skill-system-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T09:57:20+00:00
completed_at: 2026-05-25T10:06:15+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: targeted native skill manifest/dependency/root tests 24 passed; focused manifest/dependency/root/command tests 29 passed; make policy-check passed; command registry validation passed with 402 commands; full suite passed with 1139 passed, 1 skipped
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
notes: Completed SKILL-02 manifest schema/dependency gating without installs, script execution, provider/connector calls, plugin runtime, personal-data enablement, or safety bypass.
---

# Prompt

You are Codex working in this repo.

Task:
Build native skill manifest schema and dependency gating.

Goal:
Define a strict native skill manifest format so skills declare their requirements, capabilities, risks, trust level, dependencies, memory behavior, audit behavior, and platform compatibility before they can be considered usable.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- docs/native_skills/SKILL_ROOTS_AND_SCOPES.md
- docs/native_skills/SKILL_PRECEDENCE.md
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/COMMAND_REGISTRY.md, if present
- docs/COMPLETION_REPORT.md
- agent/native_skills/, if present

Scope:
- Manifest schema.
- Dependency gating.
- Validation.
- Tests.
- Docs.

Non-goals:
- Do not execute skill scripts.
- Do not install dependencies.
- Do not enable unreviewed skills.
- Do not add plugin runtime.
- Do not grant new capabilities.

Create or update:
- agent/native_skills/manifest.py
- agent/native_skills/dependencies.py
- agent/native_skills/validator.py
- agent/native_skills/models.py
- tests/native_skills/test_skill_manifest_schema.py
- tests/native_skills/test_skill_dependency_gating.py
- docs/native_skills/SKILL_MANIFEST_SCHEMA.md
- docs/native_skills/SKILL_DEPENDENCY_GATING.md
- docs/templates/native_skill_manifest_template.yaml

Manifest fields:
- skill_id
- name
- description
- version
- category
- status
- maturity_level
- root_id
- source
- provenance
- risk_level
- trust_level
- allowed_tools
- required_capabilities
- required_connectors
- required_env
- required_config
- required_binaries
- required_files
- required_platforms
- required_python
- required_model_features
- approval_required
- approval_reuse_allowed
- memory_behavior
- audit_required
- network_behavior
- filesystem_behavior
- inputs_schema
- outputs_schema
- docs_path
- tests_path
- dogfood_suite
- owner
- license
- last_reviewed
- setup_hint
- known_limitations

Dependency types:
- env vars
- config keys
- local binaries
- Python package availability, detection only
- platform capability
- ToolBroker capability
- connector availability
- model/tool-call support
- workspace files
- native app bridge availability, planned/stubbed

Requirements:
1. Missing risk_level rejects manifest.
2. Missing trust_level rejects manifest.
3. Missing memory_behavior rejects manifest.
4. Missing audit_required rejects manifest.
5. Unknown required capability rejects manifest.
6. Missing dependency marks skill unavailable/requires_setup.
7. Dependency checks do not install anything.
8. Dependency checks do not execute untrusted code.
9. Environment variables are checked by presence only and redacted.
10. Required binaries are checked safely.
11. Personal-data capabilities disabled by default.
12. CRITICAL skills require per-action approval and no approval reuse.
13. Skill instructions are never allowed to override policy.
14. Validation should be fast and lazy where possible.

Commands if practical:
- python smart_agent.py skills validate
- python smart_agent.py skills validate <skill_id>
- python smart_agent.py skills doctor <skill_id>

Tests:
- valid manifest passes.
- missing risk fails.
- missing trust fails.
- missing memory behavior fails.
- unknown capability fails.
- missing env dependency returns requires_setup.
- missing binary returns requires_setup.
- env var value redacted.
- critical skill requires per-action approval.
- personal-data skill disabled by default.
- dependency check does not install packages or execute scripts.

Update:
- docs/native_skills/NATIVE_SKILLS_PROGRAM.md if present.
- docs/native_skills/SKILL_INTAKE_PROCESS.md if present.
- docs/FEATURE_REGISTRY.md.
- docs/FEATURE_MATURITY.md.
- docs/COMMAND_REGISTRY.md if commands added.
- docs/PROJECT_STATE.md.
- docs/COMPLETION_REPORT.md.
- CHANGELOG.md.
- docs/RISK_REGISTER.md.
- docs/THREAT_MODEL.md.

Run tests/validations.

Final report:
- manifest fields added
- dependency gates added
- tests run/results
- docs updated
- next recommended prompt
