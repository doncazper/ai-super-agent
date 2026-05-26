<<<PROMPT_PACK_START>>>
pack_id: natural-language-command-understanding-v1
pack_title: Natural Language Command Understanding Track
created_by: user
mode: controlled_batch_until_blocked
default_execution: sequential
requires_sdlc: true
requires_prompt_ledger: true
requires_feature_maturity_update: true
priority: high

pack_summary:
  - This prompt pack improves the agent's ability to understand natural-language user requests in terminal/CLI mode.
  - The user often asks questions or gives loose natural-language instructions rather than exact commands.
  - The agent should infer intent, map it to existing commands/capabilities when safe, ask clarifying questions when needed, and never bypass safety rules.
  - This pack builds a natural-language intent taxonomy, command-registry intent index, parser/router, clarification flow, safe preflight/execution planner, conversational CLI UX, eval fixtures, dogfood suite, and release gate.
  - It must improve usability without turning the harness into the AI or weakening ToolBroker/Policy/Approval/Audit boundaries.

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
  - Do not allow natural-language requests to bypass risk/approval rules.
  - Do not silently execute HIGH or CRITICAL actions.
  - Do not silently send emails/messages.
  - Do not silently write calendar/contact/task/file changes.
  - Do not silently access personal data.
  - Do not store personal command content in memory by default.
  - Do not rely on LLM-only routing for safety decisions.
  - Deterministic rules and command registry metadata should be the first layer.
  - LLM interpretation may suggest intent, but PolicyEngine remains final authority.
  - Update CHANGELOG.md.
  - Update docs/PROJECT_STATE.md.
  - Update docs/FEATURE_REGISTRY.md.
  - Update docs/FEATURE_MATURITY.md.
  - Update docs/FEATURE_ROADMAP.md if status/order changes.
  - Update docs/COMMAND_REGISTRY.md if commands are added/changed.
  - Update docs/COMMAND_TEST_MATRIX.md if QA steps are added/changed.
  - Update docs/COMPLETION_REPORT.md.
  - Update docs/RISK_REGISTER.md if risk changed.
  - Update docs/THREAT_MODEL.md if threat surface changed.
  - Update docs/RELEASE_CHECKLIST.md where release-gate checks change.

stop_conditions:
  - approval_gate
  - failing_tests_not_safely_fixable
  - docs_validation_failure_not_safely_fixable
  - personal_data_access_required
  - package_install_required
  - high_or_critical_action_execution_required
  - ambiguous_requirements
  - security_policy_change_required
  - runtime_behavior_change_required_beyond_scope

expected_prompt_ids:
  - NLCMD-01
  - NLCMD-02
  - NLCMD-03
  - NLCMD-04
  - NLCMD-05
  - NLCMD-06
  - NLCMD-07
  - NLCMD-08
  - NLCMD-09
  - NLCMD-10

<<<PROMPT_START id="NLCMD-01" order="1">>
title: Natural-language command understanding architecture
category: core
risk_level: LOW
approval_gate: false
depends_on: []
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Create Natural-Language Command Understanding architecture and roadmap.

Goal:
Design a safe layer that lets the user type loose natural-language requests in terminal and have the agent infer intent, map to commands/capabilities, ask clarifying questions, or run safe preflight/dry-run flows.

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
- docs/COMMAND_TEST_MATRIX.md, if present
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/RELEASE_CHECKLIST.md
- agent/core/router.py
- smart_agent.py

Scope:
- Architecture docs.
- Intent taxonomy.
- Safety policy.
- Roadmap.
- No runtime behavior change unless trivial docs/help wiring.

Non-goals:
- Do not use LLM routing as sole safety mechanism.
- Do not execute risky actions.
- Do not add personal-data access.
- Do not bypass ToolBroker/Policy/Audit.
- Do not replace existing exact commands.

Create:
- docs/natural_language/NL_COMMAND_UNDERSTANDING_TRACK.md
- docs/natural_language/NL_INTENT_TAXONOMY.md
- docs/natural_language/NL_COMMAND_SAFETY_POLICY.md
- docs/decisions/natural_language_command_understanding.md

Define intent categories:
- chat.no_tools
- chat.general
- doctor.status
- command.help
- command.search
- weather.current
- weather.forecast
- web.research
- news.brief
- reddit.search
- file.read
- file.summarize
- memory.search
- memory.add
- prompt.queue
- git.status
- test.run
- docs.lookup
- bug.report
- session.review
- action.preflight
- personal_data.request
- send_or_write.request
- unknown
- ambiguous

Define safety outcomes:
- answer_directly
- route_to_command
- show_command_suggestion
- run_safe_command
- dry_run_only
- ask_clarifying_question
- require_approval
- deny
- unsupported
- handoff_to_help

Update roadmap/tracking docs.

Run docs validation/tests if available.

Final report:
- files created
- intent taxonomy summary
- safety policy summary
- tests/validations run
- next recommended prompt
<<<PROMPT_END id="NLCMD-01">>

<<<PROMPT_START id="NLCMD-02" order="2">>
title: Command registry intent index
category: command_registry
risk_level: LOW
approval_gate: false
depends_on: ["NLCMD-01"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build command registry intent index.

Goal:
Make docs/COMMAND_REGISTRY.md usable by the natural-language router by indexing command groups, examples, aliases, intents, risk levels, approval requirements, and prerequisites.

Scope:
- Command registry parsing/indexing.
- Alias metadata.
- Tests.
- No command execution.

Create/update:
- agent/commands/intent_index.py
- agent/commands/models.py if needed
- tests/commands/test_command_intent_index.py
- docs/natural_language/COMMAND_INTENT_INDEX.md

Index fields:
- command_id
- command
- group
- description
- examples
- aliases
- natural_language_triggers
- intent_ids
- risk_level
- approval_required
- provider_required
- connector_required
- safe_to_run_directly
- dry_run_available
- docs_link
- status

Requirements:
1. Exact command registry remains source of truth.
2. Missing command registry handled gracefully.
3. Planned/stubbed/deprecated commands are not suggested as active.
4. HIGH/CRITICAL commands are never run directly from NL intent.
5. Commands requiring providers show setup hints.
6. Alias mapping must be explicit and testable.
7. Search supports fuzzy/natural terms without LLM dependency.
8. No command execution.

Commands if practical:
- python smart_agent.py commands intents
- python smart_agent.py commands suggest "natural language request"

Tests:
- index builds from fixture registry.
- active command suggested.
- deprecated command not primary.
- stubbed command labeled.
- high-risk command dry-run/approval-only.
- provider-required command shows setup hint.
- command registry updated.

Update docs/tracking.

Final report:
- intent index added
- commands added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="NLCMD-02">>

<<<PROMPT_START id="NLCMD-03" order="3">>
title: Natural-language request parser and deterministic router
category: core
risk_level: MEDIUM
approval_gate: false
depends_on: ["NLCMD-02"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build natural-language request parser and deterministic command router.

Goal:
Given a user request, classify intent and propose the safest next action without relying on LLM-only safety decisions.

Scope:
- Parser/router.
- Deterministic rules.
- Optional LLM interpretation as non-authoritative suggestion if existing architecture supports it.
- Tests.

Non-goals:
- Do not execute high-risk commands.
- Do not route personal-data requests automatically.
- Do not add new tools.
- Do not bypass existing router or ToolBroker.

Create:
- agent/natural_language/
  - __init__.py
  - models.py
  - parser.py
  - router.py
  - safety.py
  - errors.py
- tests/natural_language/test_nl_parser_router.py

Models:
- NaturalLanguageRequest
- IntentCandidate
- CommandSuggestion
- NLRouteDecision
- ClarificationQuestion
- NLExecutionPlan

Router decision fields:
- original_text
- normalized_text
- intent
- confidence
- command_suggestions
- safety_outcome
- risk_level
- approval_required
- dry_run_required
- clarification_required
- reason
- evidence
- audit_summary

Requirements:
1. Deterministic rules first.
2. LLM suggestions, if used, cannot override safety outcome.
3. Exact commands still work normally.
4. No-tools mode preserved.
5. Ambiguous requests ask clarification.
6. Risky personal/send/write requests produce preflight/approval/dry-run only.
7. Unknown requests fall back to chat/help.
8. Natural language parser does not call tools.
9. Parser does not access personal data.
10. Router decisions are testable.

Tests:
- "what's the weather in Phoenix" maps to weather current.
- "look this up" maps to web/research with clarification if missing query.
- "what commands do I have for memory" maps to help/commands search.
- "fix the last session bugs" maps to session review/bugfix suggestion.
- "send this email" requires approval/preflight/unsupported depending capability.
- ambiguous short request asks clarification.
- no-tools mode does not route tools.
- exact command unaffected.
- high-risk request not executed.

Update docs/tracking.

Final report:
- parser/router added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="NLCMD-03">>

<<<PROMPT_START id="NLCMD-04" order="4">>
title: Clarification and confirmation flow
category: ux
risk_level: MEDIUM
approval_gate: false
depends_on: ["NLCMD-03"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build clarification and confirmation flow for natural-language commands.

Goal:
When a natural-language request is ambiguous, risky, or missing parameters, the agent should ask a useful clarifying question or show a safe command suggestion instead of failing or guessing.

Scope:
- Clarification model.
- CLI display.
- Tests.
- No risky execution.

Create/update:
- agent/natural_language/clarification.py
- agent/natural_language/preview.py
- tests/natural_language/test_clarification_flow.py
- docs/natural_language/CLARIFICATION_FLOW.md

Clarification types:
- missing_required_argument
- multiple_matching_commands
- risky_action
- personal_data_request
- provider_missing
- ambiguous_intent
- unsupported_capability
- command_is_stubbed
- command_is_deprecated

Requirements:
1. Ask one clear question when possible.
2. Offer exact command examples.
3. Show why approval/dry-run is required.
4. Do not expose secrets.
5. Do not access personal data.
6. Do not execute tools during clarification.
7. If a command is deprecated, suggest replacement.
8. If a provider is missing, suggest doctor/setup command.
9. If intent is unknown, offer help search.

Tests:
- missing location asks for location.
- multiple command matches offer choices.
- provider missing suggests doctor.
- deprecated command suggests replacement.
- personal-data request says approval/setup required.
- risky send/write request does not execute.
- command registry updated if CLI changed.

Update docs/tracking.

Final report:
- clarification flow added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="NLCMD-04">>

<<<PROMPT_START id="NLCMD-05" order="5">>
title: Safe execution planner and natural-language preflight
category: safety
risk_level: MEDIUM
approval_gate: false
depends_on: ["NLCMD-04"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build safe execution planner and natural-language preflight.

Goal:
Convert natural-language intent into a safe execution plan that can be previewed, dry-run, approved, or denied before any tool or command execution.

Scope:
- Execution plan.
- Preflight display.
- Dry-run integration.
- Tests.

Non-goals:
- Do not execute HIGH/CRITICAL actions.
- Do not auto-run personal-data commands.
- Do not bypass ToolBroker.
- Do not bypass ApprovalManager.

Create/update:
- agent/natural_language/execution_plan.py
- agent/natural_language/preflight.py
- tests/natural_language/test_nl_execution_plan_preflight.py
- docs/natural_language/NL_PREFLIGHT.md

Execution plan fields:
- plan_id
- original_request
- intent
- command
- args
- risk_level
- trust_level
- approval_required
- dry_run_required
- toolbroker_required
- expected_side_effects
- provider_requirements
- missing_requirements
- audit_preview
- memory_behavior
- safe_to_execute

Commands:
- python smart_agent.py nl preflight "request"
- python smart_agent.py nl explain "request"
- python smart_agent.py nl suggest "request"

Requirements:
1. Preflight executes no tools.
2. Safe/LOW read-only commands may be suggested for execution.
3. HIGH/CRITICAL actions require Action Center/approval.
4. Unknown commands denied/suggest help.
5. Missing provider/setup reported.
6. Plan includes exact command to run.
7. Audit summary included.
8. Command registry updated.

Tests:
- safe weather request creates safe plan.
- web research plan shows provider requirement.
- email send plan requires approval and not safe_to_execute.
- file write plan requires approval/preview.
- unknown command denied.
- preflight executes no tools.
- command registry updated.

Update docs/tracking.

Final report:
- preflight added
- commands added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="NLCMD-05">>

<<<PROMPT_START id="NLCMD-06" order="6">>
title: Conversational CLI UX for natural-language commands
category: ux
risk_level: MEDIUM
approval_gate: false
depends_on: ["NLCMD-05"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Add conversational CLI UX for natural-language command handling.

Goal:
Make terminal usage friendlier when the user types natural language. The CLI should explain what it understood, what it plans to do, what command matches, and when clarification/approval is required.

Scope:
- CLI integration.
- Help text.
- UX output.
- Tests.

Non-goals:
- Do not break existing exact commands.
- Do not require natural-language mode for all commands.
- Do not call LM Studio for simple command suggestions unless configured.
- Do not execute risky actions.

Modes:
- exact command mode
- natural-language suggestion mode
- natural-language preflight mode
- interactive clarification mode

Possible commands:
- python smart_agent.py ask "natural language request"
- python smart_agent.py nl "natural language request"
- python smart_agent.py nl suggest "request"
- python smart_agent.py nl preflight "request"
- python smart_agent.py nl explain "request"

Behavior:
1. Exact commands remain exact.
2. If user invokes `ask` or `nl`, use NL parser.
3. For safe command, show mapped command and optionally execute only if policy says safe and user requested execution mode.
4. For risky command, show preflight/approval path.
5. For ambiguity, ask clarification.
6. For unknown, offer help/command search.

Tests:
- exact command still works.
- nl weather request maps correctly.
- ask help request maps to command search.
- risky send request not executed.
- ambiguous request asks clarification.
- no-tools mode preserved.
- help text updated.
- command registry updated.

Update:
- README.md.
- docs/USER_GUIDE.md if present.
- docs/HELP.md if present.
- docs/COMMAND_REGISTRY.md.
- docs/FEATURE_MATURITY.md.
- docs/COMPLETION_REPORT.md.
- CHANGELOG.md.

Run tests/validations.

Final report:
- CLI UX changes
- tests run/results
- next recommended prompt
<<<PROMPT_END id="NLCMD-06">>

<<<PROMPT_START id="NLCMD-07" order="7">>
title: Natural-language eval fixtures
category: tests
risk_level: LOW
approval_gate: false
depends_on: ["NLCMD-06"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build natural-language command understanding eval fixtures.

Goal:
Create a repeatable eval set that checks whether the agent correctly understands common natural-language terminal requests, maps them to safe commands, asks clarifying questions, or blocks risky actions.

Create:
- eval_cases/natural_language/
- tests/natural_language/test_nl_eval_fixtures.py
- docs/natural_language/NL_EVALS.md

Eval categories:
1. weather
2. web/research
3. news
4. reddit/forums
5. help/commands
6. doctor/status
7. memory safe requests
8. workspace read/summarize
9. prompt tracker
10. bug/session review
11. ambiguous requests
12. risky personal-data requests
13. send/write requests
14. unsupported requests
15. deprecated/legacy commands

Each eval case:
- input_text
- expected_intent
- expected_safety_outcome
- expected_command_group
- should_execute
- should_clarify
- should_require_approval
- should_deny
- notes

Commands:
- python smart_agent.py eval run --natural-language
- python smart_agent.py eval report --natural-language

Tests:
- eval fixtures load.
- safe cases pass.
- risky cases do not execute.
- ambiguous cases clarify.
- unsupported cases report help.
- command registry updated.

Update docs/tracking.

Final report:
- eval fixtures added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="NLCMD-07">>

<<<PROMPT_START id="NLCMD-08" order="8">>
title: Natural-language dogfood suite and session feedback integration
category: dogfood
risk_level: LOW
approval_gate: false
depends_on: ["NLCMD-07"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build natural-language command dogfood suite and session feedback integration.

Goal:
Create manual dogfood flows that test the natural-language command layer using realistic user phrases and feed failures into bugs/regressions.

Create:
- dogfood_suites/natural_language_core.yaml
- dogfood_suites/natural_language_risky.yaml
- docs/natural_language/NL_DOGFOOD_RUNBOOK.md

Dogfood examples:
- "what can you do"
- "check if the agent is healthy"
- "what's the weather in phoenix"
- "look up current ai coding agent news"
- "summarize this file"
- "show me my prompt queue"
- "review the last session and fix bugs"
- "what commands do I have for reddit"
- "send this message to my brother" -> must not send
- "read my emails" -> must require setup/approval/selected scope
- "delete that file" -> must require approval/preflight
- "run the next prompt pack" -> must use prompt tracker rules

Requirements:
1. Safe suite runs without personal data.
2. Risky suite uses dry-run/preflight only.
3. No sends/writes.
4. No personal-data access.
5. Session logging integration if available.
6. Failures produce feedback/bug hints.
7. Command registry updated.

Commands:
- python smart_agent.py dogfood run natural_language_core --session
- python smart_agent.py dogfood run natural_language_risky --session

Tests:
- suite YAML validates.
- risky suite dry-run only.
- no personal data required.
- no high/critical execution.
- command registry updated.

Update docs/tracking.

Final report:
- dogfood suites added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="NLCMD-08">>

<<<PROMPT_START id="NLCMD-09" order="9">>
title: Natural-language bug feedback loop
category: bugs
risk_level: LOW
approval_gate: false
depends_on: ["NLCMD-08"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build natural-language bug feedback loop.

Goal:
When the agent misunderstands a natural-language request, the user should be able to flag it and the system should create a structured bug/regression fixture.

Scope:
- Feedback tags.
- Bug report templates.
- Regression fixture generation.
- Tests.

Non-goals:
- Do not fix all NL bugs in this prompt.
- Do not store personal data.
- Do not weaken policy.

Add feedback tags:
- misunderstood_intent
- wrong_command_suggested
- should_have_clarified
- should_have_denied
- should_have_required_approval
- executed_when_should_not
- failed_to_find_command
- poor_natural_language_answer

Create/update:
- docs/natural_language/NL_BUG_TRIAGE.md
- docs/templates/nl_regression_case_template.yaml
- tests/natural_language/test_nl_bug_feedback_loop.py

Commands if practical:
- python smart_agent.py feedback nl-bug --last --expected-intent <intent>
- python smart_agent.py bugs create-nl-regression <bug_id>
- python smart_agent.py nl regressions list

Requirements:
1. NL feedback attaches to last command/session entry.
2. Regression fixture contains sanitized input.
3. Personal data redacted.
4. Expected safe behavior captured.
5. Regression case can be added to eval_cases/natural_language.
6. Command registry updated.

Tests:
- feedback tag accepted.
- regression case generated.
- personal data redacted.
- fixture loads in eval suite.
- command registry updated.

Update docs/tracking.

Final report:
- feedback loop added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="NLCMD-09">>

<<<PROMPT_START id="NLCMD-10" order="10">>
title: Natural-language command understanding release gate
category: release_gate
risk_level: LOW
approval_gate: false
depends_on: ["NLCMD-09"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Run Natural-Language Command Understanding release gate and maturity review.

Goal:
Validate that the natural-language command understanding layer improves usability while preserving safety, command registry truth, approval gates, and existing exact command behavior.

Run:
1. full test suite
2. startup policy validation
3. capability manifest validation
4. docs validation
5. command registry validation
6. natural-language eval suite
7. natural-language dogfood suite with safe fixtures
8. exact command regression tests

Verify:
- exact commands still work.
- no-tools mode preserved.
- natural-language requests map to safe commands.
- ambiguous requests clarify.
- risky requests require preflight/approval.
- personal-data requests do not execute by default.
- HIGH/CRITICAL actions not executed.
- command registry is source of truth.
- evals/dogfood exist.
- feedback loop exists.
- docs/user guide updated.
- feature maturity conservative.

Create/update:
- docs/natural_language/NL_COMMAND_RELEASE_GATE.md
- docs/natural_language/NL_COMMAND_MATURITY_REVIEW.md

Maturity assessment:
- NL architecture/taxonomy
- command intent index
- parser/router
- clarification flow
- preflight/execution plan
- CLI UX
- eval fixtures
- dogfood suite
- bug feedback loop
- release gate

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
- README.md
- docs/USER_GUIDE.md if present
- docs/HELP.md if present
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/FEATURE_ROADMAP.md
- docs/COMMAND_REGISTRY.md
- docs/COMMAND_TEST_MATRIX.md if present
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/RELEASE_CHECKLIST.md

Final report:
- tests run/results
- validation results
- eval/dogfood results
- maturity score
- remaining blockers
- whether NL command understanding is safe to rely on
- next recommended feature track
<<<PROMPT_END id="NLCMD-10">>

<<<PROMPT_PACK_END>>>
