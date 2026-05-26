---
prompt_id: BRAIN-09
pack_id: brain-runtime-independence-v1
title: Provider fallback and model router
category: core
risk_level: MEDIUM
approval_gate: false
depends_on: ["BRAIN-08"]
status: completed
order: 9
created_at: 2026-05-25T15:32:48+00:00
imported_at: 2026-05-25T15:32:48+00:00
source_pack: prompts/packs/brain-runtime-independence-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T17:01:19+00:00
completed_at: 2026-05-25T17:07:00+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: provider router/fallback tests passed with 22 passed; broader brain/docs/feature-maturity/command tests passed with 89 passed; command registry validation ok with 439 commands; startup policy and capability manifest validation passed via make policy-check; CLI smokes for brain fallback-status, switch --dry-run, and route passed
docs_updated: docs/brain/PROVIDER_FALLBACK_POLICY.md, docs/brain/MODEL_ROUTING_POLICY.md, README, .env.example, command registry/test matrix, feature registry, feature maturity, roadmap, risk register, threat model
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
notes: Fallback remains disabled by default, cloud fallback disabled, auto-switch disabled, switch is dry-run only, route decisions do not call models or tools, and no live gateway/default-provider switch was added.
---

# Prompt

You are Codex working in this repo.

Task:
Build provider fallback and model router.

Goal:
Allow the agent to select or fall back between brain providers safely based on configuration, provider health, task type, and capability support, without changing safety policy.

Scope:
- Provider selection/fallback logic.
- Config.
- Tests.
- No provider default switch unless explicitly configured.

Non-goals:
- Do not use cloud/paid providers by default.
- Do not run unavailable providers.
- Do not override user-selected provider silently.
- Do not bypass ToolBroker.
- Do not change approval rules.
- Do not call provider during routing unless health is explicitly checked.

Create:
- agent/brain/provider_router.py
- agent/brain/fallback.py
- tests/brain/test_provider_router_fallback.py
- docs/brain/PROVIDER_FALLBACK_POLICY.md
- docs/brain/MODEL_ROUTING_POLICY.md

Config:
- BRAIN_FALLBACK_ENABLED=false by default
- BRAIN_PROVIDER_ORDER=lmstudio,llama_cpp_server,ollama,llama_cpp_inprocess,mlx
- BRAIN_TASK_PROVIDER_MAP={}
- BRAIN_REQUIRE_TOOL_CALL_SUPPORT_FOR_TOOLS=true
- BRAIN_AUTO_SWITCH_ON_FAILURE=false by default
- BRAIN_MAX_FALLBACK_ATTEMPTS=1
- BRAIN_ALLOW_CLOUD_FALLBACK=false

Routing inputs:
- requested provider
- task type
- requires tool calls
- requires streaming
- requires JSON/schema
- provider health
- configured provider order
- user override
- safe mode/no-tools mode

Requirements:
1. Explicit user provider wins unless unavailable and fallback enabled.
2. Fallback disabled by default.
3. Cloud/paid fallback disabled by default.
4. Tool-call tasks require provider tool-call support.
5. No-tools chat can use providers without tool-call support.
6. Provider selection decision recorded/audited/logged.
7. Missing provider returns clear error.
8. Fallback attempts bounded.
9. No model/router decision can alter ToolBroker policy.
10. Tests cover edge cases.

Commands:
- python smart_agent.py brain providers
- python smart_agent.py brain switch <provider> --dry-run
- python smart_agent.py brain fallback-status
- python smart_agent.py brain route "message"

Tests:
- explicit provider selected.
- fallback disabled blocks fallback.
- fallback enabled selects next healthy provider.
- tool-call task rejects provider without tool support.
- no-tools task allows provider without tool support.
- cloud fallback blocked.
- provider decision recorded.
- command registry updated.

Update docs/tracking.

Run tests/validations.

Final report:
- provider router added
- fallback behavior
- tests run/results
- next recommended prompt
