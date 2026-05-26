---
prompt_id: HERMES-07
pack_id: hermes-inspired-safe-autonomy-v1
title: Subagent isolation groundwork
category: autonomy
risk_level: MEDIUM
approval_gate: false
depends_on: ["HERMES-06"]
status: completed
order: 7
created_at: 2026-05-25T17:28:14+00:00
imported_at: 2026-05-25T17:28:14+00:00
source_pack: prompts/packs/hermes-inspired-safe-autonomy-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T18:10:35+00:00
completed_at: 2026-05-25T18:17:09+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: focused subagent isolation tests passed with 9 passed; command registry validation passed with 468 commands; make policy-check passed
docs_updated: README, CHANGELOG, PROJECT_STATE, TRACKER_DASHBOARD, FEATURE_REGISTRY, FEATURE_MATURITY, FEATURE_ROADMAP, COMMAND_REGISTRY, COMMAND_TEST_MATRIX, RISK_REGISTER, THREAT_MODEL, RELEASE_CHECKLIST, COMPLETION_REPORT
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
notes: Completed HERMES-07 as mock-only subagent isolation profiles; no real subagent execution, write permissions, direct tool calls, personal-data access, CRITICAL execution, approvals, parallel workflows, or background persistence.
---

# Prompt

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
