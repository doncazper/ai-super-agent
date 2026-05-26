---
prompt_id: CANON-03
pack_id: canonical-runtime-gateway-hardening-v1
title: Agent Gateway / Runtime Kernel boundary
category: runtime
risk_level: MEDIUM
approval_gate: false
depends_on: ["CANON-02"]
status: completed
order: 3
created_at: 2026-05-26T04:45:51+00:00
imported_at: 2026-05-26T04:45:51+00:00
source_pack: prompts/packs/canonical-runtime-gateway-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T05:00:36+00:00
completed_at: 2026-05-26T05:04:41+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: targeted runtime tests 27 passed; command registry validation passed with 571 commands; startup policy and capability manifest validation passed via make policy-check
docs_updated: true
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
notes: CANON-03 added Agent Gateway / Runtime Kernel boundary contracts, read-only runtime gateway/kernel/frontend commands, docs, command registry rows, and tests.
---

# Prompt

Define Agent Gateway / Runtime Kernel boundary.

Goal:
Make the long-term architecture explicit: all future frontends and channels should interact with an Agent Gateway / Runtime Kernel boundary that owns canonical state, durable execution records, approval state, checkpoint/recovery state, and safe action dispatch. The current CLI remains the first frontend.

Non-goals:
- Do not create Fastify/TypeScript gateway.
- Do not create a local web server.
- Do not create Mac/iOS/Windows UI.
- Do not start listeners.
- Do not enable Telegram/mobile channels.
- Do not expose tools externally.
- Do not replace the CLI.

Create/update:
- docs/runtime/AGENT_GATEWAY_RUNTIME_KERNEL.md
- docs/runtime/GATEWAY_OWNED_EXECUTION_TRUTH.md
- docs/runtime/FRONTEND_CHANNEL_STATE_BOUNDARY.md
- docs/runtime/GATEWAY_API_CONTRACT.md
- docs/decisions/agent_gateway_runtime_kernel.md
- agent/runtime/gateway_state.py
- agent/runtime/kernel_contract.py
- tests/runtime/test_gateway_kernel_boundary.py

Define Runtime Kernel owns:
- canonical runtime state
- durable execution records
- active job/prompt/workflow/action state
- approval-gated resume state
- checkpoints/recovery reports
- audit receipt references
- command/run summaries
- frontend/channel contracts
- no direct tool execution outside ToolBroker

Define Gateway responsibilities:
- receive frontend/channel requests
- normalize request envelopes
- assign correlation/request IDs
- route to runtime services safely
- require approval where needed
- return redacted summaries
- expose safe status
- never approve its own actions
- never execute tools directly
- never mutate policy/capabilities

Commands if practical:
- python smart_agent.py runtime gateway-status
- python smart_agent.py runtime kernel-status
- python smart_agent.py runtime frontend-contract

Tests:
- gateway request cannot execute tool directly
- approval request returns requires_review
- secrets redacted
- gateway status JSON serializable
- no server starts
- CLI remains first frontend
Update docs/tracking.
