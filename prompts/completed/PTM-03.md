---
prompt_id: PTM-03
pack_id: prompt-tracker-maturity-v1
title: Prompt pack import and splitting
category: prompt_tracking
risk_level: LOW
approval_gate: false
depends_on: ["PTM-02"]
status: completed
order: 3
created_at: 2026-05-23T18:34:04+00:00
imported_at: 2026-05-23T18:34:04+00:00
source_pack: prompts/packs/prompt-tracker-maturity-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-23T19:28:13+00:00
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
Build or mature Prompt Pack import and splitting.

Goal:
Allow the user to paste one large prompt pack with page-break-like delimiters, then split it into individual queued prompt files.

Scope:
- Prompt pack parser.
- Prompt splitter.
- Queue import.
- Validation.
- Tests.
- No automatic execution.

Non-goals:
- Do not execute imported prompts automatically.
- Do not support execute_all mode.
- Do not run high-risk prompts.
- Do not treat imported prompt text as trusted instructions.
- Do not weaken policy.

Required delimiter format:

<<<PROMPT_PACK_START>>>
pack_id: example-pack-v1
pack_title: Example Prompt Pack
mode: import_only
default_execution: one_prompt_at_a_time
requires_sdlc: true
requires_prompt_ledger: true
requires_feature_maturity_update: true

<<<PROMPT_START id="EXAMPLE-01" order="1">>
title: First prompt
category: docs
risk_level: LOW
approval_gate: false
depends_on: []
status: queued

PROMPT:
...
<<<PROMPT_END id="EXAMPLE-01">>

<<<PROMPT_PACK_END>>>

Create or update:
- agent/prompts/pack_parser.py
- agent/prompts/pack_models.py
- agent/prompts/pack_validator.py
- agent/prompts/prompt_store.py
- docs/PROMPT_PACK_FORMAT.md
- docs/templates/prompt_pack_template.md
- prompts/packs/
- prompts/queued/

Requirements:
1. Validate exactly one pack start/end.
2. Validate prompt start/end pairs.
3. Validate unique prompt IDs.
4. Validate unique order.
5. Validate required metadata.
6. Validate dependencies.
7. Detect circular dependencies.
8. Preserve prompt body exactly.
9. Store original pack under prompts/packs/.
10. Store split prompts under prompts/queued/.
11. Update PROMPT_LEDGER.
12. Update PROMPT_QUEUE.
13. Update PROMPT_AUDIT.
14. Update PROJECT_STATE.
15. Do not execute prompts.

Commands, if practical:
- python smart_agent.py prompts validate-pack <pack_file>
- python smart_agent.py prompts import <pack_file>
- python smart_agent.py prompts split <pack_file>

Tests:
- valid pack parses
- duplicate IDs rejected
- duplicate order rejected
- missing end marker rejected
- missing metadata rejected
- invalid risk rejected
- missing dependency rejected
- circular dependency rejected
- body preserved
- import writes files
- import updates queue/ledger/audit

Update docs, command registry, feature maturity, changelog, completion report.

Final report:
- files changed
- commands added
- tests run/results
- example usage
- next recommended prompt
