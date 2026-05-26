<<<PROMPT_PACK_START>>>
pack_id: canonical-runtime-gateway-hardening-v1
pack_title: Canonical Runtime State, Agent Gateway / Runtime Kernel, and External Review Hardening
created_by: user
mode: controlled_batch_until_blocked
default_execution: sequential
requires_sdlc: true
requires_prompt_ledger: true
requires_feature_maturity_update: true
priority: high

pack_summary:
  - Borrow GoatCitadel-inspired strengths without rewriting this repo.
  - Shift long-term architecture toward Agent Gateway / Runtime Kernel while preserving current Python/local-first CLI workflow.
  - Gateway/Kernel will become the owner of canonical state, durable execution records, approval state, recovery checkpoints, and future frontend/channel contracts.
  - CLI remains the first frontend; future Mac/iOS/Windows/web/Telegram/MCP surfaces must use the Gateway/Kernel boundary.
  - Includes canonical runtime state, gateway-owned execution truth, durable records, recovery checkpoints, artifact hash checks, safety lints, surface regression lanes, backup roundtrip validation, audit receipts, native skill diagnostics, source/provider explainability, approval parity checks, and maturity overclaim cleanup.
  - No web server, TypeScript rewrite, background daemon, personal-data access, live providers, sends/writes, package installs, model downloads, or GUI.

global_rules:
  - Follow SPEC.md, docs/SDLC.md, and AGENTS.md.
  - Preserve ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger.
  - Do not enable personal-data tools by default.
  - Do not enable sends/writes.
  - Do not install packages, call paid APIs, run live providers, download models, start background services, create a web server, commit, or push.
  - Do not mark planned/stubbed/metadata-only capabilities as product-ready.
  - Prefer additive docs, models, tests, diagnostics, and small anchored tracker fixes.
  - Update CHANGELOG.md, docs/PROJECT_STATE.md, docs/FEATURE_REGISTRY.md, docs/FEATURE_MATURITY.md, docs/FEATURE_ROADMAP.md, docs/COMMAND_REGISTRY.md, docs/COMMAND_TEST_MATRIX.md if present, docs/COMPLETION_REPORT.md, docs/RISK_REGISTER.md, docs/THREAT_MODEL.md, docs/RELEASE_CHECKLIST.md, and prompt tracking docs if present.

stop_conditions:
  - approval_gate
  - failing_tests_not_safely_fixable
  - docs_validation_failure_not_safely_fixable
  - package_install_required
  - personal_data_access_required
  - live_provider_required
  - paid_api_required
  - model_download_required
  - background_persistence_required
  - web_server_required
  - broad_refactor_required
  - runtime_rewrite_required
  - security_policy_change_required
  - ambiguous_requirements
  - commit_or_push_required

expected_prompt_ids:
  - CANON-01
  - CANON-02
  - CANON-03
  - CANON-04
  - CANON-05
  - CANON-06
  - CANON-07
  - CANON-08
  - CANON-09
  - EXTREV-01
  - CANON-10

<<<PROMPT_START id="CANON-01" order="1">>
title: Canonical runtime state model and source-of-truth hierarchy
category: runtime
risk_level: LOW
approval_gate: false
depends_on: []
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Create Canonical Runtime State model and source-of-truth hierarchy.

Goal:
Define a single canonical machine-readable runtime state model that future CLI/dashboard/app/channel surfaces can read, while keeping markdown trackers as human-readable summaries. This borrows runtime-truth concepts without rewriting the repo.

Before making changes, read SPEC.md, docs/SDLC.md, AGENTS.md, README.md, CHANGELOG.md, docs/PROJECT_STATE.md, docs/FEATURE_REGISTRY.md, docs/FEATURE_MATURITY.md, docs/FEATURE_ROADMAP.md, docs/COMMAND_REGISTRY.md if present, docs/COMMAND_TEST_MATRIX.md if present, docs/COMPLETION_REPORT.md, docs/RISK_REGISTER.md, docs/THREAT_MODEL.md, docs/RELEASE_CHECKLIST.md, docs/PROMPT_LEDGER.md if present, docs/PROMPT_QUEUE.md if present, docs/PROMPT_AUDIT.md if present, docs/runtime/ if present, agent/runtime/ if present, tests/runtime/ if present.

Scope:
- Canonical runtime state docs.
- Data models/schema.
- Source-of-truth hierarchy.
- Read-only metadata commands if practical.
- Tests.
- No runtime rewrite.

Non-goals:
- Do not replace markdown trackers yet.
- Do not delete tracker history.
- Do not create a daemon.
- Do not start background persistence.
- Do not alter ToolBroker/Policy/Audit behavior.

Create or update:
- docs/runtime/CANONICAL_RUNTIME_STATE_MODEL.md
- docs/runtime/SOURCE_OF_TRUTH_HIERARCHY.md
- docs/runtime/CANONICAL_STATE_BOUNDARIES.md
- docs/decisions/canonical_runtime_state.md
- agent/runtime/canonical_state.py
- tests/runtime/test_canonical_runtime_state.py

Define canonical state fields:
- schema_version, generated_at, branch, last_commit, dirty_worktree_summary
- active_prompt_id, active_prompt_pack, active_job_id, active_workflow_id, active_session_id, active_action_id
- current_phase, current_status, next_prompt_id, last_completed_prompt_id, blocked_reason, resume_instruction
- last_test_result, last_policy_check, last_capability_check, last_command_registry_check, last_prompt_audit
- safety_summary, tracker_summary, evidence_links, updated_by

Define source-of-truth hierarchy:
1. SPEC.md
2. docs/SDLC.md
3. AGENTS.md
4. config/capabilities.yaml
5. actual code/tests
6. canonical runtime state JSON/model
7. COMMAND_REGISTRY
8. FEATURE_REGISTRY / FEATURE_MATURITY
9. PROMPT_LEDGER / PROMPT_QUEUE / PROMPT_AUDIT
10. PROJECT_STATE / COMPLETION_REPORT / CHANGELOG
11. summary dashboards

Commands if practical:
- python smart_agent.py runtime canonical-state
- python smart_agent.py runtime source-of-truth
- python smart_agent.py runtime reconcile-preview

Requirements:
- JSON-serializable.
- No secrets/personal data.
- No tool execution/provider calls.
- Existing trackers remain intact.
- Tests cover serialization and conflict markers.
Update docs/tracking and run targeted tests and validations.
<<<PROMPT_END id="CANON-01">>

<<<PROMPT_START id="CANON-02" order="2">>
title: Durable job, workflow, and prompt execution records
category: runtime
risk_level: MEDIUM
approval_gate: false
depends_on: ["CANON-01"]
status: queued

PROMPT:
Create durable job, workflow, command, prompt, QA, self-heal, and approval-gated resume record contracts owned by the future Agent Gateway / Runtime Kernel.

Create/update:
- docs/runtime/DURABLE_EXECUTION_RECORDS.md
- docs/runtime/JOB_WORKFLOW_PROMPT_RECORDS.md
- agent/runtime/execution_records.py
- tests/runtime/test_execution_records.py

Define record types:
- PromptRunRecord, PromptPackRunRecord, JobRunRecord, WorkflowRunRecord, CommandRunRecord, ApprovalGatedResumeRecord, QARunRecord, SelfHealRunRecord, MediaGenerationRunRecord future/stubbed, SecretScanRunRecord future/stubbed.

Record fields:
- record_id, record_type, status, created_at, updated_at, started_at, completed_at, branch, commit_hash
- prompt_id, prompt_pack_id, command, args_redacted, risk_level, approval_required, approval_id
- toolbroker_required, audit_ids, input_hash, output_hash, artifact_hashes, checkpoint_ids
- resume_command, rollback_plan, blocked_reason, evidence_paths, test_results, docs_updated, next_record_id

Statuses:
- queued, active, waiting_for_approval, running, completed, failed, blocked, cancelled, superseded, needs_review

Commands if practical:
- python smart_agent.py runtime records list
- python smart_agent.py runtime records show <record_id>
- python smart_agent.py runtime records latest
- python smart_agent.py runtime records validate

Requirements:
- Never store raw secrets or personal data by default.
- Link to prompt tracker rows and audit ids.
- Do not run queued prompts.
- Existing prompt tracker remains compatible.
Add tests, docs, and tracking updates.
<<<PROMPT_END id="CANON-02">>

<<<PROMPT_START id="CANON-03" order="3">>
title: Agent Gateway / Runtime Kernel boundary
category: runtime
risk_level: MEDIUM
approval_gate: false
depends_on: ["CANON-02"]
status: queued

PROMPT:
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
<<<PROMPT_END id="CANON-03">>

<<<PROMPT_START id="CANON-04" order="4">>
title: Resume, recovery, and checkpoint model
category: runtime
risk_level: MEDIUM
approval_gate: false
depends_on: ["CANON-03"]
status: queued

PROMPT:
Create durable checkpoint and recovery model for interrupted prompt packs, QA runs, workflows, self-improvement/code operations, and future frontend/channel actions.

Create/update:
- docs/runtime/RESUME_RECOVERY_CHECKPOINT_MODEL.md
- docs/runtime/RECOVERY_REPORTS.md
- agent/runtime/checkpoints.py
- agent/runtime/recovery.py
- tests/runtime/test_resume_recovery_checkpoints.py

Checkpoint fields:
- checkpoint_id, record_id, created_at, kind, state_hash, input_hash, output_hash, artifact_hashes
- current_step, completed_steps, remaining_steps, approval_state, audit_ids
- resume_command, rollback_plan, safe_to_resume, human_review_required, notes

Recovery report fields:
- report_id, generated_at, interrupted_record, last_checkpoint, files_changed, commands_run, tests_run, docs_updated, blockers, safe_next_action, unsafe_actions_to_avoid

Commands if practical:
- python smart_agent.py runtime recovery-preview
- python smart_agent.py runtime checkpoints list
- python smart_agent.py runtime checkpoints show <checkpoint_id>

Rules:
- Recovery preview does not resume automatically.
- Active approval gates remain active.
- CRITICAL action resume requires fresh explicit approval.
- Prompt-pack resume uses prompt tracker evidence.
- Redacted only; no secrets/personal data.
Add tests for an interrupted prompt-pack scenario.
<<<PROMPT_END id="CANON-04">>

<<<PROMPT_START id="CANON-05" order="5">>
title: Code Mode / self-heal artifact hash checks and safety lints
category: self_improvement
risk_level: MEDIUM
approval_gate: false
depends_on: ["CANON-04"]
status: queued

PROMPT:
Build Code Mode / self-heal artifact hash checks and safety lint strategy.

Create/update:
- docs/self_improvement/CODE_ARTIFACT_HASHES.md
- docs/self_improvement/SELF_HEAL_SAFETY_LINTS.md
- docs/self_improvement/CODE_MODE_TRUTH_BOUNDARY.md
- agent/self_improvement/artifact_hashes.py or agent/workflows/self_improvement_hashes.py
- agent/self_improvement/safety_lints.py or agent/workflows/self_improvement_lints.py
- tests/test_self_improvement_artifact_hashes.py
- tests/test_self_improvement_safety_lints.py

Artifact hash coverage:
- git diff hash
- touched file hashes
- test command output hash
- generated report hash
- approval preview hash
- command registry snapshot hash
- capability manifest hash

Safety lint checks:
- disables audit logging
- weakens PolicyEngine
- bypasses ToolBroker
- changes CRITICAL approval reuse
- enables personal-data capabilities by default
- adds background persistence
- expands filesystem access outside workspace
- removes redaction
- installs packages without approval
- adds live provider default
- starts server/listener by default
- stores secrets
- weakens backup restore policy

Commands if practical:
- python smart_agent.py improve lint-diff
- python smart_agent.py improve artifact-hashes
- python smart_agent.py improve verify-artifacts

Requirements:
- Does not patch files.
- Does not commit/push.
- Hashes deterministic.
- Secrets redacted.
- High-risk findings block self-heal safe-only plan.
- Tests use fixture diffs.
<<<PROMPT_END id="CANON-05">>

<<<PROMPT_START id="CANON-06" order="6">>
title: Surface regression lanes
category: qa
risk_level: MEDIUM
approval_gate: false
depends_on: ["CANON-05"]
status: queued

PROMPT:
Build Surface Regression Lanes so every frontend/control surface has a safe regression lane.

Create/update:
- docs/qa/SURFACE_REGRESSION_LANES.md
- docs/qa/SURFACE_REGRESSION_MATRIX.md
- agent/qa/surface_lanes.py
- tests/qa/test_surface_regression_lanes.py
- dogfood_suites/surface_cli_core.yaml
- dogfood_suites/surface_runtime_gateway.yaml
- dogfood_suites/surface_promptops.yaml
- dogfood_suites/surface_action_center.yaml
- dogfood_suites/surface_app_bridge_contract.yaml
- dogfood_suites/surface_channels_status.yaml

Surface lanes:
- CLI core
- Command registry
- PromptOps
- Runtime/canonical state
- Agent Gateway / Runtime Kernel
- Action Center/approvals
- ToolBroker/policy/audit
- Web/research
- Reddit/forums
- Weather
- News planned/stubbed
- Brain providers
- Native skills
- Secrets
- QA sandbox
- Media planned/stubbed
- Platform/app bridge
- Channels/Telegram/mobile
- Memory
- Backup/restore

Commands if practical:
- python smart_agent.py qa surfaces
- python smart_agent.py qa surfaces run --dry-run
- python smart_agent.py qa surfaces matrix

Requirements:
- Default dry-run/fixture-safe.
- Personal-data and HIGH/CRITICAL excluded by default.
- Live provider checks opt-in.
- Each lane has owner docs and expected commands/tests.
- Results can feed QA dashboard later.
<<<PROMPT_END id="CANON-06">>

<<<PROMPT_START id="CANON-07" order="7">>
title: Backup roundtrip and restore hardening lane
category: backup
risk_level: MEDIUM
approval_gate: false
depends_on: ["CANON-06"]
status: queued

PROMPT:
Create backup roundtrip validation and restore policy-weakening hardening.

Create/update:
- docs/backup/BACKUP_ROUNDTRIP_VALIDATION.md
- docs/backup/RESTORE_POLICY_WEAKENING_GUARDS.md
- tests/test_backup_roundtrip_policy.py or update existing backup tests

Check/add tests for:
- backup verifies file hashes
- backup exports redacted archives where required
- restore verifies hashes before writing
- restore creates pre-restore copy where practical
- restore refuses capability manifest that enables personal-data tools by default
- restore refuses CRITICAL approval reuse
- restore refuses policy/audit weakening
- restore refuses unredacted secret material
- restore refuses path traversal
- restore is approval-gated
- disposable project copy recommended for live smoke

Commands if practical:
- python smart_agent.py backup roundtrip --dry-run
- python smart_agent.py backup policy-check
- python smart_agent.py backup restore-check <backup_id>

Do not run real restore outside disposable workspace.
<<<PROMPT_END id="CANON-07">>

<<<PROMPT_START id="CANON-08" order="8">>
title: Canonical state dashboard and docs
category: runtime
risk_level: LOW
approval_gate: false
depends_on: ["CANON-07"]
status: queued

PROMPT:
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
<<<PROMPT_END id="CANON-08">>

<<<PROMPT_START id="CANON-09" order="9">>
title: Tracker-to-canonical-state migration plan
category: prompt_tracking
risk_level: LOW
approval_gate: false
depends_on: ["CANON-08"]
status: queued

PROMPT:
Create migration plan from dense markdown trackers toward canonical runtime state as machine-readable truth.

Create/update:
- docs/runtime/TRACKER_TO_CANONICAL_STATE_MIGRATION.md
- docs/runtime/CANONICAL_STATE_TRACKER_SYNC_POLICY.md
- docs/prompt_tracker/CANONICAL_STATE_INTEGRATION.md
- tests/runtime/test_tracker_canonical_state_sync.py

Plan:
- canonical state is machine-readable truth for active work
- prompt ledger remains historical evidence
- prompt queue remains planned-order view
- prompt audit remains reconciliation view
- project state becomes human-readable resume summary
- completion report remains release evidence
- tracker dashboard remains summary only
- handoff file becomes external communication summary

Commands if practical:
- python smart_agent.py runtime tracker-sync-preview
- python smart_agent.py runtime tracker-conflicts

Do not auto-overwrite trackers broadly.
Use conflict reports and small anchored edits only.
<<<PROMPT_END id="CANON-09">>

<<<PROMPT_START id="EXTREV-01" order="10">>
title: External architecture review hardening parity checks
category: review
risk_level: MEDIUM
approval_gate: false
depends_on: ["CANON-09"]
status: queued

PROMPT:
Convert external architecture review findings into targeted hardening follow-ups.

Context:
A third-party source/documentation architecture review identified:
1. Tamper-evident audit receipts.
2. Native skill vetting diagnostics.
3. Source/provider explainability.
4. High-risk action approval semantics.
5. Backup restore policy-weakening checks.
6. Self-improvement safety lints.
It warned not to overclaim planned/scaffolded capabilities as product-ready.

Create:
- docs/reviews/EXTERNAL_ARCHITECTURE_REVIEW_FINDINGS.md
- docs/reviews/EXTERNAL_REVIEW_HARDENING_PLAN.md
- docs/reviews/EXTERNAL_REVIEW_PARITY_CHECKLIST.md

Check/report:
A. Audit receipts:
- audit hash-chain verification
- audit receipt export
- action/tool execution tied to audit receipt
- if missing, add planned command rows or small safe diagnostics only

B. Native skill diagnostics:
- manifest validation
- trust/provenance/lockfile/conflict/test harness status
- correct tracker overclaims if clear

C. Source/provider explainability:
- router explain path
- selected/skipped provider reporting
- no-store/no-memory flags visible

D. High-risk approval semantics:
- exact preview matching
- edit invalidates approval
- consume-once approval
- CRITICAL no approval reuse
- execution re-enters ToolBroker

E. Backup restore policy weakening:
- restore rejects policy/capability weakening
- pre-restore copy/hash verification

F. Self-improvement safety lints:
- protected safety files and policy-weakening diff checks

G. Overclaim cleanup:
- scan FEATURE_MATURITY and FEATURE_REGISTRY for planned/stubbed/metadata-only capabilities marked too mature
- correct only clear overclaims

Run targeted tests and validations. Do not rebuild major systems.
<<<PROMPT_END id="EXTREV-01">>

<<<PROMPT_START id="CANON-10" order="11">>
title: Canonical runtime and gateway hardening release gate
category: release_gate
risk_level: LOW
approval_gate: false
depends_on: ["EXTREV-01"]
status: queued

PROMPT:
Run the Canonical Runtime State, Agent Gateway / Runtime Kernel, and External Review Hardening release gate.

Run:
- full test suite if practical
- startup policy validation
- capability manifest validation
- command registry validation
- prompt tracker validation if available
- runtime canonical state tests
- execution record tests
- gateway/kernel boundary tests
- checkpoint/recovery tests
- self-improvement artifact/lint tests
- surface lane tests
- backup roundtrip/policy tests
- external review parity tests

Verify:
- canonical state model exists and is JSON-serializable
- Gateway/Kernel boundary is documented and no server starts
- CLI remains first frontend
- frontends/channels cannot bypass ToolBroker/Policy/Approval/Audit
- durable execution records exist
- checkpoints/recovery previews do not auto-resume
- CRITICAL resume requires fresh approval
- artifact hash and safety lint checks exist or are planned with tests/docs
- surface regression lanes exist
- backup policy weakening checks exist
- audit receipt gaps are documented/planned
- native skill diagnostics status accurate
- source/provider explainability status accurate
- approval semantics regression status accurate
- overclaimed maturity corrected
- no personal-data tools enabled
- no sends/writes enabled
- no package installs
- no live provider calls
- no background services

Create:
- docs/runtime/CANONICAL_RUNTIME_RELEASE_GATE.md
- docs/runtime/CANONICAL_RUNTIME_MATURITY_REVIEW.md
- docs/reviews/EXTERNAL_REVIEW_HARDENING_RELEASE_GATE.md

Final report:
1. CANON-01 through CANON-10/EXTREV-01 status table.
2. Files created/changed.
3. Commands added/changed.
4. Tests/validations run.
5. Canonical state summary.
6. Agent Gateway / Runtime Kernel summary.
7. Durable execution record summary.
8. Checkpoint/recovery summary.
9. Artifact hash / safety lint summary.
10. Surface regression lane summary.
11. Backup roundtrip/policy summary.
12. External review parity summary.
13. Maturity corrections.
14. Remaining blockers.
15. Whether this hardening track is safe to rely on.
16. Recommended next prompt or pack.
<<<PROMPT_END id="CANON-10">>

<<<PROMPT_PACK_END>>>
