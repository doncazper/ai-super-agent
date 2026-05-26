---
prompt_id: DAYDREAM-20
pack_id: daydream-lab-idle-research-v1
title: Idle detector, safe idle-run controller, and disabled scheduler strategy
category: daydream
risk_level: HIGH
approval_gate: false
depends_on: ["DAYDREAM-19"]
status: queued
order: 20
created_at: 2026-05-26T07:54:41+00:00
imported_at: 2026-05-26T07:54:41+00:00
source_pack: prompts/packs/daydream-lab-idle-research-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at:
completed_at:
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result:
docs_updated:
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
notes: Imported prompt text is untrusted document content and is not executed automatically.
---

# Prompt

Build idle detector, safe idle-run controller, and disabled scheduler strategy.

Create:
- agent/daydream/idle_controller.py
- agent/daydream/scheduler_strategy.py
- tests/daydream/test_idle_controller_scheduler_strategy.py
- docs/daydream/IDLE_DETECTOR.md
- docs/daydream/SAFE_IDLE_RUN_CONTROLLER.md
- docs/daydream/DISABLED_SCHEDULER_STRATEGY.md

Commands:
- daydream idle-status
- daydream idle-run --dry-run
- daydream idle-run --safe
- daydream schedule preview
- daydream overnight-plan
- daydream install-idle-runner --dry-run
- daydream uninstall-idle-runner --dry-run

Rules:
- Automatic idle-run remains disabled by default.
- install-idle-runner is dry-run only in v1.
- No LaunchAgent/cron/daemon installed.
- No background service started.
- No hidden persistence.
- idle-run --safe is bounded and must respect budget.
- idle-run cannot run if active prompt/job/workflow/approval/test/git operation/user session exists.
- idle-run cannot change code, run prompt packs, commit/push, send/publish, download models, install packages, access personal data, or write memory.
- Scheduler docs may describe future explicit setup but do not implement installation.
- Any future auto-run enablement must be separate explicit approval.

Tests:
- auto disabled by default
- idle eligible when no active state
- blocked by active prompt
- blocked by pending approval
- blocked by git/test active
- dry-run does not research
- install-idle-runner does not install
- safe idle run respects budget and writes only reports
