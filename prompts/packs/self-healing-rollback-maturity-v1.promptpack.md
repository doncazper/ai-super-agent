<<<PROMPT_PACK_START>>>
pack_id: self-healing-rollback-maturity-v1
pack_title: Self-Healing Rollback Maturity Track
created_by: user
mode: controlled_batch_until_blocked
default_execution: sequential
requires_sdlc: true
requires_prompt_ledger: true
requires_feature_maturity_update: true
priority: high

pack_summary:
  - This pack matures self-healing into an evidence-based, rollback-first engineering loop.
  - More aggressive means better diagnosis, reproduction, patch planning, isolated patching, rollback, test escalation, safety linting, confidence scoring, and reporting.
  - It does not mean reckless autonomous editing, hidden commits, unsafe policy changes, live provider changes, personal-data access, or unreviewed high-risk modifications.
  - It builds aggression levels, candidate ranking, reproduction-first workflow, regression hardening, recovery capsules, isolated worktrees, rollback verification, safety lints, invariant suites, flaky-test/bisect support, patch queue/budgets/no-fix classification, dashboards/report cards, QA sandbox integration, canonical runtime integration, release gate, and Git review/commit/push gate.
  - Git review/commit/push is a standard final gate for major prompt packs. For this pack, only SELFHEAL-16 may commit/push, and only if explicitly authorized by the wrapper, tests pass, secret scan is clean, and reviewed safe files are staged intentionally.
  - Never force push.

global_rules:
  - Follow SPEC.md, docs/SDLC.md, and AGENTS.md.
  - Preserve ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger.
  - Do not enable personal-data tools by default.
  - Do not enable sends/writes.
  - Do not alter CRITICAL approval no-reuse behavior.
  - Do not install packages, call live providers by default, call paid APIs, download models, start background services, create web servers, broadly rewrite code, commit, or push before the final Git gate.
  - Do not modify safety-control-plane files automatically.
  - Do not stage .env, token files, OAuth caches, private keys, raw logs, raw reports, .venv, __pycache__, .pytest_cache, generated junk, or personal data.
  - Do not use git add . blindly.
  - Any patch must have a rollback plan.
  - Any code patch must have test evidence or be marked needs_review.
  - Any self-heal run must produce a human-readable repair narrative.
  - Update CHANGELOG.md, docs/PROJECT_STATE.md, docs/FEATURE_REGISTRY.md, docs/FEATURE_MATURITY.md, docs/FEATURE_ROADMAP.md if status/order changes, docs/COMMAND_REGISTRY.md if commands change, docs/COMMAND_TEST_MATRIX.md if QA steps change, docs/COMPLETION_REPORT.md, docs/RISK_REGISTER.md if risk changed, docs/THREAT_MODEL.md if threat surface changed, docs/RELEASE_CHECKLIST.md where release gates change, and prompt tracking docs if present.

stop_conditions:
  - approval_gate
  - failing_tests_not_safely_fixable
  - docs_validation_failure_not_safely_fixable
  - package_install_required
  - personal_data_access_required
  - live_provider_required
  - paid_api_required
  - model_download_required
  - background_persistence_required
  - broad_refactor_required
  - safety_control_plane_patch_required_without_approval
  - security_policy_change_required
  - ambiguous_requirements
  - likely_secret_detected
  - git_force_push_required
  - commit_or_push_required_before_final_gate

expected_prompt_ids:
  - SELFHEAL-01
  - SELFHEAL-02
  - SELFHEAL-03
  - SELFHEAL-04
  - SELFHEAL-05
  - SELFHEAL-06
  - SELFHEAL-07
  - SELFHEAL-08
  - SELFHEAL-09
  - SELFHEAL-10
  - SELFHEAL-11
  - SELFHEAL-12
  - SELFHEAL-13
  - SELFHEAL-14
  - SELFHEAL-15
  - SELFHEAL-16

<<<PROMPT_START id="SELFHEAL-01" order="1">>
title: Self-healing maturity roadmap, risk model, and aggression levels
category: self_improvement
risk_level: LOW
approval_gate: false
depends_on: []
status: queued
PROMPT:
Create the self-healing maturity roadmap, risk model, and aggression levels.

Before making changes, read SPEC.md, docs/SDLC.md, AGENTS.md, README.md, CHANGELOG.md, docs/PROJECT_STATE.md, docs/FEATURE_REGISTRY.md, docs/FEATURE_MATURITY.md, docs/FEATURE_ROADMAP.md, docs/COMMAND_REGISTRY.md if present, docs/COMMAND_TEST_MATRIX.md if present, docs/COMPLETION_REPORT.md, docs/RISK_REGISTER.md, docs/THREAT_MODEL.md, docs/RELEASE_CHECKLIST.md, docs/qa/ if present, docs/performance/ if present, docs/runtime/ if present, docs/self_improvement/ if present, agent/workflows/self_improvement.py if present, agent/qa/ if present, agent/performance/ if present, agent/runtime/ if present, and tests/.

Create docs/self_heal/SELF_HEALING_ROLLBACK_TRACK.md, SELF_HEALING_RISK_MODEL.md, SELF_HEALING_AGGRESSION_LEVELS.md, SELF_HEALING_NON_GOALS.md, SELF_HEALING_ROADMAP.md, and docs/decisions/self_healing_rollback_maturity.md.

Define aggression levels: Level 0 report only; Level 1 docs/tracker/test-fixture fixes; Level 2 small local code fixes; Level 3 feature-adjacent code fixes; Level 4 runtime/router/orchestrator fixes; Level 5 safety-control-plane changes, plan only unless explicitly approved; Level 6 commit/push only through final Git gate with explicit approval.

Define hard stop areas: ToolBroker bypass, PolicyEngine weakening, ApprovalManager bypass, AuditLogger disabling, CRITICAL approval reuse, personal-data default enablement, send/write expansion, background persistence, live provider default, package/dependency change, broad refactor, and secret storage/logging.

Planned commands: self-heal status, candidates, plan, reproduce, regressions, recovery-capsule, worktree, run --safe-only, rollback, verify-rollback, flaky-check, bisect-plan, dashboard, report, git-review.

No patching yet. Update tracking docs and run validations.
<<<PROMPT_END id="SELFHEAL-01">>

<<<PROMPT_START id="SELFHEAL-02" order="2">>
title: Bug source aggregator and candidate ranking
category: self_improvement
risk_level: MEDIUM
approval_gate: false
depends_on: ["SELFHEAL-01"]
status: queued
PROMPT:
Build bug source aggregator and candidate ranking.

Create agent/self_heal/__init__.py, models.py, bug_sources.py, ranking.py, tests/self_heal/test_bug_sources_ranking.py, docs/self_heal/BUG_SOURCE_AGGREGATION.md, and docs/self_heal/CANDIDATE_RANKING.md.

Aggregate from bugs/, reports/qa/, reports/evals/, reports/performance/, reports/session_reviews/, tests/regressions/, docs/PROMPT_AUDIT.md, command-registry validation output if available, tracker consistency reports, and manual user bug records.

Candidate fields: candidate_id, source_type, source_path, source_record_id, title, description, severity, feature_area, command, reproduction_hint, evidence_paths, confidence, risk, blast_radius, no_fix_reason, status.

Ranking: P0 safety/security/data leak/policy bypass; P1 cannot run/core broken; P2 major feature broken; P3 UX/docs/command issue; P4 polish.

Commands: python smart_agent.py self-heal status; self-heal candidates; self-heal candidates --source qa.

Read metadata/redacted reports only. Do not patch. Deduplicate candidates. Add tests and update docs/tracking.
<<<PROMPT_END id="SELFHEAL-02">>

<<<PROMPT_START id="SELFHEAL-03" order="3">>
title: Reproduction-first bug workflow
category: self_improvement
risk_level: MEDIUM
approval_gate: false
depends_on: ["SELFHEAL-02"]
status: queued
PROMPT:
Build reproduction-first bug workflow. Do not patch until there is a reproduction command, failing test, fixture, static finding, tracker conflict, or clearly documented docs mismatch.

Create agent/self_heal/reproduction.py, tests/self_heal/test_reproduction_workflow.py, and docs/self_heal/REPRODUCTION_FIRST_WORKFLOW.md.

Reproduction record fields: repro_id, candidate_id, repro_type, command, expected_failure, actual_failure, fixture_path, test_path, status, confidence, safe_to_run, personal_data_required, live_provider_required, notes.

Repro types: failing_test, failing_command, fixture_repro, static_scan_finding, tracker_conflict, docs_mismatch, manual_steps_only, not_reproducible.

Commands: self-heal reproduce --candidate <candidate_id>; self-heal reproduce --bug <bug_id>; self-heal repro-status <repro_id>.

Safe commands only by default. No live providers, personal data, or HIGH/CRITICAL execution. Store redacted repro output. If no repro exists, classify as needs_repro or no_fix.
<<<PROMPT_END id="SELFHEAL-03">>

<<<PROMPT_START id="SELFHEAL-04" order="4">>
title: Regression test generator hardening
category: self_improvement
risk_level: MEDIUM
approval_gate: false
depends_on: ["SELFHEAL-03"]
status: queued
PROMPT:
Harden regression test generation from bugs/reproductions.

Create agent/self_heal/regression.py, tests/self_heal/test_regression_generation_hardening.py, docs/self_heal/REGRESSION_TEST_GENERATION.md, and docs/templates/self_heal_regression_template.py.

Rules: use fixtures/mocks/redacted data; no personal data; no live providers; no paid APIs; no sends/writes except temp/disposable workspace; generated tests may be skipped initially if manual conversion needed, but must explain why; prefer concrete assertions; link to candidate_id/repro_id/bug_id.

Commands: self-heal regressions create --candidate <candidate_id>; self-heal regressions create --repro <repro_id>; self-heal regressions list.
<<<PROMPT_END id="SELFHEAL-04">>

<<<PROMPT_START id="SELFHEAL-05" order="5">>
title: Recovery capsule and rollback system
category: self_improvement
risk_level: MEDIUM
approval_gate: false
depends_on: ["SELFHEAL-04"]
status: queued
PROMPT:
Build recovery capsule and rollback system.

Create agent/self_heal/recovery_capsule.py, agent/self_heal/rollback.py, tests/self_heal/test_recovery_capsule_rollback.py, docs/self_heal/RECOVERY_CAPSULES.md, docs/self_heal/ROLLBACK_SYSTEM.md, and reports/self_heal/recovery_capsules/.gitkeep or equivalent.

Recovery capsule contents: capsule_id, created_at, candidate/repro/bug ids, pre_patch_git_status.txt, pre_patch_diff.patch, touched_files_manifest.json, file_hashes_before.json, file_snapshots/, command_log.jsonl, test_results_before.json, patch_plan.json, rollback.sh or rollback_instructions.md, capsule_manifest.json.

Rollback mechanisms: reverse patch, file snapshot restore, git worktree/branch reset plan, manual fallback instructions.

Rollback quality grades: A isolated worktree/branch rollback plus hashes verified; B reverse patch plus hashes verified; C file snapshots available; D manual instructions only; F unsafe/incomplete rollback.

Commands: self-heal recovery-capsule create --candidate <candidate_id>; self-heal rollback --capsule <capsule_id> --dry-run; self-heal verify-rollback --capsule <capsule_id>.

Capsule creation does not patch. No secrets/personal data. Raw logs redacted. Cleanup bounded.
<<<PROMPT_END id="SELFHEAL-05">>

<<<PROMPT_START id="SELFHEAL-06" order="6">>
title: Isolated Git worktree patch sandbox
category: self_improvement
risk_level: MEDIUM
approval_gate: false
depends_on: ["SELFHEAL-05"]
status: queued
PROMPT:
Build isolated Git worktree patch sandbox strategy and optional dry-run implementation.

Create agent/self_heal/worktree.py, tests/self_heal/test_worktree_patch_sandbox.py, and docs/self_heal/ISOLATED_GIT_WORKTREE_PATCH_SANDBOX.md.

Commands: self-heal worktree plan --candidate <candidate_id>; self-heal worktree create --candidate <candidate_id> --dry-run; self-heal worktree status; self-heal worktree cleanup --dry-run.

Rules: dry-run by default; do not create worktree unless git repo and safe; do not delete user worktrees; path outside repo or approved generated path; branch name selfheal/<candidate_id>-<slug>; refuse if uncommitted work would be overwritten; no commit/push; no real patching unless explicitly fixture-safe.
<<<PROMPT_END id="SELFHEAL-06">>

<<<PROMPT_START id="SELFHEAL-07" order="7">>
title: Safe patch planner, blast-radius scoring, and confidence scoring
category: self_improvement
risk_level: MEDIUM
approval_gate: false
depends_on: ["SELFHEAL-06"]
status: queued
PROMPT:
Build safe patch planner with blast-radius scoring, confidence scoring, no-fix classifier, and patch budgets.

Create agent/self_heal/patch_planner.py, agent/self_heal/confidence.py, agent/self_heal/budgets.py, tests/self_heal/test_patch_planner_confidence.py, docs/self_heal/PATCH_PLANNER.md, docs/self_heal/BLAST_RADIUS_AND_CONFIDENCE.md, and docs/self_heal/PATCH_BUDGETS_AND_NO_FIX.md.

Patch fields: patch_id, candidate_id, repro_id, aggression_level, hypothesis, expected_files, max_files, max_lines_changed, blast_radius, confidence_score, rollback_quality_required, tests_required, docs_required, safety_lints_required, allowed_to_apply, reason, human_review_required.

Blast radius: file-level, module-level, feature-level, runtime-level, safety-control-level, repo-wide.

No-fix reasons: not a bug, docs-only issue, needs user decision, needs architecture decision, needs dependency install, needs live provider, needs approval, needs manual reproduction, too risky for self-heal.

Commands: self-heal plan --candidate <candidate_id>; self-heal plan --safe-only; self-heal no-fix --candidate <candidate_id> --reason <reason>.

Plan only. Safety-control changes plan-only unless explicit approval. Dependency changes and broad refactors blocked.
<<<PROMPT_END id="SELFHEAL-07">>

<<<PROMPT_START id="SELFHEAL-08" order="8">>
title: Safety lint gate for self-heal diffs
category: self_improvement
risk_level: HIGH
approval_gate: false
depends_on: ["SELFHEAL-07"]
status: queued
PROMPT:
Build safety lint gate for self-heal diffs.

Create agent/self_heal/safety_lints.py, tests/self_heal/test_self_heal_safety_lints.py, and docs/self_heal/SAFETY_LINT_GATE.md.

Lint for: ToolBroker bypass, PolicyEngine weakening, PermissionManager bypass, ApprovalManager bypass, AuditLogger disabling, CRITICAL approval reuse, personal-data capabilities enabled by default, secrets logged/stored, redaction removed, background persistence, server/listener default startup, package/dependency changes, live provider default, unsafe filesystem expansion, path jail weakening, new subprocess/shell=True, new eval/exec, broad glob/rglob, delete path, direct send/write expansion, backup restore policy weakening.

Commands: self-heal lint-diff; self-heal lint-diff --patch <patch_file>; self-heal lint-report --last.

Redact output. Does not patch. P0/P1 findings block safe-only self-heal. Tests use fixture diffs.
<<<PROMPT_END id="SELFHEAL-08">>

<<<PROMPT_START id="SELFHEAL-09" order="9">>
title: Test escalation ladder and invariant suite
category: self_improvement
risk_level: MEDIUM
approval_gate: false
depends_on: ["SELFHEAL-08"]
status: queued
PROMPT:
Build test escalation ladder and invariant suite.

Create agent/self_heal/test_ladder.py, agent/self_heal/invariants.py, tests/self_heal/test_test_ladder_invariants.py, docs/self_heal/TEST_ESCALATION_LADDER.md, and docs/self_heal/SELF_HEAL_INVARIANTS.md.

Test ladder: regression test, touched-area tests, safety/policy tests, command registry validation, startup policy validation, capability manifest validation, prompt tracker validation, dogfood/eval smoke if relevant, full suite.

Invariants: unknown tools denied, personal tools disabled by default, HIGH requires approval, CRITICAL no approval reuse, ToolBroker-only execution, audit logging enabled, secrets redacted, .env not tracked, no direct send/write path, no background persistence.

Commands: self-heal test-ladder --plan <patch_id> --dry-run; self-heal invariants; self-heal invariants --json.

Dry-run by default. No live providers/personal data. Invariant failure blocks patch.
<<<PROMPT_END id="SELFHEAL-09">>

<<<PROMPT_START id="SELFHEAL-10" order="10">>
title: Rollback verification and canary validation
category: self_improvement
risk_level: MEDIUM
approval_gate: false
depends_on: ["SELFHEAL-09"]
status: queued
PROMPT:
Build rollback verification and canary validation.

Create agent/self_heal/rollback_verify.py, agent/self_heal/canary.py, tests/self_heal/test_rollback_verify_canary.py, docs/self_heal/ROLLBACK_VERIFICATION.md, and docs/self_heal/CANARY_VALIDATION.md.

Rollback verification: verify capsule manifest, file hashes before/after rollback, reverse patch dry-run applies, snapshots exist, worktree branch exists if applicable, rollback quality grade.

Canary validation: scripts/agent doctor, commands validate, prompts audit if available, make policy-check if available, startup/capability validation, safe dogfood dry-run if available, light performance canary if performance scanner exists.

Commands: self-heal verify-rollback --capsule <capsule_id>; self-heal canary --safe; self-heal rollback-status --capsule <capsule_id>.

No actual rollback unless explicit and safe. No live providers/personal data. Redacted reports.
<<<PROMPT_END id="SELFHEAL-10">>

<<<PROMPT_START id="SELFHEAL-11" order="11">>
title: Flaky test detector and bisect assistant
category: self_improvement
risk_level: MEDIUM
approval_gate: false
depends_on: ["SELFHEAL-10"]
status: queued
PROMPT:
Build flaky test detector and git bisect assistant.

Create agent/self_heal/flaky.py, agent/self_heal/bisect_assistant.py, tests/self_heal/test_flaky_bisect_assistant.py, docs/self_heal/FLAKY_TEST_DETECTOR.md, and docs/self_heal/BISECT_ASSISTANT.md.

Flaky detector: rerun selected safe test N times, detect intermittent failure, mark flaky, create flaky-test candidate/bug, recommend stabilization.

Bisect assistant: dry-run plan by default, identify candidate commits from git log, propose test command, warn about dirty worktree, no destructive git reset, no automatic bisect unless explicitly approved later.

Commands: self-heal flaky-check --test <nodeid>; self-heal bisect-plan --test <command>.

Rules: no live providers/personal data; bounded reruns; timeout; no commit/push; no destructive git operations.
<<<PROMPT_END id="SELFHEAL-11">>

<<<PROMPT_START id="SELFHEAL-12" order="12">>
title: Patch queue, budgets, and no-fix classifier
category: self_improvement
risk_level: MEDIUM
approval_gate: false
depends_on: ["SELFHEAL-11"]
status: queued
PROMPT:
Build patch queue, budgets, and no-fix classifier.

Create agent/self_heal/patch_queue.py, agent/self_heal/no_fix.py, tests/self_heal/test_patch_queue_no_fix.py, docs/self_heal/PATCH_QUEUE.md, and docs/self_heal/NO_FIX_CLASSIFIER.md.

Patch queue statuses: pending, approved_to_attempt, in_progress, patched, tests_failed, rollback_required, rolled_back, needs_review, rejected, completed.

Budget fields: max_files_touched, max_lines_changed, max_attempts_per_bug, max_total_runtime, max_test_reruns, max_simultaneous_patches.

Commands: self-heal queue; self-heal queue add --candidate <candidate_id>; self-heal queue show <patch_id>; self-heal queue mark <patch_id> <status>; self-heal budget.

Rules: no patching; queue records redacted; no personal data; no commits/pushes.
<<<PROMPT_END id="SELFHEAL-12">>

<<<PROMPT_START id="SELFHEAL-13" order="13">>
title: Self-heal dashboard, report cards, and repair narrative
category: self_improvement
risk_level: LOW
approval_gate: false
depends_on: ["SELFHEAL-12"]
status: queued
PROMPT:
Build self-heal dashboard, report cards, and repair narrative.

Create agent/self_heal/dashboard.py, agent/self_heal/report_cards.py, tests/self_heal/test_dashboard_report_cards.py, docs/self_heal/SELF_HEAL_DASHBOARD.md, and docs/self_heal/REPAIR_NARRATIVE.md.

Dashboard/report card includes: bugs considered, candidates ranked, reproductions created, regressions created, patches planned, patches attempted, patches successful, rollbacks triggered, rollback quality, tests added, confidence average, highest risk touched, manual review required, next safe action.

Repair narrative sections: what broke, how reproduced, what changed, why fix is safe, what tests prove it, how to roll back, remaining concerns.

Commands: self-heal dashboard; self-heal report --last; self-heal narrative --patch <patch_id>.

Read-only. No patching. Redacted summaries only.
<<<PROMPT_END id="SELFHEAL-13">>

<<<PROMPT_START id="SELFHEAL-14" order="14">>
title: QA sandbox and canonical runtime integration
category: self_improvement
risk_level: MEDIUM
approval_gate: false
depends_on: ["SELFHEAL-13"]
status: queued
PROMPT:
Integrate self-heal with QA sandbox and canonical runtime where available.

Create docs/self_heal/QA_SANDBOX_INTEGRATION.md, docs/self_heal/CANONICAL_RUNTIME_INTEGRATION.md, agent/self_heal/integrations.py, and tests/self_heal/test_self_heal_integrations.py.

QA integration: consume QA run failures, create candidates from failed command runs, link repro command, create regression, propose patch plan.

Canonical runtime integration: record self_heal_run_id if canonical runtime exists, active patch id, checkpoint id, rollback capsule id, approval id, audit ids, status, resume command.

Rules: degrade gracefully if QA/canonical runtime modules do not exist; no background jobs; no automatic patching; no personal data; no commits/pushes.
<<<PROMPT_END id="SELFHEAL-14">>

<<<PROMPT_START id="SELFHEAL-15" order="15">>
title: Self-healing release gate
category: release_gate
risk_level: LOW
approval_gate: false
depends_on: ["SELFHEAL-14"]
status: queued
PROMPT:
Run self-healing release gate.

Run full test suite if practical, startup policy validation, capability manifest validation, command registry validation, prompt tracker validation if available, self_heal unit tests, invariants, safety lint fixture tests, rollback capsule tests, worktree dry-run tests, canary safe check, dashboard/report smoke.

Verify: no patching by default; recovery capsules exist before patches; worktree mode is dry-run/safe by default; no HIGH/CRITICAL/personal-data commands run; safety lints block policy/audit/approval weakening; rollback verification works on fixtures; flaky detector bounded; bisect plan-only; patch queue records status; report cards/narratives generated; QA/canonical integration degrades gracefully; no commit/push happened.

Create docs/self_heal/SELF_HEALING_RELEASE_GATE.md and docs/self_heal/SELF_HEALING_MATURITY_REVIEW.md. Update tracking docs. No commit/push in this prompt.
<<<PROMPT_END id="SELFHEAL-15">>

<<<PROMPT_START id="SELFHEAL-16" order="16">>
title: Code review, Git review, safe commit, and optional push gate
category: git
risk_level: MEDIUM
approval_gate: true
depends_on: ["SELFHEAL-15"]
status: queued
PROMPT:
Run code review, git review, secret scan, safe commit plan, and optional commit/push gate for this major prompt pack.

Goal: Every major prompt pack should end with a Git review and optional safe commit/push. Commit/push only if explicitly authorized by the user/wrapper and all gates pass. Never force push.

Run: git branch --show-current; git status -sb; git status --short; git diff --stat; git log --oneline --decorate -5; git remote -v; git diff --check.

Inspect staged changes, unstaged changes, untracked files, generated reports/logs, data files, .env/token/OAuth/private key files, raw session/audit reports, prompt packs, docs/tests/source/config changes.

Run validations: full test suite if practical, startup policy validation, capability manifest validation, command registry validation, prompt tracker validation if available, secret scan / git preflight if available.

Best-effort secret scan patterns: API_KEY, SECRET, TOKEN, PASSWORD, PRIVATE KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, SERPAPI_API_KEY, WEATHERAPI_API_KEY, BRAVE_SEARCH_API_KEY, REDDIT_CLIENT_SECRET, TELEGRAM_BOT_TOKEN, GMAIL_CLIENT_SECRET, GITHUB_TOKEN, ghp_, github_pat_, sk-, ya29., AIza, xoxb-, BEGIN RSA PRIVATE KEY, BEGIN OPENSSH PRIVATE KEY.

Rules: do not print secret values; do not commit/push if likely secrets found; do not use git add . blindly; do not stage .env, token files, OAuth caches, private keys, raw logs/reports, .venv, __pycache__, .pytest_cache, generated junk, or personal data; if tests fail, stop unless explicit user approval to commit known failing state; if remote missing, report setup instructions and stop; never force push.

Create/update docs/git/LAST_GIT_REVIEW.md and docs/git/SAFE_COMMIT_PLAN.md.

Final report: branch/remote/upstream status, last commit, dirty worktree summary, files safe to commit, files to exclude, suggested logical commit groups, secret scan result, tests/validations run, whether safe to commit, whether safe to push, exact recommended git commands, and blockers.

If explicit commit/push approval is not present: stop after report; do not commit; do not push.

If explicit commit approval is present: stage only reviewed safe files, commit with clear message, show commit hash.

If explicit push approval is also present: push current branch to upstream with regular git push, never force push.
<<<PROMPT_END id="SELFHEAL-16">>

<<<PROMPT_PACK_END>>>
