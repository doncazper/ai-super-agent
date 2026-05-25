# Prompt Record: PLATFORM-CAPABILITY-REGISTRY

prompt_id: PLATFORM-CAPABILITY-REGISTRY
title: Platform Capability Registry
category: platform
pack_id:
risk_level: LOW
approval_gate: false
depends_on: []
status: completed
source: user
created_at: 2026-05-25T07:44:45+00:00
pasted_to_codex: unknown
started_at: 2026-05-25T07:44:45+00:00
completed_at: 2026-05-25T07:52:24+00:00
branch: checkpoint/large-working-tree-20260523
commit_hash:
related_feature_ids: PLATFORM-CAPABILITY-REGISTRY,CROSS-PLATFORM-ARCHITECTURE-ROADMAP
related_files: agent/platforms/,tests/platforms/test_platform_capability_registry.py,docs/platforms/CAPABILITY_MATRIX.md,docs/platforms/PLATFORM_BRIDGE_STRATEGY.md
files_expected: agent/platforms/{__init__.py,models.py,registry.py,detection.py,capabilities.py,errors.py}; tests/platforms/test_platform_capability_registry.py
files_changed: agent/platforms/*,tests/platforms/test_platform_capability_registry.py,tests/test_prompt_tracking.py,platform docs,feature trackers,prompt trackers,changelog,project state,completion report,risk/threat/test/release docs
expected_outputs: Portable data-driven platform capability registry with static planned/stubbed records, safe detection metadata, structured unsupported records, and tests.
commands_expected: none
commands_run: pytest focused/full, startup policy validation, capability manifest validation, command registry validation, prompt mark-active/mark-complete/audit
tests_expected: Registry tests, startup policy validation, capability manifest validation, full suite if feasible
tests_run: yes
test_result: Registry tests 9 passed; focused platform/docs/registry/prompt tests 37 passed; full suite 1056 passed, 1 skipped; startup policy validation passed; capability manifest validation passed; command registry validation passed with 387 commands.
docs_updated: Created portable agent/platforms registry modules and tests; updated platform capability matrix/strategy, feature registry, maturity, roadmap, project state, completion report, risk register, threat model, test plan, release checklist, tracker dashboard, and changelog.
changelog_updated: yes
feature_registry_updated: yes
feature_maturity_updated: yes
command_registry_updated: no executable commands added or changed
completion_report_updated: yes
evidence_links:
blockers: none for metadata-only registry v1
next_prompt_id: PLATFORM-BRIDGE-BASE-INTERFACES
supersedes:
superseded_by:
notes: Implement Platform Capability Registry v1: portable data-driven registry, no native imports, no platform actions, planned personal-data capabilities disabled by default.
