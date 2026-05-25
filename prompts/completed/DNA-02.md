---
prompt_id: DNA-02
pack_id: agent-dna-cloneability-v1
title: Clone blueprint and migration guide
category: docs
risk_level: LOW
approval_gate: false
depends_on: ["DNA-01"]
status: completed
order: 2
created_at: 2026-05-23T22:05:13+00:00
imported_at: 2026-05-23T22:05:13+00:00
source_pack: prompts/packs/agent-dna-cloneability-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-23T22:13:54+00:00
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
docs_updated: docs/CLONE_BLUEPRINT.md; docs/MODEL_MIGRATION_GUIDE.md; docs/PLATFORM_MIGRATION_GUIDE.md; docs/REWRITE_CHECKLIST.md
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
notes: Clone blueprint and migration guides completed; no runtime behavior changed.
---

# Prompt

You are Codex working in this repo.

Task:
Create the Clone Blueprint and migration guides.

Goal:
Create documentation that explains how to rebuild, rewrite, port, or migrate the agent to a new model, new platform, new frontend, or new codebase while preserving its DNA.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- docs/AGENT_DNA.md
- docs/ARCHITECTURE_PRINCIPLES.md
- README.md
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/FEATURE_ROADMAP.md
- docs/COMMAND_REGISTRY.md, if present
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/RELEASE_CHECKLIST.md

Scope:
- Documentation only.
- Create clone and migration guides.
- Do not change runtime behavior.

Non-goals:
- Do not rewrite code.
- Do not add runtime features.
- Do not implement platform bridges.
- Do not enable personal-data tools.
- Do not weaken policy.

Create:
- docs/CLONE_BLUEPRINT.md
- docs/MODEL_MIGRATION_GUIDE.md
- docs/PLATFORM_MIGRATION_GUIDE.md
- docs/REWRITE_CHECKLIST.md

CLONE_BLUEPRINT.md must include:
1. How to rebuild the agent from scratch.
2. Required documents to read first.
3. Minimum viable architecture.
4. Required modules:
   - core
   - safety
   - tools
   - memory
   - workflows
   - config
   - docs/tracking
5. Required safety systems:
   - ToolBroker
   - PolicyEngine
   - PermissionManager
   - ApprovalManager
   - AuditLogger
   - SecretRedactor
   - Trust/Risk models
6. Required tracking systems:
   - PROJECT_STATE
   - FEATURE_REGISTRY
   - FEATURE_MATURITY
   - COMMAND_REGISTRY
   - PROMPT_LEDGER
   - CHANGELOG
   - COMPLETION_REPORT
7. Minimum test requirements.
8. Minimum docs requirements.
9. Release gate requirements.
10. Clone validation checklist.
11. How to decide whether a cloned implementation is equivalent enough.

MODEL_MIGRATION_GUIDE.md must include:
1. How to migrate from Qwopus/LM Studio to another local or API model.
2. What must not change when switching models.
3. No-tools chat preservation.
4. Tool-call protocol compatibility.
5. Prompt contamination risks.
6. Router and tool-schema tests.
7. Model-specific evals.
8. Regression suite required before switching default model.
9. How to compare answer quality.
10. How to roll back.

PLATFORM_MIGRATION_GUIDE.md must include:
1. Python core remains portable.
2. Platform bridges are optional.
3. macOS bridge philosophy.
4. iOS companion philosophy.
5. Windows bridge philosophy.
6. Web/local dashboard philosophy.
7. Platform capability registry.
8. What belongs in core vs bridge.
9. Lazy loading and overhead rules.
10. Platform-specific permission boundaries.
11. How to add a new platform bridge safely.

REWRITE_CHECKLIST.md must include:
- preserve ToolBroker-only execution
- preserve PolicyEngine checks
- preserve ApprovalManager behavior
- preserve AuditLogger
- preserve unknown capability denial
- preserve untrusted content isolation
- preserve personal-data disabled-by-default
- preserve CRITICAL per-action approval
- preserve command registry
- preserve feature maturity
- preserve prompt ledger
- preserve dogfood/eval/release gates
- pass clone validation tests

Update:
- README.md.
- AGENTS.md.
- docs/FEATURE_REGISTRY.md.
- docs/FEATURE_MATURITY.md.
- docs/PROJECT_STATE.md.
- docs/COMPLETION_REPORT.md.
- CHANGELOG.md.

Validation:
If practical, add docs validation for:
- CLONE_BLUEPRINT exists.
- MODEL_MIGRATION_GUIDE exists.
- PLATFORM_MIGRATION_GUIDE exists.
- REWRITE_CHECKLIST exists.
- README links to CLONE_BLUEPRINT.

Run relevant validations/tests.

Final report:
- files created
- migration docs summary
- tests/validation run
- next recommended prompt
