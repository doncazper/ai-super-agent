---
prompt_id: CODEBUG-04
pack_id: codebase-bug-review-and-hardening-v1
title: Core runtime and brain provider bug review
category: core
risk_level: MEDIUM
approval_gate: false
depends_on: ["CODEBUG-03"]
status: completed
order: 4
created_at: 2026-05-25T19:29:34+00:00
imported_at: 2026-05-25T19:29:34+00:00
source_pack: prompts/packs/codebase-bug-review-and-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T19:36:04+00:00
completed_at: 2026-05-25T22:00:13+00:00
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
Review core runtime and brain provider code for bugs.

Goal:
Find and fix bugs in Orchestrator, Router, LM Studio/Brain providers, no-tools behavior, debug/tool-call loop, model errors, provider setup, and startup ergonomics.

Scope:
- agent/core/
- agent/brain/ if present
- smart_agent.py
- provider docs/tests

Non-goals:
- Do not change model default without explicit reason.
- Do not remove LM Studio.
- Do not install model runtimes.
- Do not download models.
- Do not call paid providers.

Check:
- no-tools attaches no tools
- router doesn't over-attach tools
- tool-call loop bounded
- tool_call_id handling
- LMSTUDIO_MODEL missing diagnostics
- server unavailable diagnostics
- malformed model responses
- provider fallback disabled by default
- startup import overhead
- Python version guard
- exact chat quality not degraded by harness

Create/update:
- docs/bugfix/CORE_RUNTIME_REVIEW.md

Add regression tests for fixed issues.

Run targeted core/brain tests and full tests if practical.

Final report:
- runtime bugs found/fixed
- tests added
- provider status
