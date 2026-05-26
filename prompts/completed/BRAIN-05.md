---
prompt_id: BRAIN-05
pack_id: brain-runtime-independence-v1
title: Ollama provider
category: core
risk_level: MEDIUM
approval_gate: false
depends_on: ["BRAIN-04"]
status: completed
order: 5
created_at: 2026-05-25T15:32:48+00:00
imported_at: 2026-05-25T15:32:48+00:00
source_pack: prompts/packs/brain-runtime-independence-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T16:24:43+00:00
completed_at: 2026-05-25T16:32:35+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: Focused brain/Ollama/provider/docs/command-registry tests passed: 57 passed; brain providers, brain health --provider ollama, and brain doctor --provider ollama CLI smokes passed; startup policy and capability manifest validation passed via make policy-check; command registry validation passed with 437 commands.
docs_updated: Created docs/brain/providers/ollama.md; updated README, .env.example, CHANGELOG, PROJECT_STATE, TRACKER_DASHBOARD, FEATURE_REGISTRY, FEATURE_MATURITY, FEATURE_ROADMAP, COMMAND_REGISTRY, COMMAND_TEST_MATRIX, PROMPT_QUEUE, PROMPT_LEDGER, PROMPT_AUDIT, COMPLETION_REPORT, RISK_REGISTER, THREAT_MODEL, brain provider docs, and brain runtime decision docs.
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
notes: Completed BRAIN-05 Ollama provider scaffold. LM Studio remains default; Ollama is disabled unless explicitly enabled/configured; no Ollama install, model pull/download, daemon startup, default-provider change, cloud API call, MCP enablement, listener startup, memory write, unverified tool-call support, ToolBroker semantic change, or safety-control bypass.
---

# Prompt

You are Codex working in this repo.

Task:
Add Ollama BrainProvider.

Goal:
Support Ollama as an optional local model runtime provider while preserving LM Studio and llama.cpp server behavior.

Scope:
- Provider adapter.
- Config.
- Doctor/status.
- Mocked tests.
- No model pulls/downloads.

Non-goals:
- Do not install Ollama.
- Do not pull models.
- Do not start Ollama daemon.
- Do not change default provider.
- Do not assume full OpenAI compatibility for every feature.
- Do not call cloud APIs.

Create:
- agent/brain/providers/ollama.py
- tests/brain/test_ollama_provider.py
- docs/brain/providers/ollama.md

Config:
- OLLAMA_ENABLED=false
- OLLAMA_BASE_URL=http://localhost:11434
- OLLAMA_MODEL=
- OLLAMA_OPENAI_COMPAT_BASE_URL=http://localhost:11434/v1
- OLLAMA_TIMEOUT_SECONDS=60
- OLLAMA_SUPPORTS_TOOL_CALLS=config-based false by default unless verified
- OLLAMA_SUPPORTS_STREAMING=config-based

Provider behavior:
1. Support OpenAI-compatible endpoint if configured.
2. Optionally support native Ollama endpoint if existing architecture allows; otherwise document as future.
3. Missing model returns setup hint.
4. Daemon unavailable returns clear error.
5. Provider errors normalized.
6. Tool-call support explicit/configurable.
7. No model pull/download.
8. Registry lists provider disabled unless enabled.
9. Health check does not generate text unless explicitly requested.

Commands:
- python smart_agent.py brain doctor --provider ollama
- python smart_agent.py brain health --provider ollama
- python smart_agent.py brain providers

Tests:
- missing model returns setup hint.
- health mock success.
- daemon unavailable handled.
- no-tool chat mock works.
- malformed response handled.
- tool-call unsupported path handled.
- provider registry lists ollama.
- command registry updated.

Update docs/tracking.

Run tests/validations.

Final report:
- provider added
- tests run/results
- next recommended prompt
