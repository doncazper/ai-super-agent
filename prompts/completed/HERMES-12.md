---
prompt_id: HERMES-12
pack_id: hermes-inspired-safe-autonomy-v1
title: Safe autonomy dogfood and eval suite
category: tests
risk_level: MEDIUM
approval_gate: false
depends_on: ["HERMES-11"]
status: completed
order: 12
created_at: 2026-05-25T17:28:14+00:00
imported_at: 2026-05-25T17:28:14+00:00
source_pack: prompts/packs/hermes-inspired-safe-autonomy-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T18:52:04+00:00
completed_at: 2026-05-25T19:04:17+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: Focused safe autonomy dogfood/eval tests passed with 32 passed; follow-up docs/command/maturity tests passed with 24 passed; eval run --safe-autonomy passed with 4 pass and 5 personal-data skips; dogfood run safe_autonomy_core --dry-run passed; commands validate passed with 484 commands; startup policy and capability manifest validation passed via make policy-check.
docs_updated: docs/autonomy/SAFE_AUTONOMY_DOGFOOD_RUNBOOK.md; docs/TEST_PLAN.md; docs/COMMAND_REGISTRY.md; docs/COMMAND_TEST_MATRIX.md; docs/FEATURE_REGISTRY.md; docs/FEATURE_MATURITY.md; docs/FEATURE_ROADMAP.md; docs/RISK_REGISTER.md; docs/THREAT_MODEL.md; docs/RELEASE_CHECKLIST.md; docs/PROJECT_STATE.md; docs/TRACKER_DASHBOARD.md; docs/COMPLETION_REPORT.md; CHANGELOG.md
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
notes: Completed mock-first safe autonomy dogfood/eval suite. No live risky autonomy, personal data, network-required provider calls, external scripts, background persistence, browser automation, executable sandboxing, paid/cloud providers, or HIGH/CRITICAL action execution added.
---

# Prompt

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
