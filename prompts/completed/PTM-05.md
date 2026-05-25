---
prompt_id: PTM-05
pack_id: prompt-tracker-maturity-v1
title: Completion evidence auditor
category: prompt_tracking
risk_level: LOW
approval_gate: false
depends_on: ["PTM-04"]
status: completed
order: 5
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
Build Prompt Completion Evidence Auditor.

Goal:
Determine whether a prompt was actually completed by comparing prompt records against repo evidence.

Scope:
- Evidence collection.
- Audit report.
- Tests.
- No code feature implementation.

Evidence sources:
- git log
- git status
- CHANGELOG.md
- docs/COMPLETION_REPORT.md
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/COMMAND_REGISTRY.md
- tests/
- dogfood_suites/
- eval_cases/
- reports/
- bugs/

Create or update:
- agent/prompts/evidence.py
- agent/prompts/audit.py
- docs/PROMPT_AUDIT.md
- docs/prompt_tracker/PROMPT_EVIDENCE_POLICY.md

Commands:
- python smart_agent.py prompts audit
- python smart_agent.py prompts audit <prompt_id>
- python smart_agent.py prompts evidence <prompt_id>
- python smart_agent.py prompts missing

Evidence classifications:
- complete_verified
- likely_complete
- partial
- no_evidence
- failed
- blocked
- superseded
- stale

Rules:
1. Do not mark complete solely because docs mention a feature.
2. Prefer code/tests/docs/completion report together.
3. If command exists but tests do not, mark partial.
4. If docs exist but code does not, mark planned/stubbed.
5. If tests exist but docs missing, mark partial.
6. If live validation missing, do not mark live-validated.
7. Audit should be conservative.

Tests:
- prompt with files/tests/docs = complete_verified
- prompt with docs only = partial
- prompt with no evidence = no_evidence
- superseded prompt detected
- failed prompt remains failed
- evidence report includes missing pieces
- audit updates PROMPT_AUDIT

Update:
- docs/FEATURE_MATURITY.md
- docs/PROJECT_STATE.md
- docs/COMPLETION_REPORT.md
- CHANGELOG.md

Final report:
- evidence auditor status
- tests run/results
- prompts with missing evidence
- next recommended prompt
