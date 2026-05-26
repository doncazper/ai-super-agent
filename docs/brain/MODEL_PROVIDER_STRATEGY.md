# Model Provider Strategy

Provider support is local-first, explicit, and lazy. LM Studio remains the current default provider. llama.cpp server, Ollama, and llama-cpp-python in-process scaffolds are available only when explicitly configured, and all remain disabled by default. Provider fallback and routing now exist as metadata-only/dry-run decision logic; fallback remains disabled by default and does not execute model calls.

| Provider | Role | Default | Notes |
|---|---|---:|---|
| LM Studio | Current local provider and compatibility baseline | enabled when configured | Must preserve existing Qwopus/no-tool/tool-call behavior. |
| llama.cpp server | Local OpenAI-compatible provider scaffold | disabled | Uses a user-managed local server; the agent must not install, download models, or start it by default. |
| Ollama | Local daemon provider scaffold | disabled | Uses a user-managed local daemon; the agent must not install, pull models, or start it by default. |
| llama-cpp-python | Optional in-process local provider scaffold | disabled | Optional dependency only; dependency detection avoids startup imports, health checks do not load models, and chat loads lazily only when explicitly requested. |
| MLX | Apple Silicon experimental strategy/stub | disabled | Stubbed in BRAIN-07; no MLX install, model download, native import, server start, model load, or text generation by default. |
| Cloud API | Optional/stubbed fallback | disabled | Paid/cloud providers are forbidden by default and require explicit config plus future policy review. |
| Mock/test | Deterministic tests and evals | test only | Required before provider routing/fallback changes. |

## Selection Principles

- Prefer the explicitly configured local provider.
- Never fall back from local to paid/cloud automatically.
- Return setup hints when no provider is configured.
- Keep no-tools mode independent of tool attachment.
- Treat provider output as model output, not authority to approve tools or policy changes.
- Record provider decisions in diagnostics/evals where useful without storing prompt history by default.

## Fallback Principles

Fallback must be deterministic and explainable. A fallback may occur only between configured providers that are allowed by policy. Fallback must not hide quality regressions, missing tools, paid API use, or cloud egress.

See `docs/brain/PROVIDER_FALLBACK_POLICY.md` and `docs/brain/MODEL_ROUTING_POLICY.md` for the current BRAIN-09 rules.
