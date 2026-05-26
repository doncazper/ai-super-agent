---
prompt_id: BRAIN-11
pack_id: brain-runtime-independence-v1
title: Brain runtime release gate
category: release_gate
risk_level: LOW
approval_gate: false
depends_on: ["BRAIN-10"]
status: completed
order: 11
created_at: 2026-05-25T15:32:48+00:00
imported_at: 2026-05-25T15:32:48+00:00
source_pack: prompts/packs/brain-runtime-independence-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T17:11:37+00:00
completed_at: 2026-05-25T17:45:00+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: focused BRAIN/MCP/docs/command tests 97 passed; docs/feature-maturity/command registry tests 20 passed; full suite 1285 passed, 1 skipped; make policy-check passed; commands validate passed with 443 commands; brain/MCP CLI smokes passed; optional import guard passed
docs_updated: release gate, maturity review, README, changelog, project/feature/risk/threat/release/prompt trackers
changelog_updated:
feature_registry_updated:
feature_maturity_updated:
command_registry_updated:
completion_report_updated:
evidence_links:
blockers:
next_prompt_id: news-provider-registry-status-commands
supersedes:
superseded_by:
notes: LM Studio dependency partially optional; normal live chat still uses existing LM Studio-compatible path; next_prompt_id news-provider-registry-status-commands
---

# Prompt

You are Codex working in this repo.

Task:
Run Brain Runtime Independence release gate and maturity review.

Goal:
Validate that LM Studio has been decoupled behind a provider abstraction, alternate providers are safely scaffolded, model health/evals exist, fallback rules are safe, and MCP is correctly treated as optional interoperability rather than the brain runtime.

Scope:
- Validation.
- Maturity review.
- Small fixes only if needed.
- No new provider implementation beyond pack scope.

Non-goals:
- Do not remove LM Studio.
- Do not change default provider unless explicitly configured and tests support it.
- Do not install model runtimes.
- Do not download models.
- Do not run paid/cloud APIs.
- Do not enable MCP server.
- Do not start network listeners.
- Do not enable personal-data tools.

Run:
1. full test suite
2. startup policy validation
3. capability manifest validation
4. docs validation
5. command registry validation if present
6. brain provider tests
7. brain benchmark/eval tests with mocks
8. provider registry status
9. LM Studio provider mocked tests
10. optional live LM Studio doctor only if configured and existing test command supports it

Verify:
- BrainProvider interface exists.
- Model registry exists.
- LM Studio is a provider.
- Existing no-tools chat remains supported.
- Existing tool-call flow remains supported.
- llama.cpp server provider exists/stubbed and disabled by default.
- Ollama provider exists/stubbed and disabled by default.
- llama-cpp-python provider exists/stubbed and disabled by default.
- MLX provider is strategy/stubbed and disabled by default.
- Mock provider supports tests.
- Fallback disabled by default.
- Cloud/paid fallback disabled by default.
- Provider health/evals exist.
- MCP decision docs state MCP is not brain runtime.
- MCP adapters/stubs disabled by default.
- Startup overhead remains low.
- Command registry updated.
- Feature maturity conservative.

Create/update:
- docs/brain/BRAIN_RUNTIME_RELEASE_GATE.md
- docs/brain/BRAIN_RUNTIME_MATURITY_REVIEW.md

Maturity assessment:
- Brain runtime strategy
- BrainProvider interface
- Model registry
- LM Studio provider refactor
- llama.cpp server provider
- Ollama provider
- llama-cpp-python provider
- MLX provider strategy/stub
- health/benchmark/evals
- provider fallback/router
- MCP decision/adapters
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
- live tests skipped or run
- provider status table
- default provider status
- maturity score
- remaining blockers
- whether LM Studio dependency is now optional or partially optional
- next recommended track
