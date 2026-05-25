---
prompt_id: ORCH-03
pack_id: agent-runtime-orchestration-v1
title: Service registry and feature flags
category: feature
risk_level: LOW
approval_gate: false
depends_on: ["ORCH-02"]
status: completed
order: 3
created_at: 2026-05-23T21:24:19+00:00
imported_at: 2026-05-23T21:24:19+00:00
source_pack: prompts/packs/agent-runtime-orchestration-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-23T21:31:11+00:00
completed_at: 2026-05-23T21:31:11+00:00
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
notes: Added lazy service registry and default-disabled risky feature flags.
---

# Prompt

You are Codex working in this repo.

Task:
Build ServiceRegistry and FeatureFlags.

Goal:
Create a central registry for runtime services and feature flags so the agent can list what exists, what is enabled, what is disabled, what is stubbed, and what requires setup without loading or executing everything.

Scope:
- Service registry.
- Feature flags.
- Lazy service metadata.
- Tests.
- No real service execution.

Non-goals:
- Do not load heavy services at startup.
- Do not execute tools.
- Do not call connector providers.
- Do not read personal data.
- Do not enable personal-data features by default.
- Do not add send/write capabilities.

Create:
- agent/runtime/service_registry.py
- agent/runtime/feature_flags.py
- tests/runtime/test_service_registry.py
- tests/runtime/test_feature_flags.py

ServiceRegistry responsibilities:
- register service metadata
- list services
- get service by id
- report service health metadata without executing it
- lazy-load service only if explicitly requested and safe
- return setup hints
- return unavailable/disabled/stubbed/planned states
- avoid import-time heavy dependencies

FeatureFlags responsibilities:
- central feature enabled/disabled/planned/stubbed state
- default safe states
- personal-data features disabled by default
- CRITICAL features disabled by default
- config overrides, if existing config system supports it
- explanation of why feature is disabled or blocked
- optional source of truth integration with feature registry/manifests

Initial service IDs:
- core.orchestrator
- core.router
- core.toolbroker
- safety.policy
- safety.permissions
- safety.approvals
- safety.audit
- connectors.weather
- connectors.web
- connectors.news
- connectors.reddit
- connectors.calendar
- connectors.contacts
- connectors.email
- connectors.messages
- memory
- promptops
- dogfood
- command_registry
- feature_maturity
- app_bridge
- platform_bridge
- scheduler
- self_improvement

Requirements:
1. Registry loads without executing services.
2. Registry never reads personal data.
3. FeatureFlags default personal-data features disabled.
4. FeatureFlags default CRITICAL actions disabled.
5. Registry returns clear setup hints.
6. Unknown service returns structured not found.
7. Unknown feature returns structured not found.
8. Registry integrates with docs/FEATURE_REGISTRY.md or code manifests where practical but does not depend on docs for runtime safety.
9. All metadata can be displayed by runtime status commands later.
10. Tests should not require LM Studio or network.

Tests:
- register/list/get service
- unknown service handled
- disabled service reported
- planned/stubbed service reported
- no service execution during list/status
- personal features disabled by default
- critical features disabled by default
- feature override works only if safe/configured
- setup hints shown
- no heavy imports at registry import

Update:
- docs/runtime/SERVICE_REGISTRY.md
- docs/runtime/RUNTIME_CONTROL_PLANE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/PROJECT_STATE.md
- docs/COMPLETION_REPORT.md
- CHANGELOG.md

Run targeted tests and validations.

Final report:
- services registered
- feature flags added
- tests run/results
- next recommended prompt
