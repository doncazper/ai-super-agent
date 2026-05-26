---
prompt_id: DAYDREAM-01
pack_id: daydream-lab-idle-research-v1
title: Daydream Lab roadmap, philosophy, and safety policy
category: daydream
risk_level: LOW
approval_gate: false
depends_on: []
status: queued
order: 1
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

Create Daydream Lab roadmap, philosophy, and safety policy.

Before changing files, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- README.md
- CHANGELOG.md
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/FEATURE_ROADMAP.md
- docs/COMMAND_REGISTRY.md, if present
- docs/COMMAND_TEST_MATRIX.md, if present
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/RELEASE_CHECKLIST.md
- docs/runtime/, if present
- docs/memory_kernel/, if present
- docs/ai_ecosystem/, if present
- docs/authorized_scan/, if present
- docs/performance/, if present
- docs/qa/, if present

Create:
- docs/daydream/DAYDREAM_LAB_TRACK.md
- docs/daydream/DAYDREAM_PHILOSOPHY.md
- docs/daydream/DAYDREAM_SAFETY_POLICY.md
- docs/daydream/DAYDREAM_IDLE_POLICY.md
- docs/daydream/DAYDREAM_OUTPUTS.md
- docs/decisions/daydream_lab_idle_research.md

Define purpose:
- idle R&D
- curiosity engine
- product strategy
- user-interest radar
- trend/release watcher
- feature wishlist
- roadmap advisor
- prompt-pack incubator
- safe research journal

Define principle:
- wide imagination
- narrow execution
- transparent logs
- user-approved promotion
- no hidden background behavior

Define separation:
- dreams = imaginative/speculative thoughts
- recommendations = researched/ranked actionable suggestions
- prompt-pack candidates = ready-to-build drafts
- blocked/risky ideas = documented but not implemented

Define automatic idle-run:
- Supported as architecture, dry-run checks, and disabled-by-default controller.
- Not enabled by default.
- No LaunchAgent/cron/daemon install by default.
- No hidden background service.
- Explicit future user approval required to enable.

Planned commands:
- daydream status
- daydream run --safe
- daydream run --topic "<topic>"
- daydream idle-status
- daydream idle-run --dry-run
- daydream idle-run --safe
- daydream auto-status
- daydream auto-enable --dry-run
- daydream report --last
- daydream digest --quick
- daydream ideas --ranked
- daydream what-were-you-thinking
- daydream interests
- daydream interests add/mute/boost/why
- daydream sources
- daydream blocked-ideas
- daydream promote <idea_id> --to-prompt-pack --dry-run

No runtime daydream engine yet. Update trackers and validations.
