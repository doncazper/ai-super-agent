---
prompt_id: DAYDREAM-21
pack_id: daydream-lab-idle-research-v1
title: Daydream dogfood and eval suite
category: daydream
risk_level: LOW
approval_gate: false
depends_on: ["DAYDREAM-20"]
status: queued
order: 21
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

Build Daydream dogfood and eval suite.

Create:
- dogfood_suites/daydream_core.yaml
- dogfood_suites/daydream_idle.yaml
- dogfood_suites/daydream_interests.yaml
- dogfood_suites/daydream_prompt_pack_incubator.yaml
- dogfood_suites/daydream_safety.yaml
- eval_cases/daydream/core.json
- tests/daydream/test_daydream_dogfood_eval.py
- docs/daydream/DAYDREAM_DOGFOOD_RUNBOOK.md

Eval checks:
- daydream status
- idle-status disabled by default
- idle-run dry-run does not research
- auto-enable dry-run does not enable
- interest add/mute/why fixture
- idea card generation
- risky idea classifier
- blocked idea classification
- journal/report read
- what-were-you-thinking summary
- promote to prompt-pack dry-run
- build-next shortlist
- no code changes
- no prompt-pack run
- no send/publish/buy/download/install
- no memory write
- no personal data
- no bypass

Commands:
- eval run --daydream
- eval report --daydream
- dogfood run daydream_core --session
- dogfood run daydream_idle --session
- dogfood run daydream_interests --session
- dogfood run daydream_prompt_pack_incubator --session
- dogfood run daydream_safety --session

Mock/fixture/local only.
