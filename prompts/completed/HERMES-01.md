---
prompt_id: HERMES-01
pack_id: hermes-inspired-safe-autonomy-v1
title: Hermes-inspired safe autonomy architecture
category: docs
risk_level: LOW
approval_gate: false
depends_on: []
status: completed
order: 1
created_at: 2026-05-25T17:28:14+00:00
imported_at: 2026-05-25T17:28:14+00:00
source_pack: prompts/packs/hermes-inspired-safe-autonomy-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T17:28:28+00:00
completed_at: 2026-05-25T17:32:26+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: focused Hermes docs tests 2 passed; focused tracking/docs tests 15 passed; command registry validation ok with 443 commands; startup policy and capability manifest validation passed via make policy-check
docs_updated: Created Hermes autonomy decision/roadmap/risk/gates/comparison/bypass docs and updated changelog, project state, feature registry, feature maturity, roadmap, risk register, threat model, release checklist, completion report
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
notes: Documentation/policy only; no runtime autonomy, channel connection, background persistence, personal-data access, send/write behavior, browser automation, subagent write permissions, cloud private-data execution, or bypass behavior added.
---

# Prompt

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
