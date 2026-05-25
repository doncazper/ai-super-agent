<<<PROMPT_PACK_START>>>
pack_id: agent-dna-cloneability-v1
pack_title: Agent DNA, Clone Blueprint, and Build Provenance
created_by: user
mode: controlled_batch_until_blocked
default_execution: sequential
requires_sdlc: true
requires_prompt_ledger: true
requires_feature_maturity_update: true
priority: high

pack_summary:
  - This prompt pack creates the cloneable DNA of the AI Super Agent.
  - It documents the project's mission, architectural invariants, safety philosophy, clone blueprint, build history, reconstructed prompt archive, and future rewrite/migration guidance.
  - It is docs-first and should not change runtime behavior.
  - It should be run as a controlled batch unless tests fail, docs validation fails, an approval gate is hit, or requirements are ambiguous.
  - Preserve all details.
  - Do not summarize away historical or architectural intent.
  - Do not claim reconstructed prompts are exact originals unless there is evidence.

global_rules:
  - Follow SPEC.md.
  - Follow docs/SDLC.md.
  - Follow AGENTS.md.
  - Follow the safety-first architecture.
  - Do not weaken policy.
  - Do not bypass ToolBroker.
  - Do not bypass PolicyEngine.
  - Do not bypass PermissionManager.
  - Do not bypass ApprovalManager.
  - Do not bypass AuditLogger.
  - Do not enable personal-data tools by default.
  - Do not add runtime features in this pack unless explicitly needed for docs validation.
  - Do not rewrite source code.
  - Do not mark reconstructed prompt packs as exact originals without evidence.
  - Update CHANGELOG.md.
  - Update docs/PROJECT_STATE.md.
  - Update docs/FEATURE_REGISTRY.md.
  - Update docs/FEATURE_MATURITY.md.
  - Update docs/FEATURE_ROADMAP.md if status/order changes.
  - Update docs/COMMAND_REGISTRY.md if commands/docs commands are added or changed.
  - Update docs/COMPLETION_REPORT.md.
  - Update docs/PROMPT_LEDGER.md and docs/PROMPT_QUEUE.md if prompt tracking exists.

stop_conditions:
  - failing_tests_not_safely_fixable
  - docs_validation_failure_not_safely_fixable
  - approval_gate
  - ambiguous_requirements
  - runtime_behavior_change_required
  - personal_data_access_required
  - package_install_required
  - security_policy_change_required

expected_prompt_ids:
  - DNA-01
  - DNA-02
  - DNA-03
  - DNA-04
  - DNA-05
  - DNA-06

<<<PROMPT_START id="DNA-01" order="1">>
title: Agent DNA foundation
category: docs
risk_level: LOW
approval_gate: false
depends_on: []
status: queued

PROMPT:
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
<<<PROMPT_END id="DNA-01">>

<<<PROMPT_START id="DNA-02" order="2">>
title: Clone blueprint and migration guide
category: docs
risk_level: LOW
approval_gate: false
depends_on: ["DNA-01"]
status: queued

PROMPT:
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
<<<PROMPT_END id="DNA-02">>

<<<PROMPT_START id="DNA-03" order="3">>
title: Build history and provenance
category: docs
risk_level: LOW
approval_gate: false
depends_on: ["DNA-02"]
status: queued

PROMPT:
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
<<<PROMPT_END id="DNA-03">>

<<<PROMPT_START id="DNA-04" order="4">>
title: Reconstructed prompt pack archive
category: prompt_tracking
risk_level: LOW
approval_gate: false
depends_on: ["DNA-03"]
status: queued

PROMPT:
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
<<<PROMPT_END id="DNA-04">>

<<<PROMPT_START id="DNA-05" order="5">>
title: SPEC / SDLC / AGENTS alignment
category: docs
risk_level: LOW
approval_gate: false
depends_on: ["DNA-04"]
status: queued

PROMPT:
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
<<<PROMPT_END id="DNA-05">>

<<<PROMPT_START id="DNA-06" order="6">>
title: Cloneability release gate
category: release_gate
risk_level: LOW
approval_gate: false
depends_on: ["DNA-05"]
status: queued

PROMPT:
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
<<<PROMPT_END id="DNA-06">>

<<<PROMPT_PACK_END>>>
