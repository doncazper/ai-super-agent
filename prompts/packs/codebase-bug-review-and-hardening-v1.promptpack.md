<<<PROMPT_PACK_START>>>
pack_id: codebase-bug-review-and-hardening-v1
pack_title: Full Codebase Bug Review and Hardening Track
created_by: user
mode: controlled_batch_until_blocked
default_execution: sequential
requires_sdlc: true
requires_prompt_ledger: true
requires_feature_maturity_update: true
priority: high

pack_summary:
  - This prompt pack reviews the entire codebase for bugs, safety issues, broken commands, failing tests, runtime errors, docs drift, and regression gaps.
  - It is not a feature-expansion pack.
  - It should fix safe/scoped issues and create bug reports/regression tests for larger issues.
  - It should not broadly rewrite the codebase.
  - It must preserve safety architecture and stop at approval gates.

global_rules:
  - Follow SPEC.md.
  - Follow docs/SDLC.md.
  - Follow AGENTS.md.
  - Build safety first, capabilities second.
  - Do not weaken policy.
  - Do not bypass ToolBroker.
  - Do not bypass PolicyEngine.
  - Do not bypass PermissionManager.
  - Do not bypass ApprovalManager.
  - Do not bypass AuditLogger.
  - Do not enable personal-data tools by default.
  - Do not add major new features.
  - Do not install packages.
  - Do not delete tests to make failures disappear.
  - Do not hide failing tests.
  - Do not broadly rewrite unrelated code.
  - Fix safe/scoped bugs only.
  - For large or ambiguous bugs, create a bug report and fix plan.
  - Update CHANGELOG.md.
  - Update docs/PROJECT_STATE.md.
  - Update docs/FEATURE_REGISTRY.md if feature status changes.
  - Update docs/FEATURE_MATURITY.md if maturity evidence changes.
  - Update docs/COMMAND_REGISTRY.md if commands change.
  - Update docs/COMMAND_TEST_MATRIX.md if QA steps change.
  - Update docs/COMPLETION_REPORT.md.
  - Update docs/RISK_REGISTER.md if risk changed.
  - Update docs/THREAT_MODEL.md if threat surface changed.

stop_conditions:
  - approval_gate
  - failing_tests_not_safely_fixable
  - package_install_required
  - personal_data_access_required
  - security_policy_change_required
  - ambiguous_requirements
  - broad_refactor_required
  - high_or_critical_action_execution_required

expected_prompt_ids:
  - CODEBUG-01
  - CODEBUG-02
  - CODEBUG-03
  - CODEBUG-04
  - CODEBUG-05
  - CODEBUG-06
  - CODEBUG-07
  - CODEBUG-08

<<<PROMPT_START id="CODEBUG-01" order="1">>
title: Codebase bug review baseline
category: release_gate
risk_level: LOW
approval_gate: false
depends_on: []
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Run Codebase Bug Review Baseline.

Goal:
Establish current codebase health: git state, tests, validations, import errors, command errors, safety checks, and likely bug hotspots.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- README.md
- CHANGELOG.md
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/COMMAND_REGISTRY.md, if present
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/TEST_PLAN.md
- docs/RELEASE_CHECKLIST.md

Run:
- git status --short
- git diff --stat
- .venv/bin/python --version if .venv exists
- python version guard check if practical
- targeted import checks
- full test suite if practical
- startup policy validation if available
- capability manifest validation if available
- command registry validation if available
- docs validation if available

Create/update:
- docs/bugfix/CODEBASE_BUG_REVIEW_BASELINE.md
- docs/bugfix/CODEBASE_BUG_HOTSPOTS.md
- docs/bugfix/CODEBASE_BUG_FIX_QUEUE.md

Report:
- failing tests
- import errors
- CLI startup errors
- command registry drift
- docs validation issues
- safety validation issues
- uncommitted files that may affect review
- highest-risk bug hotspots
- recommended fix order

Do not fix bugs in this prompt unless a tiny test/doc issue is blocking the baseline report.

Update tracking docs.

Final report:
- baseline summary
- tests/validations run
- bug hotspot list
- next recommended prompt
<<<PROMPT_END id="CODEBUG-01">>

<<<PROMPT_START id="CODEBUG-02" order="2">>
title: Safety-control-plane bug review
category: safety
risk_level: HIGH
approval_gate: false
depends_on: ["CODEBUG-01"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Review safety control plane for bugs.

Goal:
Find and fix safe/scoped bugs in ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, AuditLogger, redaction, trust/risk models, and capability manifest validation.

Scope:
- Safety-control-plane review.
- Tests and regression tests.
- Safe/scoped fixes only.

Non-goals:
- Do not weaken policy.
- Do not make risky actions easier.
- Do not enable personal tools.
- Do not skip audits.
- Do not change CRITICAL approval reuse rules.

Check:
- unknown tools denied
- unknown capabilities denied
- ToolBroker-only execution
- PolicyEngine decisions
- approval requirements for HIGH/CRITICAL
- no approval reuse for CRITICAL
- personal-data tools disabled by default
- audit hash chain integrity
- secret redaction
- untrusted content cannot change policy
- rate limits if present
- capability manifest strictness

Create/update:
- docs/bugfix/SAFETY_CONTROL_PLANE_REVIEW.md
- tests/regressions/ for fixed bugs where practical

Run targeted safety tests and full tests if practical.

Final report:
- bugs found
- bugs fixed
- tests added
- remaining blockers
<<<PROMPT_END id="CODEBUG-02">>

<<<PROMPT_START id="CODEBUG-03" order="3">>
title: CLI and command bug review
category: command_registry
risk_level: MEDIUM
approval_gate: false
depends_on: ["CODEBUG-02"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Review CLI and command system for bugs.

Goal:
Find and fix bugs where commands fail, help text is wrong, exact commands break, natural-language routing conflicts with exact commands, commands are undocumented, or docs list commands that do not exist.

Scope:
- smart_agent.py
- CLI modules
- COMMAND_REGISTRY
- help/docs
- tests

Non-goals:
- Do not add major new command groups.
- Do not change command semantics broadly.
- Do not execute risky commands.
- Do not access personal data.

Check:
- empty invocation UX
- doctor
- --no-tools
- --debug
- --interactive
- commands list/show/search/validate if present
- runtime/brain/platform/promptops/native skill command groups if present
- deprecated/stubbed commands labeled correctly
- command examples accurate
- Python wrapper scripts if present

Create/update:
- docs/bugfix/CLI_COMMAND_REVIEW.md
- docs/COMMAND_REGISTRY.md
- docs/COMMAND_TEST_MATRIX.md if present

Add tests for fixed command bugs.

Run command validation and targeted CLI tests.

Final report:
- command bugs found/fixed
- command registry changes
- tests run/results
<<<PROMPT_END id="CODEBUG-03">>

<<<PROMPT_START id="CODEBUG-04" order="4">>
title: Core runtime and brain provider bug review
category: core
risk_level: MEDIUM
approval_gate: false
depends_on: ["CODEBUG-03"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Review core runtime and brain provider code for bugs.

Goal:
Find and fix bugs in Orchestrator, Router, LM Studio/Brain providers, no-tools behavior, debug/tool-call loop, model errors, provider setup, and startup ergonomics.

Scope:
- agent/core/
- agent/brain/ if present
- smart_agent.py
- provider docs/tests

Non-goals:
- Do not change model default without explicit reason.
- Do not remove LM Studio.
- Do not install model runtimes.
- Do not download models.
- Do not call paid providers.

Check:
- no-tools attaches no tools
- router doesn't over-attach tools
- tool-call loop bounded
- tool_call_id handling
- LMSTUDIO_MODEL missing diagnostics
- server unavailable diagnostics
- malformed model responses
- provider fallback disabled by default
- startup import overhead
- Python version guard
- exact chat quality not degraded by harness

Create/update:
- docs/bugfix/CORE_RUNTIME_REVIEW.md

Add regression tests for fixed issues.

Run targeted core/brain tests and full tests if practical.

Final report:
- runtime bugs found/fixed
- tests added
- provider status
<<<PROMPT_END id="CODEBUG-04">>

<<<PROMPT_START id="CODEBUG-05" order="5">>
title: Connector and workflow bug review
category: connector
risk_level: MEDIUM
approval_gate: false
depends_on: ["CODEBUG-04"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Review connectors and workflows for bugs.

Goal:
Find and fix safe/scoped bugs in weather, web, news, reddit/forums, workspace files, memory, calendar/contacts/email/messages/tasks stubs, workflows, dogfood/eval integrations.

Scope:
- agent/tools/
- agent/connectors/
- agent/weather/
- agent/web_acquisition/
- agent/news/
- agent/forums/
- agent/memory/
- agent/workflows/
- tests for these areas

Non-goals:
- Do not add new providers.
- Do not make live network calls unless existing safe mocked tests need no network.
- Do not enable personal-data connectors.
- Do not send/write anything.
- Do not bypass approval.

Check:
- provider missing errors
- cache/rate-limit behavior
- untrusted content wrappers
- prompt injection fixtures
- path traversal/file bounds
- memory secret refusal
- personal connector disabled defaults
- dogfood/eval fixtures not requiring personal data
- docs/commands align with implemented code

Create/update:
- docs/bugfix/CONNECTOR_WORKFLOW_REVIEW.md

Add regression tests for fixed issues.

Run targeted tests and full tests if practical.

Final report:
- connector/workflow bugs found/fixed
- tests added
- remaining blockers
<<<PROMPT_END id="CODEBUG-05">>

<<<PROMPT_START id="CODEBUG-06" order="6">>
title: Prompt tracker, docs, and maturity bug review
category: docs
risk_level: LOW
approval_gate: false
depends_on: ["CODEBUG-05"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Review prompt tracker, docs, and maturity tracking for bugs.

Goal:
Find and fix inconsistencies in prompt ledger/queue/audit, feature maturity, feature registry, command registry, changelog, completion report, roadmap, and project state.

Scope:
- docs/tracking files
- prompt files
- command registry
- feature maturity
- completion report
- changelog

Non-goals:
- Do not broadly rewrite dense trackers.
- Do not mark prompts complete without evidence.
- Do not inflate feature maturity.
- Do not delete historical evidence.

Check:
- queued prompts missing evidence
- active prompt stale
- prompt pack statuses
- feature maturity overclaiming
- commands without examples
- docs listing nonexistent commands
- changelog mismatch
- completion report mismatch
- PROJECT_STATE stale

Create/update:
- docs/bugfix/TRACKER_DOCS_REVIEW.md
- docs/PROMPT_AUDIT.md if present
- docs/TRACKER_CONSISTENCY_REPORT.md if present

Run docs/command/prompt validations if available.

Final report:
- tracker inconsistencies found/fixed
- docs updated
- prompts needing attention
<<<PROMPT_END id="CODEBUG-06">>

<<<PROMPT_START id="CODEBUG-07" order="7">>
title: Whole-codebase static bug scan
category: release_gate
risk_level: MEDIUM
approval_gate: false
depends_on: ["CODEBUG-06"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Run whole-codebase static bug scan.

Goal:
Search the entire codebase for common bug patterns and safety anti-patterns, fix safe/scoped issues, and report larger issues.

Scope:
- Static grep/code review.
- Safe fixes.
- Tests.

Non-goals:
- Do not run untrusted scripts.
- Do not install linters.
- Do not broadly refactor.
- Do not change behavior without tests.

Search for:
- TODO/FIXME/HACK/XXX
- bare except
- broad Exception swallowing
- subprocess usage
- os.system
- shell=True
- eval/exec
- importlib on untrusted paths
- direct network calls outside web/provider layer
- direct file access outside workspace/path policy
- direct tool execution outside ToolBroker
- approval bypass
- audit bypass
- secrets printed/logged
- personal data stored by default
- mutable default args
- missing timeouts
- unbounded loops
- unbounded retries
- large file reads without limits
- missing redaction
- hardcoded API keys/tokens
- path traversal risk
- unsafe YAML load
- JSON parsing without error handling in provider code

Create/update:
- docs/bugfix/STATIC_BUG_SCAN_REPORT.md

Fix safe/scoped issues and add tests.

Run targeted tests and full tests if practical.

Final report:
- patterns scanned
- findings by severity
- fixes made
- deferred issues
- tests run/results
<<<PROMPT_END id="CODEBUG-07">>

<<<PROMPT_START id="CODEBUG-08" order="8">>
title: Codebase bug review release gate
category: release_gate
risk_level: LOW
approval_gate: false
depends_on: ["CODEBUG-07"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Run Codebase Bug Review release gate.

Goal:
Validate all bug review fixes, update maturity/tracking docs, and produce a final bug review summary.

Run:
1. full test suite
2. startup policy validation
3. capability manifest validation
4. docs validation if available
5. command registry validation if available
6. prompt tracker validation if available
7. safe eval suite if available
8. dogfood validation with mocks if available

Verify:
- no P0 safety bugs remain open without explicit blocker
- no known ToolBroker bypass
- no known PolicyEngine bypass
- no known ApprovalManager bypass
- no known AuditLogger bypass
- no personal-data tools enabled by default
- no CRITICAL approval reuse
- command registry consistent enough
- docs updated
- regression tests added for fixed bugs
- feature maturity conservative

Create/update:
- docs/bugfix/CODEBASE_BUG_REVIEW_RELEASE_GATE.md
- docs/bugfix/CODEBASE_BUG_REVIEW_SUMMARY.md

Update:
- CHANGELOG.md
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md if needed
- docs/FEATURE_MATURITY.md
- docs/COMMAND_REGISTRY.md if commands changed
- docs/COMMAND_TEST_MATRIX.md if QA changed
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/RELEASE_CHECKLIST.md

Final report:
- tests run/results
- validations run/results
- bugs fixed
- bugs deferred
- regression tests added
- remaining blockers
- next recommended prompt/pack
<<<PROMPT_END id="CODEBUG-08">>

<<<PROMPT_PACK_END>>>
