<<<PROMPT_PACK_START>>>
pack_id: agent-runtime-orchestration-v1
pack_title: Agent Runtime Orchestration Track
created_by: user
mode: controlled_batch_until_blocked
default_execution: sequential
requires_sdlc: true
requires_prompt_ledger: true
requires_feature_maturity_update: true
priority: high

pack_summary:
  - This prompt pack creates the runtime orchestration layer for the AI Super Agent.
  - The project remains one shared Python codebase, but the runtime needs a control plane to coordinate CLI, future Mac app, iOS companion, future Windows bridge, tools, connectors, workflows, jobs, schedules, prompt queues, dogfood sessions, docs maintenance, feature maturity, and health/status.
  - The orchestrator coordinates. It does not bypass the safety/control plane.
  - All real tool execution still goes through ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger.
  - This track is intentionally scaffolding-first and lazy-load-first.
  - It must not increase startup overhead meaningfully.
  - It must not enable personal-data tools.
  - It must not add new send/write capabilities.
  - It must not implement Mac/iOS/Windows bridge functionality yet.
  - It must preserve CLI-only Python agent mode.

global_rules:
  - Follow SPEC.md.
  - Follow docs/SDLC.md.
  - Follow AGENTS.md.
  - Build safety first, capabilities second.
  - Keep Python agent core as the shared portable brain.
  - Native apps and platform bridges are optional frontends/bridges, not the brain.
  - Do not weaken policy.
  - Do not bypass ToolBroker.
  - Do not bypass PolicyEngine.
  - Do not bypass PermissionManager.
  - Do not bypass ApprovalManager.
  - Do not bypass AuditLogger.
  - Do not enable personal-data tools by default.
  - Do not add new email/text/message/calendar/contact send or write capabilities.
  - Do not add background persistence.
  - Do not launch background services by default.
  - Do not import heavy/native platform libraries at startup.
  - Do not call LM Studio in status/doctor commands unless explicitly requested.
  - Do not access personal data in runtime status/doctor/health commands.
  - Do not treat model output or untrusted content as runtime control instructions.
  - Update CHANGELOG.md.
  - Update docs/PROJECT_STATE.md.
  - Update docs/FEATURE_REGISTRY.md.
  - Update docs/FEATURE_MATURITY.md.
  - Update docs/FEATURE_ROADMAP.md if status/order changes.
  - Update docs/COMMAND_REGISTRY.md if commands are added/changed.
  - Update docs/COMMAND_TEST_MATRIX.md if manual QA steps are added/changed.
  - Update docs/COMPLETION_REPORT.md.
  - Update docs/RISK_REGISTER.md if risk changed.
  - Update docs/THREAT_MODEL.md if threat surface changed.
  - Run tests and validations requested in each prompt.
  - Stop at approval gates.

stop_conditions:
  - failing_tests_not_safely_fixable
  - docs_validation_failure_not_safely_fixable
  - approval_gate
  - ambiguous_requirements
  - runtime_behavior_change_required_beyond_scope
  - personal_data_access_required
  - package_install_required
  - security_policy_change_required
  - startup_overhead_regression_not_understood
  - scheduler_or_background_persistence_requested

expected_prompt_ids:
  - ORCH-01
  - ORCH-02
  - ORCH-03
  - ORCH-04
  - ORCH-05
  - ORCH-06
  - ORCH-07
  - ORCH-08
  - ORCH-09
  - ORCH-10

<<<PROMPT_START id="ORCH-01" order="1">>
title: Runtime orchestration architecture and roadmap
category: docs
risk_level: LOW
approval_gate: false
depends_on: []
status: queued

PROMPT:
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
<<<PROMPT_END id="ORCH-01">>

<<<PROMPT_START id="ORCH-02" order="2">>
title: Runtime package scaffolding and models
category: feature
risk_level: LOW
approval_gate: false
depends_on: ["ORCH-01"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Create runtime package scaffolding and core models.

Goal:
Add lightweight, platform-neutral runtime scaffolding that can represent services, features, workflows, jobs, runtime state, and health without executing tools or loading heavy modules.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- docs/runtime/RUNTIME_ORCHESTRATION_STRATEGY.md
- docs/runtime/RUNTIME_LIFECYCLE.md
- docs/runtime/STARTUP_OVERHEAD_POLICY.md
- docs/PROJECT_STATE.md
- docs/FEATURE_MATURITY.md
- docs/COMMAND_REGISTRY.md, if present
- docs/COMPLETION_REPORT.md

Scope:
- Add lightweight runtime package and dataclasses/models.
- No real orchestration side effects.
- No tool execution.
- No background services.
- No personal-data access.

Non-goals:
- Do not run workflows.
- Do not call LM Studio.
- Do not start a scheduler.
- Do not start app bridge server.
- Do not import platform/native libraries.
- Do not add send/write behavior.

Create:
- agent/runtime/__init__.py
- agent/runtime/models.py
- agent/runtime/errors.py
- agent/runtime/state.py
- tests/runtime/test_runtime_models.py
- tests/runtime/test_runtime_state.py

Models:
- RuntimeMode
- RuntimeStatus
- RuntimeHealthStatus
- RuntimeServiceStatus
- RuntimeFeatureStatus
- RuntimeWorkflowStatus
- RuntimeJobStatus
- RuntimeEventType
- RuntimeServiceInfo
- RuntimeFeatureInfo
- RuntimeWorkflowInfo
- RuntimeJobInfo
- RuntimeHealthReport
- RuntimeStateSnapshot
- RuntimeErrorBase
- RuntimeUnsupportedError
- RuntimeUnavailableError
- RuntimePolicyBlockedError

RuntimeMode values:
- cli
- interactive_cli
- mac_app_bridge
- ios_companion_bridge
- windows_app_bridge
- web_dashboard
- test
- unknown

Requirements:
1. Models must be JSON-serializable.
2. Models must not import heavy modules.
3. Runtime state must not include raw secrets.
4. Runtime state must not include raw personal data.
5. Missing fields should fail validation clearly or have safe defaults.
6. Status values should distinguish available, unavailable, disabled, planned, stubbed, blocked, and error.
7. Health reports should support warnings and failures.
8. No runtime code should execute tools.
9. No model should require LM Studio.
10. Tests should run without network/personal data.

Tests:
- models serialize to dict/JSON
- required fields validated
- secrets redaction helper used or raw secret fields rejected
- unknown status handled
- state snapshot includes no personal data
- import runtime package does not import core heavy modules unnecessarily
- test runtime mode works

Update:
- docs/runtime/RUNTIME_LIFECYCLE.md
- docs/runtime/RUNTIME_CONTROL_PLANE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/PROJECT_STATE.md
- docs/COMPLETION_REPORT.md
- CHANGELOG.md

Run:
- targeted runtime tests
- full tests if practical
- startup policy validation

Final report:
- files created
- tests run/results
- models added
- overhead notes
- next recommended prompt
<<<PROMPT_END id="ORCH-02">>

<<<PROMPT_START id="ORCH-03" order="3">>
title: Service registry and feature flags
category: feature
risk_level: LOW
approval_gate: false
depends_on: ["ORCH-02"]
status: queued

PROMPT:
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
<<<PROMPT_END id="ORCH-03">>

<<<PROMPT_START id="ORCH-04" order="4">>
title: Runtime lifecycle and kernel
category: feature
risk_level: LOW
approval_gate: false
depends_on: ["ORCH-03"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build AgentRuntimeKernel and LifecycleManager.

Goal:
Create a lightweight runtime kernel that coordinates initialization, status, health, service registry access, feature flags, and shutdown without executing tools or loading heavy services by default.

Scope:
- Runtime kernel.
- Lifecycle manager.
- Status/health aggregation.
- Tests.
- No risky execution.

Non-goals:
- Do not replace the existing orchestrator chat loop.
- Do not execute tools.
- Do not call LM Studio.
- Do not start background workers.
- Do not start scheduler.
- Do not start app bridge server.
- Do not access personal data.
- Do not enable new features.

Create:
- agent/runtime/kernel.py
- agent/runtime/lifecycle.py
- tests/runtime/test_runtime_kernel.py
- tests/runtime/test_runtime_lifecycle.py

AgentRuntimeKernel methods:
- boot()
- shutdown()
- status()
- health()
- list_services()
- list_features()
- list_workflows()
- list_jobs()
- get_state_snapshot()

LifecycleManager responsibilities:
- track boot state
- track shutdown state
- record boot warnings/errors
- expose safe lifecycle events
- prevent duplicate boot
- safe no-op shutdown when not booted
- no background persistence

Requirements:
1. Boot must be lightweight.
2. Boot must not execute tools.
3. Boot must not call LM Studio.
4. Boot must not access personal data.
5. Boot must not load platform/native bridge modules.
6. Boot must not start scheduler or event loop workers.
7. status() must be safe and read-only.
8. health() must aggregate registry/feature/audit/config state if safe.
9. shutdown() must not delete data or kill unrelated processes.
10. Runtime must work in test mode.

Tests:
- kernel boots once
- duplicate boot handled
- shutdown before boot safe
- status returns snapshot
- health returns report
- no LM Studio call during boot/status/health
- no tool execution during boot/status/health
- no personal-data access
- registry integrated
- feature flags integrated
- import/startup overhead reasonable

Update:
- docs/runtime/RUNTIME_LIFECYCLE.md
- docs/runtime/STARTUP_OVERHEAD_POLICY.md
- docs/FEATURE_MATURITY.md
- docs/PROJECT_STATE.md
- docs/COMPLETION_REPORT.md
- CHANGELOG.md

Run targeted tests and validations.

Final report:
- kernel added
- lifecycle added
- tests run/results
- overhead observations
- next recommended prompt
<<<PROMPT_END id="ORCH-04">>

<<<PROMPT_START id="ORCH-05" order="5">>
title: Event bus and runtime state
category: feature
risk_level: MEDIUM
approval_gate: false
depends_on: ["ORCH-04"]
status: queued

PROMPT:
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
<<<PROMPT_END id="ORCH-05">>

<<<PROMPT_START id="ORCH-06" order="6">>
title: Workflow runner and job queue
category: feature
risk_level: MEDIUM
approval_gate: false
depends_on: ["ORCH-05"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build safe WorkflowRunner and JobQueue scaffolding.

Goal:
Create a controlled way to represent and coordinate workflows/jobs without letting them bypass ToolBroker, PolicyEngine, ApprovalManager, or AuditLogger.

Scope:
- Workflow runner scaffolding.
- Job queue scaffolding.
- Safe metadata/state only.
- Tests.
- No risky workflow implementation.

Non-goals:
- Do not execute existing high-risk workflows automatically.
- Do not run tools directly.
- Do not start background workers.
- Do not run CRITICAL actions.
- Do not enable personal-data workflows by default.
- Do not schedule jobs persistently.
- Do not send messages/emails.
- Do not write calendar/contacts.

Create:
- agent/runtime/workflow_runner.py
- agent/runtime/job_queue.py
- tests/runtime/test_workflow_runner.py
- tests/runtime/test_job_queue.py

WorkflowRunner responsibilities:
- register workflow metadata
- list workflows
- validate workflow request
- create workflow run record
- update run status
- enforce that workflow steps request tools through ToolBroker
- refuse unknown workflow
- refuse disabled workflow
- stop at approval gates
- produce action items instead of executing high/critical actions

JobQueue responsibilities:
- create job metadata
- list jobs
- show job
- update job status
- retry safe jobs only
- mark blocked/failed/completed
- store error summary
- no background execution by default
- no CRITICAL job execution
- optional persistence only if safe and existing local state supports it

Workflow statuses:
- registered
- disabled
- planned
- running
- completed
- failed
- blocked
- approval_required

Job statuses:
- queued
- running
- completed
- failed
- blocked
- cancelled
- approval_required

Requirements:
1. WorkflowRunner does not call tools directly.
2. WorkflowRunner must be able to reference ToolBroker without bypassing it.
3. JobQueue must not run jobs automatically by default.
4. HIGH/CRITICAL workflows return approval_required/action_center style status.
5. Unknown workflows refused.
6. Disabled workflows refused.
7. Personal workflows disabled by default.
8. Workflow/job state contains no raw secrets.
9. Workflow/job state contains no raw personal data by default.
10. Audit correlation fields included.

Commands can remain planned/stubbed in COMMAND_REGISTRY for now:
- python smart_agent.py workflows list
- python smart_agent.py workflows run <workflow_id>
- python smart_agent.py jobs list
- python smart_agent.py jobs show <job_id>

Tests:
- workflow registry/list works
- unknown workflow refused
- disabled workflow refused
- high-risk workflow returns approval_required
- workflow step cannot bypass ToolBroker, or this is enforced by architecture/documented test
- job create/list/show works
- safe retry metadata works
- job queue does not auto-run by default
- CRITICAL job blocked
- personal workflow disabled by default
- secrets redacted

Update:
- docs/runtime/WORKFLOW_RUNNER.md
- docs/runtime/JOB_QUEUE.md
- docs/COMMAND_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/PROJECT_STATE.md
- docs/COMPLETION_REPORT.md
- CHANGELOG.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md

Run targeted tests and validations.

Final report:
- workflow runner added
- job queue added
- tests run/results
- command registry updates
- next recommended prompt
<<<PROMPT_END id="ORCH-06">>

<<<PROMPT_START id="ORCH-07" order="7">>
title: Scheduler policy and safe automation hooks
category: safety
risk_level: MEDIUM
approval_gate: false
depends_on: ["ORCH-06"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build SchedulerPolicy and safe automation hooks.

Goal:
Prepare for future scheduled workflows without adding hidden background persistence or allowing risky unattended actions.

Scope:
- Scheduler policy.
- Scheduled job metadata.
- Safe/manual-run scaffolding.
- Tests.
- No actual OS-level background service.

Non-goals:
- Do not create cron jobs.
- Do not create LaunchAgents.
- Do not create login items.
- Do not start background daemon.
- Do not auto-run personal workflows.
- Do not execute CRITICAL actions.
- Do not send messages/emails.
- Do not write calendar/contacts.
- Do not install persistence.

Create:
- agent/runtime/scheduler.py
- tests/runtime/test_scheduler_policy.py
- docs/runtime/SCHEDULER_POLICY.md

SchedulerPolicy must define:
- allowed scheduled workflow categories
- forbidden scheduled workflow categories
- approval behavior
- personal-data behavior
- CRITICAL action behavior
- manual-run-only mode
- future background-run requirements
- audit requirements
- user-visible setup requirements

Allowed v1 scheduled workflows:
- connector doctor
- safe eval suite
- command registry validation
- docs weekly review dry-run
- memory cleanup if no personal data is exposed
- audit summary metadata
- backup metadata/dry-run
- dogfood dry-run/mock suites

Forbidden v1 scheduled workflows:
- email send
- message send
- calendar write
- contact write
- personal-data full scans
- browser automation
- package install
- code execution with network
- policy changes
- audit deletion
- persistence creation

Requirements:
1. Scheduler is disabled by default.
2. Scheduler has no OS-level persistence.
3. Scheduler cannot execute CRITICAL actions.
4. Scheduler cannot execute HIGH actions without approval.
5. Scheduler can create Action Center items but not execute them.
6. Scheduler commands are stubbed/planned unless safe.
7. Scheduled job metadata does not contain secrets/raw personal data.
8. Scheduled run events are auditable.
9. Manual-run mode can be modeled without actual background execution.

Commands can be planned/stubbed in COMMAND_REGISTRY:
- python smart_agent.py schedule list
- python smart_agent.py schedule create
- python smart_agent.py schedule run <schedule_id>
- python smart_agent.py schedule pause <schedule_id>
- python smart_agent.py schedule delete <schedule_id>

Tests:
- scheduler disabled by default
- safe workflow category allowed
- CRITICAL workflow blocked
- HIGH workflow requires approval
- personal-data workflow blocked/approval-required
- no OS persistence created
- no background worker started
- scheduled job metadata redacts secrets
- command registry updated

Update:
- docs/runtime/SCHEDULER_POLICY.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/COMMAND_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/PROJECT_STATE.md
- docs/COMPLETION_REPORT.md
- CHANGELOG.md

Run targeted tests and validations.

Final report:
- scheduler policy added
- tests run/results
- forbidden/allowed categories
- next recommended prompt
<<<PROMPT_END id="ORCH-07">>

<<<PROMPT_START id="ORCH-08" order="8">>
title: Runtime doctor/status/commands
category: feature
risk_level: LOW
approval_gate: false
depends_on: ["ORCH-07"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Add safe runtime doctor/status CLI commands.

Goal:
Expose the runtime orchestrator state to the user without executing tools, calling LM Studio, accessing personal data, or loading heavy services.

Scope:
- Read-only commands.
- Command registry updates.
- Tests.

Non-goals:
- Do not execute tools.
- Do not call LM Studio unless explicitly using the existing doctor command and not in these runtime status commands.
- Do not access personal data.
- Do not initialize platform bridges.
- Do not start scheduler.
- Do not start app bridge.
- Do not start background workers.

Add commands if practical:
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

Command behavior:
runtime status:
- runtime mode
- boot status
- service count
- feature count
- enabled/disabled/planned counts
- job count
- workflow count
- warnings

runtime doctor:
- runtime kernel loads
- service registry loads
- feature flags load
- audit logger reachable
- policy manifest valid
- command registry status if available
- prompt queue status if available
- no heavy imports
- no personal-data tools enabled by default

runtime services:
- service id
- status
- enabled
- lazy-load state
- setup hint

runtime features:
- feature/capability
- status
- risk
- approval behavior
- enabled/default

runtime health:
- consolidated health report

jobs list/show:
- read-only job metadata
- no job execution

workflows list:
- list workflow metadata

workflows run:
- for now either refuse execution unless explicitly safe, or create a run record that stops at ToolBroker/approval gates.
- if unsure, keep as planned/stubbed and document.

events tail:
- if event bus exists, show redacted recent events.
- otherwise return setup/unavailable.

Requirements:
1. Commands are read-only unless workflows run explicitly handles safe mode.
2. Commands do not access personal data.
3. Commands do not execute tools.
4. Commands do not call LM Studio.
5. Commands do not start scheduler/app bridge/background services.
6. Commands redact secrets.
7. Commands handle missing runtime subsystems gracefully.
8. Commands update COMMAND_REGISTRY.
9. Commands include examples in docs.

Tests:
- runtime status works
- runtime doctor works
- services list works
- features list works
- health works
- jobs list/show safe
- workflows list safe
- workflows run refuses unknown/high-risk workflow
- no LM Studio call
- no tool execution
- no personal data
- command registry validation passes

Update:
- README.md
- docs/COMMAND_REGISTRY.md
- docs/COMMAND_TEST_MATRIX.md if present
- docs/runtime/RUNTIME_ORCHESTRATION_STRATEGY.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/PROJECT_STATE.md
- docs/COMPLETION_REPORT.md
- CHANGELOG.md

Run:
- targeted tests
- full tests if practical
- startup policy validation
- command registry validation

Final report:
- commands added
- tests run/results
- example command output
- next recommended prompt
<<<PROMPT_END id="ORCH-08">>

<<<PROMPT_START id="ORCH-09" order="9">>
title: App/frontend bridge integration points
category: platform
risk_level: MEDIUM
approval_gate: false
depends_on: ["ORCH-08"]
status: queued

PROMPT:
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
<<<PROMPT_END id="ORCH-09">>

<<<PROMPT_START id="ORCH-10" order="10">>
title: Runtime orchestration release gate
category: release_gate
risk_level: LOW
approval_gate: false
depends_on: ["ORCH-09"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Run Agent Runtime Orchestration release gate.

Goal:
Validate that the runtime orchestration layer is safe, modular, lazy-loaded, documented, and ready to coordinate future features/frontends without breaking the existing Python CLI agent.

Scope:
- Validation.
- Documentation review.
- Maturity review.
- Small fixes only if needed.
- No new major runtime functionality.

Non-goals:
- Do not add platform bridge implementations.
- Do not enable personal-data tools.
- Do not implement scheduler persistence.
- Do not run high/critical workflows.
- Do not start app bridge server.
- Do not add send/write capabilities.

Run:
1. full test suite
2. startup policy validation
3. capability manifest validation
4. docs validation
5. command registry validation if present
6. runtime status
7. runtime doctor
8. runtime services
9. runtime features
10. runtime health
11. runtime lazy-load/startup overhead checks if present
12. prompt tracker validation if present

Verify:
- runtime docs exist
- agent/runtime package exists if scaffolding was added
- runtime status commands are read-only
- no tools execute during runtime status/doctor
- no LM Studio call during runtime status/doctor
- no personal-data access during runtime status/doctor
- no platform/native heavy imports at startup
- no background scheduler starts by default
- no app bridge server starts by default
- personal-data features disabled by default
- CRITICAL actions disabled by default
- event bus cannot approve actions or change policy
- workflow runner cannot bypass ToolBroker
- job queue does not auto-run jobs
- scheduler policy blocks CRITICAL actions
- frontend bridge contract cannot bypass ApprovalManager
- command registry updated
- feature maturity conservative

Create/update:
- docs/runtime/RUNTIME_ORCHESTRATION_RELEASE_GATE.md
- docs/runtime/RUNTIME_ORCHESTRATION_MATURITY_REVIEW.md

Maturity assessment:
- Runtime orchestration architecture
- Runtime models
- ServiceRegistry
- FeatureFlags
- RuntimeKernel
- LifecycleManager
- EventBus
- RuntimeState
- WorkflowRunner
- JobQueue
- SchedulerPolicy
- Runtime commands
- Frontend bridge contract
- Startup overhead policy

Classify each:
- Idea
- Specified
- Scaffolded
- Implemented
- Tested
- Hardened
- Live-Validated
- User-Ready
- Mature Pattern

Update:
- CHANGELOG.md
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/FEATURE_ROADMAP.md
- docs/COMMAND_REGISTRY.md
- docs/COMMAND_TEST_MATRIX.md if present
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/RELEASE_CHECKLIST.md

Final report:
- tests run/results
- validation results
- runtime status output summary
- startup overhead findings
- maturity score
- remaining blockers
- whether the runtime orchestrator is ready to govern the shared codebase
- next recommended feature track
<<<PROMPT_END id="ORCH-10">>

<<<PROMPT_PACK_END>>>
