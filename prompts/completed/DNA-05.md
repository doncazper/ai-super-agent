---
prompt_id: DNA-05
pack_id: agent-dna-cloneability-v1
title: SPEC / SDLC / AGENTS alignment
category: docs
risk_level: LOW
approval_gate: false
depends_on: ["DNA-04"]
status: completed
order: 5
created_at: 2026-05-23T22:05:13+00:00
imported_at: 2026-05-23T22:05:13+00:00
source_pack: prompts/packs/agent-dna-cloneability-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-23T22:13:56+00:00
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
docs_updated: README.md; SPEC.md; docs/SDLC.md; AGENTS.md
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
notes: Source-of-truth docs aligned with cloneability rules.
---

# Prompt

You are Codex working in this repo.

Task:
Align SPEC.md, docs/SDLC.md, and AGENTS.md with the new Agent DNA and cloneability system.

Goal:
Make cloneability, prompt-pack discipline, and preservation of project DNA part of the formal operating rules without bloating the spec.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- docs/AGENT_DNA.md
- docs/CLONE_BLUEPRINT.md
- docs/ARCHITECTURE_PRINCIPLES.md
- docs/RECONSTRUCTED_PROMPT_PACKS.md
- docs/BUILD_HISTORY.md
- docs/BUILD_PROVENANCE.md
- docs/PROJECT_STATE.md
- docs/FEATURE_MATURITY.md
- docs/PROMPT_LEDGER.md, if present
- docs/PROMPT_QUEUE.md, if present

Scope:
- Documentation alignment only.
- Keep SPEC concise.
- Keep SDLC process-oriented.
- Keep AGENTS operational.

Non-goals:
- Do not rewrite SPEC into a giant manual.
- Do not change runtime behavior.
- Do not add features.
- Do not weaken safety rules.

Update SPEC.md:
Add a short section, such as "Cloneability and Portability":

The project must remain cloneable and portable. Its core design, safety model, prompt history, feature maturity, command registry, and SDLC artifacts should allow the agent to be rebuilt, ported to another model, or wrapped by native Mac/iOS/Windows frontends without losing its safety-first architecture.

Also ensure SPEC references:
- ToolBroker-only execution
- policy/approval/audit invariants
- untrusted content isolation
- personal-data disabled-by-default
- cloneability as a final acceptance principle

Update docs/SDLC.md:
Add a short section:
"Build Provenance and Cloneability"

It should require:
- major feature tracks use prompt packs
- major build decisions get decision records
- major features update feature maturity
- commands update command registry
- prompt packs are stored or reconstructed with clear status
- release gates verify docs/tracking
- rewrites start from CLONE_BLUEPRINT.md and AGENT_DNA.md

Update AGENTS.md:
Add permanent rules:
- Before architecture changes, read docs/AGENT_DNA.md.
- If a change violates AGENT_DNA.md, stop and ask.
- For feature tracks with 3+ prompts, use a prompt pack.
- Store original prompt packs under prompts/packs/.
- Mark reconstructed packs as reconstructed.
- Do not claim reconstructed prompts are exact originals without evidence.
- When rewriting or porting the agent, start with docs/CLONE_BLUEPRINT.md.
- Preserve CLI/manual mode.
- Preserve ToolBroker/Policy/Approval/Audit invariants.
- Preserve command registry and feature maturity tracking.
- Final reports should mention whether Agent DNA was affected.

Update:
- README.md with "Cloneability and Agent DNA" links.
- docs/PROJECT_STATE.md.
- docs/FEATURE_REGISTRY.md.
- docs/FEATURE_MATURITY.md.
- docs/COMPLETION_REPORT.md.
- CHANGELOG.md.

Validation:
If practical:
- SPEC references cloneability.
- SDLC references build provenance.
- AGENTS references AGENT_DNA.
- README links AGENT_DNA and CLONE_BLUEPRINT.

Run relevant validations/tests.

Final report:
- files changed
- alignment summary
- tests/validation run
- next recommended prompt
