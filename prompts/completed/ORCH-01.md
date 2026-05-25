---
prompt_id: ORCH-01
pack_id: agent-runtime-orchestration-v1
title: Runtime orchestration architecture and roadmap
category: docs
risk_level: LOW
approval_gate: false
depends_on: []
status: completed
order: 1
created_at: 2026-05-23T21:24:19+00:00
imported_at: 2026-05-23T21:24:19+00:00
source_pack: prompts/packs/agent-runtime-orchestration-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-23T21:25:41+00:00
completed_at: 2026-05-23T21:31:10+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: Docs and command registry updates completed; runtime architecture docs created.
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
notes: Created runtime orchestration decision, lifecycle, service registry, workflow runner, job queue, event bus, scheduler policy, startup overhead, control plane, frontend contract, release gate, and maturity docs.
---

# Prompt

You are Codex working in this repo.

Task:
Create the Agent Runtime Orchestration architecture and roadmap.

Goal:
The project is one shared Python codebase that will support many surfaces and capabilities: CLI, Mac app, iOS companion, future Windows bridge, connectors, tools, workflows, prompt queues, dogfood sessions, docs maintenance, schedules, jobs, and self-improvement. Create a runtime orchestration strategy so all of this stays modular, lazy-loaded, observable, and safety-gated.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- CHANGELOG.md
- README.md
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/FEATURE_ROADMAP.md
- docs/COMMAND_REGISTRY.md, if present
- docs/COMMAND_TEST_MATRIX.md, if present
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/RELEASE_CHECKLIST.md
- docs/PROMPT_LEDGER.md, if present
- docs/PROMPT_QUEUE.md, if present

Follow the mini-SDLC:
1. Confirm scope.
2. Confirm non-goals.
3. Define requirements.
4. Define risks and threat-model notes.
5. Implement docs/scaffolding only.
6. Add tests/validation if practical.
7. Run tests.
8. Update docs.
9. Update completion report.
10. Stop at approval gates.

Scope:
- Documentation and architecture decision records.
- No risky runtime behavior.
- No platform bridge implementation.
- No scheduler/background persistence implementation.
- No send/write implementation.

Non-goals:
- Do not implement Mac app frontend.
- Do not implement iOS companion.
- Do not implement Windows bridge.
- Do not implement Microsoft Graph.
- Do not implement EventKit/Contacts/Messages/Mail bridge.
- Do not add personal-data access.
- Do not add send/write actions.
- Do not add background persistence.
- Do not weaken ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger.
- Do not make everything load at startup.

Create:
- docs/decisions/agent_runtime_orchestration.md
- docs/runtime/RUNTIME_ORCHESTRATION_STRATEGY.md
- docs/runtime/RUNTIME_LIFECYCLE.md
- docs/runtime/SERVICE_REGISTRY.md
- docs/runtime/WORKFLOW_RUNNER.md
- docs/runtime/JOB_QUEUE.md
- docs/runtime/EVENT_BUS.md
- docs/runtime/SCHEDULER_POLICY.md
- docs/runtime/STARTUP_OVERHEAD_POLICY.md
- docs/runtime/RUNTIME_CONTROL_PLANE.md

Architecture principles:
1. Python agent core remains the shared brain.
2. Mac/iOS/Windows/web frontends are optional bridges.
3. CLI-only mode must always work.
4. Runtime orchestrator coordinates but never bypasses ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger.
5. Services are registered, lazy-loaded, health-checkable, and disableable.
6. Connectors are disabled unless configured.
7. Personal-data features are disabled by default.
8. HIGH/CRITICAL actions never run automatically.
9. Background jobs are opt-in and audited.
10. Scheduler cannot execute CRITICAL actions directly.
11. Event bus must not carry raw secrets or unredacted personal data.
12. Runtime status checks must not access personal data.
13. Startup overhead must remain low.
14. Missing services return structured unavailable/setup-required status.
15. Untrusted content may be data carried by jobs/events, but cannot become control messages.

Define runtime components:
- AgentRuntimeKernel
- LifecycleManager
- ServiceRegistry
- FeatureFlags
- WorkflowRunner
- JobQueue
- EventBus
- SchedulerPolicy
- RuntimeHealth
- RuntimeState
- Frontend/AppBridge integration points

Add roadmap track:
"Agent Runtime Orchestration Track"

Add planned prompts:
1. Runtime orchestration architecture and roadmap
2. Runtime package scaffolding and models
3. Service registry and feature flags
4. Runtime lifecycle and kernel
5. Event bus and runtime state
6. Workflow runner and job queue
7. Scheduler policy and safe automation hooks
8. Runtime doctor/status/commands
9. App/front-end bridge integration points
10. Orchestration release gate

Add planned commands to docs/COMMAND_REGISTRY.md as planned/stubbed:
- python smart_agent.py runtime status
- python smart_agent.py runtime doctor
- python smart_agent.py runtime services
- python smart_agent.py runtime features
- python smart_agent.py runtime health
- python smart_agent.py jobs list
- python smart_agent.py jobs show <job_id>
- python smart_agent.py workflows list
- python smart_agent.py workflows run <workflow_id>
- python smart_agent.py events tail

Update:
- README.md
- CHANGELOG.md
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/FEATURE_ROADMAP.md
- docs/COMMAND_REGISTRY.md
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/RELEASE_CHECKLIST.md

Run:
- full test suite if practical
- docs validation if present
- startup policy validation
- capability manifest validation
- command registry validation if present

Final report:
- scope confirmed
- non-goals confirmed
- docs created
- roadmap updates
- risk updates
- tests/validation run
- next recommended prompt
