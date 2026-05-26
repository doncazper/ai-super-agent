---
prompt_id: HERMES-10
pack_id: hermes-inspired-safe-autonomy-v1
title: Long-term memory search and cross-session continuity
category: memory
risk_level: MEDIUM
approval_gate: false
depends_on: ["HERMES-09"]
status: completed
order: 10
created_at: 2026-05-25T17:28:14+00:00
imported_at: 2026-05-25T17:28:14+00:00
source_pack: prompts/packs/hermes-inspired-safe-autonomy-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T18:41:39+00:00
completed_at: 2026-05-25T18:48:07+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: 25 focused memory/command-registry tests passed; command registry validation ok with 478 commands; startup policy and capability manifest validation passed via make policy-check; CLI smokes for memory continuity status and context-preview passed
docs_updated: docs/memory/LONG_TERM_MEMORY_SEARCH.md; docs/memory/CROSS_SESSION_CONTINUITY.md; docs/memory/MEMORY_INJECTION_POLICY.md; README.md; docs/COMMAND_REGISTRY.md; docs/COMMAND_TEST_MATRIX.md; docs/FEATURE_REGISTRY.md; docs/FEATURE_MATURITY.md; docs/FEATURE_ROADMAP.md; docs/RISK_REGISTER.md; docs/THREAT_MODEL.md; docs/RELEASE_CHECKLIST.md; CHANGELOG.md
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
notes: Completed HERMES-10 long-term memory search and cross-session continuity enhancements. Added brokered redacted memory continuity status/build-summary/clear and context-preview helpers. No cloud embeddings, no separate continuity profile persistence, no automatic prompt injection, no memory write, no personal-data inclusion by default, no paid/cloud calls, no package install, and no safety-control bypass.
---

# Prompt

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
