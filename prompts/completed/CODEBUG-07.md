---
prompt_id: CODEBUG-07
pack_id: codebase-bug-review-and-hardening-v1
title: Whole-codebase static bug scan
category: release_gate
risk_level: MEDIUM
approval_gate: false
depends_on: ["CODEBUG-06"]
status: completed
order: 7
created_at: 2026-05-25T19:29:34+00:00
imported_at: 2026-05-25T19:29:34+00:00
source_pack: prompts/packs/codebase-bug-review-and-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T19:40:42+00:00
completed_at: 2026-05-25T22:00:14+00:00
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
Run whole-codebase static bug scan.

Goal:
Search the entire codebase for common bug patterns and safety anti-patterns, fix safe/scoped issues, and report larger issues.

Scope:
- Static grep/code review.
- Safe fixes.
- Tests.

Non-goals:
- Do not run untrusted scripts.
- Do not install linters.
- Do not broadly refactor.
- Do not change behavior without tests.

Search for:
- TODO/FIXME/HACK/XXX
- bare except
- broad Exception swallowing
- subprocess usage
- os.system
- shell=True
- eval/exec
- importlib on untrusted paths
- direct network calls outside web/provider layer
- direct file access outside workspace/path policy
- direct tool execution outside ToolBroker
- approval bypass
- audit bypass
- secrets printed/logged
- personal data stored by default
- mutable default args
- missing timeouts
- unbounded loops
- unbounded retries
- large file reads without limits
- missing redaction
- hardcoded API keys/tokens
- path traversal risk
- unsafe YAML load
- JSON parsing without error handling in provider code

Create/update:
- docs/bugfix/STATIC_BUG_SCAN_REPORT.md

Fix safe/scoped issues and add tests.

Run targeted tests and full tests if practical.

Final report:
- patterns scanned
- findings by severity
- fixes made
- deferred issues
- tests run/results
