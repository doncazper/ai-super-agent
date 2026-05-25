---
prompt_id: DNA-01
pack_id: agent-dna-cloneability-v1
title: Agent DNA foundation
category: docs
risk_level: LOW
approval_gate: false
depends_on: []
status: completed
order: 1
created_at: 2026-05-23T22:05:13+00:00
imported_at: 2026-05-23T22:05:13+00:00
source_pack: prompts/packs/agent-dna-cloneability-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-23T22:05:25+00:00
completed_at: 2026-05-23T22:13:54+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: tests/test_feature_maturity_docs.py: 11 passed
docs_updated: docs/AGENT_DNA.md; docs/ARCHITECTURE_PRINCIPLES.md; README/AGENTS/SPEC/SDLC tracking updated
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
notes: DNA foundation completed as docs/provenance only; no runtime behavior changed.
---

# Prompt

You are Codex working in this repo.

Task:
Create the Agent DNA foundation.

Goal:
Create the central blueprint document that captures the identity, architecture, principles, and non-negotiables of this agent so it can be cloned, rewritten, ported to another model, or wrapped by native apps without losing its core design.

Before making changes, read:
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
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/RELEASE_CHECKLIST.md
- docs/PROMPT_LEDGER.md, if present
- docs/PROMPT_QUEUE.md, if present

Follow the mini-SDLC:
1. Confirm scope.
2. Confirm non-goals.
3. Define requirements.
4. Define risks and threat-model notes.
5. Implement docs only.
6. Add validation if practical.
7. Run tests/docs validation.
8. Update docs.
9. Update completion report.
10. Stop at approval gates.

Scope:
- Documentation only.
- Create AGENT_DNA.md and supporting architecture principle docs.
- Do not change runtime behavior.
- Do not add new tools/connectors.

Non-goals:
- Do not rewrite the agent.
- Do not add runtime features.
- Do not enable personal-data tools.
- Do not weaken policy.
- Do not bypass ToolBroker.
- Do not claim historical prompt packs are exact originals.

Create:
- docs/AGENT_DNA.md
- docs/ARCHITECTURE_PRINCIPLES.md

AGENT_DNA.md must include:
1. Mission in plain English.
2. What makes this agent different.
3. Safety-first, capabilities-second.
4. Python core as portable agent brain.
5. Native apps as bridges, not the brain.
6. CLI/manual mode must always remain usable.
7. ToolBroker-only execution.
8. PolicyEngine-enforced permissions.
9. PermissionManager and ApprovalManager responsibilities.
10. AuditLogger as append-only historical record.
11. Trust model for untrusted web/email/message/document/forum content.
12. Risk model for SAFE/LOW/MEDIUM/HIGH/CRITICAL/FORBIDDEN actions.
13. Personal-data selected-scope rules.
14. Memory rules.
15. Secret handling rules.
16. Self-improvement limits.
17. Prompt pack discipline.
18. Feature maturity discipline.
19. Command registry discipline.
20. Dogfood/session/bug/regression loop.
21. Cross-platform bridge philosophy.
22. What must survive a rewrite.
23. What must never be compromised.
24. How to evaluate if a future rewrite still has the same DNA.

ARCHITECTURE_PRINCIPLES.md must include:
1. Architectural invariants.
2. Allowed dependency directions.
3. Forbidden shortcuts.
4. ToolBroker/Policy/Audit invariants.
5. Lazy platform bridge rules.
6. Provider policy rules.
7. Untrusted content rules.
8. Approval and audit invariants.
9. Feature maturity rules.
10. Command registry rules.
11. Prompt pack rules.
12. Release-gate rules.
13. Anti-patterns to avoid.
14. Examples of acceptable changes.
15. Examples of changes that must stop and ask for approval.

Update:
- README.md with a short "Agent DNA" link.
- AGENTS.md with a rule that architectural changes must preserve docs/AGENT_DNA.md.
- docs/FEATURE_REGISTRY.md with "Agent DNA / Cloneability" as a docs/governance feature.
- docs/FEATURE_MATURITY.md with conservative maturity.
- docs/PROJECT_STATE.md.
- docs/COMPLETION_REPORT.md.
- CHANGELOG.md.

Validation:
If docs validation exists, add/check:
- docs/AGENT_DNA.md exists.
- docs/ARCHITECTURE_PRINCIPLES.md exists.
- README links to AGENT_DNA.md.
- AGENTS.md mentions AGENT_DNA.md.

Run:
- docs validation if present.
- full test suite if practical.
- startup policy validation.
- command registry validation if present.

Final report:
- files created
- files changed
- tests/validation run
- key DNA principles added
- known gaps
- next recommended prompt
