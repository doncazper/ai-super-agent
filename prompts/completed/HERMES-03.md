---
prompt_id: HERMES-03
pack_id: hermes-inspired-safe-autonomy-v1
title: Telegram and mobile access scaffolding
category: connector
risk_level: MEDIUM
approval_gate: false
depends_on: ["HERMES-02"]
status: completed
order: 3
created_at: 2026-05-25T17:28:14+00:00
imported_at: 2026-05-25T17:28:14+00:00
source_pack: prompts/packs/hermes-inspired-safe-autonomy-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T17:39:30+00:00
completed_at: 2026-05-25T17:45:21+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: focused Telegram/mobile tests 8 passed; combined channel/Telegram/mobile/secret-doctor/docs tests 45 passed; command registry validation ok with 448 commands; telegram status and mobile status CLI smokes passed; startup policy and capability manifest validation passed via make policy-check
docs_updated: Created Telegram/mobile access and mobile channel security docs; updated README, env example, changelog, project state, feature registry, feature maturity, roadmap, command registry, command test matrix, risk register, threat model, release checklist, completion report
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
notes: Scaffold/status only; no Telegram bot, polling, webhook, public listener, Telegram API call, message read/send, mobile pairing, mobile approval executor, personal-data access, background persistence, or safety-control bypass added.
---

# Prompt

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
