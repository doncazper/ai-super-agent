---
prompt_id: ORCH-09
pack_id: agent-runtime-orchestration-v1
title: App/frontend bridge integration points
category: platform
risk_level: MEDIUM
approval_gate: false
depends_on: ["ORCH-08"]
status: completed
order: 9
created_at: 2026-05-23T21:24:19+00:00
imported_at: 2026-05-23T21:24:19+00:00
source_pack: prompts/packs/agent-runtime-orchestration-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-23T21:31:14+00:00
completed_at: 2026-05-23T21:31:15+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: ./.venv/bin/python -m pytest tests/runtime -q: 31 passed
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
notes: Added frontend bridge contract and tests; approvals, tool execution, and policy changes fail closed.
---

# Prompt

You are Codex working in this repo.

Task:
Define app/frontend bridge integration points for the runtime orchestrator.

Goal:
Prepare the runtime orchestrator to support future Mac app, iOS companion, Windows app, and local dashboard frontends without coupling the core to any specific UI.

Scope:
- Docs.
- Interface stubs/models if safe.
- No actual app bridge server.
- No native app code.
- No network listener.
- Tests if models added.

Non-goals:
- Do not build Mac app.
- Do not build iOS app.
- Do not build Windows app.
- Do not start localhost server.
- Do not implement remote access.
- Do not execute approvals from frontend without ApprovalManager.
- Do not add personal-data access.
- Do not add send/write behavior.

Create/update:
- docs/runtime/FRONTEND_BRIDGE_INTEGRATION.md
- docs/runtime/APP_FRONTEND_CONTRACT.md
- docs/runtime/APPROVAL_UI_CONTRACT.md
- docs/runtime/RUNTIME_STATUS_API_CONTRACT.md
- agent/runtime/frontend_bridge.py, only if safe and lightweight
- tests/runtime/test_frontend_bridge_contract.py, if code added

Frontend surfaces:
- CLI
- interactive CLI
- Mac app
- iOS companion
- Windows app
- local web dashboard
- background scheduler/status monitor

Frontend contract must cover:
- status request
- health request
- service list
- feature list
- connector status
- pending approvals
- pending actions
- prompt queue status
- command registry search
- feature maturity summary
- submit approval decision
- submit action result
- audit summary
- dogfood/session summary

Rules:
1. Frontends are clients, not policy authorities.
2. Frontends cannot approve actions without ApprovalManager.
3. Frontends cannot execute tools directly.
4. Frontends cannot modify policy directly.
5. Frontends cannot enable personal-data tools silently.
6. Frontends cannot start background jobs silently.
7. Frontends must provide exact previews for CRITICAL actions.
8. Frontend payloads must be schema-validated.
9. Frontend requests must be auditable.
10. Status/health endpoints must not return raw personal data.
11. Remote access is disabled/deferred.
12. Pairing/auth is required for future sensitive frontends.

If code stubs are added:
- define FrontendBridgeRequest
- define FrontendBridgeResponse
- define FrontendCapability
- define FrontendApprovalDecision
- define FrontendActionResult
- no server implementation
- no network listener

Tests:
- frontend request schemas validate
- sensitive request without approval rejected
- status payload contains no raw personal data
- frontend cannot bypass approval
- no server starts
- no network listener created
- no native app imports

Update:
- docs/FEATURE_ROADMAP.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/PROJECT_STATE.md
- docs/COMPLETION_REPORT.md
- CHANGELOG.md

Final report:
- bridge contract created
- code stubs added or not
- tests run/results
- next recommended prompt
