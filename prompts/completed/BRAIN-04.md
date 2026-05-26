---
prompt_id: BRAIN-04
pack_id: brain-runtime-independence-v1
title: llama.cpp server provider
category: core
risk_level: MEDIUM
approval_gate: false
depends_on: ["BRAIN-03"]
status: completed
order: 4
created_at: 2026-05-25T15:32:48+00:00
imported_at: 2026-05-25T15:32:48+00:00
source_pack: prompts/packs/brain-runtime-independence-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T15:57:33+00:00
completed_at: 2026-05-25T16:24:31+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: Focused brain/llama.cpp server/docs/command-registry tests passed: 49 passed; brain providers, brain health --provider llama_cpp_server, and brain doctor --provider llama_cpp_server CLI smokes passed; startup policy and capability manifest validation passed via make policy-check; command registry validation passed with 437 commands.
docs_updated: Created docs/brain/providers/llama_cpp_server.md; updated README, .env.example, CHANGELOG, PROJECT_STATE, TRACKER_DASHBOARD, FEATURE_REGISTRY, FEATURE_MATURITY, FEATURE_ROADMAP, COMMAND_REGISTRY, COMMAND_TEST_MATRIX, PROMPT_QUEUE, PROMPT_LEDGER, PROMPT_AUDIT, COMPLETION_REPORT, RISK_REGISTER, and THREAT_MODEL.
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
notes: Completed BRAIN-04 llama.cpp server provider scaffold. LM Studio remains default; llama.cpp server is disabled unless explicitly enabled/configured; no llama.cpp install, model download, server startup, default-provider change, paid/cloud default, MCP enablement, listener startup, memory write, unverified tool-call support, ToolBroker semantic change, or safety-control bypass.
---

# Prompt

You are Codex working in this repo.

Task:
Add llama.cpp server BrainProvider.

Goal:
Support a lightweight local model runtime using an OpenAI-compatible llama.cpp server, without requiring LM Studio.

Scope:
- Provider adapter.
- Config.
- Doctor/status.
- Tests with mocked HTTP responses.
- No model download.
- No server installation.

Non-goals:
- Do not install llama.cpp.
- Do not download models.
- Do not start llama-server automatically.
- Do not remove LM Studio.
- Do not change default provider yet.
- Do not assume tool-call support unless verified/configured.

Create:
- agent/brain/providers/llama_cpp_server.py
- tests/brain/test_llama_cpp_server_provider.py
- docs/brain/providers/llama_cpp_server.md

Config:
- LLAMA_CPP_SERVER_ENABLED=false
- LLAMA_CPP_SERVER_BASE_URL=http://localhost:8080/v1
- LLAMA_CPP_SERVER_MODEL=
- LLAMA_CPP_SERVER_TIMEOUT_SECONDS=60
- LLAMA_CPP_SERVER_SUPPORTS_TOOL_CALLS=false by default unless verified
- LLAMA_CPP_SERVER_SUPPORTS_STREAMING=false or config-based

Commands:
- python smart_agent.py brain doctor --provider llama_cpp_server
- python smart_agent.py brain providers
- python smart_agent.py brain health --provider llama_cpp_server

Provider behavior:
1. OpenAI-compatible chat endpoint.
2. Optional /v1/models check.
3. Missing base URL/model returns setup hint.
4. Server unavailable returns clear error.
5. Tool-call support explicit/configurable.
6. If provider does not support tool calls, no-tool chat can still work.
7. Provider errors normalized.
8. No search/personal data behavior.
9. No server process start by default.
10. Registry lists provider as disabled unless enabled.

Tests:
- missing config returns setup hint.
- server health mock success.
- server unavailable handled.
- no-tool chat mock works.
- malformed response handled.
- tool-call unsupported path handled.
- provider registry lists llama_cpp_server.
- command registry updated.

Update:
- docs/brain/providers/llama_cpp_server.md
- README model runtimes section.
- .env.example.
- docs/COMMAND_REGISTRY.md.
- docs/FEATURE_MATURITY.md.
- docs/PROJECT_STATE.md.
- docs/COMPLETION_REPORT.md.
- CHANGELOG.md.

Run tests/validations.

Final report:
- provider added
- config added
- tests run/results
- next recommended prompt
