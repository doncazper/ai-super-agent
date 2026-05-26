---
prompt_id: HERMES-09
pack_id: hermes-inspired-safe-autonomy-v1
title: Model switching and session continuity
category: core
risk_level: MEDIUM
approval_gate: false
depends_on: ["HERMES-08"]
status: completed
order: 9
created_at: 2026-05-25T17:28:14+00:00
imported_at: 2026-05-25T17:28:14+00:00
source_pack: prompts/packs/hermes-inspired-safe-autonomy-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T18:33:50+00:00
completed_at: 2026-05-25T18:41:35+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: 20 focused tests passed; command registry validation ok with 474 commands; startup policy and capability manifest validation passed via make policy-check
docs_updated: docs/autonomy/MODEL_SWITCHING.md; docs/autonomy/CROSS_SESSION_CONTINUITY.md; README.md; .env.example; docs/COMMAND_REGISTRY.md; docs/COMMAND_TEST_MATRIX.md; docs/FEATURE_REGISTRY.md; docs/FEATURE_MATURITY.md; docs/FEATURE_ROADMAP.md; docs/RISK_REGISTER.md; docs/THREAT_MODEL.md; docs/RELEASE_CHECKLIST.md; CHANGELOG.md
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
notes: Completed metadata-only model switching and session continuity groundwork. Non-dry-run provider switches remain blocked, LM Studio remains default, no model calls, no tool execution, no paid/cloud default, no personal-data carryover, no memory write, and no continuity store.
---

# Prompt

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
