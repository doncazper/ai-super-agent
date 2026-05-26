<<<PROMPT_PACK_START>>>
pack_id: command-qa-sandbox-self-heal-v1
pack_title: Command QA Sandbox and Self-Healing Loop
created_by: user
mode: controlled_batch_until_blocked
default_execution: sequential
requires_sdlc: true
requires_prompt_ledger: true
requires_feature_maturity_update: true
priority: high

pack_summary:
  - Build a safe command QA sandbox that systematically tests known CLI commands over time.
  - Start with safe/read-only commands, then progressively add mocked provider tests, disposable workspace tests, safe live checks, and manual approval-gated tests.
  - Log every command run, rank results, generate bugs, create regression tests, update maturity, and propose safe self-healing fixes.
  - Do not blindly run every command against real data.
  - Do not run HIGH/CRITICAL actions automatically.
  - Do not access personal data by default.
  - Do not send emails/messages or write calendar/contacts/tasks/files except inside an approved disposable QA workspace.
  - Do not commit, push, or merge automatically.

global_rules:
  - Follow SPEC.md, docs/SDLC.md, and AGENTS.md.
  - Build safety first, capabilities second.
  - Do not weaken or bypass ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger.
  - Do not enable personal-data tools by default.
  - Do not install packages or create background persistence.
  - Do not delete tests to make the suite pass.
  - Use mocks, fixtures, dry-runs, and disposable workspaces.
  - Update CHANGELOG.md, docs/PROJECT_STATE.md, docs/FEATURE_REGISTRY.md, docs/FEATURE_MATURITY.md, docs/FEATURE_ROADMAP.md if needed, docs/COMMAND_REGISTRY.md if commands change, docs/COMMAND_TEST_MATRIX.md if QA steps change, docs/COMPLETION_REPORT.md, docs/RISK_REGISTER.md if risk changes, docs/THREAT_MODEL.md if threat surface changes, docs/RELEASE_CHECKLIST.md if release-gate checks change, and prompt tracker docs if present.

stop_conditions:
  - approval_gate
  - failing_tests_not_safely_fixable
  - command_would_access_personal_data
  - command_would_send_or_write_real_external_data
  - command_would_delete_or_mutate_real_user_files
  - package_install_required
  - background_persistence_required
  - security_policy_change_required
  - ambiguous_requirements
  - git_commit_or_push_required_without_user_approval

expected_prompt_ids:
  - QA-01
  - QA-02
  - QA-03
  - QA-04
  - QA-05
  - QA-06
  - QA-07
  - QA-08
  - QA-09
  - QA-10

<<<PROMPT_START id="QA-01" order="1">>
title: Command QA sandbox architecture and safety policy
category: dogfood
risk_level: LOW
approval_gate: false
depends_on: []
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Create Command QA Sandbox architecture and safety policy.

Goal:
Design a safe, systematic command-testing system that can run through known commands, log results, rank failures, create bugs, create regression tests, and propose self-healing fixes without unsafe side effects.

Before making changes, read SPEC.md, docs/SDLC.md, AGENTS.md, README.md, CHANGELOG.md, docs/PROJECT_STATE.md, docs/FEATURE_REGISTRY.md, docs/FEATURE_MATURITY.md, docs/FEATURE_ROADMAP.md, docs/COMMAND_REGISTRY.md if present, docs/COMMAND_TEST_MATRIX.md if present, docs/COMPLETION_REPORT.md, docs/RISK_REGISTER.md, docs/THREAT_MODEL.md, docs/TEST_PLAN.md, docs/RELEASE_CHECKLIST.md, dogfood_suites/ if present, reports/sessions/ if present, bugs/ if present, and tests/regressions/ if present.

Scope:
- Architecture, docs, QA policy, run tiers, result schema, self-heal policy.
- No runtime command execution beyond validations/tests.

Non-goals:
- Do not run all commands yet.
- Do not execute HIGH/CRITICAL commands.
- Do not access personal data.
- Do not send/write/delete real data.
- Do not implement self-healing patches yet.
- Do not create background automation.

Create:
- docs/qa/COMMAND_QA_SANDBOX_STRATEGY.md
- docs/qa/COMMAND_QA_SAFETY_POLICY.md
- docs/qa/COMMAND_QA_TIERS.md
- docs/qa/COMMAND_QA_RESULT_SCHEMA.md
- docs/qa/SELF_HEALING_LOOP_POLICY.md
- docs/decisions/command_qa_sandbox_self_heal.md

Define QA tiers:
- Tier 0: registry/docs validation only
- Tier 1: help/status/doctor/read-only local commands
- Tier 2: mocked provider commands
- Tier 3: disposable workspace write commands
- Tier 4: dry-run personal-data commands
- Tier 5: safe live provider commands with configured providers
- Tier 6: approval-gated HIGH commands, manual only
- Tier 7: CRITICAL sends/writes, never auto-run; manual approval/review only

Define result schema with run_id, command_id, command_string, qa_tier, risk_level, start_time, duration_ms, exit_code, redacted stdout/stderr excerpts, full_log_path, status, failure_type, severity, suspected_area, linked_bug_id, regression_test_path, feature_id, maturity_impact, audit_ids, notes.

Define self-healing policy: branch-based, evidence-based, regression-test-gated, safe-only by default, no commit/push/merge without approval, no policy weakening, no high-risk behavior enabling.

Update planned commands in docs/COMMAND_REGISTRY.md if present:
- python smart_agent.py qa sandbox status
- python smart_agent.py qa commands plan
- python smart_agent.py qa commands run --tier 1
- python smart_agent.py qa commands run --group weather
- python smart_agent.py qa commands report --last
- python smart_agent.py qa bugs create --from-run <run_id>
- python smart_agent.py qa regressions create --from-bug <bug_id>
- python smart_agent.py qa self-heal plan
- python smart_agent.py qa self-heal run --safe-only

Run docs validation, command registry validation, startup policy validation, and full tests if practical.

Final report: files created/changed, QA tiers, planned commands, tests/validations, blockers, next prompt.
<<<PROMPT_END id="QA-01">>

<<<PROMPT_START id="QA-02" order="2">>
title: Command inventory to QA plan generator
category: command_registry
risk_level: LOW
approval_gate: false
depends_on: ["QA-01"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build command inventory to QA plan generator.

Goal:
Use docs/COMMAND_REGISTRY.md and code-discovered CLI commands to create a ranked, safe command QA plan.

Scope:
- Command inventory parsing.
- QA tier classification.
- Run plan generation.
- Tests.
- No command execution.

Create:
- agent/qa/__init__.py
- agent/qa/models.py
- agent/qa/command_inventory.py
- agent/qa/qa_plan.py
- agent/qa/safety.py
- agent/qa/errors.py
- tests/qa/test_command_inventory_qa_plan.py
- docs/qa/COMMAND_QA_PLAN.md

Commands:
- python smart_agent.py qa commands plan
- python smart_agent.py qa commands plan --tier 1
- python smart_agent.py qa commands plan --group weather
- python smart_agent.py qa commands plan --safe-only

Requirements:
1. Read command registry as source of truth when present.
2. Cross-check with code-discovered commands if practical.
3. Classify every command by QA tier.
4. Identify commands missing examples/risk levels/tests/docs.
5. Skip planned/stubbed/deprecated commands unless explicitly requested.
6. Identify provider/API setup requirements.
7. Identify commands requiring disposable workspace.
8. Identify commands requiring approval.
9. Generate deterministic run order.
10. Do not execute commands.

QA plan fields: plan_id, generated_at, command_count, safe_count, skipped_count, blocked_count, commands_by_tier, commands_by_group, recommended_first_batch, setup_required, risks, notes.

Tests: registry fixture parsed, tier 1 selected, high/critical excluded from safe-only, planned/stubbed skipped, missing examples reported, provider-required marked setup_required, deterministic order.

Update docs/tracking and run tests/validations.
<<<PROMPT_END id="QA-02">>

<<<PROMPT_START id="QA-03" order="3">>
title: Safe command runner sandbox
category: dogfood
risk_level: MEDIUM
approval_gate: false
depends_on: ["QA-02"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build safe command runner sandbox.

Goal:
Run only safe/approved command tiers in a controlled subprocess wrapper that captures stdout/stderr/exit codes, redacts output, enforces timeouts, and writes structured run logs.

Scope:
- Subprocess runner for approved commands.
- Timeouts/redaction/logging.
- Tier 0/Tier 1 safe commands only by default.
- Tests.

Non-goals:
- Do not run HIGH/CRITICAL commands.
- Do not run personal-data commands.
- Do not run send/write/delete commands.
- Do not run arbitrary shell.
- Do not run commands not in QA plan.
- Do not install packages.

Create:
- agent/qa/runner.py
- agent/qa/logging.py
- agent/qa/redaction.py
- tests/qa/test_safe_command_runner.py
- reports/qa/.gitkeep
- docs/qa/COMMAND_QA_RUNNER.md

Commands:
- python smart_agent.py qa commands run --tier 0
- python smart_agent.py qa commands run --tier 1
- python smart_agent.py qa commands run --safe-only
- python smart_agent.py qa commands report --last

Runner requirements:
1. Runs only commands from generated QA plan.
2. Safe-only default.
3. Denies HIGH/CRITICAL/personal-data/send/write/delete commands.
4. Uses repo venv Python.
5. Sets safe environment variables.
6. Redacts secrets from stdout/stderr.
7. Applies timeout per command.
8. Captures exit code/duration/stdout/stderr excerpts.
9. Stores full redacted logs under reports/qa/.
10. Produces JSONL and markdown summary.
11. Does not mutate real files except reports/qa and later disposable workspace.

Tests: safe command runs, disallowed command blocked, timeout handled, stdout/stderr captured, secret redacted, report written, high/critical denied, personal-data denied, arbitrary command rejected.

Update docs/tracking and run tests/validations.
<<<PROMPT_END id="QA-03">>

<<<PROMPT_START id="QA-04" order="4">>
title: Disposable workspace and fixture sandbox
category: tests
risk_level: MEDIUM
approval_gate: false
depends_on: ["QA-03"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build disposable workspace and fixture sandbox for deeper command testing.

Goal:
Allow safe deeper testing of file/document/write commands by creating a disposable QA workspace with fixture files, fake data, and cleanup.

Scope:
- Disposable workspace manager.
- Fixtures.
- Tier 2/Tier 3 command test support.
- Tests.

Non-goals:
- Do not touch real user files.
- Do not test destructive commands outside disposable workspace.
- Do not test personal-data connectors.
- Do not send/write external services.

Create:
- agent/qa/disposable_workspace.py
- agent/qa/fixtures.py
- tests/qa/test_disposable_workspace.py
- qa_fixtures/files/
- qa_fixtures/docs/
- qa_fixtures/web/
- qa_fixtures/memory/
- qa_fixtures/commands/
- docs/qa/DISPOSABLE_WORKSPACE.md

Commands:
- python smart_agent.py qa sandbox init
- python smart_agent.py qa sandbox status
- python smart_agent.py qa sandbox clean
- python smart_agent.py qa commands run --tier 3 --sandbox

Requirements:
1. Disposable workspace path under .qa_workspace/ or reports/qa/workspaces/.
2. Never use home/Documents/Desktop by default.
3. Fixture data is fake and non-personal.
4. Cleanup bounded to disposable path.
5. Path traversal prevented.
6. File writes only inside sandbox.
7. Reports include sandbox path.
8. Tier 3 commands require --sandbox.
9. Delete commands still dry-run unless explicitly fixture-safe.

Tests: workspace init, fixture creation, cleanup bounded, path traversal blocked, command run with sandbox env, real file path rejected.

Update docs/tracking and run tests/validations.
<<<PROMPT_END id="QA-04">>

<<<PROMPT_START id="QA-05" order="5">>
title: Result ranking, bug generation, and regression creation
category: bugs
risk_level: MEDIUM
approval_gate: false
depends_on: ["QA-04"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build result ranking, bug generation, and regression creation.

Goal:
Turn QA command run results into ranked failures, structured bug reports, and regression test stubs.

Create:
- agent/qa/analyzer.py
- agent/qa/bug_generator.py
- agent/qa/regression_generator.py
- tests/qa/test_qa_analyzer_bug_regression.py
- docs/qa/COMMAND_QA_BUG_TRIAGE.md

Commands:
- python smart_agent.py qa results rank --last
- python smart_agent.py qa bugs create --from-run <run_id>
- python smart_agent.py qa bugs create --from-report <report_id>
- python smart_agent.py qa regressions create --from-bug <bug_id>
- python smart_agent.py qa regressions create --from-run <run_id>

Failure types:
- command_not_found, import_error, usage_error, bad_help, bad_output, timeout, exception, policy_failure, approval_failure, audit_failure, redaction_failure, provider_missing_bad_error, docs_mismatch, command_registry_mismatch, test_gap, flaky, unknown.

Ranking:
- P0 safety/security/data leak/policy bypass
- P1 core runtime command broken
- P2 feature command broken
- P3 UX/docs/help issue
- P4 polish/noise

Bug report fields: bug_id, run_id, command_id, command, severity, failure_type, expected_behavior, actual_behavior, reproduction_command, redacted stdout/stderr excerpts, suspected_area, suggested_fix, suggested_regression_test, status.

Requirements:
1. No raw secrets in bug reports.
2. Personal data redacted.
3. Regression tests use fixtures/mocks.
4. Do not mark bug fixed automatically.
5. Bugs saved under bugs/.
6. Regression stubs saved under tests/regressions/.
7. Feature maturity impacted conservatively.

Tests: rank failures, generate bug from failed run, redact secrets, generate regression stub, docs mismatch bug, safety failure P0.

Update docs/tracking and run tests/validations.
<<<PROMPT_END id="QA-05">>

<<<PROMPT_START id="QA-06" order="6">>
title: Safe self-healing patch loop
category: self_improvement
risk_level: MEDIUM
approval_gate: false
depends_on: ["QA-05"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build safe self-healing patch loop.

Goal:
Create a controlled loop that takes ranked bugs/regressions, proposes safe fixes, applies only scoped low/medium-risk patches on a branch, runs tests, updates docs, and stops for human review before commit/merge.

Create:
- agent/qa/self_heal.py
- agent/qa/patch_plan.py
- tests/qa/test_self_heal_patch_loop.py
- docs/qa/SELF_HEALING_PATCH_LOOP.md

Commands:
- python smart_agent.py qa self-heal plan
- python smart_agent.py qa self-heal plan --bug <bug_id>
- python smart_agent.py qa self-heal run --safe-only --bug <bug_id>
- python smart_agent.py qa self-heal report --last

Patch plan fields: patch_id, bug_id, severity, allowed_to_patch, reason, branch_name, files_expected, tests_required, docs_required, risk, rollback_plan, human_review_required.

Rules:
1. Safe-only by default.
2. P0/P1 safety bugs get plans but automatic patching only if trivially safe.
3. P2/P3 local bugs can be patched if scoped.
4. Must run regression and targeted tests.
5. Must update docs/tracking.
6. No commit/push.
7. Stop if broad refactor, policy change, or package install needed.

Tests: patch plan, high-risk review-required, safe P3 allowed, broad refactor blocked, regression required, no commit/push, report written.

Update docs/tracking and run tests/validations.
<<<PROMPT_END id="QA-06">>

<<<PROMPT_START id="QA-07" order="7">>
title: Progressive deepening and scheduled QA policy
category: scheduler
risk_level: MEDIUM
approval_gate: false
depends_on: ["QA-06"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build progressive deepening and scheduled QA policy.

Goal:
Let command QA mature over time by progressively deepening from registry checks to read-only commands, mocked providers, sandbox writes, safe live providers, and manual approval-gated commands. Add policy for scheduled/daily/weekly QA without starting background jobs by default.

Create:
- agent/qa/progressive.py
- agent/qa/schedule_policy.py
- tests/qa/test_progressive_deepening.py
- docs/qa/PROGRESSIVE_QA_DEEPENING.md
- docs/qa/SCHEDULED_COMMAND_QA_POLICY.md

Progression:
- daily: Tier 0-1
- every few days: Tier 2 mocked provider
- weekly: Tier 3 disposable workspace
- manual: Tier 4-5 live/dry-run
- never automatic: Tier 6-7 high/critical

Commands:
- python smart_agent.py qa next-batch
- python smart_agent.py qa daily --dry-run
- python smart_agent.py qa weekly --dry-run
- python smart_agent.py qa depth status

Requirements:
1. No scheduler enabled by default.
2. Dry-run by default.
3. Daily/weekly QA generates plan/report.
4. Does not auto-run high/critical commands.
5. Does not access personal data.
6. Creates Action Center item or TODO if scheduler exists.
7. Updates maturity evidence only after runs.

Tests: next batch selects oldest untested safe commands, daily excludes high/critical, weekly excludes personal data, dry-run writes plan only.

Update docs/tracking and run tests/validations.
<<<PROMPT_END id="QA-07">>

<<<PROMPT_START id="QA-08" order="8">>
title: QA dashboard and maturity integration
category: dashboard
risk_level: LOW
approval_gate: false
depends_on: ["QA-07"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build QA dashboard and feature maturity integration.

Goal:
Show command QA status, pass/fail trends, bug rankings, commands needing tests, features needing maturity work, and next recommended QA batch.

Create:
- agent/qa/dashboard.py
- tests/qa/test_qa_dashboard.py
- docs/qa/COMMAND_QA_DASHBOARD.md

Commands:
- python smart_agent.py qa dashboard
- python smart_agent.py qa status
- python smart_agent.py qa feature-maturity-impact
- python smart_agent.py qa next-fix

Dashboard shows:
- total/tested/untested commands
- pass/fail/skip/blocked counts
- failures by severity/feature
- stale commands
- commands missing examples/tests
- features needing live validation
- top bugs
- next recommended QA batch
- next safe self-heal candidate

Requirements:
1. Read-only.
2. No command execution.
3. No personal data.
4. Uses QA reports, command registry, and feature maturity.
5. Feature maturity updated conservatively only with evidence.

Tests: dashboard renders, no reports handled, next fix selects highest safe bug, maturity impact conservative.

Update docs/tracking and run tests/validations.
<<<PROMPT_END id="QA-08">>

<<<PROMPT_START id="QA-09" order="9">>
title: Command QA dogfood and eval suite
category: tests
risk_level: LOW
approval_gate: false
depends_on: ["QA-08"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build Command QA dogfood and eval suite.

Goal:
Create dogfood/eval suites for the QA sandbox itself.

Create:
- dogfood_suites/command_qa_core.yaml
- dogfood_suites/command_qa_sandbox.yaml
- dogfood_suites/command_qa_self_heal.yaml
- eval_cases/command_qa/
- docs/qa/COMMAND_QA_DOGFOOD_RUNBOOK.md

Dogfood scenarios:
- generate QA plan
- run Tier 0
- run Tier 1 safe-only
- create disposable workspace
- run sandbox fixture command
- rank failures from fixture report
- generate bug from fixture failure
- generate regression stub
- create self-heal plan
- show dashboard

Requirements:
1. Fixtures/mocks only.
2. No high/critical commands.
3. No personal data.
4. No real sends/writes.
5. No commits/pushes.
6. Results logged to reports/qa.

Tests: suite YAML validates, eval fixtures load, dogfood commands safe.

Update docs/tracking and run tests/validations.
<<<PROMPT_END id="QA-09">>

<<<PROMPT_START id="QA-10" order="10">>
title: Command QA sandbox release gate
category: release_gate
risk_level: LOW
approval_gate: false
depends_on: ["QA-09"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Run Command QA Sandbox release gate and maturity review.

Goal:
Validate that the command QA sandbox can systematically test commands, log results, rank failures, create bugs/regressions, and propose safe self-healing patches without unsafe side effects.

Run:
1. full test suite
2. startup policy validation
3. capability manifest validation
4. docs validation if available
5. command registry validation
6. QA unit tests
7. QA dogfood suite with fixtures
8. QA eval suite
9. Tier 0 command QA plan/run
10. Tier 1 safe-only command QA run, if safe

Verify:
- command inventory works
- QA plan works
- safe runner blocks high/critical
- personal-data commands blocked
- reports redacted
- disposable workspace bounded
- bug generation works
- regression generation works
- self-heal plan safe
- no auto-commit/push
- progressive QA safe
- dashboard works
- command registry updated
- feature maturity conservative

Create/update:
- docs/qa/COMMAND_QA_RELEASE_GATE.md
- docs/qa/COMMAND_QA_MATURITY_REVIEW.md

Maturity assessment:
- QA architecture/policy
- command inventory/planner
- safe runner
- disposable workspace
- result ranking/bug generation
- regression generation
- self-heal loop
- progressive QA
- dashboard
- dogfood/evals
- release gate

Update all required tracking docs.

Final report:
- tests run/results
- validation results
- QA run results
- bugs generated
- regressions generated
- maturity score
- remaining blockers
- whether command QA sandbox is safe to rely on
- next recommended feature track
<<<PROMPT_END id="QA-10">>

<<<PROMPT_PACK_END>>>
