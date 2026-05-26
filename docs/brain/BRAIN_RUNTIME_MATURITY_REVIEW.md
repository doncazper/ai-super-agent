# Brain Runtime Maturity Review

Status: conservative maturity review after BRAIN-11 release gate on 2026-05-25.

## Summary

The Brain Runtime Independence track is safe to rely on for provider-neutral metadata, diagnostics, mock-first benchmark/eval evidence, and future-provider scaffolding. It is not yet a fully provider-independent live chat runtime because normal chat still uses the existing LM Studio/Qwopus-compatible path.

## Maturity Table

| Area | Classification | Evidence | Remaining work |
|---|---|---|---|
| Brain runtime strategy | Tested | Architecture, provider strategy, LM Studio decoupling, MCP decision docs, command tracking, and release-gate validation exist | Keep docs updated as the gateway becomes executable |
| BrainProvider interface | Tested | Shared provider models, abstract interface, normalized errors, mock provider, and tests pass | Wire all live chat through a gateway only after separate approval and regression tests |
| Model registry | Tested | Lazy registry, provider status, unknown-provider handling, safe defaults, import guards, and tests pass | Add live setup QA for configured providers |
| LM Studio provider refactor | Tested | `LMStudioBrainProvider` wraps existing `LMStudioClient`; no-tools and tool-call compatibility tests pass | Live no-tools/tool-call smoke should be recorded before user-ready provider switching claims |
| llama.cpp server provider | Tested scaffold | Disabled-by-default provider, setup hints, mocked chat/health, docs, and tests pass | Live user-managed server validation remains opt-in |
| Ollama provider | Tested scaffold | Disabled-by-default provider, setup hints, mocked chat/health, docs, and tests pass | Live user-managed daemon/model validation remains opt-in |
| llama-cpp-python provider | Tested scaffold | Disabled-by-default provider, dependency/model-path gates, fake-backend tests, docs, and tests pass | Real dependency/model validation and isolation review remain future work |
| MLX provider strategy/stub | Tested scaffold | Disabled-by-default non-generating stub, Apple Silicon metadata, docs, and tests pass | Real MLX implementation requires a future approved prompt |
| Health, benchmark, and evals | Tested | Safe mock benchmark/eval/report commands pass and write redacted local reports | Live provider quality baselines remain opt-in |
| Provider fallback/router | Tested scaffold | Metadata-only routing, disabled fallback, dry-run switch, cloud fallback denial, and tests pass | Gateway integration and persisted provider switching remain future work |
| MCP decision/adapters | Tested scaffold | Docs and disabled server/client stubs pass; no listener, external connection, or tools exposed | Real MCP interop requires future policy and ToolBroker routing work |
| Release gate | Tested | BRAIN-11 validation passed with tests, policy/manifest checks, command validation, CLI smokes, and import guard | Broader live/manual validation still required before user-ready classification |

## Conservative Score

Readiness score: 74/100.

The track is locally tested and safety-hardened for scaffold behavior. It is not `Live-Validated`, `User-Ready`, or a `Mature Pattern` for provider switching because alternate providers have not been exercised live and the normal runtime gateway is not fully wired.

## What Is Safe To Rely On

- BrainProvider interface and shared models.
- Lazy model registry and setup hints.
- Existing LM Studio/Qwopus compatibility path.
- Disabled-by-default alternate provider scaffolds.
- Mock-first brain benchmark/eval harness.
- Provider fallback/router policy metadata.
- MCP not-brain-runtime decision and disabled stubs.

## What Is Not Ready Yet

- Fully provider-independent normal chat.
- Automatic fallback after provider failure.
- Persisted provider switching.
- Live alternate-provider quality claims.
- MCP server/client runtime use.
- Cloud or paid provider fallback.

## Next Recommended Work

Run a focused Brain Runtime Gateway wiring prompt only after this batch is reviewed. That prompt should keep LM Studio as the default, route all provider calls through the provider-neutral gateway, preserve no-tools and ToolBroker tool-call behavior, add regression tests for both paths, and avoid any provider install/download or paid/cloud default.
