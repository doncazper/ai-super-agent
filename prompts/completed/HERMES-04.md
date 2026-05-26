---
prompt_id: HERMES-04
pack_id: hermes-inspired-safe-autonomy-v1
title: Repeated-task skill creation proposals
category: native_skills
risk_level: MEDIUM
approval_gate: false
depends_on: ["HERMES-03"]
status: completed
order: 4
created_at: 2026-05-25T17:28:14+00:00
imported_at: 2026-05-25T17:28:14+00:00
source_pack: prompts/packs/hermes-inspired-safe-autonomy-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T17:45:25+00:00
completed_at: 2026-05-25T17:54:56+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: tests/autonomy/test_skill_proposals.py 8 passed; combined HERMES/channel/Telegram/mobile/skill-proposal/maturity docs tests 41 passed; commands validate ok with 453 commands; make policy-check passed; CLI smokes passed
docs_updated: README, CHANGELOG, PROJECT_STATE, TRACKER_DASHBOARD, FEATURE_REGISTRY, FEATURE_MATURITY, FEATURE_ROADMAP, COMMAND_REGISTRY, COMMAND_TEST_MATRIX, COMPLETION_REPORT, RISK_REGISTER, THREAT_MODEL, RELEASE_CHECKLIST, autonomy/native skill proposal docs
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
notes: Implemented proposal-only repeated-task skill proposal engine and brokered CLI; no automatic skill creation/import/enablement/execution, package install, personal-data access, or vetting bypass.
---

# Prompt

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
