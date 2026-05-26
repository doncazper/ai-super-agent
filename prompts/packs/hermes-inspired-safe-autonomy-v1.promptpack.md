<<<PROMPT_PACK_START>>>
pack_id: hermes-inspired-safe-autonomy-v1
pack_title: Hermes-Inspired Safe Autonomy Groundwork Track
created_by: user
mode: controlled_batch_until_blocked
default_execution: sequential
requires_sdlc: true
requires_prompt_ledger: true
requires_feature_maturity_update: true
priority: high

pack_summary:
  - This prompt pack lays safe groundwork for Hermes-inspired features without copying risky autonomy blindly.
  - It covers gateway/channel process, Telegram/mobile access, repeated-task skill creation, skill improvement from experience, scheduler UX, subagent isolation, sandbox backend abstraction, model switching, long-term memory search, and cross-session continuity.
  - It also documents and gates future high-risk autonomy: automatic skill creation, automatic scheduled actions, unattended workflows, browser automation, background persistence, cross-platform messaging sends, subagents with write permissions, and cloud/server execution with private data.
  - The pack creates safe scaffolding, policies, decision records, stubs, tests, and release gates.
  - It does not enable high-risk autonomy by default.
  - It does not implement CAPTCHA bypass, Cloudflare bypass, proxy evasion, login-wall bypass, or human impersonation.
  - The user's requested future “brute force scrape” idea must be handled as a policy decision record for authorized first-party or explicitly permissioned testing only, not as third-party anti-bot bypass capability.

global_rules:
  - Follow SPEC.md.
  - Follow docs/SDLC.md.
  - Follow AGENTS.md.
  - Build safety first, capabilities second.
  - Do not weaken policy.
  - Do not bypass ToolBroker.
  - Do not bypass PolicyEngine.
  - Do not bypass PermissionManager.
  - Do not bypass ApprovalManager.
  - Do not bypass AuditLogger.
  - Do not enable personal-data tools by default.
  - Do not add silent send/write behavior.
  - Do not implement automatic high-risk actions.
  - Do not add arbitrary browser automation.
  - Do not create background persistence.
  - Do not implement unauthorized CAPTCHA bypass, Cloudflare bypass, proxy evasion, login-wall bypass, paywall bypass, or human impersonation.
  - Allowed only for documented, authorized first-party/contracted test environments: official test keys, staging login-flow tests, user-in-the-loop manual steps, official APIs, OAuth, approved partner access.
  - Do not access private cloud/server data without explicit authorization.
  - Do not run subagents with write permissions by default.
  - Do not expose tools through gateways/channels without ToolBroker and policy gates.
  - Do not run unattended workflows that can perform HIGH/CRITICAL actions.
  - Update CHANGELOG.md.
  - Update docs/PROJECT_STATE.md.
  - Update docs/FEATURE_REGISTRY.md.
  - Update docs/FEATURE_MATURITY.md.
  - Update docs/FEATURE_ROADMAP.md if status/order changes.
  - Update docs/COMMAND_REGISTRY.md if commands are added/changed.
  - Update docs/COMMAND_TEST_MATRIX.md if QA steps are added/changed.
  - Update docs/COMPLETION_REPORT.md.
  - Update docs/RISK_REGISTER.md if risk changed.
  - Update docs/THREAT_MODEL.md if threat surface changed.
  - Update docs/RELEASE_CHECKLIST.md where release-gate checks change.

stop_conditions:
  - approval_gate
  - failing_tests_not_safely_fixable
  - docs_validation_failure_not_safely_fixable
  - personal_data_access_required
  - package_install_required
  - external_network_access_required_unexpectedly
  - background_persistence_required
  - high_or_critical_action_execution_required
  - browser_automation_required_beyond_stub
  - cloud_private_data_access_required
  - subagent_write_permissions_required
  - anti_bot_or_captcha_bypass_requested
  - security_policy_change_required
  - ambiguous_requirements

expected_prompt_ids:
  - HERMES-01
  - HERMES-02
  - HERMES-03
  - HERMES-04
  - HERMES-05
  - HERMES-06
  - HERMES-07
  - HERMES-08
  - HERMES-09
  - HERMES-10
  - HERMES-11
  - HERMES-12
  - HERMES-13

<<<PROMPT_START id="HERMES-01" order="1">>
title: Hermes-inspired safe autonomy architecture
category: docs
risk_level: LOW
approval_gate: false
depends_on: []
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Create Hermes-Inspired Safe Autonomy architecture and roadmap.

Goal:
Plan safe groundwork for selected Hermes-like capabilities: gateway/channel process, Telegram/mobile access, repeated-task skill creation, skill improvement from experience, scheduler UX, subagent isolation, sandbox backend abstraction, model switching, long-term memory search, and cross-session continuity.

Also document future high-risk autonomy ideas and keep them gated: automatic skill creation, automatic scheduled actions, unattended workflows, browser automation, background persistence, cross-platform messaging sends, subagents with write permissions, and cloud/server execution with private data.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- README.md
- CHANGELOG.md
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/FEATURE_ROADMAP.md
- docs/COMMAND_REGISTRY.md, if present
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/RELEASE_CHECKLIST.md
- docs/native_skills/, if present
- docs/runtime/, if present
- docs/brain/, if present

Follow the mini-SDLC.

Scope:
- Documentation and roadmap.
- Safe autonomy policy.
- No high-risk automation implementation.

Non-goals:
- Do not implement unattended high-risk workflows.
- Do not implement arbitrary browser automation.
- Do not create background persistence.
- Do not enable sends/writes.
- Do not enable personal-data tools.
- Do not implement anti-bot/CAPTCHA bypass.
- Do not add cloud/server private-data execution.

Create:
- docs/decisions/hermes_inspired_safe_autonomy.md
- docs/autonomy/SAFE_AUTONOMY_ROADMAP.md
- docs/autonomy/AUTONOMY_RISK_MODEL.md
- docs/autonomy/HIGH_RISK_AUTONOMY_GATES.md
- docs/autonomy/HERMES_FEATURE_COMPARISON.md
- docs/autonomy/UNAUTHORIZED_BYPASS_POLICY.md

Define safe groundwork tracks:
1. Gateway/channel process
2. Telegram/mobile access
3. Skill creation from repeated tasks
4. Skill improvement from experience
5. Scheduler UX
6. Subagent isolation
7. Sandbox backend abstraction
8. Model switching
9. Long-term memory search
10. Cross-session continuity

Define high-risk future gates:
1. automatic skill creation
2. automatic scheduled actions
3. unattended workflows
4. browser automation
5. background persistence
6. cross-platform messaging sends
7. subagents with write permissions
8. cloud/server execution with private data

For each high-risk future gate, define:
- why it is risky
- required prerequisites
- required tests
- approval requirements
- audit requirements
- rollback requirements
- what is forbidden in v1

Create explicit boundary:
Unauthorized CAPTCHA/Cloudflare/anti-bot/proxy/login-wall/paywall bypass and human impersonation are forbidden for third-party sites. Authorized first-party testing, official test keys, user-in-the-loop manual login, official APIs, OAuth, and approved partner access may be documented and tested only when scoped, audited, and disabled by default.

Update:
- docs/FEATURE_ROADMAP.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/PROJECT_STATE.md
- docs/COMPLETION_REPORT.md
- CHANGELOG.md
- docs/COMMAND_REGISTRY.md with planned/stubbed commands if needed

Run validations/tests.

Final report:
- docs created
- roadmap updates
- risk gates added
- tests/validation run
- next recommended prompt
<<<PROMPT_END id="HERMES-01">>

<<<PROMPT_START id="HERMES-02" order="2">>
title: Gateway and channel process
category: connector
risk_level: MEDIUM
approval_gate: false
depends_on: ["HERMES-01"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build safe Gateway/Channel process scaffolding.

Goal:
Create a channel-neutral gateway architecture for Telegram, mobile companion, CLI, local dashboard, email, future Slack/Discord/WhatsApp/Signal, and app bridge frontends. Channels can submit requests and display responses, but cannot bypass ToolBroker, policy, approvals, or audit.

Scope:
- Gateway/channel models.
- Registry.
- Read-only status commands.
- Tests.
- No external channel connections yet.

Non-goals:
- Do not implement real Telegram bot.
- Do not implement Slack/Discord/WhatsApp/Signal.
- Do not expose remote server.
- Do not send messages.
- Do not enable personal-data tools.
- Do not bypass approval.
- Do not create background persistence.

Create:
- agent/channels/
  - __init__.py
  - models.py
  - registry.py
  - gateway.py
  - security.py
  - errors.py
- tests/channels/test_channel_gateway.py
- docs/channels/GATEWAY_CHANNEL_ARCHITECTURE.md
- docs/channels/CHANNEL_SECURITY_MODEL.md

Channel types:
- cli
- interactive_cli
- telegram
- ios_companion
- mac_app
- windows_app
- local_web_dashboard
- email
- manual_handoff
- mock

Channel request fields:
- channel_id
- channel_type
- user_ref
- session_id
- message_text
- attachments
- trust_level
- risk_context
- received_at
- metadata_redacted
- correlation_id

Channel response fields:
- response_id
- session_id
- channel_id
- content
- actions
- approval_required
- audit_ids
- safe_to_display
- redaction_status

Requirements:
1. Channel gateway does not execute tools directly.
2. Channel gateway submits requests to orchestrator/runtime only.
3. Channel gateway cannot approve its own actions.
4. Channel gateway cannot bypass ApprovalManager.
5. Channel gateway cannot expose personal data by default.
6. Channel metadata must be redacted.
7. Unknown channel denied.
8. Remote channels disabled by default.
9. Incoming channel content is untrusted unless from trusted CLI user.
10. Audit correlation required.

Commands if practical:
- python smart_agent.py channels list
- python smart_agent.py channels status
- python smart_agent.py channels show <channel_id>

Tests:
- channel registry loads.
- unknown channel denied.
- mock channel submits safe request.
- channel cannot execute tools.
- channel cannot approve actions.
- remote channels disabled by default.
- secrets redacted.
- command registry updated.

Update docs/tracking.

Final report:
- gateway scaffolding added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="HERMES-02">>

<<<PROMPT_START id="HERMES-03" order="3">>
title: Telegram and mobile access scaffolding
category: connector
risk_level: MEDIUM
approval_gate: false
depends_on: ["HERMES-02"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build Telegram/mobile access scaffolding.

Goal:
Prepare safe mobile access through Telegram and future iOS companion without enabling sends or remote execution by default.

Scope:
- Telegram doctor/config status.
- Mobile channel models.
- Allowlisted chat/user policy.
- Tests.
- No live Telegram send/receive loop.

Non-goals:
- Do not start Telegram bot.
- Do not send Telegram messages.
- Do not poll Telegram by default.
- Do not create webhook server.
- Do not expose public network listener.
- Do not enable personal-data tools.
- Do not accept remote commands that can run tools without policy.

Create:
- agent/channels/telegram.py
- agent/channels/mobile.py
- tests/channels/test_telegram_mobile_scaffolding.py
- docs/channels/TELEGRAM_MOBILE_ACCESS.md
- docs/channels/MOBILE_CHANNEL_SECURITY.md

Config:
- TELEGRAM_ENABLED=false
- TELEGRAM_BOT_TOKEN
- TELEGRAM_ALLOWED_CHAT_IDS
- TELEGRAM_DEFAULT_CHAT_ID
- TELEGRAM_ALLOW_SEND=false
- TELEGRAM_ALLOW_POLLING=false
- TELEGRAM_ALLOW_WEBHOOK=false
- MOBILE_COMPANION_ENABLED=false
- MOBILE_APPROVALS_ENABLED=false

Commands:
- python smart_agent.py telegram doctor
- python smart_agent.py telegram status
- python smart_agent.py mobile status
- python smart_agent.py mobile pairing-status

Requirements:
1. Secrets redacted.
2. Token presence only checked; token not printed.
3. Telegram disabled by default.
4. Send disabled by default.
5. Polling/webhook disabled by default.
6. Allowed chat IDs required before any future send.
7. Remote channel messages are UNTRUSTED_MESSAGE unless explicitly authenticated/paired.
8. Mobile approvals future path must still use ApprovalManager.
9. No personal-data access.
10. No background service.

Tests:
- missing token setup hint.
- token redacted.
- disabled by default.
- send disabled by default.
- polling/webhook disabled by default.
- chat allowlist required.
- mobile disabled by default.
- no network call in tests.
- command registry updated.

Update docs/tracking.

Final report:
- Telegram/mobile scaffolding added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="HERMES-03">>

<<<PROMPT_START id="HERMES-04" order="4">>
title: Repeated-task skill creation proposals
category: native_skills
risk_level: MEDIUM
approval_gate: false
depends_on: ["HERMES-03"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build repeated-task skill creation proposal system.

Goal:
Observe safe, non-personal workflow patterns from session logs, command history, dogfood results, and user-approved examples, then propose candidate native skills. Do not auto-create or enable skills.

Scope:
- Candidate proposal logic.
- Reports.
- CLI.
- Tests.
- No automatic skill generation/enabling.

Non-goals:
- Do not auto-create enabled skills.
- Do not run external skills.
- Do not use personal data without approval.
- Do not inspect private session content by default.
- Do not add write/send skills.
- Do not bypass skill vetting.

Create:
- agent/autonomy/skill_proposals.py
- tests/autonomy/test_skill_proposals.py
- docs/autonomy/SKILL_CREATION_FROM_REPEATED_TASKS.md
- docs/native_skills/SKILL_PROPOSAL_PROCESS.md

Commands:
- python smart_agent.py skills propose-from-sessions
- python smart_agent.py skills propose-from-commands
- python smart_agent.py skills proposals list
- python smart_agent.py skills proposals show <proposal_id>
- python smart_agent.py skills proposals approve <proposal_id> --dry-run

Proposal fields:
- proposal_id
- title
- observed_pattern
- sources
- frequency
- user_value
- risk_level
- required_tools
- required_capabilities
- suggested_manifest
- suggested_tests
- suggested_docs
- privacy_review
- approval_required
- status

Requirements:
1. Uses only redacted session/command metadata by default.
2. Does not read personal content by default.
3. Creates proposals only, not enabled skills.
4. Proposed skills start as candidate/unreviewed.
5. High-risk proposed skills require human review.
6. Personal-data skills require explicit approval.
7. Suggested manifest must include risk/trust/memory/audit fields.
8. Proposal evidence links included.
9. Skill vetting required before import/enable.
10. Audit/log proposal generation.

Tests:
- repeated safe command pattern creates proposal.
- personal-data pattern skipped/redacted by default.
- high-risk proposal marked review-required.
- proposal does not create enabled skill.
- suggested manifest includes required fields.
- command registry updated.

Update docs/tracking.

Final report:
- proposal system added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="HERMES-04">>

<<<PROMPT_START id="HERMES-05" order="5">>
title: Skill improvement from experience
category: native_skills
risk_level: MEDIUM
approval_gate: false
depends_on: ["HERMES-04"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build skill improvement from experience scaffolding.

Goal:
Allow the agent to propose improvements to existing native skills based on failed dogfood runs, user feedback, bug reports, regression tests, and command QA results. Do not auto-edit or auto-enable improved skills.

Scope:
- Improvement proposal workflow.
- Evidence analysis.
- Reports.
- Tests.
- No automatic skill modification.

Non-goals:
- Do not modify skills automatically.
- Do not run untrusted skill scripts.
- Do not auto-update lockfile.
- Do not enable risky skills.
- Do not bypass review.

Create:
- agent/autonomy/skill_improvements.py
- tests/autonomy/test_skill_improvements.py
- docs/autonomy/SKILL_IMPROVEMENT_FROM_EXPERIENCE.md
- docs/native_skills/SKILL_IMPROVEMENT_REVIEW.md

Commands:
- python smart_agent.py skills improve-propose <skill_id>
- python smart_agent.py skills improve-from-bugs <skill_id>
- python smart_agent.py skills improve-from-dogfood <skill_id>
- python smart_agent.py skills improvements list
- python smart_agent.py skills improvements show <improvement_id>

Improvement proposal fields:
- improvement_id
- skill_id
- evidence_sources
- bug_ids
- dogfood_failures
- user_feedback
- proposed_change
- risk_level
- files_expected
- tests_required
- docs_required
- lockfile_impact
- rollback_plan
- human_review_required
- status

Requirements:
1. Uses evidence, not vague model guesses.
2. Does not modify files by default.
3. Proposed changes must include tests.
4. Proposed changes must include rollback.
5. High-risk changes require human review.
6. Skill maturity not increased until tests/docs/release gate.
7. Lockfile impact must be noted.
8. No personal content used by default.
9. Command registry updated.

Tests:
- bug evidence creates improvement proposal.
- dogfood failure creates proposal.
- no evidence returns no proposal or low-confidence.
- proposal includes tests/rollback.
- no file modification occurs.
- high-risk proposal review-required.
- command registry updated.

Update docs/tracking.

Final report:
- improvement proposal system added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="HERMES-05">>

<<<PROMPT_START id="HERMES-06" order="6">>
title: Scheduler UX for safe automations
category: scheduler
risk_level: MEDIUM
approval_gate: false
depends_on: ["HERMES-05"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build Scheduler UX scaffolding for safe automations.

Goal:
Improve the user experience for reviewing, creating, pausing, running, and understanding scheduled workflows without enabling risky automatic actions or background persistence.

Scope:
- Scheduler UX/metadata.
- Dry-run/manual-run commands.
- Docs/tests.
- No OS background persistence.

Non-goals:
- Do not create cron/LaunchAgent/Login Item.
- Do not run schedules automatically.
- Do not run HIGH/CRITICAL actions automatically.
- Do not send messages/emails.
- Do not write calendar/contacts.
- Do not enable personal-data workflows by default.

Create:
- agent/autonomy/scheduler_ux.py
- tests/autonomy/test_scheduler_ux.py
- docs/autonomy/SCHEDULER_UX.md
- docs/autonomy/SCHEDULED_ACTION_GATES.md

Commands:
- python smart_agent.py schedule explain
- python smart_agent.py schedule templates
- python smart_agent.py schedule preview <workflow_id>
- python smart_agent.py schedule dry-run <workflow_id>
- python smart_agent.py schedule risks <workflow_id>
- python smart_agent.py schedule review

Scheduler UX should show:
- workflow name
- risk level
- required tools
- approval requirements
- personal-data use
- write/send behavior
- whether background execution is allowed
- whether Action Center item will be created
- tests/dogfood status
- last run result
- next safe action

Requirements:
1. Dry-run only by default.
2. High/critical workflows create action/approval requirements, not execution.
3. Personal-data workflows disabled by default.
4. Scheduler explains why a workflow is blocked.
5. No OS persistence.
6. No background service.
7. Command registry updated.
8. Feature maturity conservative.

Tests:
- schedule templates list safe templates.
- preview shows risk/approval.
- dry-run executes no tools.
- high-risk workflow blocked/approval-required.
- critical workflow never auto-runs.
- personal workflow disabled.
- command registry updated.

Update docs/tracking.

Final report:
- Scheduler UX added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="HERMES-06">>

<<<PROMPT_START id="HERMES-07" order="7">>
title: Subagent isolation groundwork
category: autonomy
risk_level: MEDIUM
approval_gate: false
depends_on: ["HERMES-06"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build subagent isolation groundwork.

Goal:
Prepare for future subagents such as researcher, coder, tester, security reviewer, docs reviewer, and planner, while ensuring they are isolated, profiled, policy-gated, and cannot bypass ToolBroker or approvals.

Scope:
- Subagent profiles/models.
- Capability allowlists.
- Isolation policy.
- Tests.
- No real subagent execution yet unless mock-only.

Non-goals:
- Do not run subagents with write permissions.
- Do not enable autonomous subagent execution.
- Do not run parallel workflows.
- Do not let subagents call tools directly.
- Do not give subagents personal-data access.
- Do not bypass approvals.

Create:
- agent/autonomy/subagents.py
- tests/autonomy/test_subagent_isolation.py
- docs/autonomy/SUBAGENT_ISOLATION.md
- docs/autonomy/SUBAGENT_PROFILES.md

Subagent profiles:
- researcher
- coder
- tester
- security_reviewer
- docs_reviewer
- planner
- locked_down
- experimental

Subagent fields:
- subagent_id
- profile
- purpose
- allowed_tools
- blocked_tools
- risk_ceiling
- can_write_files
- can_access_network
- can_access_personal_data
- can_create_actions
- can_request_approval
- can_execute_critical
- memory_scope
- audit_scope
- status

Default rules:
1. No subagent has personal-data access by default.
2. No subagent can execute CRITICAL actions.
3. No subagent can bypass ToolBroker.
4. Write permissions disabled by default.
5. Network disabled unless profile allows and policy allows.
6. Subagent outputs are MODEL_OUTPUT, not trusted instructions.
7. Subagents can propose actions, not approve them.
8. Subagents are auditable.
9. Subagent execution is stubbed/mock-only in this prompt.

Commands:
- python smart_agent.py subagents list
- python smart_agent.py subagents show <profile>
- python smart_agent.py subagents policy
- python smart_agent.py subagents dry-run <profile> "task"

Tests:
- default subagents no personal data.
- critical execution denied.
- write permissions disabled.
- locked_down has no tools.
- researcher network allowed only if configured.
- coder cannot bypass ToolBroker.
- dry-run mock works.
- command registry updated.

Update docs/tracking.

Final report:
- subagent groundwork added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="HERMES-07">>

<<<PROMPT_START id="HERMES-08" order="8">>
title: Sandbox backend abstraction
category: safety
risk_level: MEDIUM
approval_gate: false
depends_on: ["HERMES-07"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build sandbox backend abstraction.

Goal:
Prepare a pluggable sandbox abstraction for future code execution, browser automation, subagents, and self-improvement, while keeping all risky sandbox execution disabled or mock-only by default.

Scope:
- Sandbox backend interface.
- Mock/local workspace-safe backend.
- Policy docs.
- Tests.
- No Docker/VM installation.
- No browser automation.

Non-goals:
- Do not install Docker or sandbox tools.
- Do not execute arbitrary code.
- Do not run browser automation.
- Do not enable networked sandbox.
- Do not grant broad filesystem access.
- Do not run untrusted scripts.

Create:
- agent/sandbox/
  - __init__.py
  - base.py
  - models.py
  - registry.py
  - mock_backend.py
  - policy.py
  - errors.py
- tests/sandbox/test_sandbox_abstraction.py
- docs/autonomy/SANDBOX_BACKEND_ABSTRACTION.md
- docs/autonomy/SANDBOX_POLICY.md

Sandbox backend types:
- mock
- local_workspace_safe
- docker_rootless, planned
- macos_sandbox, planned
- firecracker_vm, planned
- browser_sandbox, planned
- cloud_sandbox, deferred

Sandbox request fields:
- sandbox_id
- task_type
- risk_level
- network_allowed
- filesystem_roots
- time_limit_seconds
- memory_limit_mb
- command_allowlist
- personal_data_allowed
- audit_required

Requirements:
1. Mock backend only by default.
2. No arbitrary command execution.
3. No network by default.
4. Workspace roots only.
5. Personal data not allowed by default.
6. Sandbox cannot bypass ToolBroker/PolicyEngine.
7. All sandbox operations auditable.
8. Docker/VM/browser/cloud backends planned/stubbed only.
9. Clear setup hints.
10. Command registry updated.

Commands:
- python smart_agent.py sandbox backends
- python smart_agent.py sandbox policy
- python smart_agent.py sandbox dry-run

Tests:
- mock backend works.
- unknown backend denied.
- network disabled by default.
- personal data disabled.
- arbitrary command rejected.
- planned backend returns setup/stub.
- command registry updated.

Update docs/tracking.

Final report:
- sandbox abstraction added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="HERMES-08">>

<<<PROMPT_START id="HERMES-09" order="9">>
title: Model switching and session continuity
category: core
risk_level: MEDIUM
approval_gate: false
depends_on: ["HERMES-08"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build model switching and session continuity groundwork.

Goal:
Support safe switching between brain providers/models during or between sessions while preserving context rules, tool compatibility, audit trail, and rollback.

Scope:
- Model switch metadata.
- Session continuity rules.
- Provider compatibility checks.
- Tests.
- No new model provider implementation.

Non-goals:
- Do not add new provider backends here.
- Do not change default provider without explicit config.
- Do not call paid providers by default.
- Do not store personal data in session continuity.
- Do not bypass tool compatibility checks.

Create:
- agent/autonomy/model_switching.py
- agent/autonomy/session_continuity.py
- tests/autonomy/test_model_switching_continuity.py
- docs/autonomy/MODEL_SWITCHING.md
- docs/autonomy/CROSS_SESSION_CONTINUITY.md

Model switch record:
- switch_id
- from_provider
- from_model
- to_provider
- to_model
- reason
- session_id
- tool_call_support_required
- compatibility_check
- context_migration_summary
- risk_level
- approved_by_user
- audit_ids
- rollback_plan

Session continuity rules:
1. Session continuity is opt-in/configured.
2. Personal data not carried across sessions by default.
3. Tool-call compatibility checked before switch.
4. No-tools mode unaffected.
5. Context summaries must be redacted.
6. Model switch logged/audited.
7. User-visible notice when model changes.
8. Failed switch rolls back to previous provider.
9. Cloud/paid provider switch blocked unless allowed.
10. Session continuity does not bypass memory policy.

Commands:
- python smart_agent.py brain switch <provider> --dry-run
- python smart_agent.py brain switch <provider>
- python smart_agent.py session continuity status
- python smart_agent.py session continuity export --redacted
- python smart_agent.py session continuity clear

Tests:
- dry-run switch checks compatibility.
- switch blocked when provider unavailable.
- tool-call incompatibility blocks tool-required route.
- cloud/paid provider blocked by policy.
- context summary redacted.
- personal data not carried by default.
- rollback plan present.
- command registry updated.

Update docs/tracking.

Final report:
- model switching groundwork added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="HERMES-09">>

<<<PROMPT_START id="HERMES-10" order="10">>
title: Long-term memory search and cross-session continuity
category: memory
risk_level: MEDIUM
approval_gate: false
depends_on: ["HERMES-09"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build long-term memory search and cross-session continuity enhancements.

Goal:
Make cross-session continuity useful without leaking secrets, personal data, or unapproved memories into future prompts.

Scope:
- Memory search improvements.
- Continuity profile.
- Session summaries.
- Tests.
- No personal-data storage by default.

Non-goals:
- Do not store email/message/calendar/contact content by default.
- Do not store secrets.
- Do not inject PII without approval.
- Do not bypass memory policy.
- Do not use cloud embeddings by default.

Create or update:
- agent/memory/continuity.py
- agent/memory/search.py, if present
- tests/memory/test_cross_session_continuity.py
- docs/memory/LONG_TERM_MEMORY_SEARCH.md
- docs/memory/CROSS_SESSION_CONTINUITY.md
- docs/memory/MEMORY_INJECTION_POLICY.md

Continuity features:
- project facts
- user preferences
- workflow lessons
- safe recurring context
- last session summary
- active project state
- open tasks/bugs/prompts summary
- redacted memory snippets

Commands:
- python smart_agent.py memory search "query"
- python smart_agent.py memory continuity status
- python smart_agent.py memory continuity build-summary
- python smart_agent.py memory continuity clear
- python smart_agent.py memory context-preview "query"

Requirements:
1. Secrets never stored.
2. Personal data requires approval.
3. Context injection logs what was injected.
4. User can preview context before injection.
5. Token limits enforced.
6. Memory search respects categories/scope.
7. Continuity summaries redacted.
8. No cloud embeddings by default.
9. Memory deletion respected.
10. Command registry updated.

Tests:
- safe project fact retrieved.
- secret rejected/redacted.
- personal memory requires approval.
- context preview excludes PII by default.
- token limit enforced.
- deletion removes item from search.
- continuity summary redacted.
- command registry updated.

Update docs/tracking.

Final report:
- memory continuity improved
- tests run/results
- next recommended prompt
<<<PROMPT_END id="HERMES-10">>

<<<PROMPT_START id="HERMES-11" order="11">>
title: Authorized web automation boundary
category: web
risk_level: MEDIUM
approval_gate: false
depends_on: ["HERMES-10"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Create Authorized Web Automation Boundary.

Goal:
Document and scaffold a safe policy boundary for future browser automation and user-requested deep web scanning. The user eventually wants to ask the agent to gather as much information as possible from a webpage. This prompt must explicitly prohibit unauthorized CAPTCHA/Cloudflare/anti-bot/paywall/login-wall bypass and define allowed first-party/authorized testing paths.

Scope:
- Decision record.
- Policy docs.
- Risk gates.
- Test fixtures for blocked/unavailable behavior.
- No browser automation implementation.
- No bypass implementation.

Non-goals:
- Do not implement CAPTCHA bypass.
- Do not implement Cloudflare bypass.
- Do not implement anti-bot evasion.
- Do not implement proxy rotation/evasion.
- Do not impersonate humans.
- Do not bypass login walls or paywalls.
- Do not add browser automation.
- Do not scrape third-party sites beyond existing compliant fetch/search policy.

Create:
- docs/decisions/authorized_web_automation_boundary.md
- docs/web/AUTHORIZED_WEB_AUTOMATION_POLICY.md
- docs/web/BLOCKED_SOURCE_AND_BYPASS_POLICY.md
- docs/web/FIRST_PARTY_TESTING_POLICY.md
- docs/web/DEEP_SCAN_POLICY.md
- tests/web/test_authorized_web_automation_policy.py, if web tests exist

Policy:
Forbidden for third-party or unauthorized sites:
- CAPTCHA bypass
- Cloudflare/anti-bot bypass
- proxy evasion
- rate-limit evasion
- login-wall bypass
- paywall bypass
- cookie/session scraping
- human impersonation
- stealth browser automation

Allowed only when explicitly documented and scoped:
- first-party staging app testing
- official CAPTCHA/Turnstile/reCAPTCHA test keys
- user-in-the-loop manual login
- official APIs/OAuth
- approved partner access
- contracted security testing with written scope
- user-provided exports
- browser selected-page handoff where user controls session

Deep scan v1 definition:
- gather all publicly accessible linked resources from a user-provided URL within policy
- respect robots/crawl policy
- rate limit
- no login/CAPTCHA/paywall bypass
- no binary downloads by default
- produce source map and unavailable/blocked report
- content is UNTRUSTED_WEB
- audit all network domains

Future deep scan gates:
- explicit user approval
- domain allowlist
- crawl budget
- rate limit
- robots policy
- legal/compliance note
- data retention policy
- no paid API unless allowed
- no bypass/evasion
- dogfood/eval suite

Requirements:
1. Blocked sources return blocked/unavailable, not bypass attempts.
2. Tests/fixtures verify blocked-source behavior.
3. Router/doctor/docs should use this language.
4. Command registry updated only for planned/stubbed future commands:
   - python smart_agent.py web deep-scan <url> --dry-run
   - python smart_agent.py web source-map <url>
   - python smart_agent.py web blocked-report <url>
5. Feature maturity should mark deep scan as planned/stubbed, not implemented.

Update:
- docs/RISK_REGISTER.md.
- docs/THREAT_MODEL.md.
- docs/FEATURE_ROADMAP.md.
- docs/FEATURE_REGISTRY.md.
- docs/FEATURE_MATURITY.md.
- docs/COMMAND_REGISTRY.md.
- docs/PROJECT_STATE.md.
- docs/COMPLETION_REPORT.md.
- CHANGELOG.md.

Run tests/validations.

Final report:
- policy boundary created
- blocked behavior documented
- tests run/results
- next recommended prompt
<<<PROMPT_END id="HERMES-11">>

<<<PROMPT_START id="HERMES-12" order="12">>
title: Safe autonomy dogfood and eval suite
category: tests
risk_level: MEDIUM
approval_gate: false
depends_on: ["HERMES-11"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build Safe Autonomy dogfood and eval suite.

Goal:
Validate the Hermes-inspired groundwork: channels, Telegram/mobile scaffolding, skill proposals, skill improvement proposals, scheduler UX, subagent isolation, sandbox abstraction, model switching, memory continuity, and authorized web automation boundaries.

Create/update:
- dogfood_suites/safe_autonomy_core.yaml
- dogfood_suites/channels_gateway.yaml
- dogfood_suites/telegram_mobile_scaffolding.yaml
- dogfood_suites/skill_proposals.yaml
- dogfood_suites/subagent_isolation.yaml
- dogfood_suites/sandbox_abstraction.yaml
- dogfood_suites/memory_continuity.yaml
- dogfood_suites/authorized_web_boundary.yaml
- eval_cases/safe_autonomy/
- docs/autonomy/SAFE_AUTONOMY_DOGFOOD_RUNBOOK.md

Dogfood/eval checks:
- channel gateway cannot execute tools directly
- Telegram send disabled by default
- mobile companion disabled by default
- skill proposals do not enable skills
- skill improvements do not edit files automatically
- scheduler dry-run executes no tools
- subagents have no personal-data/default write access
- sandbox mock only by default
- model switch dry-run does not call paid/cloud providers
- continuity context excludes personal data by default
- blocked web/CAPTCHA/paywall bypass requests are refused/reported as unavailable
- all new commands present in command registry

Commands:
- python smart_agent.py dogfood run safe_autonomy_core --session
- python smart_agent.py eval run --safe-autonomy
- python smart_agent.py eval report --safe-autonomy

Tests:
- dogfood suite YAML validates.
- eval fixtures run with mocks.
- no personal data required.
- no network required unless mocked.
- no external scripts.
- no high/critical actions executed.
- command registry updated.

Update:
- docs/autonomy/SAFE_AUTONOMY_DOGFOOD_RUNBOOK.md.
- docs/TEST_PLAN.md.
- docs/COMMAND_REGISTRY.md.
- docs/FEATURE_MATURITY.md.
- docs/PROJECT_STATE.md.
- docs/COMPLETION_REPORT.md.
- CHANGELOG.md.

Run tests/validations.

Final report:
- dogfood/eval suites added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="HERMES-12">>

<<<PROMPT_START id="HERMES-13" order="13">>
title: Hermes-inspired safe autonomy release gate
category: release_gate
risk_level: LOW
approval_gate: false
depends_on: ["HERMES-12"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Run Hermes-Inspired Safe Autonomy release gate and maturity review.

Goal:
Validate that the safe groundwork for Hermes-like capabilities is documented, tested, policy-gated, disabled-by-default where risky, and ready for future implementation without introducing dangerous autonomy.

Scope:
- Validation.
- Maturity review.
- Small fixes only if needed.
- No new feature implementation.

Non-goals:
- Do not implement high-risk autonomy.
- Do not enable background persistence.
- Do not enable unattended workflows with high/critical actions.
- Do not enable cross-platform messaging sends.
- Do not enable subagents with write permissions.
- Do not implement browser automation.
- Do not implement CAPTCHA/anti-bot bypass.
- Do not connect to cloud/server private data.

Run:
1. full test suite
2. startup policy validation
3. capability manifest validation
4. docs validation
5. command registry validation
6. safe autonomy dogfood suite
7. safe autonomy eval suite
8. skill proposal tests
9. subagent isolation tests
10. sandbox abstraction tests
11. scheduler UX tests
12. memory continuity tests
13. authorized web automation boundary tests

Verify:
- gateway/channel scaffolding exists and cannot bypass ToolBroker
- Telegram/mobile access disabled by default
- skill creation from repeated tasks proposes only
- skill improvement from experience proposes only
- scheduler UX dry-run only by default
- subagents isolated and no writes/personal data by default
- sandbox backend abstraction mock-only by default
- model switching dry-run safe
- long-term memory search respects privacy policy
- cross-session continuity redacted
- unauthorized bypass/evasion forbidden
- high-risk autonomy gates documented
- command registry updated
- feature maturity conservative

Create/update:
- docs/autonomy/HERMES_INSPIRED_RELEASE_GATE.md
- docs/autonomy/HERMES_INSPIRED_MATURITY_REVIEW.md

Maturity assessment:
- Gateway/channel process
- Telegram/mobile access scaffolding
- Skill creation from repeated tasks
- Skill improvement from experience
- Scheduler UX
- Subagent isolation
- Sandbox backend abstraction
- Model switching
- Long-term memory search
- Cross-session continuity
- Authorized web automation boundary
- Safe autonomy dogfood/evals
- High-risk autonomy gates

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
- README.md if needed
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
- dogfood/eval results
- maturity score
- remaining blockers
- whether safe autonomy groundwork is ready
- high-risk features still forbidden/deferred
- next recommended feature track
<<<PROMPT_END id="HERMES-13">>

<<<PROMPT_PACK_END>>>
