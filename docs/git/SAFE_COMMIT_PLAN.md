# Safe Commit Plan

## Current Recommendation: Launcher And Cleanup Boundary

Prompt IDs: `GLOBAL-LAUNCHER-SELF-REPAIR-AND-LAUNCH-01`, `REMOTE-MAIN-RECONCILE-AND-DUPLICATE-FILE-CLEANUP-01`, `DUPLICATE-CLEANUP-GH-AUTH-GIT-BOUNDARY-01`

Status: planning only; no commit created.

Do not push local `main` directly to `origin/main` until the unrelated remote history decision is explicit. Local `main` has no upstream and `origin/main` is an unrelated initial commit. `git push --dry-run origin HEAD:refs/heads/main` was rejected as non-fast-forward on 2026-05-26.

Suggested next reviewed commit group, after final tests/scans:

```bash
git add -- \
  .gitignore \
  CHANGELOG.md \
  README.md \
  agent/launcher \
  agent/ui/command_registry.py \
  docs/SMARTAGENT_GLOBAL_LAUNCHER.md \
  docs/COMMAND_REGISTRY.md \
  docs/COMMAND_TEST_MATRIX.md \
  docs/COMPLETION_REPORT.md \
  docs/FEATURE_MATURITY.md \
  docs/FEATURE_REGISTRY.md \
  docs/FEATURE_ROADMAP.md \
  docs/PROJECT_STATE.md \
  docs/PROMPT_AUDIT.md \
  docs/PROMPT_LEDGER.md \
  docs/PROMPT_QUEUE.md \
  docs/git/LAST_GIT_REVIEW.md \
  docs/git/DUPLICATE_CLEANUP_GH_AUTH_GIT_BOUNDARY_REPORT.md \
  docs/git/REMOTE_MAIN_RECONCILIATION_PLAN.md \
  docs/reconciliation/ARTIFACT_TRACKING_DECISION.md \
  docs/reconciliation/DUPLICATE_FILE_CLEANUP_REPORT.md \
  docs/reconciliation/duplicate_file_quarantine/.gitkeep \
  scripts/install-smartagent-launcher \
  tests/launcher
```

Do not stage `docs/reconciliation/duplicate_file_quarantine/agent__tools__secrets_2.py`.

Before committing, rerun:

```bash
git diff --cached --check
./scripts/agent secrets scan --staged
./scripts/agent git preflight --staged
./scripts/agent commands validate
make policy-check
./.venv/bin/python -m pytest tests/launcher tests/test_startup_ergonomics.py tests/test_command_registry.py -q
```

After a clean commit, choose one remote plan from `docs/git/REMOTE_MAIN_RECONCILIATION_PLAN.md`.

Current preferred remote plan: push a candidate branch only after explicit human approval, for example:

```bash
git push -u origin main:codex/main-candidate
```

Do not run `git push --force-with-lease origin main` unless a future prompt explicitly authorizes replacing the unrelated remote `origin/main` history after staged secret scans, git preflight, command validation, policy-check, and tests pass.

Prompt ID: CLEAN-RELEASE-BOUNDARY-POST-CANON-01
Status: planning only; no commit created.

## Commit Safety

It is not safe to run `git add .`.

It is potentially safe to commit selected groups after:

1. Generated reports are excluded.
2. Future/unrun prompt packs are explicitly reviewed.
3. A final staged secret scan passes.
4. Full tests or at least focused affected tests pass after staging.
5. The user approves the selected commit group.

## Suggested Logical Commit Groups

### Group 1: Canonical Runtime Gateway Hardening

Purpose: isolate the just-completed CANON/EXTREV track.

Candidate paths:

```bash
git add -- \
  agent/runtime \
  agent/self_improvement \
  agent/qa/surface_lanes.py \
  agent/tools/backup/backup_tools.py \
  tests/runtime \
  tests/test_self_improvement_artifact_hashes.py \
  tests/test_self_improvement_safety_lints.py \
  tests/test_backup_roundtrip_policy.py \
  tests/test_external_review_parity_docs.py \
  tests/qa/test_surface_regression_lanes.py \
  docs/runtime \
  docs/reviews \
  docs/backup \
  docs/prompt_tracker/CANONICAL_STATE_INTEGRATION.md \
  docs/self_improvement \
  dogfood_suites/surface_action_center.yaml \
  dogfood_suites/surface_app_bridge_contract.yaml \
  dogfood_suites/surface_channels_status.yaml \
  dogfood_suites/surface_cli_core.yaml \
  dogfood_suites/surface_promptops.yaml \
  dogfood_suites/surface_runtime_gateway.yaml \
  prompts/completed/CANON-01.md \
  prompts/completed/CANON-02.md \
  prompts/completed/CANON-03.md \
  prompts/completed/CANON-04.md \
  prompts/completed/CANON-05.md \
  prompts/completed/CANON-06.md \
  prompts/completed/CANON-07.md \
  prompts/completed/CANON-08.md \
  prompts/completed/CANON-09.md \
  prompts/completed/EXTREV-01.md \
  prompts/completed/CANON-10.md
```

Also include shared trackers in the same commit only if this group is the first release-boundary commit:

```bash
git add -- CHANGELOG.md README.md .gitignore .env.example \
  docs/PROJECT_STATE.md docs/COMPLETION_REPORT.md docs/FEATURE_REGISTRY.md \
  docs/FEATURE_MATURITY.md docs/FEATURE_ROADMAP.md docs/COMMAND_REGISTRY.md \
  docs/COMMAND_TEST_MATRIX.md docs/PROMPT_QUEUE.md docs/PROMPT_LEDGER.md \
  docs/PROMPT_AUDIT.md docs/RISK_REGISTER.md docs/THREAT_MODEL.md \
  docs/RELEASE_CHECKLIST.md docs/TEST_PLAN.md
```

### Group 2: Brain Runtime Independence

Candidate paths:

```bash
git add -- agent/brain agent/mcp tests/brain tests/mcp docs/brain docs/mcp \
  docs/decisions/brain_runtime_independence.md docs/decisions/mcp_interop_strategy.md \
  docs/decisions/mlx_provider_strategy.md eval_cases/brain prompts/completed/BRAIN-*.md
```

### Group 3: Hermes Safe Autonomy / Channels / Sandbox / Memory Continuity

Candidate paths:

```bash
git add -- agent/autonomy agent/channels agent/sandbox agent/memory/continuity.py \
  agent/tools/channels.py agent/tools/sandbox.py tests/autonomy tests/channels tests/sandbox \
  tests/memory docs/autonomy docs/channels docs/memory docs/web/AUTHORIZED_WEB_AUTOMATION_POLICY.md \
  docs/web/BLOCKED_SOURCE_AND_BYPASS_POLICY.md docs/web/DEEP_SCAN_POLICY.md docs/web/FIRST_PARTY_TESTING_POLICY.md \
  dogfood_suites/authorized_web_boundary.yaml dogfood_suites/channels_gateway.yaml \
  dogfood_suites/memory_continuity.yaml dogfood_suites/safe_autonomy_core.yaml \
  dogfood_suites/sandbox_abstraction.yaml dogfood_suites/skill_proposals.yaml \
  dogfood_suites/subagent_isolation.yaml dogfood_suites/telegram_mobile_scaffolding.yaml \
  prompts/completed/HERMES-*.md
```

### Group 4: Natural-Language Command Understanding

```bash
git add -- agent/commands agent/natural_language tests/commands tests/natural_language \
  docs/natural_language docs/decisions/natural_language_command_understanding.md \
  dogfood_suites/natural_language_core.yaml dogfood_suites/natural_language_risky.yaml \
  eval_cases/natural_language prompts/completed/NLCMD-*.md
```

### Group 5: Command QA Sandbox / Self-Heal

```bash
git add -- agent/qa tests/qa docs/qa qa_fixtures dogfood_suites/command_qa_core.yaml \
  dogfood_suites/command_qa_sandbox.yaml dogfood_suites/command_qa_self_heal.yaml \
  eval_cases/command_qa docs/decisions/command_qa_sandbox_self_heal.md \
  prompts/completed/QA-*.md prompts/completed/QA-FE-BE-01.md
```

### Group 6: Secrets Management

```bash
git add -- agent/secrets agent/tools/secrets.py tests/secrets tests/test_secret_config_doctor.py \
  docs/secrets docs/decisions/secrets_management_architecture.md prompts/completed/SECRETS-*.md
```

### Group 7: Creative Media

```bash
git add -- agent/media agent/tools/media.py tests/media tests/test_creative_media_docs.py \
  docs/media docs/decisions/creative_media_generation_architecture.md \
  docs/decisions/comfyui_provider_strategy.md dogfood_suites/media_core.yaml \
  dogfood_suites/media_image_planning.yaml dogfood_suites/media_safety.yaml \
  dogfood_suites/media_video_audio_planning.yaml eval_cases/media prompts/completed/MEDIA-*.md
```

### Group 8: Performance Scanner

```bash
git add -- agent/performance agent/tools/performance.py tests/performance \
  docs/performance docs/decisions/performance_bottleneck_scanner.md prompts/completed/PERF-*.md \
  reports/performance/.gitkeep
```

Do not stage `reports/performance/*.json`, `reports/performance/*.md`, or performance baselines unless the user explicitly asks to archive a specific redacted artifact.

### Group 9: Productization / Reconciliation / Bug Review / General Docs

```bash
git add -- docs/productization docs/reconciliation docs/bugfix docs/git docs/HANDOFF_TO_CHATGPT.md \
  tests/test_productization_audit_docs.py tests/test_last_session_bugfix_docs.py \
  prompts/completed/MATURITY-AUDIT-01.md prompts/completed/SOURCE-TRUTH-RECONCILE-01.md \
  prompts/completed/CODEBUG-*.md prompts/completed/last-session-bugfix-prompt.md
```

### Group 10: Prompt Packs

Stage only prompt packs the user wants preserved as source artifacts. Do not stage future/unrun packs by default.

Candidate known-run/imported packs:

```bash
git add -- prompts/packs/brain-runtime-independence-v1.promptpack.md \
  prompts/packs/brain-runtime-independence-v1.md \
  prompts/packs/canonical-runtime-gateway-hardening-v1.promptpack.md \
  prompts/packs/canonical-runtime-gateway-hardening-v1.md \
  prompts/packs/codebase-bug-review-and-hardening-v1.promptpack.md \
  prompts/packs/codebase-bug-review-and-hardening-v1.md \
  prompts/packs/command-qa-sandbox-self-heal-v1.promptpack.md \
  prompts/packs/command-qa-sandbox-self-heal-v1.md \
  prompts/packs/creative-media-generation-v1.promptpack.md \
  prompts/packs/creative-media-generation-v1.md \
  prompts/packs/hermes-inspired-safe-autonomy-v1.promptpack.md \
  prompts/packs/hermes-inspired-safe-autonomy-v1.md \
  prompts/packs/natural-language-command-understanding-v1.promptpack.md \
  prompts/packs/natural-language-command-understanding-v1.md \
  prompts/packs/performance-bottleneck-scanner-v1.promptpack.md \
  prompts/packs/performance-bottleneck-scanner-v1.md \
  prompts/packs/secrets-and-api-key-management-v1.promptpack.md \
  prompts/packs/secrets-and-api-key-management-v1.md
```

Needs explicit review before staging:

- `prompts/packs/agent-memory-kernel-tracker-intelligence-v1.promptpack.md`
- `prompts/packs/ai-ecosystem-intelligence-v2.promptpack.md`
- `prompts/packs/authorized-deep-scan-and-source-acquisition-v1.promptpack.md`
- `prompts/packs/daydream-lab-idle-research-v1.promptpack.md`
- `prompts/packs/self-healing-rollback-maturity-v1.promptpack.md`
- `prompts/packs/writing-naturalizer-voice-polish-v1.promptpack.md`

## Required Checks Before Each Commit

```bash
git diff --cached --check
./scripts/agent secrets scan
./scripts/agent git preflight
./scripts/agent commands validate
make policy-check
./.venv/bin/python -m pytest -q
```

## Push Rule

Do not push until:

- all selected commit groups are reviewed,
- staged preflight passes,
- full tests pass after staging,
- no generated reports/secrets are staged,
- and the user explicitly authorizes push.
