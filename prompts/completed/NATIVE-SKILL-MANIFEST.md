# Prompt Record: NATIVE-SKILL-MANIFEST

prompt_id: NATIVE-SKILL-MANIFEST
title: Native skill manifest and loader
category: native-skills
status: completed
source: user
created_at: 2026-05-23T08:25:06+00:00
pasted_to_codex: unknown
started_at: 2026-05-23T08:25:06+00:00
completed_at: 2026-05-23T08:31:53+00:00
branch:
commit_hash:
related_feature_ids: NATIVE-SKILL-MANIFEST
related_files: agent/native_skills/models.py, agent/native_skills/manifest.py, agent/native_skills/loader.py, agent/native_skills/validator.py, agent/native_skills/registry.py, native_skills/native_skill_vetter.yaml, tests/test_native_skill_manifests.py
expected_outputs: Metadata-only manifest models, loader, validator, registry, CLI list/show/validate/doctor, docs, tests, and built-in vetter manifest.
commands_expected: pytest, startup validation, capability validation, command validation, skills doctor
commands_run: pytest tests/test_native_skill_manifests.py; focused validation; full pytest; startup validation; capability validation; commands validate; skills validate; skills doctor
tests_expected: Native skill manifest tests and full suite
tests_run: yes
test_result: focused validation 37 passed; full suite 546 passed; startup policy ok; capability manifest ok; command registry ok; skills doctor ok
docs_updated: yes
changelog_updated: yes
feature_registry_updated: yes
feature_maturity_updated: yes
completion_report_updated: yes
blockers: none
next_prompt_id: SKILL-FINDER-NATIVE
supersedes:
superseded_by:
notes: Native skill manifest loader implemented as metadata-only discovery; no scripts executed, no packages installed, no permissions granted, no tools enabled.
