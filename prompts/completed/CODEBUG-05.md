---
prompt_id: CODEBUG-05
pack_id: codebase-bug-review-and-hardening-v1
title: Connector and workflow bug review
category: connector
risk_level: MEDIUM
approval_gate: false
depends_on: ["CODEBUG-04"]
status: completed
order: 5
created_at: 2026-05-25T19:29:34+00:00
imported_at: 2026-05-25T19:29:34+00:00
source_pack: prompts/packs/codebase-bug-review-and-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T19:38:14+00:00
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
Review connectors and workflows for bugs.

Goal:
Find and fix safe/scoped bugs in weather, web, news, reddit/forums, workspace files, memory, calendar/contacts/email/messages/tasks stubs, workflows, dogfood/eval integrations.

Scope:
- agent/tools/
- agent/connectors/
- agent/weather/
- agent/web_acquisition/
- agent/news/
- agent/forums/
- agent/memory/
- agent/workflows/
- tests for these areas

Non-goals:
- Do not add new providers.
- Do not make live network calls unless existing safe mocked tests need no network.
- Do not enable personal-data connectors.
- Do not send/write anything.
- Do not bypass approval.

Check:
- provider missing errors
- cache/rate-limit behavior
- untrusted content wrappers
- prompt injection fixtures
- path traversal/file bounds
- memory secret refusal
- personal connector disabled defaults
- dogfood/eval fixtures not requiring personal data
- docs/commands align with implemented code

Create/update:
- docs/bugfix/CONNECTOR_WORKFLOW_REVIEW.md

Add regression tests for fixed issues.

Run targeted tests and full tests if practical.

Final report:
- connector/workflow bugs found/fixed
- tests added
- remaining blockers
