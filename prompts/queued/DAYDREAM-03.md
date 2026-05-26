---
prompt_id: DAYDREAM-03
pack_id: daydream-lab-idle-research-v1
title: Daydream budgets, modes, and automatic disabled-by-default config
category: daydream
risk_level: MEDIUM
approval_gate: false
depends_on: ["DAYDREAM-02"]
status: queued
order: 3
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

Build Daydream budgets, modes, and automatic disabled-by-default config.

Create:
- agent/daydream/config.py
- agent/daydream/budgets.py
- tests/daydream/test_daydream_config_budgets.py
- docs/daydream/DAYDREAM_BUDGETS.md
- docs/daydream/AUTOMATIC_DAYDREAM_DISABLED_BY_DEFAULT.md

Config defaults:
- DAYDREAM_ENABLED=false
- DAYDREAM_AUTO_IDLE_ENABLED=false
- DAYDREAM_MAX_RUNTIME_MINUTES=30
- DAYDREAM_MAX_SOURCES=20
- DAYDREAM_MAX_TOPICS=5
- DAYDREAM_MAX_COST_USD=0
- DAYDREAM_ALLOW_PAID_APIS=false
- DAYDREAM_ALLOW_PERSONAL_DATA=false
- DAYDREAM_ALLOW_MEMORY_WRITE=false
- DAYDREAM_ALLOW_MODEL_DOWNLOADS=false
- DAYDREAM_ALLOW_CODE_CHANGES=false
- DAYDREAM_ALLOW_COMMIT_PUSH=false
- DAYDREAM_ALLOW_LIVE_PROVIDERS=false
- DAYDREAM_SERENDIPITY_PERCENT=20
- DAYDREAM_INTEREST_PERCENT=80

Modes:
- manual
- manual_safe
- idle_dry_run
- idle_safe
- scheduled_preview
- overnight_plan
- auto_disabled

Commands:
- daydream status
- daydream budget
- daydream auto-status
- daydream auto-enable --dry-run
- daydream auto-disable --dry-run

No actual auto-enable or scheduler install.
