---
prompt_id: DNA-04
pack_id: agent-dna-cloneability-v1
title: Reconstructed prompt pack archive
category: prompt_tracking
risk_level: LOW
approval_gate: false
depends_on: ["DNA-03"]
status: completed
order: 4
created_at: 2026-05-23T22:05:13+00:00
imported_at: 2026-05-23T22:05:13+00:00
source_pack: prompts/packs/agent-dna-cloneability-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-23T22:13:55+00:00
completed_at: 2026-05-23T22:13:56+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: tests/test_feature_maturity_docs.py: 11 passed
docs_updated: docs/RECONSTRUCTED_PROMPT_PACKS.md; docs/templates/reconstructed_prompt_pack_template.md; prompts/packs/reconstructed/*.reconstructed.promptpack.md
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
notes: Created 11 reconstructed packs, all labeled reconstructed and exact_original false with caveats.
---

# Prompt

You are Codex working in this repo.

Task:
Create the Reconstructed Prompt Pack Archive.

Goal:
Create a best-effort historical archive of major prompt packs that were used or designed before prompt packs became formal. These should preserve build intent for future cloning and rewrites.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- docs/AGENT_DNA.md
- docs/CLONE_BLUEPRINT.md
- docs/BUILD_HISTORY.md
- docs/BUILD_PROVENANCE.md
- CHANGELOG.md
- docs/COMPLETION_REPORT.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/FEATURE_ROADMAP.md
- docs/PROMPT_LEDGER.md, if present
- docs/PROMPT_QUEUE.md, if present
- docs/PROMPT_AUDIT.md, if present
- prompts/packs/, if present
- git log, if useful

Scope:
- Documentation and prompt archive only.
- Reconstruct prior prompt packs as best-effort historical artifacts.
- Do not run reconstructed prompts.
- Do not change runtime behavior.

Non-goals:
- Do not claim reconstructed prompt packs are exact originals unless evidence proves it.
- Do not fabricate historical commits or completion status.
- Do not mark reconstructed packs as executed.
- Do not add runtime features.

Create:
- docs/RECONSTRUCTED_PROMPT_PACKS.md
- docs/templates/reconstructed_prompt_pack_template.md
- prompts/packs/reconstructed/

RECONSTRUCTED_PROMPT_PACKS.md must explain:
1. What a reconstructed prompt pack is.
2. Difference between original and reconstructed packs.
3. Evidence requirements.
4. Naming convention.
5. Confidence levels:
   - low
   - medium
   - high
6. Caveat language.
7. How to use reconstructed packs.
8. How to avoid confusing reconstructed packs with executed prompts.
9. How to promote reconstructed prompts into new real prompt packs if needed.

Create best-effort reconstructed prompt pack files under:
prompts/packs/reconstructed/

At minimum create:
1. baseline-safety-control-plane.reconstructed.promptpack.md
2. core-runtime.reconstructed.promptpack.md
3. weather-connector.reconstructed.promptpack.md
4. web-internet-access.reconstructed.promptpack.md
5. news-intelligence.reconstructed.promptpack.md
6. reddit-forum-intelligence.reconstructed.promptpack.md
7. prompt-tracker-maturity.reconstructed.promptpack.md
8. command-registry-qa.reconstructed.promptpack.md
9. apple-messaging-bridge.reconstructed.promptpack.md
10. cross-platform-bridge.reconstructed.promptpack.md
11. docs-user-guide-maintenance.reconstructed.promptpack.md

Every reconstructed prompt pack must include metadata:
- pack_id
- title
- status: reconstructed
- exact_original: false unless evidence proves otherwise
- reconstruction_sources
- related_features
- related_docs
- related_commits, if known
- confidence: low | medium | high
- caveats
- prompt_ids
- prompt bodies or summarized prompt bodies, clearly labeled

If exact prompt text is not available:
- mark each prompt as reconstructed_summary
- do not claim it is verbatim
- include enough detail to rebuild the intent
- link to evidence docs

If exact prompt text is available from prompts/packs or docs:
- mark exact_original: true only for that exact prompt/pack
- cite the source path

Update:
- docs/PROMPT_LEDGER.md with reconstructed packs clearly marked reconstructed/not executed.
- docs/PROMPT_QUEUE.md only if the user wants to queue a reconstructed pack later; do not auto-queue by default.
- docs/PROMPT_AUDIT.md with reconstruction summary.
- docs/FEATURE_MATURITY.md.
- docs/PROJECT_STATE.md.
- docs/COMPLETION_REPORT.md.
- CHANGELOG.md.
- README.md with a link to RECONSTRUCTED_PROMPT_PACKS.md.

Validation:
If practical, validate:
- reconstructed folder exists.
- each reconstructed file includes status: reconstructed.
- each reconstructed file includes exact_original.
- each reconstructed file includes confidence and caveats.
- no reconstructed file is marked active/completed unless evidence exists.

Run relevant validations/tests.

Final report:
- reconstructed packs created
- confidence level for each pack
- exact originals found, if any
- caveats
- tests/validation run
- next recommended prompt
