---
prompt_id: DNA-03
pack_id: agent-dna-cloneability-v1
title: Build history and provenance
category: docs
risk_level: LOW
approval_gate: false
depends_on: ["DNA-02"]
status: completed
order: 3
created_at: 2026-05-23T22:05:13+00:00
imported_at: 2026-05-23T22:05:13+00:00
source_pack: prompts/packs/agent-dna-cloneability-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-23T22:13:55+00:00
completed_at: 2026-05-23T22:13:55+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: tests/test_feature_maturity_docs.py: 11 passed
docs_updated: docs/BUILD_HISTORY.md; docs/BUILD_PROVENANCE.md; docs/DECISION_INDEX.md
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
notes: Build history/provenance completed with conservative evidence hierarchy.
---

# Prompt

You are Codex working in this repo.

Task:
Create Build History and Build Provenance documentation.

Goal:
Create a narrative and evidence-based record of how the agent was built, so future rewrites and model migrations can understand why the architecture evolved the way it did.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- CHANGELOG.md
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/FEATURE_ROADMAP.md
- docs/COMPLETION_REPORT.md
- docs/PROMPT_LEDGER.md, if present
- docs/PROMPT_QUEUE.md, if present
- docs/PROMPT_AUDIT.md, if present
- docs/COMMAND_REGISTRY.md, if present
- git log, if useful

Scope:
- Documentation only.
- Evidence-based build history.
- Do not change runtime behavior.

Non-goals:
- Do not invent exact historical details.
- Do not claim reconstructed prompts are exact originals.
- Do not change feature status without evidence.
- Do not mark features mature without evidence.

Create:
- docs/BUILD_HISTORY.md
- docs/BUILD_PROVENANCE.md
- docs/DECISION_INDEX.md

BUILD_HISTORY.md must include:
1. Origin and motivation.
2. Initial LM Studio/Qwopus harness problem.
3. Safety-first foundation.
4. Baseline M0-M11.
5. Weather as first mature connector pattern.
6. Web/internet access track.
7. News intelligence track.
8. Reddit/forum intelligence track.
9. Native skills track.
10. Prompt tracker / PromptOps track.
11. Command registry / manual QA track.
12. Dogfood/session/bug/regression track.
13. Apple messaging/lead response track.
14. Cross-platform app bridge track.
15. User guide/docs automation track.
16. Release hardening loops.
17. What has become core DNA.
18. What is still experimental or planned.

BUILD_PROVENANCE.md must include:
- how to prove a feature exists
- what counts as evidence
- source-of-truth hierarchy:
  1. code
  2. tests
  3. command registry
  4. completion report
  5. changelog
  6. feature registry
  7. feature maturity
  8. prompt ledger
  9. roadmap
- how to distinguish implemented vs planned/stubbed
- how to distinguish original vs reconstructed prompt packs
- how to avoid overclaiming

DECISION_INDEX.md must include a table of major decision records:
- decision file
- topic
- status
- date/commit if known
- related features
- active/superseded
- next review needed

Update:
- README.md with Build History link.
- docs/FEATURE_REGISTRY.md.
- docs/FEATURE_MATURITY.md.
- docs/PROJECT_STATE.md.
- docs/COMPLETION_REPORT.md.
- CHANGELOG.md.

Validation:
If practical, add docs validation for these files and links.

Run relevant validations/tests.

Final report:
- files created
- key historical sections
- evidence gaps
- tests/validation run
- next recommended prompt
