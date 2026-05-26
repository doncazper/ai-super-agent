---
prompt_id: CANON-08
pack_id: canonical-runtime-gateway-hardening-v1
title: Canonical state dashboard and docs
category: runtime
risk_level: LOW
approval_gate: false
depends_on: ["CANON-07"]
status: completed
order: 8
created_at: 2026-05-26T04:45:51+00:00
imported_at: 2026-05-26T04:45:51+00:00
source_pack: prompts/packs/canonical-runtime-gateway-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T05:38:33+00:00
completed_at: 2026-05-26T05:46:45+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: runtime canonical dashboard/canonical state/gateway/recovery/runtime CLI tests 30 passed; command registry validation 585; policy-check passed
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
notes: Added read-only canonical-dashboard and handoff commands/docs; no file writes, tracker mutation, provider calls, server, or auto-resume.
---

# Prompt

Create read-only canonical state dashboard and docs.

Create/update:
- docs/runtime/CANONICAL_STATE_DASHBOARD.md
- docs/runtime/CANONICAL_STATE_HANDOFF.md
- agent/runtime/canonical_dashboard.py
- tests/runtime/test_canonical_state_dashboard.py

Commands if practical:
- python smart_agent.py runtime canonical-dashboard
- python smart_agent.py runtime handoff
- python smart_agent.py runtime handoff --for-chatgpt

Dashboard should show:
- canonical state summary
- active prompt/job/workflow/action
- next prompt
- last validation
- tracker conflicts
- dirty worktree summary
- safety summary
- Gateway/Kernel status
- recovery/resume hints
- handoff file recommendation

Rules:
- Read-only.
- No tool execution.
- No provider calls.
- No secrets/personal data.
- JSON and Markdown output if practical.
