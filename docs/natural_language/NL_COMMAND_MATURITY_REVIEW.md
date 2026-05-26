# Natural-Language Command Understanding Maturity Review

Date: 2026-05-25

## Summary

Natural-Language Command Understanding is locally tested and safe as an advisory layer. It maps loose requests to command-registry-backed suggestions, clarifications, or preflight plans, but it does not execute mapped commands, consume approvals, call providers, access personal data, or write memory.

Overall maturity: **4 Tested**.

Readiness score: **74 / 100**.

## Component Maturity

| Component | Maturity | Evidence | Notes |
|---|---|---|---|
| NL architecture/taxonomy | Specified | `docs/natural_language/NL_COMMAND_UNDERSTANDING_TRACK.md`, taxonomy, safety policy, decision record | Docs-only foundation |
| Command intent index | Tested | `agent.commands.intent_index`, `commands intents`, `commands suggest`, tests | Metadata-only; no execution |
| Parser/router | Tested | `agent.natural_language.parser/router/safety`, tests | Deterministic-first route decisions |
| Clarification flow | Tested | clarification and preview helpers, tests | Redacted previews; no commands executed |
| Preflight/execution plan | Tested | `nl preflight/explain/suggest`, tests | `safe_to_execute` remains conservative |
| CLI UX | Tested | `nl "<request>"`, `ask "<request>"`, tests | Conversational explanation only |
| Eval fixtures | Tested | `eval_cases/natural_language`, `eval run --natural-language`, tests | Fixture-backed; no mapped command execution |
| Dogfood suite | Tested | `natural_language_core`, `natural_language_risky`, runbook, tests | Risky suite is preflight-only |
| Bug feedback loop | Tested | `feedback nl-bug`, `bugs create-nl-regression`, `nl regressions list`, tests | Redacted local QA artifacts |
| Release gate | Tested | `NL_COMMAND_RELEASE_GATE.md`, full suite, policy/manifest/registry/eval/dogfood evidence | No live/manual user-ready claim |

## What Is User-Ready

- Asking for a safe command explanation with `nl "<request>"` or `ask "<request>"`.
- Building a no-execution preflight with `nl preflight "<request>"`.
- Running fixture evals with `eval run --natural-language`.
- Running local NL dogfood suites.
- Capturing NL misunderstanding feedback into redacted bug/fixture artifacts.

## What Is Not User-Ready

- Silent or automatic execution from loose natural-language requests.
- Personal-data command execution from natural language.
- HIGH/CRITICAL action execution from natural language.
- LLM-only routing or safety decisions.
- Live/manual UX maturity claims.

## Next Maturity Work

1. Run a real manual NL dogfood session with feedback attached.
2. Review generated NL regression fixtures and promote useful cases into the checked-in eval set.
3. Add a docs validator or wire docs validation into an existing release-gate command.
4. Continue broader release hardening before adding natural-language execution modes.
