---
prompt_id: ORCH-05
pack_id: agent-runtime-orchestration-v1
title: Event bus and runtime state
category: feature
risk_level: MEDIUM
approval_gate: false
depends_on: ["ORCH-04"]
status: completed
order: 5
created_at: 2026-05-23T21:24:19+00:00
imported_at: 2026-05-23T21:24:19+00:00
source_pack: prompts/packs/agent-runtime-orchestration-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-23T21:31:12+00:00
completed_at: 2026-05-23T21:31:12+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: ./.venv/bin/python -m pytest tests/runtime -q: 31 passed; events tail smoke passed
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
notes: Added redacted in-process event bus and untrusted-control denial.
---

# Prompt

You are Codex working in this repo.

Task:
Build safe EventBus and RuntimeState.

Goal:
Create a lightweight event system and runtime state tracker for internal coordination without allowing untrusted content, model output, or events to bypass safety controls.

Scope:
- Internal event bus.
- Runtime state store.
- Redaction.
- Tests.
- No external messaging.
- No background workers by default.

Non-goals:
- Do not create a network event bus.
- Do not create background persistence.
- Do not execute tools from events.
- Do not let model output publish control events.
- Do not carry raw secrets or raw personal data.
- Do not allow events to modify policy or approvals.
- Do not call LM Studio.

Create:
- agent/runtime/event_bus.py
- agent/runtime/state_store.py
- tests/runtime/test_event_bus.py
- tests/runtime/test_runtime_state_store.py

EventBus requirements:
1. In-process only.
2. Disabled or minimal by default.
3. Supports publish/subscribe for safe internal events.
4. Redacts secrets in event payloads.
5. Blocks or rejects control events from untrusted sources.
6. No event may directly execute tools.
7. No event may change policy, grant permissions, or approve actions.
8. Event handlers must be explicit and registered.
9. Events should include correlation_id.
10. Events should include trust/risk metadata when relevant.

Event types:
- runtime.booted
- runtime.shutdown
- service.registered
- service.health_changed
- feature.enabled
- feature.disabled
- job.created
- job.completed
- job.failed
- workflow.started
- workflow.completed
- workflow.failed
- approval.requested
- audit.event_written
- prompt.status_changed
- dogfood.session_started
- dogfood.session_finished

RuntimeStateStore requirements:
1. Store lightweight runtime state only.
2. Do not store raw personal data.
3. Do not store secrets.
4. Provide snapshot.
5. Provide update methods with validation.
6. Persist only if existing config explicitly supports safe local state; otherwise in-memory is fine.
7. State writes should be safe and testable.

Tests:
- event publish/subscribe works
- untrusted control event rejected
- secret redaction works
- event does not execute tools
- event cannot approve action
- event cannot change policy
- state snapshot safe
- state rejects personal/secrets payloads
- correlation IDs present
- no background worker starts

Update:
- docs/runtime/EVENT_BUS.md
- docs/runtime/RUNTIME_CONTROL_PLANE.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/FEATURE_MATURITY.md
- docs/PROJECT_STATE.md
- docs/COMPLETION_REPORT.md
- CHANGELOG.md

Run targeted tests and validations.

Final report:
- event bus added
- runtime state added
- tests run/results
- safety notes
- next recommended prompt
