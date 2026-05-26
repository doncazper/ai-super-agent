---
prompt_id: HERMES-13
pack_id: hermes-inspired-safe-autonomy-v1
title: Hermes-inspired safe autonomy release gate
category: release_gate
risk_level: LOW
approval_gate: false
depends_on: ["HERMES-12"]
status: completed
order: 13
created_at: 2026-05-25T17:28:14+00:00
imported_at: 2026-05-25T17:28:14+00:00
source_pack: prompts/packs/hermes-inspired-safe-autonomy-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T19:04:20+00:00
completed_at: 2026-05-25T19:11:17+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: Full suite passed with 1380 passed, 1 skipped; focused HERMES release-gate tests passed with 74 passed; docs/tracker tests passed with 26 passed; eval run --safe-autonomy passed with 4 pass, 0 fail, 5 personal-data skips; dogfood run safe_autonomy_core --dry-run passed; commands validate passed with 484 commands; startup policy and capability manifest validation passed via make policy-check.
docs_updated: docs/autonomy/HERMES_INSPIRED_RELEASE_GATE.md; docs/autonomy/HERMES_INSPIRED_MATURITY_REVIEW.md; docs/PROJECT_STATE.md; docs/FEATURE_REGISTRY.md; docs/FEATURE_MATURITY.md; docs/FEATURE_ROADMAP.md; docs/COMMAND_REGISTRY.md; docs/COMMAND_TEST_MATRIX.md; docs/COMPLETION_REPORT.md; docs/RISK_REGISTER.md; docs/THREAT_MODEL.md; docs/TEST_PLAN.md; docs/RELEASE_CHECKLIST.md; docs/TRACKER_DASHBOARD.md; CHANGELOG.md
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
notes: Release gate passed locally. Safe autonomy groundwork remains local-tested only; no high-risk autonomy, background persistence, browser automation, personal-data access, send/write behavior, executable sandboxing, subagent writes, paid/cloud defaults, or bypass behavior enabled.
---

# Prompt

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
