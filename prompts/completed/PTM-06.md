---
prompt_id: PTM-06
pack_id: prompt-tracker-maturity-v1
title: PROJECT_STATE / FEATURE_MATURITY integration
category: prompt_tracking
risk_level: LOW
approval_gate: false
depends_on: ["PTM-05"]
status: completed
order: 6
created_at: 2026-05-23T18:34:04+00:00
imported_at: 2026-05-23T18:34:04+00:00
source_pack: prompts/packs/prompt-tracker-maturity-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-23T19:28:14+00:00
completed_at: 2026-05-23T19:28:14+00:00
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
Integrate prompt tracker with PROJECT_STATE and FEATURE_MATURITY.

Goal:
The project should always know the active prompt, next prompt, queue status, and how prompt counts affect feature maturity.

Scope:
- Docs/tracking integration.
- Tests/validation.
- No prompt execution.

Update docs/PROJECT_STATE.md to include:
- active_prompt_id
- next_prompt_id
- active_prompt_pack
- prompt_queue_status
- last_prompt_audit_result
- current_prompt_batch
- prompt_blockers
- prompt_resume_instructions

Update docs/FEATURE_MATURITY.md to include:
- prompt_count
- last_prompt_id
- last_prompt_batch
- implementation_prompt_count
- hardening_prompt_count
- dogfood_prompt_count
- release_gate_prompt_count
- prompt_evidence_status

Rules:
1. Prompt count is context, not proof of maturity.
2. A feature can have many prompts and still be immature if tests/live validation are missing.
3. A feature cannot be marked mature without tests/docs/policy/audit evidence.
4. Active prompt and next prompt must be visible in PROJECT_STATE.
5. Finished prompt runs must update feature maturity if feature behavior changed.

Validation:
- PROJECT_STATE has active_prompt_id and next_prompt_id.
- FEATURE_MATURITY has prompt_count/last_prompt_id fields.
- Prompt CLI updates PROJECT_STATE.
- Completion evidence can update maturity status conservatively.
- AGENTS.md requires updates.

Update:
- AGENTS.md
- docs/PROMPT_LEDGER.md
- docs/PROMPT_QUEUE.md
- docs/PROMPT_AUDIT.md
- docs/PROJECT_STATE.md
- docs/FEATURE_MATURITY.md
- docs/COMPLETION_REPORT.md
- CHANGELOG.md

Tests:
- update active prompt updates PROJECT_STATE.
- complete prompt updates last_prompt_id.
- maturity prompt count increments.
- prompt count alone does not mark feature mature.
- docs validation passes.

Final report:
- files changed
- tests run/results
- PROJECT_STATE prompt fields
- maturity integration
- next recommended prompt
