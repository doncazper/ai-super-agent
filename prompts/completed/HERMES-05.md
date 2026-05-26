---
prompt_id: HERMES-05
pack_id: hermes-inspired-safe-autonomy-v1
title: Skill improvement from experience
category: native_skills
risk_level: MEDIUM
approval_gate: false
depends_on: ["HERMES-04"]
status: completed
order: 5
created_at: 2026-05-25T17:28:14+00:00
imported_at: 2026-05-25T17:28:14+00:00
source_pack: prompts/packs/hermes-inspired-safe-autonomy-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T17:56:30+00:00
completed_at: 2026-05-25T18:04:00+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: focused skill improvement tests passed with 9 passed; combined HERMES/channel/Telegram/mobile/skill-proposal/skill-improvement/maturity docs tests passed with 50 passed; command registry validation passed with 458 commands; make policy-check passed
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
notes: Completed HERMES-05 as proposal-only skill improvement workflow; no skill edits, lockfile updates, enablement, script execution, package install, personal-data evidence, or review bypass.
---

# Prompt

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
