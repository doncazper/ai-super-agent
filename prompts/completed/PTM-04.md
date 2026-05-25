---
prompt_id: PTM-04
pack_id: prompt-tracker-maturity-v1
title: Prompt status CLI
category: prompt_tracking
risk_level: LOW
approval_gate: false
depends_on: ["PTM-03"]
status: completed
order: 4
created_at: 2026-05-23T18:34:04+00:00
imported_at: 2026-05-23T18:34:04+00:00
source_pack: prompts/packs/prompt-tracker-maturity-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-23T19:28:13+00:00
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
Build Prompt Status CLI.

Goal:
Give the user simple terminal commands to inspect, search, show, and update prompt status.

Scope:
- CLI commands.
- Prompt state updates.
- Validation.
- Tests.
- No prompt execution yet.

Commands:
- python smart_agent.py prompts list
- python smart_agent.py prompts next
- python smart_agent.py prompts show <prompt_id>
- python smart_agent.py prompts search "<query>"
- python smart_agent.py prompts mark-active <prompt_id>
- python smart_agent.py prompts mark-complete <prompt_id>
- python smart_agent.py prompts mark-failed <prompt_id>
- python smart_agent.py prompts mark-skipped <prompt_id>
- python smart_agent.py prompts mark-superseded <prompt_id> --by <replacement_id>
- python smart_agent.py prompts audit
- python smart_agent.py prompts missing

Requirements:
1. prompts list shows ID, title, status, category, risk, dependencies.
2. prompts next returns the next queued prompt with dependencies complete.
3. prompts next must not return approval-gated high/critical prompts without clear warning.
4. prompts show displays metadata and prompt body.
5. mark-active enforces only one active prompt unless configured otherwise.
6. mark-complete requires evidence fields or --unknown flag.
7. mark-failed requires reason.
8. mark-superseded requires replacement.
9. prompts missing reports queued prompts with no completion evidence.
10. All status changes update PROMPT_LEDGER, PROMPT_QUEUE, PROMPT_AUDIT, and PROJECT_STATE.
11. Command registry updated.

Tests:
- list works
- next respects dependencies
- next skips blocked/superseded
- high/critical approval-gated prompt blocked or warned
- show works
- mark-active updates state
- mark-complete requires evidence
- mark-failed requires reason
- mark-superseded requires replacement
- missing detects no evidence
- command registry validation passes

Update docs and tracking files.

Final report:
- commands added
- tests run/results
- docs updated
- next recommended prompt
