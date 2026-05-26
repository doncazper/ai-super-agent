---
prompt_id: HERMES-02
pack_id: hermes-inspired-safe-autonomy-v1
title: Gateway and channel process
category: connector
risk_level: MEDIUM
approval_gate: false
depends_on: ["HERMES-01"]
status: completed
order: 2
created_at: 2026-05-25T17:28:14+00:00
imported_at: 2026-05-25T17:28:14+00:00
source_pack: prompts/packs/hermes-inspired-safe-autonomy-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T17:32:32+00:00
completed_at: 2026-05-25T17:39:26+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: focused channel tests 10 passed; combined channel/feature-maturity/Hermes docs tests 25 passed; command registry validation ok with 446 commands; channels status and show telegram CLI smokes passed; startup policy and capability manifest validation passed via make policy-check
docs_updated: Created channel gateway architecture/security docs and updated README, changelog, project state, feature registry, feature maturity, roadmap, command registry, command test matrix, risk register, threat model, release checklist, completion report
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
notes: Scaffold/status only; no external channel connection, Telegram/mobile bot, listener, background persistence, personal-data access, send/write behavior, browser automation, self-approval, direct tool execution, or safety-control bypass added.
---

# Prompt

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
