# LM Studio Decoupling Plan

LM Studio stays supported throughout the Brain Runtime Independence Track. The decoupling work is staged so the current behavior remains the baseline.

## Current Coupling

- `agent/core/orchestrator.py` accepts an `LMStudioClient`.
- `agent/core/lmstudio_client.py` builds OpenAI-compatible chat completion payloads.
- CLI setup docs assume LM Studio at `http://localhost:1234/v1`.

## Staged Plan

1. Document the provider-neutral architecture.
2. Add a `BrainProvider` interface and model/provider registry without changing runtime behavior. Complete in `BRAIN-02`.
3. Wrap LM Studio behind an `LMStudioBrainProvider` while preserving payloads, errors, and tests. Complete in `BRAIN-03`.
4. Change the orchestrator to accept provider-neutral responses while preserving the existing OpenAI-compatible ToolBroker loop. Complete in `BRAIN-03`.
5. Add local provider stubs and implementations one at a time.
6. Add health, benchmark, quality, and fallback checks.
7. Run release gate before changing defaults.

## Compatibility Rules

- Existing `LMSTUDIO_*` environment variables continue to work.
- No-tools chat output path must not attach tools.
- Tool-call payloads must remain compatible with ToolBroker execution.
- LM Studio errors should remain clear and actionable.
- Startup must not import optional runtime packages.
- Full tests must pass after the LM Studio provider refactor.

## BRAIN-03 Compatibility Result

- `LMStudioClient` remains available as the low-level compatibility wrapper.
- `LMStudioBrainProvider` delegates request construction and HTTP behavior to `LMStudioClient`.
- `LMSTUDIO_BASE_URL`, `LMSTUDIO_MODEL`, `LMSTUDIO_TEMPERATURE`, `LMSTUDIO_TOP_P`, and `LMSTUDIO_MAX_TOKENS` continue to work.
- The orchestrator can consume `BrainChatResponse` while still presenting OpenAI-shaped tool calls to `ToolBroker`.
- `brain providers`, `brain status`, and `brain doctor` are metadata-only diagnostics and do not generate model text.

## Stop Conditions

Stop if a change requires installing a runtime, downloading a model, enabling MCP, calling paid/cloud APIs, starting a network listener, weakening safety controls, or changing normal chat behavior without tests.
