---
prompt_id: DNA-06
pack_id: agent-dna-cloneability-v1
title: Cloneability release gate
category: release_gate
risk_level: LOW
approval_gate: false
depends_on: ["DNA-05"]
status: completed
order: 6
created_at: 2026-05-23T22:05:13+00:00
imported_at: 2026-05-23T22:05:13+00:00
source_pack: prompts/packs/agent-dna-cloneability-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-23T22:13:56+00:00
completed_at: 2026-05-23T22:13:57+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: tests/test_feature_maturity_docs.py: 11 passed; full validations pending final gate
docs_updated: docs/cloneability/CLONEABILITY_RELEASE_GATE.md; docs/cloneability/CLONEABILITY_MATURITY_REVIEW.md; tracking docs
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
notes: Cloneability release-gate docs completed; final validations will be run before final response.
---

# Prompt

You are Codex working in this repo.

Task:
Run Cloneability Release Gate.

Goal:
Validate that the Agent DNA / Clone Blueprint / Build Provenance system is complete enough to preserve the project's architecture in a rewrite, model migration, platform port, or future agent clone.

Scope:
- Validation.
- Documentation review.
- Maturity review.
- Small docs fixes only if needed.
- No runtime feature implementation.

Non-goals:
- Do not rewrite code.
- Do not add runtime features.
- Do not enable personal-data tools.
- Do not modify safety policy except documentation clarification.
- Do not run reconstructed prompts.

Run:
1. full test suite if practical
2. startup policy validation
3. capability manifest validation
4. docs validation if present
5. command registry validation if present
6. prompt tracker validation if present

Verify:
- docs/AGENT_DNA.md exists.
- docs/CLONE_BLUEPRINT.md exists.
- docs/ARCHITECTURE_PRINCIPLES.md exists.
- docs/BUILD_HISTORY.md exists.
- docs/BUILD_PROVENANCE.md exists.
- docs/RECONSTRUCTED_PROMPT_PACKS.md exists.
- docs/MODEL_MIGRATION_GUIDE.md exists.
- docs/PLATFORM_MIGRATION_GUIDE.md exists.
- docs/REWRITE_CHECKLIST.md exists.
- README links to AGENT_DNA and CLONE_BLUEPRINT.
- SPEC references cloneability.
- SDLC references build provenance.
- AGENTS requires preserving AGENT_DNA.
- reconstructed prompt packs are clearly marked reconstructed.
- reconstructed prompt packs are not marked exact_original unless evidence exists.
- prompt ledger/audit distinguish original vs reconstructed.
- feature maturity has an entry for Agent DNA / Cloneability.
- command registry mentions any new docs/validation commands, if added.
- no runtime behavior changed unexpectedly.

Create or update:
- docs/cloneability/CLONEABILITY_RELEASE_GATE.md
- docs/cloneability/CLONEABILITY_MATURITY_REVIEW.md

Maturity assessment:
- AGENT_DNA
- CLONE_BLUEPRINT
- ARCHITECTURE_PRINCIPLES
- BUILD_HISTORY
- BUILD_PROVENANCE
- RECONSTRUCTED_PROMPT_PACKS
- SPEC/SDLC/AGENTS alignment
- README docs map
- cloneability validation

Classify each:
- Idea
- Specified
- Scaffolded
- Implemented
- Tested
- Hardened
- Live-Validated
- User-Ready
- Mature Pattern

Update:
- CHANGELOG.md
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/FEATURE_ROADMAP.md
- docs/COMMAND_REGISTRY.md if relevant
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md if risk changed
- docs/THREAT_MODEL.md if threat surface changed
- docs/RELEASE_CHECKLIST.md

Final report:
- tests run/results
- validation results
- cloneability maturity score
- reconstructed packs created and confidence levels
- remaining blockers
- whether this system is ready to support a future rewrite/model migration/platform port
- next recommended feature track
