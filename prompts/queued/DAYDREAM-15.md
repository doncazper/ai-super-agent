---
prompt_id: DAYDREAM-15
pack_id: daydream-lab-idle-research-v1
title: What have you been thinking about command
category: daydream
risk_level: LOW
approval_gate: false
depends_on: ["DAYDREAM-14"]
status: queued
order: 15
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

Build “what have you been thinking about?” command.

Create:
- agent/daydream/thought_summary.py
- tests/daydream/test_what_were_you_thinking.py
- docs/daydream/WHAT_HAVE_YOU_BEEN_THINKING_ABOUT.md

Behavior:
- Summarize recent daydream journal entries.
- Separate dreams, recommendations, blocked ideas, and prompt-pack candidates.
- Natural conversational summary.
- Include top 3-5 thoughts.
- Include why they matter.
- Include source/evidence IDs.
- Include what was not verified.
- Include “ask me if you want to build one” next steps.

Commands:
- daydream what-were-you-thinking
- daydream thoughts
- daydream thoughts --since <date>
- daydream thoughts --topic <topic>

No new research from summary commands. Read-only.
