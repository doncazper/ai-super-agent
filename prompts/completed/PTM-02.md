---
prompt_id: PTM-02
pack_id: prompt-tracker-maturity-v1
title: Prompt ledger / queue / audit schema hardening
category: prompt_tracking
risk_level: LOW
approval_gate: false
depends_on: ["PTM-01"]
status: completed
order: 2
created_at: 2026-05-23T18:34:04+00:00
imported_at: 2026-05-23T18:34:04+00:00
source_pack: prompts/packs/prompt-tracker-maturity-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-23T19:28:12+00:00
completed_at: 2026-05-23T19:28:13+00:00
branch:
commit_hash:
related_feature_ids: [PROMPT-LEDGER, PROMPTOPS-WORKBENCH]
expected_outputs:
tests_expected:
tests_run:
test_result: targeted prompt tracker tests passed: 54 passed
docs_updated: yes
changelog_updated:
feature_registry_updated:
feature_maturity_updated:
completion_report_updated:
blockers:
next_prompt_id:
supersedes:
superseded_by:
notes: Completed during controlled PTM batch run; evidence recorded in docs/prompt_tracker and targeted tests.
---

# Prompt

You are Codex working in this repo.

Task:
Harden Prompt Ledger, Prompt Queue, and Prompt Audit schemas.

Goal:
Make prompt tracking consistent, durable, and machine-checkable.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- docs/PROJECT_STATE.md
- docs/FEATURE_MATURITY.md
- docs/COMMAND_REGISTRY.md, if present
- docs/PROMPT_LEDGER.md, if present
- docs/PROMPT_QUEUE.md, if present
- docs/PROMPT_AUDIT.md, if present
- docs/prompt_tracker/PROMPT_TRACKER_AUDIT.md, if present

Scope:
- Schema/docs/data files.
- Validation tests if practical.
- No prompt execution.

Create or update:
- docs/PROMPT_LEDGER.md
- docs/PROMPT_QUEUE.md
- docs/PROMPT_AUDIT.md
- docs/templates/prompt_record_template.md
- docs/templates/prompt_pack_template.md
- docs/templates/prompt_completion_evidence_template.md

Required prompt fields:
- prompt_id
- pack_id
- title
- category
- status
- risk_level
- approval_gate
- depends_on
- source
- created_at
- imported_at
- started_at
- completed_at
- branch
- commit_hash
- related_feature_ids
- expected_outputs
- files_expected
- files_changed
- commands_expected
- commands_run
- tests_expected
- tests_run
- test_result
- docs_updated
- changelog_updated
- feature_registry_updated
- feature_maturity_updated
- command_registry_updated
- completion_report_updated
- blockers
- next_prompt_id
- supersedes
- superseded_by
- evidence_links
- notes

Statuses:
- queued
- active
- completed
- failed
- skipped
- superseded
- blocked
- approval_required
- needs_review

Prompt categories:
- docs
- tests
- diagnostics
- feature
- connector
- workflow
- safety
- policy
- prompt_tracking
- dogfood
- release_gate
- refactor
- platform
- web
- news
- reddit
- weather
- messaging
- native_skills

Rules:
- Only one active prompt at a time unless explicitly allowed.
- Completed prompts require evidence.
- Superseded prompts require superseded_by.
- Failed prompts require blocker or failure reason.
- Approval-required prompts must not be auto-run.
- High/critical prompts require manual review before execution.

Add validation if practical:
- required fields present
- unique prompt_id
- valid status
- valid risk_level
- dependencies point to existing prompt IDs
- no dependency cycles
- completed prompts have evidence
- only one active prompt unless multi-active mode enabled

Update:
- AGENTS.md prompt tracker rules
- docs/PROJECT_STATE.md prompt fields
- docs/FEATURE_MATURITY.md prompt tracker entry
- docs/COMMAND_REGISTRY.md if validation commands exist
- CHANGELOG.md
- docs/COMPLETION_REPORT.md

Run tests and validations.

Final report:
- schema changes
- validation added
- tests run/results
- next recommended prompt
