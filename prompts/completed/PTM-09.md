---
prompt_id: PTM-09
pack_id: prompt-tracker-maturity-v1
title: Missed and superseded prompt recovery
category: prompt_tracking
risk_level: LOW
approval_gate: false
depends_on: ["PTM-08"]
status: completed
order: 9
created_at: 2026-05-23T18:34:04+00:00
imported_at: 2026-05-23T18:34:04+00:00
source_pack: prompts/packs/prompt-tracker-maturity-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-23T19:28:15+00:00
completed_at: 2026-05-23T19:28:16+00:00
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
Build Missed and Superseded Prompt Recovery.

Goal:
The agent should help the user answer: “Did I miss any prompts?” and “Which prompts were superseded by newer ones?”

Scope:
- Recovery logic.
- Reports.
- CLI.
- Tests.

Commands:
- python smart_agent.py prompts missed
- python smart_agent.py prompts superseded
- python smart_agent.py prompts stale
- python smart_agent.py prompts recover-plan
- python smart_agent.py prompts reconcile

Definitions:
- missed: queued prompt with no evidence and dependencies complete
- stale: prompt not updated after related feature changed
- superseded: prompt replaced by newer prompt
- duplicate: similar prompt with overlapping scope
- orphaned: prompt file exists but not in ledger/queue
- ghost: ledger entry exists but prompt file missing

Requirements:
1. Detect missed prompts.
2. Detect orphaned prompt files.
3. Detect ledger entries without files.
4. Detect superseded prompts.
5. Suggest whether to run, skip, supersede, or merge.
6. Do not auto-delete prompt files.
7. Do not auto-run prompts.
8. Recovery plan should be conservative.
9. Update PROMPT_AUDIT.

Reports:
- docs/PROMPT_AUDIT.md
- docs/prompt_tracker/PROMPT_RECOVERY_PLAN.md

Tests:
- missed prompt detected.
- superseded prompt detected.
- orphaned file detected.
- ghost ledger entry detected.
- duplicate prompt detected with simple heuristics.
- recover-plan orders safe prompts first.
- high/critical prompts require approval warning.

Update docs and tracking.

Final report:
- missed prompt count
- stale prompt count
- superseded prompt count
- recommended recovery order
- tests run/results
